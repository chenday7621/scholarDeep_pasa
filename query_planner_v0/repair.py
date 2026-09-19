"""Generic bounded recovery for failed stages; never edits a generated query by hand."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from query_planner_v0.generate import ROOT,deny_network,parse_output,validate,ground_extraction,digest

SINGLE='''Generate ONE concise English academic search query for the assigned facet, using only the original question and extracted constraints. Preserve explicit named entities and task restrictions relevant to this facet. Do not invent a benchmark, dataset, model, method, or technical mechanism. Do not merely replace papers with research. Do not broaden away the core task. Return ONLY a JSON object with query (string) and covered_constraints (array of constraint FIELD NAMES). Do not return a facet label, list, Search/Expand tag, explanation, or search results. The facet assignment is managed by the program. Do not include site/date operators.
USER QUESTION: {question}
CONSTRAINTS: {constraints}
ASSIGNED FACET: {facet}
ALL PLANNED FACETS (different roles): {facets}
'''

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--results',default=str(ROOT/'CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json'))
    p.add_argument('--artifacts',default='/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0/repair')
    p.add_argument('--batch-size',type=int,default=8)
    a=p.parse_args();data=json.loads(Path(a.results).read_text());folder=Path(a.artifacts);folder.mkdir(parents=True,exist_ok=True)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    sys.addaudithook(deny_network)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    path=data['generation_metadata']['checkpoint'];torch.manual_seed(42);torch.cuda.manual_seed_all(42)
    t=AutoTokenizer.from_pretrained(path,local_files_only=True,padding_side='left')
    m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,torch_dtype='auto',device_map={'':0});m.eval()
    prompts=json.loads(Path(__file__).with_name('prompts.json').read_text())
    meta={'policy':'After primary three-attempt failure, retry extraction/facets at most three times; replace a failed five-query batch with five independently generated facet-bound queries, at most three attempts each. Successful primary rows are unchanged.','seed':42,'script_sha256':digest(__file__),'single_facet_prompt':SINGLE,'checkpoint':path,'batch_size':a.batch_size}
    (folder/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    def batch(tasks,prefix,max_tokens,check):
        passed={}
        for task in tasks:
            f=folder/(task['key']+'.json')
            if f.exists():
                old=json.loads(f.read_text())
                if old['status']=='PASS':passed[task['key']]=check(task,old['parsed'])[0]
        todo=[x for x in tasks if x['key'] not in passed]
        for start in range(0,len(todo),a.batch_size):
            work=[dict(x,attempts=[]) for x in todo[start:start+a.batch_size]]
            for attempt in range(1,4):
                if not work:break
                texts=[t.apply_chat_template([{'role':'user','content':w['prompt']}],tokenize=False,add_generation_prompt=True)+prefix for w in work]
                x=t(texts,padding=True,return_tensors='pt').to(m.device);begin=time.perf_counter()
                with torch.inference_mode():y=m.generate(**x,max_new_tokens=max_tokens)
                raws=t.batch_decode(y[:,x['input_ids'].shape[1]:],skip_special_tokens=True);elapsed=time.perf_counter()-begin
                next_work=[]
                for w,raw in zip(work,raws):
                    raw=prefix+raw;error=None;obj=None;rejected=[]
                    try:obj,rejected=check(w,parse_output(raw))
                    except (ValueError,KeyError,TypeError) as e:error=str(e)
                    w['attempts'].append({'attempt':attempt,'prompt':w['prompt'],'assistant_prefix':prefix,'raw_output':raw,'validation_error':error,'rejected_ungrounded_extractions':rejected,'batch_latency_seconds':elapsed})
                    record={'query_id':w['row']['query_id'],'status':'FAIL' if error else 'PASS','stage':w['stage'],'parsed':obj,'attempts':w['attempts']}
                    (folder/(w['key']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
                    print(w['key'],record['status'],error or '',flush=True)
                    if error:
                        w['prompt']+='\nValidation error: '+error+'. Return corrected JSON only with the exact requested fields.';next_work.append(w)
                    else:passed[w['key']]=obj
                work=next_work
        return passed
    for stage,field,prefix in [('extract','constraint_json','{"topic":'),('facets','planned_facets','[{"facet":')]:
        tasks=[]
        for i,row in enumerate(data['rows']):
            if row.get(field):continue
            if stage=='facets' and not row.get('constraint_json'):continue
            prompt=prompts[stage].format(question=row['user_question'],constraints=json.dumps(row['constraint_json']),facets='[]')
            tasks.append({'key':f'{i:02d}_{stage}','stage':stage,'row':row,'prompt':prompt})
        def check(task,obj):
            rejected=[]
            if stage=='extract':obj,rejected=ground_extraction(obj,task['row']['user_question'])
            return validate(stage,obj,task['row']['user_question']),rejected
        got=batch(tasks,prefix,1200,check)
        for task in tasks:
            if task['key'] in got:task['row'][field]=got[task['key']]
    tasks=[]
    for i,row in enumerate(data['rows']):
        if row['constraint_queries'] or len(row['planned_facets'])!=5:continue
        for j,facet in enumerate(row['planned_facets']):
            tasks.append({'key':f'{i:02d}_query_{j+1}','stage':'single_facet_query','row':row,'facet':facet,'index':j,'prompt':SINGLE.format(question=row['user_question'],constraints=json.dumps(row['constraint_json']),facet=json.dumps(facet),facets=json.dumps(row['planned_facets']))})
    def check_query(task,obj):
        if not isinstance(obj,dict) or set(obj)!= {'query','covered_constraints'}:raise ValueError('Exactly query and covered_constraints keys required')
        result=dict(obj,facet=task['facet']['facet'])
        # Reuse full query validation with a synthetic five-label scaffold; the
        # actual query is unmodified and its real facet is assigned externally.
        scaffold=[dict(result,facet=f'check_{j}') for j in range(5)]
        validate('generate',scaffold,task['row']['user_question'],[{'facet':f'check_{j}'} for j in range(5)])
        if '[' in result['query'] or ']' in result['query']:raise ValueError('Action tags are not search query text')
        return obj,[]
    got=batch(tasks,'{"query":',350,check_query)
    grouped={}
    for task in tasks:
        if task['key'] in got:
            grouped.setdefault(task['row']['query_id'],[]).append((task['index'],dict(got[task['key']],facet=task['facet']['facet'])))
    for row in data['rows']:
        if not row['constraint_queries'] and len(grouped.get(row['query_id'],[]))==5:
            row['constraint_queries']=[q for _,q in sorted(grouped[row['query_id']])]
            row['generation_path']='single_facet_recovery'
        else:row.setdefault('generation_path','primary_three_stage')
        row['generation_status']='PASS' if len(row['constraint_queries'])==5 else 'FAIL'
    data['generation_success_count']=sum(r['generation_status']=='PASS' for r in data['rows']);data['recovery_metadata']=meta
    Path(a.results).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('FINAL SUCCESS',data['generation_success_count'],'/',len(data['rows']),flush=True)

if __name__=='__main__':main()
