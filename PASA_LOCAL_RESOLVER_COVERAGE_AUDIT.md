# PaSa Local Resolver Coverage Audit

Audit date: 2026-09-09  
Scope: offline-only audit of all 50 `RealScholarQuery` samples and the existing Q0 `REPRO_LOCAL_RESOLVER_001` output. No model was loaded, no network endpoint was accessed, and no source or dataset file was modified.

## Data and matching definition

- Evaluation data: `data/RealScholarQuery/test.jsonl` (50 rows, SHA-256 `b3b570411ce2399ce4ea145ba9b2d3d0048b248030edeeb44ba95a7e9dc575c2`).
- ID/title metadata: `data/paper_database/id2paper.json` (569,432 rows, SHA-256 `dcbabaf06021dfc25fb97585a7066845fa6ba3a4d477aa155351841a700b74d5`).
- Local paper content: `data/paper_database/cs_paper_2nd.zip`.
- Q0 run artifact: `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/0.json`.
- Q0 metrics artifact: `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/smoke_report.json`.
- Normalization is exactly the rule used by `REPRO_LOCAL_RESOLVER_001`: retain every Unicode character for which `str.isalpha()` is true, concatenate them, and lowercase the result (`keep_letters`). Digits, whitespace, punctuation, mathematical symbols, and markup are discarded.
- A paper is counted as locally usable by ID only when its ID occurs in `id2paper.json` **and** the ZIP contains the normalized title entry used by `search_paper_by_arxiv_id`. Metadata-only IDs without a ZIP entry are reported separately.
- A title is a unique local hit only when its normalized key maps to exactly one ID globally and that title has a ZIP entry. A key mapping to multiple IDs is ambiguous and is not selected.

## RealScholarQuery GT coverage

The 50 samples contain 791 GT occurrences, representing 772 unique arXiv IDs. Repeated GT annotations are retained in occurrence-level statistics because they contribute separately to the 50-query evaluation; unique-ID statistics are also shown.

| Metric | GT occurrences (n=791) | Unique GT IDs (n=772) |
|---|---:|---:|
| ID present in `id2paper.json` | 739 (93.43%) | 720 (93.26%) |
| ID has usable local ZIP content | **737 (93.17%)** | **718 (93.01%)** |
| Exact normalized title is a unique local hit | **685 (86.60%)** | **667 (86.40%)** |
| Exact normalized title miss | **104 (13.15%)** | **103 (13.34%)** |
| Exact normalized title ambiguous | **2 (0.25%)** | **2 (0.26%)** |

The title categories partition all annotations: `685 unique hits + 104 misses + 2 ambiguous = 791`.

The two ambiguous GTs are `Panacea+` (arXiv `2408.07605`) and `Panacea` (arXiv `2311.16813`). Because `keep_letters` discards `+`, digits, punctuation, and whitespace, both titles collapse to the same key. The resolver correctly refuses to choose one.

Of the 104 title misses, 50 occurrences (49 unique IDs) have usable paper content in the ZIP under the GT arXiv ID. These are confirmed title variants or metadata differences, not missing papers. They are 6.32% of all GT annotations and 48.08% of GT title misses. The remaining 54 occurrences lack usable local content by ID; 52 IDs are absent from `id2paper.json`, while two IDs have metadata but no corresponding ZIP entry.

Representative GT title differences:

| arXiv ID | GT title | Local metadata title | Cause |
|---|---|---|---|
| `2210.03629` | `ReAct: Synergizing Reasoning and Acting in Language Models` | `\model: Synergizing Reasoning and Acting in Language Models` | LaTeX macro replaced the model name |
| `2312.08935` | `Math-shepherd: Verify and reinforce llms step-by-step without human annotations` | `\methodname: Verify and Reinforce LLMs Step-by-step without Human Annotations` | LaTeX macro replaced the method name |
| `2106.13043` | `Audioclip: Extending clip to image, text and audio` | `AudioCLIP: Extending CLIP to Image, Text and AudioThis work was supported ...` | Local title contains appended acknowledgement text |
| `2310.08540` | `Do pretrained Transformers Learn In-Context by Gradient Descent?` | `Revisiting In-context Learning and Gradient Descent Analogy` | Substantial title/version change |
| `2210.05675` | `... context vs in weights.` | `... context vs weights` | Small wording difference |
| `2111.12417` | `N\"UWA: ...` | `NÜWA: ...` | TeX accent versus Unicode |

This is a meaningful exact-match limitation, but it is not evidence that the resolver index is corrupt. The ID path confirms the local papers exist. No fuzzy resolver was implemented in this audit.

## Q0 local-miss reconstruction

The Q0 run reported:

- `LOCAL_TITLE_LOOKUPS=1236`
- `LOCAL_TITLE_HITS=905`
- `LOCAL_TITLE_MISSES=329`
- `LOCAL_TITLE_AMBIGUOUS=2`
- `ARXIV_FALLBACKS=331`

The old instrumentation stored aggregate counters and 220 unique final-failure titles, but did not store every title for every logical call. The output tree makes 274 of the 329 miss calls exactly recoverable: every child section proves that the section was selected, and all 1,062 citations in those sections were looked up. These citations contain 786 local hits, 274 local misses, and both ambiguous calls.

The remaining selected sections produced no novel child, so their names were not serialized. Counter reconciliation proves that they account for 174 lookups: 119 local hits and 55 local misses. Comparing the 226 arXiv fallback cache keys against the recoverable calls identifies 24 additional local-miss keys that must each have appeared at least once. Therefore 298 miss occurrences can be assigned to a known title/category, while the titles of the last 31 repeated calls cannot be recovered uniquely from the saved artifacts. Assigning those 31 to `OTHER` avoids fabricating evidence.

