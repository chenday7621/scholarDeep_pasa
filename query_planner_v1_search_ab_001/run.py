"""One fixed live Search-only A/B run. This process never decodes GT answers."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from common import ROOT,WORK,OUT,DATA,CHECKPOINT,B_TEMPLATE,now,sha,save,read,native_search_spec,native_function,protected,project_questions

ENDPOINT='https://google.serper.dev/search'

def prepare():
    assert not OUT.exists(),'Refuse to overwrite an existing experiment'
    a=read(ROOT/'agent_prompt.json')['generate_query']
    pattern,limit,source=native_search_spec()
    _,search_source=native_function('google_search_arxiv_id',{'datetime':dt.datetime})
    queries=project_questions()
    for q in queries:
        q['groups']={group:{'prompt':template.format(user_query=q['original_question']).strip(),'searches':[]} for group,template in [('A',a),('B',B_TEMPLATE)]}
    p={'dataset':str(DATA),'dataset_sha256':sha(DATA),'checkpoint':str(CHECKPOINT),'seed':42,
       'A_template':a,'B_template':B_TEMPLATE,'A_whitespace_policy':'Read exact native agent_prompt.json generate_query string; no reformatting beyond native .strip().',
       'native_search_regex':pattern,'native_search_query_limit':limit,'native_search_method_source':source,'native_serper_function_source':search_source,
       'native_sources':{name:sha(ROOT/name) for name in ('agent_prompt.json','models.py','paper_agent.py','utils.py','metrics.py','run_paper_agent.py')},
       'protected_before':protected(),'generation_isolation':'Only question, qid and publication date are projected; answer/answer_arxiv_id are not decoded by generation/search runner. No GT or previous experiment output enters prompt.',
       'seed_policy':'Reset Python, NumPy, torch and all CUDA RNGs to frozen seed 42 before each individual A/B generation. PYTHONHASHSEED=42 at interpreter start.',
       'search_policy':'Fresh real Serper POST for every generated query, even identical A/B queries. Within Q, generate A then B; alternate Search groups at each query index, A first for even Q and B first for odd Q. No old baseline/page2 replay, cache, query padding or query deduplication.',
       'request_parameters':{'endpoint':ENDPOINT,'page':1,'num':10,'site':'arxiv.org','before_rule':'source_meta.published_time minus 7 days; same run_paper_agent.py logic'},
       'retry_policy':'Up to 3 HTTP attempts per logical query, matching native attempt cap; fixed connect/read timeouts 15/60 seconds, 1/2-second backoff (Retry-After honored up to 30 s). All attempts count as Serper calls; failures are retained, never retried for effectiveness.',
       'evaluation_policy':'After all Search is finished, resolve titles only for directly returned IDs using unmodified native search_paper_by_arxiv_id, shared across A/B. Apply frozen keep_letters/cal_micro. No Selector/Expand. Official Search recall = macro per-Q title recall; also pooled micro and GT found per actual Serper attempt.',
       'scope':'No Citation Expand, Selector, full PaSa, facet planner, acronym expansion, external LLM, page2, baseline/evaluator/checkpoint mutation, GT-based query editing or Git commit.'}
    save(OUT,{'experiment':'QUERY_PLANNER_V1_SEARCH_AB_001','status':'prepared','provenance':p,'per_query':queries})
    print('Prepared 50 question-only A/B prompt pairs; frozen seed 42; page=1 num=10 before=2024-09-24.',flush=True)

def live():
    if os.environ.get('PYTHONHASHSEED')!='42':
        os.environ['PYTHONHASHSEED']='42'
        os.execv(sys.executable,[sys.executable,str(Path(__file__).resolve()),'live'])
    os.environ.update(CUDA_VISIBLE_DEVICES='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',WANDB_DISABLED='true')
    import torch,transformers,requests
    from transformers import AutoModelForCausalLM,AutoTokenizer,set_seed
    from urllib.parse import urlparse
    assert torch.cuda.is_available()
    d=read();assert d['status']=='prepared','No automatic repeat/resume of completed generations or Search'
    key=os.environ.get('SERPER_API_KEY','').strip()
    key_source='SERPER_API_KEY environment'
    if not key:
        key=Path('/mnt/nvme3/chenyi/pasa/secrets/serper_api_key').read_text().strip()
        key_source='local protected serper_api_key file'
    assert key,'Serper credential unavailable'
    p=d['provenance'];p.update(started_utc=now(),python=sys.version,torch=torch.__version__,transformers=transformers.__version__,requests=requests.__version__,gpu=torch.cuda.get_device_name(0),physical_gpu_index=1,batch_size=1,credential_source=key_source,runner_sha256=sha(Path(__file__)),common_sha256=sha(WORK/'common.py'))
    start=time.monotonic();save(OUT,d)
    original_request=requests.sessions.Session.request
    def guarded_request(session,method,url,*args,**kwargs):
        if urlparse(url).hostname!='google.serper.dev' or method.upper()!='POST':
            raise RuntimeError('Only Serper POST is allowed in this generation/Search process')
        return original_request(session,method,url,*args,**kwargs)
    requests.sessions.Session.request=guarded_request
    p['checkpoint_files']={}
    for f in sorted(CHECKPOINT.iterdir()):
        if f.is_file():p['checkpoint_files'][f.name]={'bytes':f.stat().st_size,'sha256':sha(f)}
    print('Frozen checkpoint hashes complete; loading Crawler only.',flush=True)
    tokenizer=AutoTokenizer.from_pretrained(CHECKPOINT,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(CHECKPOINT,local_files_only=True,torch_dtype='auto',device_map={'':'cuda:0'}).eval()
    p['generation_config_file']=read(CHECKPOINT/'generation_config.json');p['effective_generation_config']=model.generation_config.to_dict()
    p['generation_call_overrides']={'max_new_tokens':512}
    assert model.generation_config.do_sample is True
    eos=model.generation_config.eos_token_id;eos_ids=eos if isinstance(eos,list) else [eos]
    client=requests.Session()
    headers={'X-API-KEY':key,'Content-Type':'application/json'}
    sequence=0
    def search_one(q,group,index,text):
        nonlocal sequence
        payload={'q':f"{text} before:{q['before_date']} site:arxiv.org",'num':10,'page':1}
        result={'query_sequence':index+1,'crawler_query':text,'request_payload':payload,'attempts':[],'status':'FAILED','returned_arxiv_ids':[],'organic_hits':[]}
        for attempt in range(1,4):
            sequence+=1
            record={'global_attempt_sequence':sequence,'query_id':q['query_id'],'group':group,'query_sequence':index+1,'attempt':attempt,'request_payload':payload,'started_utc':now()}
            t=time.monotonic();response=None
            try:
                response=client.post(ENDPOINT,headers=headers,data=json.dumps(payload),timeout=(15,60),allow_redirects=False)
                body=response.text
                record.update(http_status=response.status_code,response_text=body,response_sha256=hashlib.sha256(response.content).hexdigest())
                try:structured=response.json()
                except ValueError:structured=None
                record['structured_response']=structured
                if response.status_code!=200:
                    record['status']='HTTP_FAILURE'
                elif not isinstance(structured,dict) or not isinstance(structured.get('organic'),list):
                    record['status']='RESPONSE_SCHEMA_FAILURE'
                else:
                    params=structured.get('searchParameters',{})
                    mismatches={k:{'requested':v,'echoed':params[k]} for k,v in payload.items() if k in params and params[k]!=v}
                    record['echoed_parameter_mismatches']=mismatches
                    if mismatches:record['status']='PARAMETER_MISMATCH'
                    else:
                        hits=[]
                        for rank,hit in enumerate(structured['organic'],1):
                            match=re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)',hit.get('link',''))
                            if match:hits.append({'arxiv_id':match.group(1),'organic_index':rank-1,'position':hit.get('position',rank),'title':hit.get('title'),'link':hit.get('link'),'snippet':hit.get('snippet')})
                        record['status']='PASS';result.update(status='PASS',organic_hits=hits,returned_arxiv_ids=sorted({h['arxiv_id'] for h in hits}),organic_result_count=len(structured['organic']))
            except Exception as exc:
                record.update(status='TRANSPORT_OR_CLIENT_FAILURE',http_status=None,error_type=type(exc).__name__,error_message=str(exc).replace(key,'[REDACTED]'))
            record.update(finished_utc=now(),elapsed_seconds=time.monotonic()-t)
            path=WORK/'requests'/f"{q['query_id']}_{group}_{index+1:02d}_attempt{attempt}.json"
            record['artifact_path']=str(path);save(path,record);result['attempts'].append(record)
            if result['status']=='PASS':break
            if attempt<3:
                pause=float(attempt)
                if response is not None:
                    try:pause=max(pause,min(30,float(response.headers.get('Retry-After','0'))))
                    except ValueError:pass
                time.sleep(pause)
        return result
    d['status']='running'
    for q in d['per_query']:
        qstart=time.monotonic();q['started_utc']=now()
        for group,g in q['groups'].items():
            formatted=tokenizer.apply_chat_template([{'role':'user','content':g['prompt'].strip()}],tokenize=False,max_length=992,add_generation_prompt=True)
            inputs=tokenizer([formatted],return_tensors='pt').to(model.device)
            set_seed(42);gentime=time.monotonic()
            with torch.inference_mode():output=model.generate(**inputs,max_new_tokens=512)
            ids=output[0,inputs.input_ids.shape[1]:].tolist();raw=tokenizer.decode(ids,skip_special_tokens=True)
            all_queries=[x.strip() for x in re.findall(p['native_search_regex'],raw,flags=re.DOTALL)]
            g.update(seed=42,formatted_prompt=formatted,prompt_sha256=hashlib.sha256(formatted.encode()).hexdigest(),raw_output=raw,raw_output_with_special_tokens=tokenizer.decode(ids,skip_special_tokens=False),generated_token_ids=ids,generated_token_count=len(ids),ended_with_eos=ids[-1] in eos_ids,input_token_count=inputs.input_ids.shape[1],generation_seconds=time.monotonic()-gentime,all_parsed_queries=all_queries,queries=all_queries[:5],discarded_queries=all_queries[5:])
        save(WORK/'generations'/f"{q['query_id']}.json",q)
        q['search_order_first_group']='A' if q['query_index']%2==0 else 'B'
        order=['A','B'] if q['search_order_first_group']=='A' else ['B','A']
        searchstart=time.monotonic();q['search_started_utc']=now()
        for index in range(max(len(g['queries']) for g in q['groups'].values())):
            for group in order:
                g=q['groups'][group]
                if index<len(g['queries']):g['searches'].append(search_one(q,group,index,g['queries'][index]))
        q.update(search_finished_utc=now(),search_seconds=time.monotonic()-searchstart,finished_utc=now(),elapsed_seconds=time.monotonic()-qstart)
        save(WORK/'completed_queries'/f"{q['query_id']}.json",q);save(OUT,d)
        print(f"{q['query_id']} complete: A queries={len(q['groups']['A']['queries'])}, B queries={len(q['groups']['B']['queries'])}; logical failures={sum(s['status']!='PASS' for g in q['groups'].values() for s in g['searches'])}; cumulative Serper attempts={sequence}",flush=True)
    p.update(search_finished_utc=now(),generation_search_wall_seconds=time.monotonic()-start,protected_after_search=protected())
    assert p['protected_before']==p['protected_after_search'],'Protected inputs changed'
    d['status']='search_complete';save(OUT,d)
    print('All 50 fresh A/B searches complete. GT evaluation has not run in this process.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','live']);args=parser.parse_args()
    {'prepare':prepare,'live':live}[args.phase]()
