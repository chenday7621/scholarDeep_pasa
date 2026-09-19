"""Standalone offline query generation. Never imports the PaSa search pipeline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('topic', 'task', 'method', 'model', 'dataset', 'benchmark', 'domain', 'evaluation')
ARRAY_FIELDS = ('negative_constraints', 'important_entities')
ALL_FIELDS = set(FIELDS + ARRAY_FIELDS)

def deny_network(event, args):
    if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo'):
        if event == 'socket.getaddrinfo' or args[0].family != socket.AF_UNIX:
            raise RuntimeError('Offline planner prohibits network access')

def canonical(s):
    return ' '.join(s.lower().split())

def parse_output(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    obj,end=json.JSONDecoder().raw_decode(text)
    tail=text[end:].strip()
    # PaSa may append an action after an otherwise complete JSON value.
    # Keep that text in raw logs; never execute it or turn it into a query.
    if tail and not re.fullmatch(r'(?:\[(?:Search|Expand)\][\s\S]*?\[Stop(?:Search|Expand)\]\s*)+',tail):
        raise ValueError('Unexpected text after JSON')
    return obj

def validate(stage, obj, question, facets=None):
    if stage == 'extract':
        if not isinstance(obj, dict) or set(obj) != ALL_FIELDS:
            raise ValueError('Extraction must have exactly the ten specified fields')
        for k in FIELDS:
            if not isinstance(obj[k], str):
                raise ValueError(f'{k} must be a string')
        for k in ARRAY_FIELDS:
            if not isinstance(obj[k], list) or any(not isinstance(x, str) for x in obj[k]):
                raise ValueError(f'{k} must be a string array')
        for k,v in obj.items():
            for text in (v if isinstance(v, list) else [v]):
                if text and canonical(text) not in canonical(question):
                    raise ValueError(f'{k}: non-verbatim constraint {text!r}')
    else:
        if not isinstance(obj, list) or len(obj) != 5:
            raise ValueError('Exactly five objects required')
        names = []
        for i,x in enumerate(obj):
            keys = {'facet','focus','required_constraints'} if stage == 'facets' else {'query','facet','covered_constraints'}
            if not isinstance(x, dict) or set(x) != keys:
                raise ValueError(f'Invalid {stage} object fields')
            for k in ('facet', 'focus' if stage == 'facets' else 'query'):
                if not isinstance(x[k], str) or not x[k].strip():
                    raise ValueError(f'{k} must be nonempty text')
            field = 'required_constraints' if stage == 'facets' else 'covered_constraints'
            if not isinstance(x[field], list) or any(not isinstance(k,str) or k not in ALL_FIELDS for k in x[field]):
                raise ValueError('Unknown constraint field')
            names.append(x['facet'])
            if stage == 'generate':
                if x['facet'] != facets[i]['facet']:
                    raise ValueError('Facet assignment/order changed')
                if not re.search('[a-zA-Z]', x['query']) or re.search('[\u4e00-\u9fff]', x['query']):
                    raise ValueError('Query must be English')
                if re.search(r'\b(?:site|before|after):', x['query']):
                    raise ValueError('Search operators are not part of this generation task')
                if len(x['query'].split()) > 48:
                    raise ValueError('Query exceeds 48-word safety limit')
        if len(set(names)) != 5:
            raise ValueError('Facet labels must be unique')
    return obj

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ground_extraction(obj, question):
    """Reject unsupported model extractions, without inventing replacement values."""
    if not isinstance(obj,dict) or set(obj)!=ALL_FIELDS:
        return obj,[]
    rejected=[];out={}
    for key,value in obj.items():
        if key in ARRAY_FIELDS and isinstance(value,list):
            out[key]=[]
            for item in value:
                if isinstance(item,str) and canonical(item) in canonical(question):out[key].append(item)
                else:rejected.append({'field':key,'value':item})
        elif isinstance(value,str):
            out[key]=value if canonical(value) in canonical(question) else ''
            if value and not out[key]:rejected.append({'field':key,'value':value})
        else:out[key]=value
    return out,rejected

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint', default='/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler')
    p.add_argument('--baseline', default='/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/summary.json')
    p.add_argument('--artifacts', default='/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0')
    p.add_argument('--output', default=str(ROOT/'CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json'))
    p.add_argument('--batch-size', type=int, default=4)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--smoke', action='store_true', help='Use one synthetic question, never a benchmark item')
    a = p.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    sys.addaudithook(deny_network)
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); torch.cuda.manual_seed_all(a.seed)
    prompts_path = Path(__file__).with_name('prompts.json')
    prompts = json.loads(prompts_path.read_text())
    outdir=Path(a.artifacts)/('smoke' if a.smoke else 'run')
    outdir.mkdir(parents=True,exist_ok=True)
    if a.smoke:
        rows=[{'query_id':'synthetic_format_check','user_question':'Find papers using graph neural networks for molecular property prediction evaluated on QM9. Exclude surveys.','baseline_queries':[]}]
    else:
        # Ground-truth answers and results never enter any model prompt.
        questions=[{'query_id':d['qid'],'user_question':d['question']} for d in map(json.loads,(ROOT/'data/RealScholarQuery/test.jsonl').read_text().splitlines())]
        summary=json.loads(Path(a.baseline).read_text())
        smokes={q['query_id']:q['smoke_report_path'] for q in summary['queries']}
        rows=[]
        for row in questions:
            f=smokes[row['query_id']];s=json.loads(Path(f).read_text())
            row.update(baseline_queries=s['crawler_generated_search_queries'],baseline_provenance={'smoke_report':f,'sha256':digest(f)},constraint_json={},planned_facets=[],constraint_queries=[])
            rows.append(row)
    manifest={'checkpoint':a.checkpoint,'seed':a.seed,'batch_size':a.batch_size,'max_new_tokens':1200,'prompt_sha256':digest(prompts_path),'script_sha256':digest(__file__),'sampling':'checkpoint generation_config without overrides','network':'socket network access blocked; HF offline/local_files_only','baseline_regenerated':False}
    manifest_file=outdir/'manifest.json'
    if manifest_file.exists() and json.loads(manifest_file.read_text()) != manifest:
        raise RuntimeError('Existing run has a different configuration; use a new artifacts directory')
    manifest_file.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Loading existing local Crawler checkpoint',flush=True)
    tokenizer=AutoTokenizer.from_pretrained(a.checkpoint,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(a.checkpoint,local_files_only=True,torch_dtype='auto',device_map={'':0})
    model.eval()
    manifest['actual_generation_config']=model.generation_config.to_dict()
    stage_keys={'extract':'constraint_json','facets':'planned_facets','generate':'constraint_queries'}
    for stage in stage_keys:
        pending=[]
        for i,row in enumerate(rows):
            file=outdir/f'{i:02d}_{stage}.json'
            if file.exists():
                record=json.loads(file.read_text())
                if record['status']=='PASS':
                    row[stage_keys[stage]]=validate(stage,record['parsed'],row['user_question'],row.get('planned_facets'))
                    continue
            if stage!='extract' and not row.get('constraint_json'):
                continue
            if stage=='generate' and not row.get('planned_facets'):
                continue
            pending.append(i)
        for start in range(0,len(pending),a.batch_size):
            indexes=pending[start:start+a.batch_size]
            work=[]
            for i in indexes:
                row=rows[i]
                prompt=prompts[stage].format(question=row['user_question'],constraints=json.dumps(row.get('constraint_json',{}),ensure_ascii=False),facets=json.dumps(row.get('planned_facets',[]),ensure_ascii=False))
                work.append({'i':i,'prompt':prompt,'attempts':[]})
            for attempt in range(1,4):
                if not work:break
                prefix={'extract':'{"topic":','facets':'[{"facet":','generate':'[{"query":'}[stage]
                texts=[tokenizer.apply_chat_template([{'role':'user','content':w['prompt']}],tokenize=False,add_generation_prompt=True)+prefix for w in work]
                inputs=tokenizer(texts,padding=True,return_tensors='pt').to(model.device)
                t=time.perf_counter()
                with torch.inference_mode():
                    outputs=model.generate(**inputs,max_new_tokens=1200)
                raw=tokenizer.batch_decode(outputs[:,inputs['input_ids'].shape[1]:],skip_special_tokens=True)
                elapsed=time.perf_counter()-t
                again=[]
                for w,text in zip(work,raw):
                    text=prefix+text
                    row=rows[w['i']];error=None;obj=None;rejected=[]
                    try:
                        obj=parse_output(text)
                        if stage=='extract':obj,rejected=ground_extraction(obj,row['user_question'])
                        obj=validate(stage,obj,row['user_question'],row.get('planned_facets'))
                    except (ValueError,TypeError,KeyError) as e:error=str(e)
                    w['attempts'].append({'attempt':attempt,'prompt':w['prompt'],'assistant_prefix':prefix,'raw_output':text,'rejected_ungrounded_extractions':rejected,'validation_error':error,'batch_latency_seconds':elapsed})
                    record={'query_id':row['query_id'],'stage':stage,'status':'FAIL' if error else 'PASS','parsed':obj,'attempts':w['attempts']}
                    (outdir/f"{w['i']:02d}_{stage}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
                    print(json.dumps({'id':row['query_id'],'stage':stage,'attempt':attempt,'status':record['status'],'error':error}),flush=True)
                    if error:
                        w['prompt'] += '\nYour previous response failed validation: '+error+'\nReturn a corrected JSON response only, using the same original inputs.'
                        again.append(w)
                    else:row[stage_keys[stage]]=obj
                work=again
    for row in rows:
        row['generation_status']='PASS' if len(row.get('constraint_queries',[]))==5 else 'FAIL'
    result={'experiment':'CONSTRAINT_QUERY_PLANNER_V0','generation_metadata':manifest,'dataset_size':len(rows),'generation_success_count':sum(r['generation_status']=='PASS' for r in rows),'search_calls':0,'rows':rows}
    dest=outdir/'results.json' if a.smoke else Path(a.output)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'RESULTS={dest} SUCCESS={result["generation_success_count"]}/{len(rows)}',flush=True)

if __name__=='__main__':main()
