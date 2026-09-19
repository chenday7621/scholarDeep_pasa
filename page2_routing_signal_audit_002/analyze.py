"""Only this stage joins frozen outcomes/GT for retrospective analysis."""
from collections import Counter, defaultdict
import csv
import random
import sys

from audit_common import HERE, REPO, PREVIOUS, SOURCE, SHARED_CODE, Guard, read, save, sha, digest, hits, check_response
from statistics_utils import summarize, discrimination, hedges_g, metric_bundle, conditional, strata, quantile, self_test
from render_report import render

SEED = 20260917
BOOTSTRAPS = 1000


def main():
    names = ['page1_features.json','feature_access.json','environment_audit.json','analysis_plan.json','feature_definitions.json','validation_feature_isolation.json']
    feature_inputs = [HERE / p for p in names]
    previous_inputs = [PREVIOUS / p for p in ['states.json','decisions.json','snapshot_manifest.json','evaluation_query_outcomes.json','results.json','validation_evaluation.json']]
    original = REPO / 'PAGE2_SEARCH_PROBE_001.json'
    protected = [REPO / p for p in ['paper_agent.py','utils.py','models.py','metrics.py','paper_node.py','run_paper_agent.py','agent_prompt.json']]
    code = [HERE / p for p in ['analyze.py','extract_features.py','statistics_utils.py','render_report.py','environment_probe.py','validate_features.py']] + SHARED_CODE
    outputs = [HERE / p for p in ['query_signal_table.json','query_signal_table.csv','feature_stats.json','validation.json','analysis_access.json','manifest.json','PAGE2_ROUTING_SIGNAL_AUDIT_002.md']]
    guard = Guard([*feature_inputs,*previous_inputs,original,*protected],outputs,code)
    before = {str(p):sha(p) for p in [*feature_inputs,*previous_inputs,original,*protected,*code]}
    assert self_test()
    extracted = read(HERE/'page1_features.json')
    isolation=read(HERE/'validation_feature_isolation.json')
    assert isolation['status']=='PASS' and isolation['feature_sha256']==sha(HERE/'page1_features.json')
    access = read(HERE/'feature_access.json')
    rows = extracted['rows']
    states = read(PREVIOUS/'states.json')
    snapshots = read(PREVIOUS/'snapshot_manifest.json')
    old_outcomes = {r['query_key']:r for r in read(PREVIOUS/'evaluation_query_outcomes.json')['queries']}
    old_results = read(PREVIOUS/'results.json')
    original_data = read(original)
    assert extracted['frozen_states_sha256']==sha(PREVIOUS/'states.json')
    assert extracted['page1_snapshot_id']==states['page1_snapshot_id']
    assert snapshots['snapshot_id']==digest(snapshots['responses'])==old_results['snapshot_id']
    assert len(rows)==len(snapshots['responses'])==len(old_outcomes)==248
    assert Counter(r['query_index'] for r in rows)=={q:4 if q in [18,28] else 5 for q in range(50)}
    assert len({r['query_key'] for r in rows})==248
    permitted_feature_reads = {str(p.resolve()) for p in [PREVIOUS/'states.json',HERE/'environment_audit.json', SOURCE/'request_plan.json', HERE/'extract_features.py', PREVIOUS/'features.py',*SHARED_CODE]}
    permitted_feature_reads.update(str(p['path']) for p in extracted['question_provenance'].values())
    permitted_feature_reads.update(r['page1_path'] for r in rows)
    assert set(access['read_paths']) <= permitted_feature_reads
    assert access['denied_attempts']==[]
    # Verify actual extraction hashes and prompt question identity.
    guard.allow(extracted['source_hashes'])
    assert all(sha(p)==h for p,h in extracted['source_hashes'].items())
    assert extracted['analysis_plan_content_digest']==digest(read(HERE/'analysis_plan.json'))
    for q,prov in extracted['question_provenance'].items():
        guard.allow([prov['path']])
        assert sha(prov['path'])==prov['sha256']
    refs = {(r['query_index'],r['query_sequence']):r for r in original_data['requests']}
    gt = defaultdict(list)
    for g in original_data['all_gt_cases']:
        gt[g['query_index']].append(g)
    assert sum(map(len,gt.values()))==790
    page1, page2, p1_unions = {}, {}, defaultdict(set)
    row_by_key = {r['query_key']:r for r in rows}
    for k,pair in snapshots['responses'].items():
        guard.allow([pair['page1_path'],pair['page2_path']])
        assert sha(pair['page1_path'])==pair['page1_sha256']==row_by_key[k]['page1_sha256']
        assert sha(pair['page2_path'])==pair['page2_sha256']
        r1,r2=read(pair['page1_path']),read(pair['page2_path'])
        check_response(r1);check_response(r2)
        assert r1['request_payload']['page']==1 and r2['request_payload']==dict(r1['request_payload'],page=2)
        page1[k]={h['arxiv_id'] for h in hits(r1)}
        page2[k]={h['arxiv_id'] for h in hits(r2)}
        row=row_by_key[k]
        rr=refs[(row['query_index'],row['query_sequence'])]
        assert sorted(page1[k])==rr['page1_ids'] and sorted(page2[k])==rr['page2_ids']
        p1_unions[row['query_index']].update(page1[k])
        assert row['question']==original_data['per_query'][row['query_index']]['user_question'].strip()
    table=[]
    union_gain=set()
    base_found=0
    for q,cases in gt.items():
        base_found+=sum(bool(set(g['gt_arxiv_ids']) & p1_unions[q]) for g in cases)
    assert base_found==157
    for r in rows:
        k,q=r['query_key'],r['query_index']
        matches=[g['normalized_gt_title'] for g in gt[q] if not (set(g['gt_arxiv_ids']) & p1_unions[q]) and (set(g['gt_arxiv_ids']) & page2[k])]
        previous=old_outcomes[k]
        assert len(matches)==previous['isolated_new_gt_vs_all_page1']
        assert set(matches)=={g['normalized_gt_title'] for g in previous['new_gt']}
        assert abs(r['features']['original_need_more_search_score']-previous['need_more_search_score'])<1e-15
        union_gain.update((q,t) for t in matches)
        table.append({k0:r[k0] for k0 in ['query_key','query_index','query_sequence','question','native_query','features']} |
                     {'page2_gain':len(matches),'positive':bool(matches),'label':'positive' if matches else 'negative',
                      'new_gt_normalized_titles':sorted(matches),'snapshot_id':snapshots['snapshot_id']})
    assert len(union_gain)==63
    npos=sum(r['positive'] for r in table)
    by_question=defaultdict(list)
    for i,r in enumerate(table):by_question[r['query_index']].append(i)
    rng=random.Random(SEED)
    cluster_draws=[[rng.randrange(50) for _ in range(50)] for _ in range(BOOTSTRAPS)]
    verify_rng=random.Random(SEED)
    assert cluster_draws==[[verify_rng.randrange(50) for _ in range(50)] for _ in range(BOOTSTRAPS)]
    stats={}
    for index,name in enumerate(sorted(extracted['feature_definitions'])):
        valid=[r for r in table if r['features'][name] is not None]
        xs=[r['features'][name] for r in valid]
        gains=[r['page2_gain'] for r in valid]
        yy=[int(g>0) for g in gains]
        qq=[r['query_index'] for r in valid]
        pos=[x for x,y in zip(xs,yy) if y]
        neg=[x for x,y in zip(xs,yy) if not y]
        high=discrimination(xs,yy);low=discrimination([-x for x in xs],yy)
        bundle=metric_bundle(xs,gains)
        boot_by_question=defaultdict(list)
        for x,g,q in zip(xs,gains,qq):boot_by_question[q].append((x,g))
        samples=defaultdict(list)
        for draw in cluster_draws:
            pairs=[pair for q in draw for pair in boot_by_question[q]]
            bx,bg=map(list,zip(*pairs))
            for metric,value in metric_bundle(bx,bg).items():
                if value is not None:samples[metric].append(value)
        ci={metric:{'low':quantile(samples[metric],.025),'high':quantile(samples[metric],.975),'valid_draws':len(samples[metric])} for metric in bundle}
        ecdf=[]
        buckets=defaultdict(lambda:[0,0])
        for x,y in zip(xs,yy):buckets[x][0 if y else 1]+=1
        pc=nc=0
        for value,(p,n) in sorted(buckets.items()):
            pc+=p;nc+=n
            ecdf.append({'value':value,'positive_count':p,'negative_count':n,'positive_ecdf':pc/len(pos) if pos else None,'negative_ecdf':nc/len(neg) if neg else None})
        missing=[r for r in table if r['features'][name] is None]
        stats[name]={'family':extracted['feature_definitions'][name]['family'],
                     'n_valid':len(valid),'n_missing':len(missing),'missing_positive':sum(r['positive'] for r in missing),
                     'missing_negative':sum(not r['positive'] for r in missing),'positive':summarize(pos),'negative':summarize(neg),
                     'effect_size':{'hedges_g_positive_minus_negative':hedges_g(xs,yy),'cliffs_delta':2*high['roc_auc']-1 if high['roc_auc'] is not None else None},
                     'high_is_positive':high,'low_is_positive':low,'valid_subset_positive_prevalence':sum(yy)/len(yy),
                     'correlation_with_integer_page2_gain':{'pearson':bundle['pearson_gain'],'spearman':bundle['spearman_gain']},
                     'question_cluster_bootstrap_95ci':ci,'conditional_within_question':conditional(xs,gains,qq),
                     'pooled_quintile_strata':strata(xs,gains),'empirical_distributions':ecdf}
        if (index+1)%6==0: print(f'Analyzed {index+1}/36 features with {BOOTSTRAPS} cluster bootstrap draws',flush=True)
    # Common-support sensitivity: tail is missing on some queries. Compare on
    # identical rows with paired question-cluster draws, never impute missing tail.
    pairs=[(f'{source}_lexical_{metric}',base) for source in ['question','query']
           for metric in ['mean','tail3'] for base in ['mean_jaccard','max_jaccard']]
    pairs += [(f'{source}_lexical_tail3',f'{source}_lexical_mean') for source in ['question','query']]
    paired=[]
    for left,right in pairs:
        valid=[r for r in table if r['features'][left] is not None and r['features'][right] is not None]
        groups=defaultdict(list)
        for r in valid:groups[r['query_index']].append(r)
        def compare(selected):
            y=[int(r['positive']) for r in selected]
            a=discrimination([r['features'][left] for r in selected],y)
            b=discrimination([r['features'][right] for r in selected],y)
            return a,b
        a,b=compare(valid)
        differences=[];ap_differences=[]
        for draw in cluster_draws:
            aa,bb=compare([r for q in draw for r in groups[q]])
            if aa['roc_auc'] is not None and bb['roc_auc'] is not None:
                differences.append(aa['roc_auc']-bb['roc_auc'])
                ap_differences.append(aa['average_precision']-bb['average_precision'])
        paired.append({'left':left,'right':right,'orientation':'higher value predicts positive for both; descriptive comparison only',
                       'common_support_n':len(valid),'positive_count':sum(r['positive'] for r in valid),
                       'left_auc':a['roc_auc'],'right_auc':b['roc_auc'],
                       'auc_difference_left_minus_right':a['roc_auc']-b['roc_auc'],
                       'auc_difference_cluster_95ci':[quantile(differences,.025),quantile(differences,.975)],
                       'left_ap':a['average_precision'],'right_ap':b['average_precision'],
                       'ap_difference_left_minus_right':a['average_precision']-b['average_precision'],
                       'ap_difference_cluster_95ci':[quantile(ap_differences,.025),quantile(ap_differences,.975)]})
    result={'experiment':HERE.name,'status':'PASS','snapshot_id':snapshots['snapshot_id'],
            'query_count':248,'question_count':50,'positive_count':npos,'negative_count':248-npos,'positive_prevalence':npos/248,
            'gain_distribution':dict(sorted(Counter(r['page2_gain'] for r in table).items())),
            'sum_isolated_query_gains':sum(r['page2_gain'] for r in table),'union_new_gt':63,
            'semantic_embedding_status':'NOT_MEASURED_NO_LOCAL_EMBEDDING_MODEL',
            'bootstrap':{'unit':'user question (all its native queries resampled together)','seed':SEED,'draws':BOOTSTRAPS,'draws_sha256':digest(cluster_draws),'confidence':'percentile marginal 95%; exploratory, not adjusted for multiple features'},
            'metric_notes':{'PR_AUC_primary':'average_precision (step integral), tied score blocks processed together; random reference is positive prevalence',
                            'PR_AUC_secondary':'trapezoidal interpolation including initial (recall=0,precision=1); can look optimistic with ties',
                            'effect_direction':'positive minus negative; signed Cliff delta = 2*high-oriented ROC AUC - 1',
                            'correlation':'integer isolated query gain, NOT cumulative gain in a selected policy',
                            'low_orientation':'explicit descriptive negative direction only; no chosen threshold, feature combination or policy',
                            'constant_features':'ROC .5/AP prevalence; zero variance correlations and Hedges g null',
                            'dependencies':'query pairs within a question correlated; complementary/duplicate features not independent evidence'},
            'features':stats,'paired_common_support_comparisons':paired,
            'page1_features_sha256':sha(HERE/'page1_features.json'),'python_version':sys.version,
            'network_requests':0,'model_calls':0,'crawler_generations':0,'policy_created':False}
    # Inputs, controller artifacts, and all historical response files must remain frozen.
    assert all(sha(p)==h for p,h in before.items())
    for pair in snapshots['responses'].values():
        assert sha(pair['page1_path'])==pair['page1_sha256']
        assert sha(pair['page2_path'])==pair['page2_sha256']
    save(HERE/'query_signal_table.json',{'snapshot_id':snapshots['snapshot_id'],'feature_source':'page1_features.json','semantic_embedding_status':result['semantic_embedding_status'],'rows':table})
    fields=['query_key','query_index','query_sequence','question','native_query','label','positive','page2_gain']+sorted(stats)
    with (HERE/'query_signal_table.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in table:writer.writerow({k:r[k] for k in fields if k in r}|r['features'])
    save(HERE/'feature_stats.json',result)
    validation={'status':'PASS','query_count_and_snapshot_match':True,'query_count':248,'snapshot_id':snapshots['snapshot_id'],
                'labels_recomputed_from_frozen_gt_groups_and_cached_ids':True,'all_248_gains_equal_previous_experiment':True,
                'page1_gt_found':base_found,'union_page2_new_gt':len(union_gain),
                'question_text_matches_original_50':True,'feature_stage_access_allowlist_verified':True,
                'six_protected_read_attempts_denied_before_io':True,
                'feature_stage_no_gt_or_page2_outcome_reads':True,'all_496_response_files_unchanged':True,
                'all_source_and_frozen_input_hashes_unchanged':True,'bootstrap_draws_reproduced':True,'tie_and_null_statistics_unit_checks':True,
                'source_feature_sha256':sha(HERE/'page1_features.json'),'new_model_calls':0,'new_network_requests':0,'policy_created':False}
    save(HERE/'validation.json',validation)
    guard.allow([HERE/'query_signal_table.json',HERE/'query_signal_table.csv',HERE/'feature_stats.json'])
    save(HERE/'manifest.json',{'inputs':before,'snapshot_id':snapshots['snapshot_id'],'outputs':{str(p):sha(p) for p in [HERE/'query_signal_table.json',HERE/'query_signal_table.csv',HERE/'feature_stats.json']}})
    render(result,read(HERE/'environment_audit.json'))
    save(HERE/'analysis_access.json',guard.evidence())
    print(f'PASS: {npos} positive / {248-npos} negative; 36 features; frozen snapshot unchanged.')


if __name__=='__main__':
    main()
