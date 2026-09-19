"""Frozen title matching on Search-returned IDs only; optional separate ID diagnostic."""
import collections
import contextlib
import datetime as dt
import io
import itertools
import json
from pathlib import Path
import re
import runpy
import statistics
import sys
import time
import types
import warnings
import zipfile
from common import ROOT,WORK,OUT,DATA,now,sha,save,read,native_function,protected

def qnorm(text):return ' '.join(re.findall(r'[a-z0-9]+',text.casefold()))

def overlaps(group):
    searches=group['searches'];pairs=[]
    for i,j in itertools.combinations(range(len(searches)),2):
        x,y=set(searches[i]['returned_arxiv_ids']),set(searches[j]['returned_arxiv_ids'])
        a,b=qnorm(searches[i]['crawler_query']),qnorm(searches[j]['crawler_query'])
        aw,bw=set(a.split()),set(b.split())
        pairs.append({'query_indices':[i,j],'normalized_query_identical':a==b,
          'query_token_jaccard':len(aw&bw)/len(aw|bw) if aw|bw else 0,
          'returned_id_overlap':sorted(x&y),'returned_id_jaccard':len(x&y)/len(x|y) if x|y else 0})
    occurrences=sum(len(s['returned_arxiv_ids']) for s in searches)
    ids=set().union(*(set(s['returned_arxiv_ids']) for s in searches)) if searches else set()
    return {'query_pairs':pairs,'normalized_duplicate_pair_count':sum(p['normalized_query_identical'] for p in pairs),
      'near_duplicate_pair_count':sum(not p['normalized_query_identical'] and p['query_token_jaccard']>=.85 for p in pairs),
      'returned_id_occurrences_after_within_response_dedup':occurrences,'unique_arxiv_id_count':len(ids),
      'repeated_id_occurrences_between_queries':occurrences-len(ids),
      'mean_pairwise_returned_id_jaccard':statistics.mean(p['returned_id_jaccard'] for p in pairs) if pairs else 0}

