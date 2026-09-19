"""Independent offline V1.1 generation probe; never imports PaSa pipeline code."""
import argparse
import ast
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(__file__).resolve().parent
OUT=ROOT/'QUERY_PLANNER_V1_1_GENERATION_PROBE_001.json'
REPORT=ROOT/'QUERY_PLANNER_V1_1_GENERATION_PROBE_001.md'
MANUAL=ROOT/'QUERY_PLANNER_V1_1_GENERATION_MANUAL_REVIEW.md'
DATA=Path('/mnt/nvme3/chenyi/pasa/data/RealScholarQuery/test.jsonl')
CHECKPOINT=Path('/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler')
B_TEMPLATE='''Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.

Keep explicit important entities, benchmarks, methods, comparison relations, exclusions, and negations from the User Query in the search queries. Avoid introducing unsupported specific models, datasets, methods, or benchmarks.

Please return only [Search] queries followed by [StopSearch].

User Query: {user_query}'''

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def read(path=OUT):return json.loads(Path(path).read_text())

def questions():
    result=[]
    # Only decode the question JSON string, never the complete GT-containing record.
    for i,line in enumerate(DATA.open()):
        m=re.search(r'"question"\s*:\s*',line);assert m
        question,_=json.JSONDecoder().raw_decode(line[m.end():]);assert isinstance(question,str)
        result.append({'query_index':i,'query_id':f'Q{i}','original_question':question})
    assert len(result)==50
    return result

def native_spec():
    source=(ROOT/'paper_agent.py').read_text();tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PaperAgent')
    init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    defaults=dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):],init.args.defaults))
    cap=ast.literal_eval(defaults['search_queries']);pattern=None
    for node in ast.walk(init):
        if isinstance(node,ast.Dict):
            for k,v in zip(node.keys,node.values):
                if isinstance(k,ast.Constant) and k.value=='search_template':pattern=ast.literal_eval(v)
    assert cap==5 and pattern
    search=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='search')
    return pattern,cap,ast.get_source_segment(source,search)

def protected():
    files=list(ROOT.glob('*.py'))+[ROOT/'agent_prompt.json',ROOT/'BASELINE_REALScholarQuery50.md',DATA]
    files+=list((ROOT/'query_planner_v0').glob('*.py'))+list((ROOT/'query_planner_v0').glob('*.json'))
    files += [ROOT/'QUERY_PLANNER_V1_SEARCH_AB_001.json',ROOT/'QUERY_PLANNER_V1_SEARCH_AB_001.md']
    return {str(p):sha(p) for p in sorted(set(files)) if p.is_file()}

