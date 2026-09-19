"""Offline native-search A/B inference. No imports from the PaSa pipeline."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ACRONYM_EXPANSION_PROBE_002.json'
SOURCE = ROOT / 'ACRONYM_EXPANSION_PROBE_001.json'
CHECKPOINT = Path('/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler')
B_INSTRUCTION = ('For acronyms in the user query, always preserve the original acronym. '
                 'When you are confident about its full form, you may also use the full form '
                 'together with the acronym in one of the search queries. Do not guess.')

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def save(data):
    temp = OUT.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    temp.replace(OUT)

def native_spec():
    # Read source as AST, never import/construct PaperAgent (which could invoke tools).
    text = (ROOT/'paper_agent.py').read_text()
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PaperAgent')
    init = next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    defaults = dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):],init.args.defaults))
    limit = ast.literal_eval(defaults['search_queries'])
    patterns = []
    for n in ast.walk(init):
        if isinstance(n,ast.Dict):
            for k,v in zip(n.keys,n.values):
                if isinstance(k,ast.Constant) and k.value=='search_template': patterns.append(ast.literal_eval(v))
    assert len(patterns)==1
    search = next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='search')
    return patterns[0],limit,ast.get_source_segment(text,search)

def snapshot():
    # Hash only protected local code/config and previous experiment artifacts; no GT access.
    paths = list(ROOT.glob('*.py'))+[ROOT/'agent_prompt.json']
    paths += list((ROOT/'query_planner_v0').rglob('*.py'))
    paths += list((ROOT/'query_planner_v0').glob('*.json'))
    paths += list(ROOT.glob('BASELINE*.md'))
    paths += [SOURCE, ROOT/'ACRONYM_EXPANSION_PROBE_001.md', ROOT/'ACRONYM_EXPANSION_MANUAL_REVIEW.md']
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths)) if p.is_file()}

def prepare():
    assert not OUT.exists(), 'Refuse to overwrite an existing experiment'
    src = json.loads(SOURCE.read_text())
    template = json.loads((ROOT/'agent_prompt.json').read_text())['generate_query']
    pattern,limit,parser_source = native_spec()
    samples=[]
    for i,s in enumerate(src['samples']):
        # No previous outputs, review labels or expansions are copied into inputs.
        sample = {k:s[k] for k in ('sample_id','query_id','original_question','acronym','mentions','question_zh')}
        prompt_a = template.format(user_query=s['original_question']).strip()
        sample['groups'] = {g:{'prompt':p,'runs':[]} for g,p in [('A',prompt_a),('B',prompt_a+'\n'+B_INSTRUCTION)]}
        sample['sample_index']=i
        sample['human_review']={'gold_expansion':None,'A_judgment':None,'B_judgment':None,'B_vs_A':None,'notes':None}
        samples.append(sample)
    assert len(samples)==29 and len({s['acronym'] for s in samples})==14
    d={'experiment':'ACRONYM_EXPANSION_PROBE_002','status':'prepared','provenance':{
        'source_path':str(SOURCE),'source_sha256':sha(SOURCE),
        'source_projection_fields':['sample_id','query_id','original_question','acronym','mentions','question_zh'],
        'data_isolation':'Reuse 001 samples and review-only translations; no 001 outputs/gold/judgments enter inference or expansion detection. No GT, audits, papers, search results or network data.',
        'checkpoint':str(CHECKPOINT),'native_prompt_template':template,'B_instruction':B_INSTRUCTION,
        'native_search_regex':pattern,'native_search_query_limit':limit,'native_search_method_source':parser_source,
        'native_source_files':{n:sha(ROOT/n) for n in ('agent_prompt.json','paper_agent.py','models.py','run_paper_agent.py')},
        'protected_files_before':snapshot(),
        'seed_policy':'Independent single-sample generation; seed=2026091300+sample_index*10+(run_number-1). Paired A/B use the same seed; all 145 sample/run seeds are distinct. No reuse across samples sharing a question.',
        'input_policy':'Only complete original question appears in A; B adds exactly the B instruction after a newline. The target acronym is an evaluation field, never an extra prompt field.',
        'translation_policy':'Copied unchanged from 001; review-only, never fed into Crawler.',
        'network_policy':'HF offline + local_files_only; Python audit hook denies AF_INET/AF_INET6 socket creation and DNS throughout inference; no external LLM or API.',
        'execution_policy':'Native Search strings parsed only; no Serper, Selector, Expand, PaperAgent constructor or pipeline import. No baseline/Planner/checkpoint changes, SFT data or git commit.',
        'inference_overrides':{'max_new_tokens':512,'use_cache':True},
        'cache_note':'Enable KV cache for speed; same numerical precision, native prompt/chat template and checkpoint sampling configuration.',
        'analysis_policy':'Expansion attempts are lexical candidates, not verified full forms. No gold dictionary, model judge or automatic correctness label. Detection algorithm is fixed in metrics.py before inference.'},'samples':samples}
    save(d)
    print(json.dumps({'status':d['status'],'samples':len(samples),'unique_acronyms':len({s['acronym'] for s in samples}),'regex':pattern,'limit':limit},ensure_ascii=False))

def run():
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',WANDB_DISABLED='true',CUDA_VISIBLE_DEVICES='1',TOKENIZERS_PARALLELISM='false')
    import socket
    def audit(event,args):
        if event=='socket.__new__' and args[1] in (socket.AF_INET,socket.AF_INET6):
            raise RuntimeError('Internet sockets forbidden for offline probe')
        if event in ('socket.getaddrinfo','socket.gethostbyname'):
            raise RuntimeError('DNS forbidden for offline probe')
    sys.addaudithook(audit)
    import torch
    import transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
    d=json.loads(OUT.read_text())
    assert d['status']=='prepared','Refuse to overwrite generations'
    assert torch.cuda.is_available()
    p=d['provenance']
    p.update(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0),physical_gpu_index=1,batch_size=1,
             inference_script_sha256=sha(Path(__file__)),metrics_script_sha256_at_inference=sha(Path(__file__).with_name('metrics.py')))
    p['checkpoint_files']={}
    for f in sorted(CHECKPOINT.iterdir()):
        if f.is_file(): p['checkpoint_files'][f.name]={'bytes':f.stat().st_size,'sha256':sha(f)}
    print('Checkpoint fingerprints complete',flush=True)
    tokenizer=AutoTokenizer.from_pretrained(CHECKPOINT,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(CHECKPOINT,local_files_only=True,torch_dtype='auto',device_map={'':'cuda:0'}).eval()
    p['generation_config_file']=json.loads((CHECKPOINT/'generation_config.json').read_text())
    p['loaded_generation_config']=model.generation_config.to_dict()
    assert model.generation_config.do_sample is True
    eos=model.generation_config.eos_token_id
    eos_ids=eos if isinstance(eos,list) else [eos]
    d['status']='running'
    for s in d['samples']:
        for group,g in s['groups'].items():
            g['formatted_prompt']=tokenizer.apply_chat_template([{'role':'user','content':g['prompt'].strip()}],tokenize=False,max_length=992,add_generation_prompt=True)
            g['prompt_sha256']=hashlib.sha256(g['formatted_prompt'].encode()).hexdigest()
    save(d)
    for s in d['samples']:
        encoded={group:tokenizer([g['formatted_prompt']],return_tensors='pt').to(model.device) for group,g in s['groups'].items()}
        for run_number in range(1,6):
            seed=2026091300+s['sample_index']*10+run_number-1
            for group,g in s['groups'].items():
                set_seed(seed)
                inputs=encoded[group]
                with torch.inference_mode():
                    result=model.generate(**inputs,max_new_tokens=512,use_cache=True)
                ids=result[0,inputs.input_ids.shape[1]:].tolist()
                raw=tokenizer.decode(ids,skip_special_tokens=True)
                all_queries=[q.strip() for q in re.findall(p['native_search_regex'],raw,flags=re.DOTALL)]
                queries=all_queries[:p['native_search_query_limit']]
                g['runs'].append({'run':run_number,'seed':seed,'prompt_sha256':g['prompt_sha256'],'raw_output':raw,
                    'raw_output_with_special_tokens':tokenizer.decode(ids,skip_special_tokens=False),
                    'generated_token_ids':ids,'generated_token_count':len(ids),'ended_with_eos':ids[-1] in eos_ids,
                    'input_token_count':inputs.input_ids.shape[1],'all_parsed_search_queries':all_queries,'search_queries':queries,
                    'discarded_queries_by_native_cap':all_queries[p['native_search_query_limit']:]})
            save(d)
        print(f"Completed {s['sample_index']+1}/29 {s['sample_id']}: A {sum(bool(r['search_queries']) for r in s['groups']['A']['runs'])}/5 parsed, B {sum(bool(r['search_queries']) for r in s['groups']['B']['runs'])}/5 parsed",flush=True)
    p['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p['protected_files_after']=snapshot()
    assert p['protected_files_before']==p['protected_files_after'],'Protected files changed during experiment'
    d['status']='generations_complete'
    save(d)

if __name__=='__main__':
    {'prepare':prepare,'run':run}[sys.argv[1]]()
