# ScholarQuest Page2 opportunity probe 005

This isolated experiment compares only Native Page1 with Always Page2. It does not implement or evaluate a Router. Formal PaSa sources are protected by hashes in `registration_manifest.json`.

The official dataset, 50 questions, GT IDs, seeds, sampling algorithm, opportunity gate, collector source and PaSa configuration were frozen before generation/Search. The full protocol is in `PREREGISTRATION.md`.

Files:

- `source/`: exact official dataset bytes and README at the pinned Git commit.
- `dataset_manifest.json`: all frozen question identities, official answer IDs, sampling provenance and hashes.
- `questions.json`: GT-free input to native generation and Search.
- `generations/`: one original Crawler output per question, including prompt, parsed queries and timestamps.
- `responses/`, `attempts/`: successful snapshots and every HTTP attempt; complete response bytes are losslessly Base64-encoded.
- `snapshot_manifest.json`: immutable index and SHA-256 hashes of captured evidence.
- `query_outcomes.json`: both pages' ID sets and gains for each native query, in original generation order.
- `question_outcomes.json`: within-question union and GT deduplication.
- `results.json`: the two requested policies and the fixed opportunity gate.
- `SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005.md`: final report.
- `validation.json`: independently reconstructed checks and artifact hashes.

Read-only-from-snapshot regeneration (no network or model inference):

```bash
cd /home/chenyi/pasa
python3 scholarquest_page2_opportunity_probe_005/evaluate.py
python3 scholarquest_page2_opportunity_probe_005/report.py
python3 scholarquest_page2_opportunity_probe_005/validate.py
```

Evaluation requires the entire 50-question capture to be complete. The final validator also checks local checkpoint hashes, so allow time to read the weight files. Do not rerun `prepare.py`: it deliberately rejects an already frozen registration. Successful Search responses must never be refreshed. `collect.py` supports only resuming an interrupted capture under the same protocol; it refuses a completed run.

Primary isolated query gain is relative to **all native Page1 results for the question**, not just that query's Page1. Pair-local gain is separately labeled. Summing overlapping isolated gains is not a valid total ΔGT; use the within-question union.
