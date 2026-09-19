# SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005 — preregistration

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
