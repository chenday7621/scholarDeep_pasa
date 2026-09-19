"""Only Native Page1 versus Always Page2; no routing decisions or GT-derived queries."""
import base64, hashlib, json
from common import ROOT, read, save, sha, digest, ids, now, verify_freeze


def main():
    reg=verify_freeze()
    run=read(ROOT/'run_manifest.json')
    assert run['status']=='SNAPSHOT_COMPLETE', 'Never evaluate incomplete subset as ScholarQuest-50'
    dataset=read(ROOT/'dataset_manifest.json')
    files={}
    outcomes=[]; question_outcomes=[]; gaps=[]
    adherence={str(p):{'organic_results':0,'parseable_arxiv_results':0,'queries_with_non_arxiv_results':0} for p in (1,2)}
    for question in dataset['sample']:
        qid=question['question_id']; g=set(question['gt_arxiv_ids'])
        gp=ROOT/'generations'/f'{qid}.json'; generation=read(gp)
        files[str(gp.relative_to(ROOT))]=sha(gp)
        records=[]
        for i,query in enumerate(generation['queries']):
            pages={}
            for p in (1,2):
                path=ROOT/'responses'/f'{qid}_q{i:02d}_page{p}.json'
                response=read(path); assert response['status']=='PASS'
                raw=base64.b64decode(response['raw_response_base64'])
                assert hashlib.sha256(raw).hexdigest()==response['response_bytes_sha256']
                assert json.loads(raw)==response['structured_response']
                files[str(path.relative_to(ROOT))]=sha(path)
                pages[p]=(response,set(ids(response['structured_response'])))
                a=adherence[str(p)]; hits=response['structured_response']['organic']
                valid=sum(bool(ids({'organic':[hit]})) for hit in hits)
                a['organic_results']+=len(hits);a['parseable_arxiv_results']+=valid
                a['queries_with_non_arxiv_results']+=int(valid<len(hits))
            from datetime import datetime
            gaps.append((datetime.fromisoformat(pages[2][0]['started_utc'])-datetime.fromisoformat(pages[1][0]['finished_utc'])).total_seconds())
            records.append((i,query,pages))
        p1=set().union(*(r[2][1][1] for r in records)); p2=set().union(*(r[2][2][1] for r in records))
        found1=g&p1;found12=g&(p1|p2); gain=found12-found1
        question_outcomes.append({'question_id':qid,'source_query_id':question['source_query_id'],'question':question['question'],'status':'COMPLETE','native_query_count':len(records),'gt_count':len(g),'gt_arxiv_ids':sorted(g),'page1_ids':sorted(p1),'page2_ids':sorted(p2),'page1_gt_ids':sorted(found1),'page1_page2_gt_ids':sorted(found12),'page2_gain_gt_ids':sorted(gain),'page1_gt_found':len(found1),'page1_page2_gt_found':len(found12),'delta_gt':len(gain),'page1_recall':len(found1)/len(g),'page1_page2_recall':len(found12)/len(g),'extra_page2_calls':len(records)})
        for i,query,pages in records:
            x,y=pages[1][1],pages[2][1]
            outcomes.append({'question_id':qid,'source_query_id':question['source_query_id'],'query_index':i,'query':query,'page1_ids':sorted(x),'page2_ids':sorted(y),'page1_gt_ids':sorted(g&x),'page2_gt_ids':sorted(g&y),'page2_isolated_gain_gt_ids':sorted((g&y)-p1),'page2_isolated_gain':len((g&y)-p1),'page2_pair_local_gain_gt_ids':sorted((g&y)-x),'page2_pair_local_gain':len((g&y)-x),'responses':{str(p):{'path':pages[p][0]['artifact_path'],'sha256':sha(ROOT/pages[p][0]['artifact_path']),'response_bytes_sha256':pages[p][0]['response_bytes_sha256']} for p in (1,2)}})
    for path in sorted((ROOT/'attempts').glob('*.json')): files[str(path.relative_to(ROOT))]=sha(path)
    files['run_manifest.json']=sha(ROOT/'run_manifest.json')
    files['registration_manifest.json']=sha(ROOT/'registration_manifest.json')
    snapshot={'experiment':'SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005','status':'COMPLETE','frozen_utc':now(),'dataset_manifest_sha256':sha(ROOT/'dataset_manifest.json'),'sample_sha256':dataset['sample_sha256'],'files':files,'snapshot_id':digest(files),'questions_complete':len(question_outcomes),'native_query_count':len(outcomes),'page1_responses':len(outcomes),'page2_responses':len(outcomes),'http_attempts':len(list((ROOT/'attempts').glob('*.json')))}
    if (ROOT/'snapshot_manifest.json').exists():
        old=read(ROOT/'snapshot_manifest.json'); assert old['snapshot_id']==snapshot['snapshot_id']; snapshot=old
    else: save(ROOT/'snapshot_manifest.json',snapshot)
    n=len(question_outcomes); total_gt=sum(q['gt_count'] for q in question_outcomes)
    f1=sum(q['page1_gt_found'] for q in question_outcomes); f12=sum(q['page1_page2_gt_found'] for q in question_outcomes)
    nq=len(outcomes); delta=f12-f1; gain_questions=sum(q['delta_gt']>0 for q in question_outcomes)
    native={'gt_found':f1,'macro_search_recall':sum(q['page1_recall'] for q in question_outcomes)/n,'micro_search_recall':f1/total_gt,'extra_page2_calls':0}
    always={'gt_found':f12,'macro_search_recall':sum(q['page1_page2_recall'] for q in question_outcomes)/n,'micro_search_recall':f12/total_gt,'extra_page2_calls':nq}
    gate=reg['opportunity_gate']
    passed=n==50 and delta>=gate['minimum_delta_gt'] and gain_questions>=gate['minimum_gain_questions'] and delta/nq>=gate['minimum_delta_gt_per_page2_call']
    for a in adherence.values(): a['parseable_arxiv_fraction']=a['parseable_arxiv_results']/a['organic_results'] if a['organic_results'] else None
    results={'experiment':'SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005','status':'COMPLETE','dataset_manifest_sha256':sha(ROOT/'dataset_manifest.json'),'snapshot_id':snapshot['snapshot_id'],'snapshot_manifest_sha256':sha(ROOT/'snapshot_manifest.json'),'questions_requested':50,'questions_complete':n,'native_query_count':nq,'total_gt':total_gt,'policies':{'Native Page1':native,'Always Page2':always},'delta_gt':delta,'incremental_macro_search_recall':always['macro_search_recall']-native['macro_search_recall'],'incremental_micro_search_recall':delta/total_gt,'questions_with_page2_gain':gain_questions,'queries_with_page2_isolated_gain':sum(q['page2_isolated_gain']>0 for q in outcomes),'queries_with_page2_pair_local_gain':sum(q['page2_pair_local_gain']>0 for q in outcomes),'extra_page2_calls':nq,'delta_gt_per_extra_page2_call':delta/nq,'http_attempts':snapshot['http_attempts'],'successful_page1_responses':nq,'successful_page2_responses':nq,'source_adherence':adherence,'page_pair_gap_seconds':{'min':min(gaps),'mean':sum(gaps)/len(gaps),'max':max(gaps)},'opportunity_gate':gate,'opportunity_gate_passed':passed,'recommend_independent_fixed_max_jaccard_top1_validation':passed,'router_implemented_or_evaluated':False,'isolated_gain_definition':'GT intersect (query Page2 IDs minus all native Page1 IDs of this question)','pair_local_gain_definition':'GT intersect (query Page2 IDs minus this query Page1 IDs)'}
    save(ROOT/'query_outcomes.json',{'snapshot_id':snapshot['snapshot_id'],'isolated_gain_definition':results['isolated_gain_definition'],'pair_local_gain_definition':results['pair_local_gain_definition'],'queries':outcomes})
    save(ROOT/'question_outcomes.json',{'snapshot_id':snapshot['snapshot_id'],'questions':question_outcomes})
    save(ROOT/'results.json',results)
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
