"""Cross-check raw generation evidence, native contract, artifacts and frozen inputs."""
import collections
import hashlib
import itertools
import json
import re
import statistics
import subprocess
from probe import ROOT, WORK, OUT, REPORT, MANUAL, CHECKPOINT, B_TEMPLATE, read, questions, protected, sha, save, now

def main():
    d=read();p=d['provenance'];assert d['status']=='complete'
    assert p['protected_before']==p['protected_after']==protected()
    checkpoint_after={f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(CHECKPOINT.iterdir()) if f.is_file()}
    assert checkpoint_after==p['checkpoint_files']
    assert sha(WORK/'analysis.py')==p['analysis_sha256_before_inference']
    assert sha(WORK/'probe.py')==p['runner_sha256']
    assert p['A_template']==read(ROOT/'agent_prompt.json')['generate_query']
    assert p['B_template']==B_TEMPLATE
    assert p['generation_overrides']=={'max_new_tokens':512}
    assert p['physical_gpu_index']==1 and p['seed']==42 and p['batch_size']==1
    assert all(event in ('socket.__new__','socket.getaddrinfo','socket.gethostbyname') for event in p['blocked_network_events'])
    for key in ('do_sample','temperature','top_p','top_k','repetition_penalty','eos_token_id'):
        assert p['loaded_generation_config'][key]==p['generation_config_file'][key]
    raw_files=list((WORK/'raw_generations').glob('*.json'));assert len(raw_files)==100
    manual=MANUAL.read_text();report=REPORT.read_text()
    assert re.findall(r'^## (Q\d+)$',manual,re.M)==[f'Q{i}' for i in range(50)]
    assert manual.count('中文翻译：')==50 and manual.count('Notes:')==50
    projections=questions();assert len(d['per_query'])==len(projections)==50
    previous_time=''
    for q,orig in zip(d['per_query'],projections):
        assert all(q[k]==v for k,v in orig.items())
        assert q['question_zh'] in manual
        section=re.search(r'^## '+q['query_id']+r'\n(.*?)(?=^## Q\d+\n|\Z)',manual,re.S|re.M)[1]
        assert q['original_question'].strip() in section
        for group in ('A','B'):
            g=q['groups'][group];saved=read(WORK/'raw_generations'/f"{q['query_id']}_{group}.json")
            assert {k:v for k,v in g.items() if k!='metrics'}==saved
            assert g['seed']==42
            assert g['prompt']==p[f'{group}_template'].format(user_query=q['original_question']).strip()
            assert hashlib.sha256(g['formatted_prompt'].encode()).hexdigest()==g['prompt_sha256']
            parsed=[x.strip() for x in re.findall(r'Search\](.*?)\[',g['raw_output'],re.S)]
            assert parsed==g['all_parsed_queries'] and parsed[:5]==g['queries'] and parsed[5:]==g['discarded_queries']
            assert len(g['generated_token_ids'])==g['generated_token_count']<=512
            assert g['started_utc']>=previous_time;previous_time=g['finished_utc']
            label='Baseline Queries:' if group=='A' else 'V1.1 Queries:'
            actual=section.split(label,1)[1].split('V1.1 Queries:',1)[0] if group=='A' else section.split(label,1)[1].split('关键实体 /',1)[0]
            assert re.findall(r'^\d+\. (.*)$',actual,re.M)==g['queries']
        if q['query_index'] in (18,28,43,48):
            focus=report.split('### '+q['query_id']+'\n',1)[1].split('\n### Q',1)[0]
            for g in q['groups'].values():
                assert g['raw_output'] in focus
                assert all(f'{i+1}. {v}' in focus for i,v in enumerate(g['queries']))
    independent={}
    for group in ('A','B'):
        gs=[q['groups'][group] for q in d['per_query']];allpairs=[];exactentries=exactpairs=highpairs=nearpairs=0
        per_question=[];dist=collections.Counter()
        for g in gs:
            qs=g['queries'];dist[str(len(qs))]+=1;exactentries+=len(qs)-len(set(qs));scores=[]
            for x,y in itertools.combinations(qs,2):
                tx=set(re.findall('[a-z0-9]+',x.lower()));ty=set(re.findall('[a-z0-9]+',y.lower()))
                score=len(tx&ty)/len(tx|ty) if tx|ty else 0;scores.append(score);allpairs.append(score)
                exactpairs+=x==y;highpairs+=score>=.85;nearpairs+=score>=.85 and x!=y
            if scores:per_question.append(statistics.mean(scores))
        s=d['summary'][group]
        check={'total_query_count':sum(len(g['queries']) for g in gs),'search_parse_success':sum(bool(g['queries']) for g in gs),'query_count_distribution':dict(dist),'exact_duplicate_query_count':exactentries,'exact_duplicate_pair_count':exactpairs,'high_similarity_pair_count':highpairs,'near_duplicate_pair_count':nearpairs,'pair_count':len(allpairs),'mean_pairwise_token_jaccard_pooled':statistics.mean(allpairs),'mean_pairwise_token_jaccard_macro_eligible':statistics.mean(per_question)}
        assert all(s[k]==v for k,v in check.items());independent[group]=check
    diff=subprocess.run(['git','diff','--quiet','HEAD','--'],cwd=ROOT)
    assert diff.returncode==0,'Tracked working tree differs from HEAD'
    evidence={'validated_utc':now(),'checks':'PASS: 100 raw records, exact prompts/questions/seeds/native parse, matching run config, independent duplication statistics, all 50 translated review entries, focused raw/parsed output, recorded network creation attempts denied, unchanged protected files/checkpoint/analysis, no tracked diff.', 'blocked_network_events':p['blocked_network_events'],'independent_statistics':independent,'checkpoint_after':checkpoint_after,'output_sha256':{f.name:sha(f) for f in (OUT,REPORT,MANUAL)},'validator_sha256':sha(__file__)}
    save(WORK/'validation.json',evidence)
    print(evidence['checks'])
if __name__=='__main__':main()
