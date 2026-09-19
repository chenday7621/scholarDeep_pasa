"""Independent read-only reconstruction. Writes only validation.json; no Search or model calls."""
import base64, hashlib, json, math, random, re
from datetime import datetime
from pathlib import Path
from common import ROOT, REPO, read, sha, digest, save, now


def main():
    checks={}
    def check(name,condition):
        checks[name]=bool(condition)
        assert condition,name
    try:
        reg=read(ROOT/'registration_manifest.json'); dataset=read(ROOT/'dataset_manifest.json'); snapshot=read(ROOT/'snapshot_manifest.json'); run=read(ROOT/'run_manifest.json')
        for name,h in reg['frozen_files'].items(): check('frozen_file:'+name,sha(ROOT/name)==h)
        for name,h in reg['protected_sources'].items(): check('protected_source:'+name,sha(REPO/name)==h)
        check('dataset_hash',sha(ROOT/'dataset_manifest.json')==snapshot['dataset_manifest_sha256'])
        check('original_official_file_hash',sha(ROOT/'source/ScholarQuest.jsonl')==dataset['source_sha256'])
        rows=[json.loads(l) for l in (ROOT/'source/ScholarQuest.jsonl').read_text().splitlines() if l.strip()]
        eligible=[i for i,r in enumerate(rows) if isinstance(r.get('final_query'),str) and r['final_query'].strip() and isinstance(r.get('answer_arxiv_ids'),list) and r['answer_arxiv_ids']]
        chosen=random.Random(20260919).sample(eligible,50)
        check('sample_reproduced',chosen==[q['source_row_index'] for q in dataset['sample']])
        check('eligible_pool_exact',eligible==dataset['eligible_source_row_indices'] and len(eligible)==dataset['eligible_rows']==len(rows)==1111)
        check('sample_hash',digest(dataset['sample'])==dataset['sample_sha256']==snapshot['sample_sha256'])
        check('unique_fifty_questions',len(dataset['sample'])==len(set(chosen))==50)
        for name,h in snapshot['files'].items(): check('snapshot_file:'+name,sha(ROOT/name)==h)
        check('snapshot_identity',digest(snapshot['files'])==snapshot['snapshot_id'])
        check('all_attempts_frozen',set('attempts/'+p.name for p in (ROOT/'attempts').glob('*.json'))=={p for p in snapshot['files'] if p.startswith('attempts/')})
        attempts={p:read(ROOT/p) for p in snapshot['files'] if p.startswith('attempts/')}
        sequence=[x['global_http_attempt_sequence'] for x in attempts.values()]
        check('unique_contiguous_http_sequence',sorted(sequence)==list(range(1,len(sequence)+1)))
        check('run_complete',run['status']=='SNAPSHOT_COMPLETE')
        check('collector_code_hash',sha(ROOT/'collect.py')==run['runner_sha256'])
        check('checkpoint_provenance',all(sha(Path(run['checkpoint'])/n)==v['sha256'] for n,v in run['checkpoint_files'].items()))
        config=run['effective_generation_config']
        expected={'do_sample':True,'temperature':0.7,'top_p':0.8,'top_k':20,'repetition_penalty':1.05}
        check('native_generation_config',all(config[k]==v for k,v in expected.items()) and run['generation_call_override']=={'max_new_tokens':512} and run['model_seed_per_question']==42)
        questions=read(ROOT/'questions.json')['questions']; prompt_template=read(REPO/'agent_prompt.json')['generate_query']
        oq=read(ROOT/'query_outcomes.json')['queries']; outcomes={(x['question_id'],x['query_index']):x for x in oq}
        question_output=read(ROOT/'question_outcomes.json')['questions']; qout={q['question_id']:q for q in question_output}
        totals={'gt':0,'p1':0,'p12':0,'gain_questions':0,'gain_queries':0,'pair_gain_queries':0,'queries':0}; macro1=[];macro12=[];expected_keys=set(); response_keys=set(); generation_keys=set();gaps=[]
        adherence={str(p):{'organic_results':0,'parseable_arxiv_results':0,'queries_with_non_arxiv_results':0} for p in (1,2)}
        all_starts=[]
        def idset(record):
            # Independent implementation of the unchanged modern arXiv URL parser.
            found=set()
            for item in record['structured_response']['organic']:
                match=re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)',item.get('link',''))
                if match: found.add(match.group(1))
            return found
        for j,q in enumerate(dataset['sample']):
            qid=q['question_id']; source=rows[chosen[j]]
            gold={re.sub(r'v\d+$','',x) for x in source['answer_arxiv_ids']}
            check(qid+':source_identity',q['source_record_sha256']==digest(source) and q['source_query_id']==source['query_id'] and q['question']==source['final_query'] and q['answer_arxiv_ids']==source['answer_arxiv_ids'] and q['gt_arxiv_ids']==sorted(gold))
            check(qid+':gold_free_generation_input',questions[j]=={'question_id':qid,'source_query_id':source['query_id'],'question':source['final_query']})
            gen=read(ROOT/'generations'/f'{qid}.json'); generation_keys.add(f'generations/{qid}.json')
            raw=gen['raw_output']; parsed=[s.strip() for s in re.findall(r'Search\](.*?)\[',raw,flags=re.DOTALL)]
            check(qid+':original_prompt_parser',gen['status']=='PASS' and gen['seed']==42 and gen['prompt']==prompt_template.format(user_query=q['question']).strip() and gen['queries']==parsed[:5] and gen['all_parsed_queries']==parsed and 1<=len(gen['queries'])<=5)
            check(qid+':generation_hashes',hashlib.sha256(raw.encode()).hexdigest()==gen['raw_output_sha256'] and hashlib.sha256(gen['prompt'].encode()).hexdigest()==gen['prompt_sha256'])
            check(qid+':frozen_before_generation',reg['frozen_utc']<gen['started_utc'])
            pairs=[]
            for i,text in enumerate(gen['queries']):
                expected_keys.add((qid,i)); pair={}
                for page in (1,2):
                    name=f'responses/{qid}_q{i:02d}_page{page}.json'; response_keys.add(name); rec=read(ROOT/name)
                    raw=base64.b64decode(rec['raw_response_base64']); body=json.loads(raw)
                    payload={'q':f'{text} before:2026-09-19 site:arxiv.org','num':10,'page':page}
                    check(name+':raw_bytes',hashlib.sha256(raw).hexdigest()==rec['response_bytes_sha256'] and len(raw)==rec['response_bytes'] and body==rec['structured_response'])
                    check(name+':payload_identity',rec['request_payload']==payload and rec['question_id']==qid and rec['query_index']==i and rec['page']==page and rec['status']=='PASS' and rec['http_status']==200)
                    check(name+':echoed_parameters',all(k not in body.get('searchParameters',{}) or body['searchParameters'][k]==v for k,v in payload.items()))
                    check(name+':frozen_before_request',reg['frozen_utc']<rec['started_utc'] and gen['finished_utc']<=rec['started_utc'])
                    all_starts.append(rec['started_utc'])
                    record_attempts=rec['attempts']; check(name+':bounded_retries',1<=len(record_attempts)<=3)
                    for ai,entry in enumerate(record_attempts):
                        ar=attempts[entry['path']]
                        check(entry['path']+':attempt',sha(ROOT/entry['path'])==entry['sha256'] and ar['attempt']==ai+1 and ar['request_payload']==payload)
                        if ai<len(record_attempts)-1: check(entry['path']+':retryable_only',ar['status']!='PASS' and ar['retryable'])
                        if 'raw_response_base64' in ar:
                            ab=base64.b64decode(ar['raw_response_base64']);check(entry['path']+':bytes',hashlib.sha256(ab).hexdigest()==ar['response_bytes_sha256'])
                    final_attempt=attempts[record_attempts[-1]['path']]
                    check(name+':success_not_repeated',final_attempt['status']=='PASS' and sum(a['status']=='PASS' for a in attempts.values() if a['question_id']==qid and a['query_index']==i and a['page']==page)==1)
                    check(name+':final_attempt_matches',all(rec[k]==v for k,v in final_attempt.items()))
                    ids=idset(rec);pair[page]=(ids,rec)
                    stat=adherence[str(page)];organic=body['organic']; valid=sum(bool(re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)',v.get('link',''))) for v in organic)
                    stat['organic_results']+=len(organic);stat['parseable_arxiv_results']+=valid;stat['queries_with_non_arxiv_results']+=int(valid<len(organic))
                check(f'{qid}:{i}:pair_order',pair[1][1]['finished_utc']<=pair[2][1]['started_utc'])
                # With retries, the first Page2 attempt must immediately follow the last Page1 attempt.
                check(f'{qid}:{i}:consecutive_pair',attempts[pair[2][1]['attempts'][0]['path']]['global_http_attempt_sequence']==pair[1][1]['global_http_attempt_sequence']+1)
                gaps.append((datetime.fromisoformat(pair[2][1]['started_utc'])-datetime.fromisoformat(pair[1][1]['finished_utc'])).total_seconds())
                pairs.append((i,text,pair))
            union1=set();union2=set()
            for _,_,p in pairs:union1.update(p[1][0]);union2.update(p[2][0])
            first=gold&union1; both=gold&(union1|union2); gain=both-first
            qo=qout[qid]
            for field,val in [('page1_ids',union1),('page2_ids',union2),('gt_arxiv_ids',gold),('page1_gt_ids',first),('page1_page2_gt_ids',both),('page2_gain_gt_ids',gain)]:check(qid+':'+field,qo[field]==sorted(val))
            check(qid+':counts',qo['gt_count']==len(gold) and qo['page1_gt_found']==len(first) and qo['page1_page2_gt_found']==len(both) and qo['delta_gt']==len(gain) and qo['native_query_count']==len(pairs) and qo['extra_page2_calls']==len(pairs))
            check(qid+':recall',qo['page1_recall']==len(first)/len(gold) and qo['page1_page2_recall']==len(both)/len(gold))
            totals['gt']+=len(gold);totals['p1']+=len(first);totals['p12']+=len(both);totals['gain_questions']+=bool(gain);totals['queries']+=len(pairs);macro1.append(len(first)/len(gold));macro12.append(len(both)/len(gold))
            isolated_union=set()
            for i,text,p in pairs:
                o=outcomes[(qid,i)];x,y=p[1][0],p[2][0];isolated=(gold&y)-union1;local=(gold&y)-x
                isolated_union.update(isolated);totals['gain_queries']+=bool(isolated);totals['pair_gain_queries']+=bool(local)
                check(f'{qid}:{i}:text',o['query']==text)
                for field,v in [('page1_ids',x),('page2_ids',y),('page1_gt_ids',gold&x),('page2_gt_ids',gold&y),('page2_isolated_gain_gt_ids',isolated),('page2_pair_local_gain_gt_ids',local)]:check(f'{qid}:{i}:'+field,o[field]==sorted(v))
                check(f'{qid}:{i}:gains',o['page2_isolated_gain']==len(isolated) and o['page2_pair_local_gain']==len(local))
                for page in (1,2):
                    ix=o['responses'][str(page)];check(f'{qid}:{i}:{page}:index',ix['sha256']==sha(ROOT/ix['path']) and ix['response_bytes_sha256']==p[page][1]['response_bytes_sha256'])
            check(qid+':query_union_gain',isolated_union==gain)
        check('exact_generation_set',generation_keys=={p for p in snapshot['files'] if p.startswith('generations/')})
        check('exact_response_set',response_keys=={p for p in snapshot['files'] if p.startswith('responses/')})
        check('exact_outcome_sets',set(outcomes)==expected_keys and len(outcomes)==len(oq) and set(qout)=={q['question_id'] for q in dataset['sample']} and len(question_output)==50)
        r=read(ROOT/'results.json');n=totals['queries'];delta=totals['p12']-totals['p1']
        for key,value in {'questions_complete':50,'native_query_count':n,'total_gt':totals['gt'],'delta_gt':delta,'questions_with_page2_gain':totals['gain_questions'],'queries_with_page2_isolated_gain':totals['gain_queries'],'queries_with_page2_pair_local_gain':totals['pair_gain_queries'],'extra_page2_calls':n,'http_attempts':len(attempts),'successful_page1_responses':n,'successful_page2_responses':n}.items():check('aggregate:'+key,r[key]==value)
        check('only_two_policies',set(r['policies'])=={'Native Page1','Always Page2'})
        for policy,found,macro,calls in [('Native Page1',totals['p1'],sum(macro1)/50,0),('Always Page2',totals['p12'],sum(macro12)/50,n)]:
            p=r['policies'][policy];check(policy+':metrics',p['gt_found']==found and math.isclose(p['micro_search_recall'],found/totals['gt'],abs_tol=1e-12) and math.isclose(p['macro_search_recall'],macro,abs_tol=1e-12) and p['extra_page2_calls']==calls)
        check('efficiency',math.isclose(r['delta_gt_per_extra_page2_call'],delta/n,abs_tol=1e-12))
        check('recall_increments',math.isclose(r['incremental_micro_search_recall'],delta/totals['gt'],abs_tol=1e-12) and math.isclose(r['incremental_macro_search_recall'],sum(macro12)/50-sum(macro1)/50,abs_tol=1e-12))
        gate=delta>=10 and totals['gain_questions']>=5 and delta/n>=0.05
        check('preregistered_gate',r['opportunity_gate_passed']==gate and r['recommend_independent_fixed_max_jaccard_top1_validation']==gate and r['opportunity_gate']==reg['opportunity_gate'])
        for a in adherence.values():a['parseable_arxiv_fraction']=a['parseable_arxiv_results']/a['organic_results'] if a['organic_results'] else None
        check('source_adherence',r['source_adherence']==adherence)
        check('pair_gaps',r['page_pair_gap_seconds']=={'min':min(gaps),'mean':sum(gaps)/len(gaps),'max':max(gaps)})
        check('snapshot_counts',snapshot['questions_complete']==50 and snapshot['native_query_count']==n and snapshot['page1_responses']==n and snapshot['page2_responses']==n and snapshot['http_attempts']==len(attempts))
        check('run_counts',run['successful_generations']==50 and run['successful_page1']==n and run['successful_page2']==n and run['http_attempts']==len(attempts))
        check('gt_total',dataset['total_gt']==totals['gt'])
        check('result_snapshot',r['snapshot_id']==snapshot['snapshot_id'] and r['snapshot_manifest_sha256']==sha(ROOT/'snapshot_manifest.json'))
        check('no_router_results',r['router_implemented_or_evaluated'] is False)
        result={'experiment':r['experiment'],'status':'PASS','validated_utc':now(),'check_count':len(checks),'checks':checks,'independently_recomputed':totals|{'delta_gt':delta,'opportunity_gate_passed':gate},'first_search_utc':min(all_starts),'last_search_started_utc':max(all_starts),'registration_frozen_utc':reg['frozen_utc'],'artifact_hashes':{n:sha(ROOT/n) for n in ['dataset_manifest.json','registration_manifest.json','snapshot_manifest.json','query_outcomes.json','question_outcomes.json','results.json','SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005.md','evaluate.py','report.py','validate.py']}}
        save(ROOT/'validation.json',result);print(json.dumps({'status':'PASS','checks':len(checks),'totals':result['independently_recomputed']},indent=2))
    except BaseException as e:
        save(ROOT/'validation.json',{'status':'FAIL','validated_utc':now(),'checks':checks,'error':str(e),'error_type':type(e).__name__});raise

if __name__=='__main__':main()
