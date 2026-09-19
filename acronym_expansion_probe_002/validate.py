"""Artifact integrity and accounting checks, without a correctness oracle."""
import hashlib
import json
from pathlib import Path
import re
from probe import OUT, ROOT, SOURCE, B_INSTRUCTION, native_spec, sha, snapshot
from metrics import metrics, summarize

def main():
    d=json.loads(OUT.read_text()); src=json.loads(SOURCE.read_text())
    assert d['status']=='complete'
    assert len(d['samples'])==29
    source={s['sample_id']:s for s in src['samples']}
    pattern,cap,_=native_spec()
    assert cap==5
    group_seeds={'A':set(),'B':set()}
    for s in d['samples']:
        original=source[s['sample_id']]
        for k in ('query_id','original_question','acronym','mentions','question_zh'): assert s[k]==original[k]
        assert all(v is None for v in s['human_review'].values())
        a=s['groups']['A']; b=s['groups']['B']
        assert a['prompt']==d['provenance']['native_prompt_template'].format(user_query=s['original_question']).strip()
        assert b['prompt']==a['prompt']+'\n'+B_INSTRUCTION
        assert [r['seed'] for r in a['runs']]==[r['seed'] for r in b['runs']]
        for g,data in s['groups'].items():
            assert [r['run'] for r in data['runs']]==[1,2,3,4,5]
            assert len({r['seed'] for r in data['runs']})==5
            prompt_hash=hashlib.sha256(data['formatted_prompt'].encode()).hexdigest()
            assert data['prompt_sha256']==prompt_hash
            for r in data['runs']:
                assert r['seed'] not in group_seeds[g]
                group_seeds[g].add(r['seed'])
                assert r['prompt_sha256']==prompt_hash
                queries=[q.strip() for q in re.findall(pattern,r['raw_output'],flags=re.DOTALL)]
                assert r['all_parsed_search_queries']==queries and r['search_queries']==queries[:cap]
                assert r['discarded_queries_by_native_cap']==queries[cap:]
                assert len(r['generated_token_ids'])==r['generated_token_count']<=512
                assert r['metrics']==metrics(r,s)
                for q in r['metrics']['per_query']:
                    for candidate in q['expansion_candidates']:
                        assert q['query'][candidate['start']:candidate['end']]==candidate['text']
                        assert candidate['human_judgment'] is None
    for group in ('A','B'):
        assert len(group_seeds[group])==145
        assert d['summary'][group]==summarize(d['samples'],group)
    assert group_seeds['A']==group_seeds['B']
    assert snapshot()==d['provenance']['protected_files_before']==d['provenance']['protected_files_after']
    # Same frozen checkpoint as 001, including every weight shard fingerprint.
    assert d['provenance']['checkpoint_files']==src['provenance']['checkpoint_files']
    for name in ('config.json','generation_config.json','tokenizer_config.json'):
        assert sha(Path(d['provenance']['checkpoint'])/name)==d['provenance']['checkpoint_files'][name]['sha256']
    manual=(ROOT/'ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW.md').read_text()
    assert manual.count('Gold Expansion:\n[人工填写]')==29
    assert manual.count('Notes:\n[人工填写]')==29
    assert manual.count('- [ ] 正确展开')==58
    assert manual.count('- [ ] 更好')==29
    assert '- [x]' not in manual.lower()
    for n in range(1,6): assert manual.count(f'#### Run {n}\n')==58
    assert d['summary']['combined']['expansion_accuracy'] is None
    print('PASS: 29 identical source samples, 290 complete generations, paired unique seeds, exact A/B prompt delta, native parsing/cap, literal candidate spans, independently recomputed metrics, blank human fields, and unchanged protected files/checkpoint.')
    for name in ('ACRONYM_EXPANSION_PROBE_002.json','ACRONYM_EXPANSION_PROBE_002.md','ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW.md'):
        path=ROOT/name
        print(path,path.stat().st_size,'bytes')

if __name__=='__main__':main()