def main():
    d=read();assert d['status'] in ('search_complete','metadata_running'),'No repeat scoring over an already finalized experiment'
    p=d['provenance'];assert protected()==p['protected_before']
    p['evaluation_started_utc']=now();evalstart=time.monotonic()
    keep,keep_source=native_function('keep_letters');cal,cal_source=native_function('cal_micro')
    p['frozen_evaluator_functions']={'keep_letters':keep_source,'cal_micro':cal_source}
    p['evaluator_script_sha256']=sha(Path(__file__))
    ids=sorted({aid for q in d['per_query'] for g in q['groups'].values() for s in g['searches'] for aid in s['returned_arxiv_ids']})
    import arxiv,requests
    from urllib.parse import urlparse
    network=[]
    original_request=requests.sessions.Session.request
    def guarded(session,method,url,*args,**kwargs):
        if urlparse(url).hostname not in ('export.arxiv.org','arxiv.org') or method.upper()!='GET':
            raise RuntimeError('Metadata stage permits native arXiv GET only')
        params=kwargs.get('params') or {}
        if isinstance(params,dict) and params.get('search_query') not in (None,''):
            raise RuntimeError('No title searches or expanded candidate searches allowed')
        record={'method':method,'url':url,'params':params,'started_utc':now()};start=time.monotonic()
        try:
            response=original_request(session,method,url,*args,**kwargs)
            record['http_status']=response.status_code
            return response
        except Exception as exc:
            record.update(http_status=None,error_type=type(exc).__name__,error_message=str(exc))
            raise
        finally:
            record.update(finished_utc=now(),elapsed_seconds=time.monotonic()-start)
            network.append(record)
            save(WORK/'metadata_network.json',network)
    requests.sessions.Session.request=guarded
    database=Path('/mnt/nvme3/chenyi/pasa/data/paper_database')
    index=read(database/'id2paper.json');paper_db=zipfile.ZipFile(database/'cs_paper_2nd.zip','r')
    namespace={'keep_letters':keep,'id2paper':index,'paper_db':paper_db,'_paper_db_names':set(paper_db.namelist()),'json':json,'arxiv':arxiv,'arxiv_client':arxiv.Client(delay_seconds=.05),'warnings':warnings}
    resolve,resolve_source=native_function('search_paper_by_arxiv_id',namespace)
    p['native_metadata_function_source']=resolve_source
    p['metadata_policy']='Unmodified native function: local title-key ZIP record first; native arXiv ID metadata lookup on local miss. Shared ID->result snapshot across A/B; no GT title substitution, Serper title fallback, fuzzy match, or new candidates. Failure leaves title unresolved and excludes it from official title metric, while ID diagnostic still records Search URL coverage.'
    p['metadata_database_files']={n:{'sha256':sha(database/n),'bytes':(database/n).stat().st_size} for n in ('id2paper.json','cs_paper_2nd.zip')}
    d['status']='metadata_running';save(OUT,d)
    metadata={}
    for index_num,aid in enumerate(ids,1):
        path=WORK/'metadata'/f'{aid}.json'
        if path.exists():
            record=read(path)
        else:
            start=time.monotonic();record={'arxiv_id':aid,'started_utc':now()}
            try:
                result=resolve(aid)
                if result is None:record.update(status='UNRESOLVED',title=None,source=None)
                else:record.update(status='PASS',title=result['title'],normalized_title=keep(result['title']),source=result['source'])
            except Exception as exc:
                record.update(status='UNRESOLVED',title=None,source=None,error_type=type(exc).__name__,error_message=str(exc))
            record.update(finished_utc=now(),elapsed_seconds=time.monotonic()-start);save(path,record)
        metadata[aid]=record
        if index_num%25==0 or index_num==len(ids):print(f'Metadata {index_num}/{len(ids)}; unresolved={sum(x["status"]!="PASS" for x in metadata.values())}',flush=True)
    paper_db.close()
    # First decode of GT answers in this experiment's workflow; all generation/search is done.
    rows=[json.loads(line) for line in DATA.open()]
    all_cases=[]
    for q,row in zip(d['per_query'],rows):
        assert row['question']==q['original_question']
        grouped={}
        for i,(title,aid) in enumerate(zip(row['answer'],row['answer_arxiv_id'])):
            grouped.setdefault(keep(title),[]).append({'annotation_index':i,'title':title,'arxiv_id':re.sub(r'v\d+$','',aid)})
        labels=set(grouped)
        q['gt']={'raw_annotation_count':len(row['answer']),'normalized_title_count':len(labels),'unique_gt_id_count':len(set(row['answer_arxiv_id'])),'groups':[{'normalized_title':k,'annotations':v} for k,v in grouped.items()]}
        gtids={re.sub(r'v\d+$','',x) for x in row['answer_arxiv_id']}
        for group,g in q['groups'].items():
            foundids=sorted({aid for s in g['searches'] for aid in s['returned_arxiv_ids']})
            candidates=[metadata[aid] for aid in foundids]
            pred={r['normalized_title'] for r in candidates if r['status']=='PASS'}
            tp,fp,fn=cal(pred,labels)
            attempts=[a for s in g['searches'] for a in s['attempts']]
            g.update(query_count=len(g['queries']),serper_calls=len(attempts),logical_search_calls=len(g['searches']),
              successful_logical_calls=sum(s['status']=='PASS' for s in g['searches']),returned_unique_arxiv_ids=foundids,
              candidate_titles=[{'arxiv_id':r['arxiv_id'],'title':r.get('title'),'source':r.get('source'),'status':r['status']} for r in candidates],
              missing_metadata_ids=[r['arxiv_id'] for r in candidates if r['status']!='PASS'],
              formal_evaluation={'TOTAL_GT':len(labels),'SEARCH_GT_FOUND':tp,'SEARCH_RECALL':tp/(tp+fn if tp+fn>0 else 1e-9),
                'SEARCH_RECALL_PER_CALL':tp/len(attempts) if attempts else None,'matched_normalized_gt_titles':sorted(pred&labels),
                'unique_normalized_candidate_titles':len(pred),'false_positive_title_count':fp,'false_negative_gt_count':fn},
              query_overlap=overlaps(g),
              id_aware_diagnostic={'TOTAL_GT_IDS':len(gtids),'FOUND_GT_IDS':len(gtids&set(foundids)),'RECALL':len(gtids&set(foundids))/len(gtids) if gtids else 0,
                'matched_gt_ids':sorted(gtids&set(foundids)),'found_normalized_gt_groups_by_annotated_id':sum(bool({a['arxiv_id'] for a in annotations}&set(foundids)) for annotations in grouped.values())})
        aa=set(q['groups']['A']['formal_evaluation']['matched_normalized_gt_titles']);bb=set(q['groups']['B']['formal_evaluation']['matched_normalized_gt_titles'])
        q['comparison']={'recall_delta':q['groups']['B']['formal_evaluation']['SEARCH_RECALL']-q['groups']['A']['formal_evaluation']['SEARCH_RECALL'],
          'found_count_delta':len(bb)-len(aa),'B_new_gt':sorted(bb-aa),'B_lost_gt':sorted(aa-bb),'both_found_gt':sorted(aa&bb),'both_missed_gt':sorted(labels-(aa|bb))}
        ids_a=set(q['groups']['A']['returned_unique_arxiv_ids']);ids_b=set(q['groups']['B']['returned_unique_arxiv_ids'])
        q['comparison']['candidate_id_overlap']={'both':sorted(ids_a&ids_b),'A_only':sorted(ids_a-ids_b),'B_only':sorted(ids_b-ids_a),'jaccard':len(ids_a&ids_b)/len(ids_a|ids_b) if ids_a|ids_b else 0}
        cases=[]
        for key,annotations in grouped.items():
            hit_a,hit_b=key in aa,key in bb
            case={'query_id':q['query_id'],'normalized_gt_title':key,'annotations':annotations,
              'category':'both_found' if hit_a and hit_b else 'B_new' if hit_b else 'B_lost' if hit_a else 'both_missed'}
            for group,g in q['groups'].items():
                matching_ids={aid for aid in g['returned_unique_arxiv_ids'] if metadata[aid]['status']=='PASS' and metadata[aid]['normalized_title']==key}
                case[group+'_evidence']=[{'query_sequence':s['query_sequence'],'crawler_query':s['crawler_query'],'arxiv_id':h['arxiv_id'],'organic_index':h['organic_index'],'link':h['link'],
                  'metadata_title':metadata[h['arxiv_id']]['title'],'response_artifact':s['attempts'][-1]['artifact_path']} for s in g['searches'] for h in s['organic_hits'] if h['arxiv_id'] in matching_ids]
            cases.append(case)
        q['gt_comparison_cases']=cases;all_cases.extend(cases)
    summaries={}
    for group in ('A','B'):
        groups=[q['groups'][group] for q in d['per_query']]
        total_gt=sum(g['formal_evaluation']['TOTAL_GT'] for g in groups);found=sum(g['formal_evaluation']['SEARCH_GT_FOUND'] for g in groups)
        calls=sum(g['serper_calls'] for g in groups);attempts=[a for g in groups for s in g['searches'] for a in s['attempts']]
        ids_union=set().union(*(set(g['returned_unique_arxiv_ids']) for g in groups))
        summaries[group]={'TOTAL_GT':total_gt,'SEARCH_GT_FOUND':found,'SEARCH_RECALL':statistics.mean(g['formal_evaluation']['SEARCH_RECALL'] for g in groups),
          'MICRO_SEARCH_RECALL':found/total_gt,'SEARCH_RECALL_PER_CALL':found/calls if calls else None,
          'SERPER_CALLS':calls,'LOGICAL_SEARCH_CALLS':sum(g['logical_search_calls'] for g in groups),
          'SUCCESSFUL_LOGICAL_CALLS':sum(g['successful_logical_calls'] for g in groups),'FAILED_LOGICAL_CALLS':sum(g['logical_search_calls']-g['successful_logical_calls'] for g in groups),
          'FAILED_HTTP_ATTEMPTS':sum(a['status']!='PASS' for a in attempts),'HTTP_429_COUNT':sum(a.get('http_status')==429 for a in attempts),
          'HTTP_STATUS_DISTRIBUTION':dict(collections.Counter(str(a.get('http_status')) for a in attempts)),
          'UNIQUE_CANDIDATE_PAPERS_GLOBAL':len(ids_union),'UNIQUE_CANDIDATE_PAPERS_SUM_PER_Q':sum(len(g['returned_unique_arxiv_ids']) for g in groups),
          'RESOLVED_TITLE_CANDIDATES_GLOBAL':sum(metadata[aid]['status']=='PASS' for aid in ids_union),
          'MISSING_METADATA_IDS_GLOBAL':[aid for aid in sorted(ids_union) if metadata[aid]['status']!='PASS'],
          'NORMALIZED_CANDIDATE_TITLE_COUNT_SUM_PER_Q':sum(g['formal_evaluation']['unique_normalized_candidate_titles'] for g in groups),
          'QUERY_COUNT_DISTRIBUTION':dict(collections.Counter(str(g['query_count']) for g in groups)),
          'GENERATIONS_WITH_ZERO_QUERIES':sum(g['query_count']==0 for g in groups),
          'GENERATIONS_WITH_EMPTY_QUERY':sum(any(not x for x in g['queries']) for g in groups),
          'NON_EOS_GENERATIONS':sum(not g['ended_with_eos'] for g in groups),
          'NORMALIZED_DUPLICATE_QUERY_PAIRS':sum(g['query_overlap']['normalized_duplicate_pair_count'] for g in groups),
          'NEAR_DUPLICATE_QUERY_PAIRS':sum(g['query_overlap']['near_duplicate_pair_count'] for g in groups),
          'REPEATED_ID_OCCURRENCES_BETWEEN_QUERIES':sum(g['query_overlap']['repeated_id_occurrences_between_queries'] for g in groups),
          'MEAN_PER_Q_PAIRWISE_ID_JACCARD':statistics.mean(g['query_overlap']['mean_pairwise_returned_id_jaccard'] for g in groups),
          'ID_AWARE_DIAGNOSTIC':{'TOTAL_GT_IDS':sum(g['id_aware_diagnostic']['TOTAL_GT_IDS'] for g in groups),
            'FOUND_GT_IDS':sum(g['id_aware_diagnostic']['FOUND_GT_IDS'] for g in groups),
            'MICRO_ID_RECALL':sum(g['id_aware_diagnostic']['FOUND_GT_IDS'] for g in groups)/sum(g['id_aware_diagnostic']['TOTAL_GT_IDS'] for g in groups),
            'MACRO_ID_RECALL':statistics.mean(g['id_aware_diagnostic']['RECALL'] for g in groups),
            'FOUND_TITLE_GROUPS_BY_ID':sum(g['id_aware_diagnostic']['found_normalized_gt_groups_by_annotated_id'] for g in groups)}}
    a,b=summaries['A'],summaries['B'];categories=collections.Counter(c['category'] for c in all_cases)
    summaries['comparison']={'macro_recall_absolute_delta':b['SEARCH_RECALL']-a['SEARCH_RECALL'],'macro_recall_relative_delta':(b['SEARCH_RECALL']/a['SEARCH_RECALL']-1) if a['SEARCH_RECALL'] else None,
      'micro_recall_absolute_delta':b['MICRO_SEARCH_RECALL']-a['MICRO_SEARCH_RECALL'],'micro_recall_relative_delta':(b['MICRO_SEARCH_RECALL']/a['MICRO_SEARCH_RECALL']-1) if a['MICRO_SEARCH_RECALL'] else None,
      'B_new_gt_count':categories['B_new'],'B_lost_gt_count':categories['B_lost'],'both_found_gt_count':categories['both_found'],'both_missed_gt_count':categories['both_missed'],
      'queries_improved':sum(q['comparison']['recall_delta']>0 for q in d['per_query']),'queries_declined':sum(q['comparison']['recall_delta']<0 for q in d['per_query']),'queries_tied':sum(q['comparison']['recall_delta']==0 for q in d['per_query'])}
    # Run the untouched official metrics.py on minimal Search-only trees.
    # select_score=0 is a schema sentinel, not a Selector prediction; only crawler recall is validated.
    official={}
    for group in ('A','B'):
        folder=WORK/'official_metric_inputs'/group
        for q in d['per_query']:
            nodes=[{'title':c['title'],'child':{},'select_score':0} for c in q['groups'][group]['candidate_titles'] if c['status']=='PASS']
            tree={'title':q['original_question'],'extra':{'answer':[a['title'] for x in q['gt']['groups'] for a in x['annotations']]},'child':{'Search-only candidates':nodes}}
            save(folder/f"{q['query_id']}.json",tree)
        shim=types.ModuleType('utils');shim.keep_letters=keep;shim.cal_micro=cal
        old_utils=sys.modules.get('utils');old_argv=sys.argv[:];sys.modules['utils']=shim
        sys.argv=[str(ROOT/'metrics.py'),'--output_folder',str(folder)]
        out=io.StringIO()
        try:
            with contextlib.redirect_stdout(out):runpy.run_path(str(ROOT/'metrics.py'),run_name='__main__')
        finally:
            sys.argv=old_argv
            if old_utils is None:sys.modules.pop('utils',None)
            else:sys.modules['utils']=old_utils
        value=float(out.getvalue().strip().splitlines()[0].split('&')[0])
        assert value==round(summaries[group]['SEARCH_RECALL'],4)
        official[group]={'metrics_py_sha256':sha(ROOT/'metrics.py'),'stdout':out.getvalue(),'official_crawler_recall_on_search_only_trees':value,'agrees_with_report_macro_recall':True}
    d['summary']=summaries;d['metadata']=metadata
    p['official_evaluator_verification']=official
    p['official_evaluator_verification_note']='Execute original metrics.py unmodified, injecting only original keep_letters/cal_micro via minimal utils module to avoid pipeline imports. Search-only nodes have select_score=0 solely as schema sentinel; other printed Selector/ranking metrics are not experiment outcomes.'
    p['metadata_request_log']=network
    p['metadata_summary']={'unique_search_ids':len(ids),'resolved_titles':sum(r['status']=='PASS' for r in metadata.values()),'unresolved_ids':[aid for aid,r in metadata.items() if r['status']!='PASS'],'source_counts':dict(collections.Counter(r.get('source') for r in metadata.values())),'http_requests':len(network),'http_429_count':sum(x.get('http_status')==429 for x in network)}
    p.update(evaluation_finished_utc=now(),evaluation_wall_seconds=time.monotonic()-evalstart,protected_after_evaluation=protected())
    assert p['protected_after_evaluation']==p['protected_before']
    p['total_run_wall_seconds']=(dt.datetime.fromisoformat(p['evaluation_finished_utc'])-dt.datetime.fromisoformat(p['started_utc'])).total_seconds()
    d['status']='evaluated';save(OUT,d)
    print(json.dumps(summaries,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