After excluding the two ambiguous Nemotron titles, the 329 local misses represent 224 unique fallback cache keys. Each unique key was reviewed offline against `id2paper.json` and the ZIP. Character/token similarity was used only to propose local candidates for manual inspection; it was not added to PaSa.

Classification precedence:

1. `TITLE_VARIANT`: a high-confidence matching paper and ZIP entry exist locally, but the exact normalized titles differ.
2. `DIRTY_OR_INCOMPLETE`: the citation field is visibly an author fragment, malformed bibliography, truncated string, or corrupted title.
3. `NON_ARXIV`: the reference is clearly a website, model card, repository, legal case, book/report, legacy publication, or other non-arXiv item based on the saved citation text and offline metadata.
4. `NOT_IN_DB`: a clean paper-like citation has no validated usable local match. This does not claim the paper does not exist externally; it means it is not present in the supplied local database.
5. `OTHER`: repeat calls whose exact title cannot be recovered from the old aggregate-only instrumentation.

### Call-level result

| Category | Calls | Share of 329 | Unique known keys | Representative examples |
|---|---:|---:|---:|---|
| Paper not in supplied local DB | **113** | **34.35%** | 87 | `Mamba: Linear-time sequence modeling with selective state spaces`; `Gemini: A family of highly capable multimodal models`; `Self-RAG: Learning to retrieve, generate, and critique through self-reflection` |
| Local paper, title variant | **42** | **12.77%** | 33 | `Self-Instruct...` versus local `ACL 2023 Self-Instruct...`; `D2 pruning...` versus local `𝔻² Pruning...`; `ReAct...` versus local `\model...`; `Turning big data... k-means` versus local mathematical Unicode `𝑘-means` |
| Dirty or incomplete citation title | **8** | **2.43%** | 8 | `B`; `Borgeaud, A`; a long author list beginning `Dai, Thanumalayan...`; malformed `J. Ren ... ZeRO-Offload...` bibliography text |
| Non-arXiv/reference material | **135** | **41.03%** | 96 | `Common Crawl - commoncrawl.org`; `OpenAI: Introducing ChatGPT`; Anthropic Claude URL; `Doe 1 v. GitHub`; `BLEU...`; `Latent Dirichlet Allocation` |
| Other / exact repeated title unrecoverable | **31** | **9.42%** | — | Aggregate-only logging proves these are repeats of already seen fallback cache keys, but not which keys |
| **Total** | **329** | **100.00%** | **224** | |

The first four call counts are confirmed lower bounds because the unresolved 31 repeats may belong to any of those categories. Corresponding upper bounds are obtained by adding 31: `NOT_IN_DB <= 144`, `TITLE_VARIANT <= 73`, `DIRTY_OR_INCOMPLETE <= 39`, and `NON_ARXIV <= 166`. The unique-key classification is complete: 87 not in DB, 33 title variants, 8 dirty/incomplete, and 96 non-arXiv (`87 + 33 + 8 + 96 = 224`).

### Is exact matching missing a large amount of local content?

There is a material minority, not a majority:

- Q0 has 42 confirmed title-variant calls (12.77% of all 329 misses) across 33 unique keys (14.73% of 224 unique miss keys).
- Because 31 repeated calls lack per-call attribution, the strict worst-case upper bound is 73/329 (22.19%).
- Across the full GT set, 50/791 annotations (6.32%) have usable local content by ID but miss exact title matching.

The main causes are LaTeX placeholders (`\model`, `\methodname`, `\ours`), title/version changes, prefixes or suffixes added to metadata, Unicode/TeX representation differences, and a few parser-corrupted titles. Punctuation alone is generally not the cause because the current normalization already removes it.

## Pilot readiness

`LOCAL_RESOLVER_READY_FOR_5_QUERY_PILOT=NO` under the current configuration.

The exact resolver itself is internally consistent and gives strong GT coverage, but the decision includes known behavior from the already-saved Q0 run: 331 fallbacks produced 856 arXiv HTTP requests, 840 HTTP 429 responses, and 220 final lookup failures. The full GT audit also finds 50 annotations whose local paper is available but inaccessible by exact title. Running five queries now would therefore mix model quality with a large, known resolver/fallback failure mode. This audit does not implement fuzzy matching or any algorithm change.

## Requested summary

```text
GT_TOTAL=791
GT_UNIQUE=772
GT_ID_IN_LOCAL_DB=737/791 (93.17%); UNIQUE=718/772 (93.01%)
GT_TITLE_UNIQUE_HIT=685/791 (86.60%); UNIQUE=667/772 (86.40%)
GT_LOCAL_ID_COVERAGE=93.17% (occurrence); 93.01% (unique ID)
GT_LOCAL_TITLE_COVERAGE=86.60% (occurrence); 86.40% (unique ID)
GT_TITLE_MISS=104/791 (13.15%); UNIQUE=103/772 (13.34%)
GT_TITLE_AMBIGUOUS=2/791 (0.25%); UNIQUE=2/772 (0.26%)

Q0_LOCAL_MISSES=329
Q0_MISS_NOT_IN_DB=113 (34.35%)
Q0_MISS_TITLE_VARIANT=42 (12.77%)
Q0_MISS_DIRTY_OR_INCOMPLETE=8 (2.43%)
Q0_MISS_NON_ARXIV=135 (41.03%)
Q0_MISS_OTHER=31 (9.42%)

LOCAL_RESOLVER_READY_FOR_5_QUERY_PILOT=NO
```
