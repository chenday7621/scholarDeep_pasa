"""Freeze official input, random sample, protocol and source hashes before Search."""
import json, random, re
from common import ROOT, REPO, save, sha, digest, now

SEED = 20260919
REVISION = 'a0c6a6a14e70cb776598f878cc28237d81add278'

def main():
    assert not (ROOT/'registration_manifest.json').exists(), 'Never resample a frozen experiment'
    assert not list((ROOT/'responses').glob('*.json')) and not list((ROOT/'attempts').glob('*.json'))
    rows = [json.loads(line) for line in (ROOT/'source/ScholarQuest.jsonl').read_text().splitlines() if line.strip()]
    # Source order, no topic/count/difficulty/local-DB coverage filtering.
    eligible = [i for i,r in enumerate(rows) if isinstance(r.get('final_query'),str) and r['final_query'].strip() and isinstance(r.get('answer_arxiv_ids'),list) and r['answer_arxiv_ids']]
    assert len({r['query_id'] for r in rows}) == len(rows)
    for i in eligible:
        assert all(isinstance(x,str) and re.fullmatch(r'\d{4}\.\d{4,5}(?:v\d+)?',x) for x in rows[i]['answer_arxiv_ids']), i
    chosen = random.Random(SEED).sample(eligible,50)
    sample=[]
    for j,i in enumerate(chosen):
        r=rows[i]
        sample.append({'question_id':f'Q{j:02d}','source_row_index':i,'source_query_id':r['query_id'],'question':r['final_query'], 'answer_arxiv_ids':r['answer_arxiv_ids'], 'gt_arxiv_ids': sorted({re.sub(r'v\d+$','',x) for x in r['answer_arxiv_ids']}), 'source_record_sha256':digest(r)})
    save(ROOT/'dataset_manifest.json',{'experiment':'SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005','frozen_utc':now(),'source_repository':'https://github.com/pty12345/ScholarQuest','source_revision':REVISION,'source_url':f'https://raw.githubusercontent.com/pty12345/ScholarQuest/{REVISION}/datasets/ScholarQuest.jsonl','source_sha256':sha(ROOT/'source/ScholarQuest.jsonl'),'source_rows':len(rows),'eligible_rows':len(eligible),'eligibility':'Nonempty official final_query and explicit nonempty answer_arxiv_ids; no difficulty, topic, GT-count, local-database or Search-outcome filtering. All ID syntax checked before sampling.','eligible_source_row_indices':eligible,'sampling_seed':SEED,'sampling_method':'Python random.Random(seed).sample(eligible source row indices in file order, 50), preserving sampled order','sample_size':50,'sample_sha256':digest(sample),'gt_rule':'Only frozen answer_arxiv_ids, remove optional version suffix and deduplicate per question; never infer GT from titles or local DB','total_gt':sum(len(q['gt_arxiv_ids']) for q in sample),'sample':sample})
    save(ROOT/'questions.json',{'questions':[{k:q[k] for k in ['question_id','source_query_id','question']} for q in sample]})
    protocol='''# SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005 — preregistration

Freeze before any native generation or Serper Search. Official ScholarQuest commit a0c6a6a14e70cb776598f878cc28237d81add278, datasets/ScholarQuest.jsonl. Exactly 50 uniformly sampled eligible rows, seed=20260919, source file order. No seed changes, resampling, query rewriting, filtering difficult questions or outcome-dependent exclusion.

## Native generation and Search

Use existing models.Agent.infer, checkpoints/pasa-7b-crawler, agent_prompt.json.generate_query and PaperAgent's original regex and first-five cap. Per-question Python/NumPy/Torch/CUDA seed=42; PYTHONHASHSEED=42. Preserve checkpoint generation config (do_sample=true, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.05) and max_new_tokens=512. Save complete prompt/raw output/parsed queries. One generation per question; fewer than five queries retained; zero queries or generation error means INCOMPLETE and stop, never repair or replace.

For each native query, sequentially request Page1 Top10 then Page2 Top10 with q='{native query} before:2026-09-19 site:arxiv.org', num=10, page=1/2. Fixed cutoff uses current experiment date because official data has no per-question benchmark publication cutoff. No Selector, citation expansion or local-paper resolver. No Router implementation/evaluation. Save complete response bytes, parsed JSON, request payload, UTC timestamps, latency and hashes. Network/429/5xx retries capped at three attempts, never retry successful responses, preserve failures. Nonretryable failure or exhausted retries means INCOMPLETE, no smaller-subset effectiveness claim. Native modern arXiv URL parser remains unchanged; inspect site adherence separately.

## Endpoints

GT = frozen official answer_arxiv_ids with optional version suffix stripped. Deduplicate IDs within each question across queries/pages; count the same ID separately for different questions. Let G be question GT, P1 union all native Page1 IDs, P2 union all native Page2 IDs. Native Page1 finds G∩P1; Always Page2 finds G∩(P1∪P2); question gain is G∩(P2−P1). Macro recall = average question recall over all 50; Micro = pooled found/pooled GT.

Primary isolated query gain = G∩(query Page2−all-question Page1 union). This is the relevant opportunity label for future replay; overlapping gains across queries are NOT summed as question gain. Also save pair-local gain G∩(query Page2−query Page1) under a separate name. Save every Page1/Page2 ID set, gained GT IDs, query index and question outcomes. Denominator for ΔGT/extra Page2 call = all native queries, irrespective of gained GT or retry count. Report actual HTTP attempts separately.

## Fixed exploratory opportunity gate

Continue to an independent fixed max_jaccard top1 routing validation only if COMPLETE (50/50), total ΔGT>=10, at least five questions gain >=1 GT, and ΔGT/extra Page2 call>=0.05. This conservative practical threshold is set before Search; it is not a significance test or evidence of any Router benefit. Always Page2 measures available opportunity only. Do not run, implement, select, tune or evaluate a Router here. Search snapshots are dynamic; conclusions are conditional on this sample, source and time. No post-hoc alternate threshold.

## Required outputs

dataset_manifest.json, snapshot_manifest.json, query_outcomes.json, question_outcomes.json, results.json, SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005.md, validation.json. Independently reproduce sampling, hashes, raw-byte decoding, parser, paired order, per-query and per-question set arithmetic, aggregate metrics and gate; verify protected sources unchanged. The final report ends with only the opportunity question and its answer.
'''
    (ROOT/'PREREGISTRATION.md').write_text(protocol)
    frozen=['source/ScholarQuest.jsonl','source/README.md','dataset_manifest.json','questions.json','PREREGISTRATION.md','common.py','prepare.py','collect.py']
    save(ROOT/'input_manifest.json',{'files':{'questions.json':sha(ROOT/'questions.json')}})
    frozen.append('input_manifest.json')
    protected=['paper_agent.py','models.py','agent_prompt.json','utils.py','run_paper_agent.py','metrics.py','checkpoints/pasa-7b-crawler/config.json','checkpoints/pasa-7b-crawler/generation_config.json']
    save(ROOT/'registration_manifest.json',{'status':'ACTIVE','frozen_utc':now(),'search_requests_at_freeze':0,'generation_calls_at_freeze':0,'frozen_files':{n:sha(ROOT/n) for n in frozen},'protected_sources':{n:sha(REPO/n) for n in protected},'opportunity_gate':{'minimum_delta_gt':10,'minimum_gain_questions':5,'minimum_delta_gt_per_page2_call':0.05}})
    print(json.dumps({'sample_size':len(sample),'eligible':len(eligible),'total_gt':sum(len(q['gt_arxiv_ids']) for q in sample),'dataset_manifest_sha256':sha(ROOT/'dataset_manifest.json'),'sample_sha256':digest(sample)},indent=2))

if __name__=='__main__': main()