def prepare():
    assert not OUT.exists(),'Refuse to overwrite an existing probe'
    a=read(ROOT/'agent_prompt.json')['generate_query'];pattern,cap,source=native_spec()
    qs=questions()
    for q in qs:
        q['groups']={group:{'prompt':template.format(user_query=q['original_question']).strip()} for group,template in [('A',a),('B',B_TEMPLATE)]}
    p={'dataset':str(DATA),'question_projection_sha256':hashlib.sha256(json.dumps(questions(),ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),
      'checkpoint':str(CHECKPOINT),'A_template':a,'B_template':B_TEMPLATE,'native_parser_regex':pattern,'native_query_cap':cap,'native_search_method_source':source,
      'seed':42,'max_new_tokens':512,'physical_gpu_index':1,'batch_size':1,'protected_before':protected(),
      'input_isolation':'Decode only original question string for Q0-Q49; no GT answers, old model outputs, search results, or previous manual judgments used to generate or score queries. Frozen artifacts are hashed only for integrity.',
      'generation_policy':'Exactly one fresh generation per Q per group; no resampling, repair, format conversion, query padding, or prompt retuning. Reset all RNGs to 42 before each generate; PYTHONHASHSEED=42 at process start.',
      'network_policy':'HF offline/local_files_only; Python audit hook denies Internet socket creation and DNS. No Search, Serper, metadata HTTP, extra LLM/API, Selector, Expand or full PaSa imports.',
      'scope':'Only isolated probe artifacts are written. No baseline/checkpoint/evaluator changes, facet planner, acronym expansion, constraint extraction JSON or repair model; no Git commit.',
      'quality_policy':'No automated semantic or GT-based query-quality judgment. Chinese translations are review-only and never fed into Crawler. Final semantic comparison awaits human review.',
      'redundancy_policy':'Fixed before inference in analysis.py; final native first-5 queries only, within-Q pairs, no deduplication before counting.'}
    save(OUT,{'experiment':'QUERY_PLANNER_V1_1_GENERATION_PROBE_001','status':'prepared','provenance':p,'per_query':qs})
    print('Prepared 50 paired prompts; seed=42, GPU=1, max_new_tokens=512, native cap=5.',flush=True)

def run():
    if os.environ.get('PYTHONHASHSEED')!='42':
        os.environ['PYTHONHASHSEED']='42';os.execv(sys.executable,[sys.executable,str(Path(__file__).resolve()),'run'])
    os.environ.update(CUDA_VISIBLE_DEVICES='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',WANDB_DISABLED='true')
    import socket
    denied=[]
    def audit(event,args):
        if (event=='socket.__new__' and args[1] in (socket.AF_INET,socket.AF_INET6)) or event in ('socket.getaddrinfo','socket.gethostbyname'):
            denied.append(event);raise RuntimeError('Network disabled for generation-only probe')
    sys.addaudithook(audit)
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
    d=read();assert d['status']=='prepared','Refuse to repeat generations'
    assert torch.cuda.is_available()
    p=d['provenance'];p.update(started_utc=now(),python=sys.version,torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0),runner_sha256=sha(Path(__file__)),analysis_sha256_before_inference=sha(WORK/'analysis.py'))
    start=time.monotonic();p['checkpoint_files']={};save(OUT,d)
    for f in sorted(CHECKPOINT.iterdir()):
        if f.is_file():p['checkpoint_files'][f.name]={'bytes':f.stat().st_size,'sha256':sha(f)}
    print('Frozen checkpoint fingerprints complete; loading Crawler only.',flush=True)
    tokenizer=AutoTokenizer.from_pretrained(CHECKPOINT,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(CHECKPOINT,local_files_only=True,torch_dtype='auto',device_map={'':'cuda:0'}).eval()
    p['generation_config_file']=read(CHECKPOINT/'generation_config.json');p['loaded_generation_config']=model.generation_config.to_dict();p['generation_overrides']={'max_new_tokens':512}
    assert model.generation_config.do_sample
    eos=model.generation_config.eos_token_id;eos_ids=eos if isinstance(eos,list) else [eos]
    d['status']='running';save(OUT,d)
    for q in d['per_query']:
        for group,g in q['groups'].items():
            formatted=tokenizer.apply_chat_template([{'role':'user','content':g['prompt'].strip()}],tokenize=False,max_length=992,add_generation_prompt=True)
            inputs=tokenizer([formatted],return_tensors='pt').to(model.device)
            set_seed(42);t=time.monotonic();started=now()
            with torch.inference_mode():output=model.generate(**inputs,max_new_tokens=512)
            ids=output[0,inputs.input_ids.shape[1]:].tolist();raw=tokenizer.decode(ids,skip_special_tokens=True)
            queries=[x.strip() for x in re.findall(p['native_parser_regex'],raw,flags=re.DOTALL)]
            g.update(seed=42,formatted_prompt=formatted,prompt_sha256=hashlib.sha256(formatted.encode()).hexdigest(),input_token_count=inputs.input_ids.shape[1],raw_output=raw,raw_output_with_special_tokens=tokenizer.decode(ids,skip_special_tokens=False),generated_token_ids=ids,generated_token_count=len(ids),ended_with_eos=ids[-1] in eos_ids,all_parsed_queries=queries,queries=queries[:p['native_query_cap']],discarded_queries=queries[p['native_query_cap']:],started_utc=started,finished_utc=now(),generation_seconds=time.monotonic()-t)
            save(WORK/'raw_generations'/f"{q['query_id']}_{group}.json",g)
            save(OUT,d)
        print(f"{q['query_id']}: A={len(q['groups']['A']['queries'])}, B={len(q['groups']['B']['queries'])}; B Expand={'[Expand]' in q['groups']['B']['raw_output']}",flush=True)
    p.update(finished_utc=now(),inference_wall_seconds=time.monotonic()-start,blocked_network_events=denied,protected_after=protected())
    assert p['protected_before']==p['protected_after'],'Frozen inputs changed'
    d['status']='generations_complete';save(OUT,d)
    print('All 100 generations complete. No Search executed.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','run']);args=parser.parse_args();{'prepare':prepare,'run':run}[args.phase]()
