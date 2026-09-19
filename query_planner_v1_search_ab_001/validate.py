"""Integrity checks for fixed prompts, fresh requests, and frozen evaluation accounting."""
import hashlib
import json
import math
from pathlib import Path
import re
from common import ROOT,WORK,OUT,REPORT,CHECKPOINT,B_TEMPLATE,read,sha,native_function,native_search_spec,protected,project_questions

def main():
    d=read();assert d['status']=='complete'
    p=d['provenance'];projection=project_questions();pattern,cap,_=native_search_spec()
    keep,_=native_function('keep_letters');cal,_=native_function('cal_micro')
    assert len(d['per_query'])==50
    sequence=[];partitions={'B_new':0,'B_lost':0,'both_found':0,'both_missed':0}
    for q,original in zip(d['per_query'],projection):
        for k,v in original.items():assert q[k]==v
        assert q['before_date']=='2024-09-24'
        assert q['groups']['A']['prompt']==p['A_template'].format(user_query=q['original_question']).strip()
        assert q['groups']['B']['prompt']==B_TEMPLATE.format(user_query=q['original_question']).strip()
        labels={g['normalized_title'] for g in q['gt']['groups']}
        for group,g in q['groups'].items():
            assert g['seed']==42
            assert hashlib.sha256(g['formatted_prompt'].encode()).hexdigest()==g['prompt_sha256']
            parsed=[s.strip() for s in re.findall(pattern,g['raw_output'],flags=re.DOTALL)]
            assert g['queries']==parsed[:cap] and g['all_parsed_queries']==parsed
            assert len(g['queries'])==len(g['searches'])==g['query_count']
            assert len(g['generated_token_ids'])==g['generated_token_count']<=512
            candidate_ids=set()
            for index,s in enumerate(g['searches'],1):
                assert s['crawler_query']==g['queries'][index-1] and s['query_sequence']==index
                expected={'q':f"{s['crawler_query']} before:2024-09-24 site:arxiv.org",'num':10,'page':1}
                assert s['request_payload']==expected
                assert 1<=len(s['attempts'])<=3
                for attempt in s['attempts']:
                    sequence.append(attempt['global_attempt_sequence'])
                    assert attempt['query_id']==q['query_id'] and attempt['group']==group
                    assert attempt['request_payload']==expected
                    assert read(attempt['artifact_path'])==attempt
                    if attempt['status']=='PASS':assert attempt['http_status']==200
                if s['status']=='PASS':
                    last=s['attempts'][-1]
                    hits=[]
                    for hit in last['structured_response']['organic']:
                        m=re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)',hit.get('link',''))
                        if m:hits.append(m.group(1))
                    assert set(hits)==set(s['returned_arxiv_ids'])
                else:assert not s['returned_arxiv_ids']
                candidate_ids.update(s['returned_arxiv_ids'])
            assert set(g['returned_unique_arxiv_ids'])==candidate_ids
            assert g['serper_calls']==sum(len(s['attempts']) for s in g['searches'])
            pred={keep(d['metadata'][aid]['title']) for aid in candidate_ids if d['metadata'][aid]['status']=='PASS'}
            tp,fp,fn=cal(pred,labels);e=g['formal_evaluation']
            assert e['SEARCH_GT_FOUND']==tp and e['TOTAL_GT']==tp+fn
            assert math.isclose(e['SEARCH_RECALL'],tp/len(labels))
            assert e['matched_normalized_gt_titles']==sorted(pred&labels)
            assert e['SEARCH_RECALL_PER_CALL']==(tp/g['serper_calls'] if g['serper_calls'] else None)
        assert len(q['gt_comparison_cases'])==len(labels)
        for case in q['gt_comparison_cases']:
            partitions[case['category']]+=1
            for group in ('A','B'):
                expected=case['normalized_gt_title'] in q['groups'][group]['formal_evaluation']['matched_normalized_gt_titles']
                assert bool(case[group+'_evidence'])==expected
        a=q['groups']['A']['formal_evaluation'];b=q['groups']['B']['formal_evaluation']
        assert math.isclose(q['comparison']['recall_delta'],b['SEARCH_RECALL']-a['SEARCH_RECALL'])
    assert sorted(sequence)==list(range(1,len(sequence)+1))
    assert sum(partitions.values())==790
    a,b=d['summary']['A'],d['summary']['B'];c=d['summary']['comparison']
    assert a['SEARCH_GT_FOUND']==partitions['both_found']+partitions['B_lost']
    assert b['SEARCH_GT_FOUND']==partitions['both_found']+partitions['B_new']
    assert c['B_new_gt_count']==partitions['B_new'] and c['B_lost_gt_count']==partitions['B_lost']
    for group in ('A','B'):
        s=d['summary'][group];gs=[q['groups'][group] for q in d['per_query']]
        assert s['TOTAL_GT']==790
        assert s['SERPER_CALLS']==sum(g['serper_calls'] for g in gs)
        assert s['SEARCH_GT_FOUND']==sum(g['formal_evaluation']['SEARCH_GT_FOUND'] for g in gs)
        assert math.isclose(s['SEARCH_RECALL'],sum(g['formal_evaluation']['SEARCH_RECALL'] for g in gs)/50)
        assert s['MICRO_SEARCH_RECALL']==s['SEARCH_GT_FOUND']/790
        assert s['SEARCH_RECALL_PER_CALL']==s['SEARCH_GT_FOUND']/s['SERPER_CALLS']
        assert p['official_evaluator_verification'][group]['agrees_with_report_macro_recall']
    assert protected()==p['protected_before']==p['protected_after_search']==p['protected_after_evaluation']
    for name in ('config.json','generation_config.json','tokenizer_config.json'):
        assert sha(CHECKPOINT/name)==p['checkpoint_files'][name]['sha256']
    previous=read(ROOT/'ACRONYM_EXPANSION_PROBE_002.json')
    assert p['checkpoint_files']==previous['provenance']['checkpoint_files']
    assert p['generation_config_file']==read(CHECKPOINT/'generation_config.json')
    assert p['generation_call_overrides']=={'max_new_tokens':512}
    # Ensure credentials have not leaked into requested final artifacts.
    secret=Path('/mnt/nvme3/chenyi/pasa/secrets/serper_api_key').read_text().strip()
    assert secret and secret not in OUT.read_text() and secret not in REPORT.read_text()
    result={'status':'PASS','checked_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
       'checks':['50 question-only projections and fixed A/B prompts','100 generations with native parsing and paired seed 42','fresh contiguous HTTP attempt records and fixed page/num/before/site','candidate IDs only from native organic URL parsing','frozen normalized-title matching and disjoint GT partitions','macro/micro/per-call arithmetic and official metrics.py agreement','unchanged protected source/config/checkpoint','no credentials in final JSON/MD'],
       'final_artifact_sha256':{str(OUT):sha(OUT),str(REPORT):sha(REPORT)}}
    from common import save
    save(WORK/'validation.json',result)
    print('PASS:', '; '.join(result['checks']))

if __name__=='__main__':main()
