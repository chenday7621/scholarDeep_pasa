# RealScholarQuery-50 local-only reproduction baseline

本报告记录 `SEED=42`、`REPRO_LOCAL_ONLY_001` 与 `REPRO_SELECTOR_SERIALIZATION_001` 下的完整 RealScholarQuery Q0–Q49 baseline。每题使用独立 Python 进程串行运行；一题完成并确认 GPU 回落后才启动下一题。Crawler、Selector、Prompt、checkpoint、检索深度和生成参数均未改变。

```text
REALSCHOLARQUERY_50_BASELINE=PASS
VALID_QUERIES=50
SEED=42
MACRO_F1=0.3547
MICRO_F1=0.3793
CRAWLER_RECALL=0.4947
MAIN_RECALL_BOTTLENECK=CRAWLER_SEARCH_MISS (283/416, 68.03%)
INFRASTRUCTURE_ISSUES=无执行失败；最高GPU显存38642MiB（RealScholarQuery_3），未发生OOM或worker exception；live Serper响应仍是跨次运行变动源
READY_FOR_ERROR_ANALYSIS=YES
NEXT_STEP_RECOMMENDATION=使用本次Serper replay做离线错误分析，优先检查Crawler Search miss，再审计Citation Expand miss和local exact unresolved；在形成证据前不改算法
```

## Configuration and provenance

- Seed sources: `PYTHONHASHSEED`, Python `random`, NumPy, `torch`, `torch.cuda.manual_seed`, `torch.cuda.manual_seed_all`, all 42.
- Parameters: `expand_layers=2`, `search_queries=5`, `search_papers=10`, `expand_papers=20`, `threads_num=20`. `search_queries=5` is a maximum; Q18 and Q28 each produced four parseable queries, and no query was synthesized to fill the fifth slot.
- Checkpoints: `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler` and `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-selector`.
- Physical GPUs: A100-PCIE-40GB indices 1 and 2. Selector maximum observed GPU-forward concurrency was 1.
- `ONLINE_TITLE_REQUESTS=0`: local exact misses and ambiguous titles were skipped; neither arXiv HTML nor API title search was called.
- Worker exception propagation passed the pre-run probe. All 50 queries completed two Expand layers and ended with GPU 1/2 at 0 MiB.
- The source hash set was checked before every query. Run-before/run-after hashes match.
- No SFT, PPO, alias, fuzzy matching, embedding resolver, or non-arXiv filter was used.

## Aggregate metrics

```text
VALID_QUERIES=50
TOTAL_GT=790
TOTAL_CRAWLER_GT_FOUND=404
TOTAL_FINAL_GT_FOUND=374
MACRO_PRECISION=0.3609
MACRO_RECALL=0.4535
MACRO_F1=0.3547
MICRO_PRECISION=0.3164
MICRO_RECALL=0.4734
MICRO_F1=0.3793
CRAWLER_RECALL=0.4947
MICRO_CRAWLER_RECALL=0.5114
AVG_LATENCY=79.947s
P50_LATENCY=78.196s
P95_LATENCY=108.253s
MAX_LATENCY=126.798s
TOTAL_SERPER_CALLS=248
AVG_SEARCH_NODES=28.06
AVG_EXPAND_NODES=428.16
AVG_SELECTOR_PROMPTS=456.22
AVG_LOCAL_TITLE_HIT_RATE=66.01%
MAX_GPU_MEMORY=38642MiB
OOM_QUERIES=0
FAILED_QUERIES=0
```

原始数据有 791 个 GT 标注；Q45 有两个仅排版不同、归一化后相同的标题。因此仓库 `metrics.py` 的集合语义得到 `TOTAL_GT=790`。报告中的 Precision/Recall/F1 均使用相同的 `keep_letters` 标题归一化和 `select_score > 0.5` 阈值。

官方 `metrics.py` 复算输出：

```text
0.4947 & 0.3609 & 0.4535 & 0.4936 & 0.48 & 0.4189
0.4947 & 111.42 & 0.0347 & 0.3609  & 0.4535
```

第一行前三项分别为官方 Macro Crawler Recall、Precision、Recall：`0.4947 / 0.3609 / 0.4535`，与独立汇总一致。

## Per-query summary

| Query | GT | Crawler GT | Final GT | Returned | P | R | F1 | Search | Expand | Prompts | Local hit | Serper | Latency | Peak GPU1/GPU2 MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q0 | 9 | 4 | 3 | 10 | 0.3000 | 0.3333 | 0.3158 | 28 | 423 | 451 | 71.37% | 5 | 90.83s | 23762/27374 |
| Q1 | 29 | 18 | 17 | 30 | 0.5667 | 0.5862 | 0.5763 | 27 | 454 | 481 | 73.40% | 5 | 99.61s | 23684/27318 |
| Q2 | 21 | 15 | 15 | 23 | 0.6522 | 0.7143 | 0.6818 | 24 | 424 | 448 | 83.87% | 5 | 63.52s | 22532/26128 |
| Q3 | 42 | 22 | 22 | 60 | 0.3667 | 0.5238 | 0.4314 | 34 | 916 | 950 | 77.52% | 5 | 126.80s | 32822/38642 |
| Q4 | 44 | 19 | 17 | 56 | 0.3036 | 0.3864 | 0.3400 | 33 | 684 | 717 | 65.05% | 5 | 98.45s | 30720/34332 |
| Q5 | 7 | 5 | 4 | 10 | 0.4000 | 0.5714 | 0.4706 | 35 | 480 | 515 | 77.94% | 5 | 76.42s | 19130/22734 |
| Q6 | 24 | 6 | 6 | 30 | 0.2000 | 0.2500 | 0.2222 | 19 | 334 | 353 | 80.54% | 5 | 72.32s | 21966/25592 |
| Q7 | 35 | 11 | 11 | 47 | 0.2340 | 0.3143 | 0.2683 | 32 | 555 | 587 | 64.78% | 5 | 84.98s | 27910/31542 |
| Q8 | 16 | 8 | 8 | 34 | 0.2353 | 0.5000 | 0.3200 | 22 | 331 | 353 | 64.98% | 5 | 84.10s | 18262/21866 |
| Q9 | 39 | 16 | 16 | 39 | 0.4103 | 0.4103 | 0.4103 | 24 | 380 | 404 | 67.85% | 5 | 80.99s | 18326/21930 |
| Q10 | 15 | 8 | 6 | 8 | 0.7500 | 0.4000 | 0.5217 | 33 | 585 | 618 | 78.15% | 5 | 96.31s | 21466/25076 |
| Q11 | 20 | 11 | 8 | 11 | 0.7273 | 0.4000 | 0.5161 | 15 | 374 | 389 | 82.12% | 5 | 54.12s | 19204/22814 |
| Q12 | 17 | 9 | 9 | 21 | 0.4286 | 0.5294 | 0.4737 | 33 | 703 | 736 | 79.43% | 5 | 93.40s | 29726/33336 |
| Q13 | 12 | 5 | 3 | 4 | 0.7500 | 0.2500 | 0.3750 | 22 | 358 | 380 | 73.68% | 5 | 76.80s | 19854/23458 |
| Q14 | 9 | 5 | 5 | 24 | 0.2083 | 0.5556 | 0.3030 | 34 | 530 | 564 | 65.49% | 5 | 103.80s | 25482/29094 |
| Q15 | 5 | 2 | 2 | 3 | 0.6667 | 0.4000 | 0.5000 | 29 | 320 | 349 | 63.41% | 5 | 63.00s | 19470/23074 |
| Q16 | 8 | 5 | 4 | 19 | 0.2105 | 0.5000 | 0.2963 | 24 | 203 | 227 | 44.02% | 5 | 51.88s | 17702/21328 |
| Q17 | 9 | 4 | 3 | 3 | 1.0000 | 0.3333 | 0.5000 | 30 | 403 | 433 | 72.04% | 5 | 83.00s | 17118/20760 |
| Q18 | 5 | 1 | 1 | 12 | 0.0833 | 0.2000 | 0.1176 | 33 | 422 | 455 | 66.89% | 4 | 76.99s | 20702/24314 |
| Q19 | 37 | 19 | 14 | 17 | 0.8235 | 0.3784 | 0.5185 | 21 | 223 | 244 | 57.28% | 5 | 74.21s | 18026/21640 |
| Q20 | 4 | 1 | 1 | 6 | 0.1667 | 0.2500 | 0.2000 | 36 | 869 | 905 | 60.59% | 5 | 120.14s | 30250/33862 |
| Q21 | 2 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 34 | 413 | 447 | 71.38% | 5 | 80.46s | 18444/21856 |
| Q22 | 3 | 1 | 1 | 1 | 1.0000 | 0.3333 | 0.5000 | 30 | 316 | 346 | 59.54% | 5 | 61.56s | 17444/21064 |
| Q23 | 2 | 0 | 0 | 1 | 0.0000 | 0.0000 | 0.0000 | 26 | 365 | 391 | 78.23% | 5 | 66.64s | 18216/21826 |
| Q24 | 11 | 7 | 6 | 20 | 0.3000 | 0.5455 | 0.3871 | 31 | 513 | 544 | 64.36% | 5 | 108.68s | 23278/26872 |
| Q25 | 1 | 1 | 1 | 4 | 0.2500 | 1.0000 | 0.4000 | 33 | 499 | 532 | 64.70% | 5 | 77.70s | 23526/27166 |
| Q26 | 2 | 2 | 2 | 6 | 0.3333 | 1.0000 | 0.5000 | 16 | 318 | 334 | 78.37% | 5 | 60.88s | 19038/22650 |
| Q27 | 9 | 5 | 4 | 6 | 0.6667 | 0.4444 | 0.5333 | 25 | 222 | 247 | 60.75% | 5 | 71.47s | 16720/20334 |
| Q28 | 4 | 2 | 2 | 6 | 0.3333 | 0.5000 | 0.4000 | 28 | 404 | 432 | 69.16% | 4 | 80.23s | 25254/28870 |
| Q29 | 8 | 3 | 1 | 14 | 0.0714 | 0.1250 | 0.0909 | 28 | 307 | 335 | 68.56% | 5 | 72.10s | 18296/21900 |
| Q30 | 6 | 3 | 2 | 8 | 0.2500 | 0.3333 | 0.2857 | 27 | 533 | 560 | 71.60% | 5 | 79.36s | 20562/23794 |
| Q31 | 15 | 11 | 10 | 13 | 0.7692 | 0.6667 | 0.7143 | 23 | 443 | 466 | 73.86% | 5 | 74.09s | 19842/23438 |
| Q32 | 16 | 4 | 4 | 11 | 0.3636 | 0.2500 | 0.2963 | 20 | 14 | 34 | 5.57% | 5 | 55.42s | 15082/18688 |
| Q33 | 13 | 7 | 7 | 12 | 0.5833 | 0.5385 | 0.5600 | 22 | 206 | 228 | 67.89% | 5 | 70.88s | 21572/25194 |
| Q34 | 7 | 4 | 4 | 35 | 0.1143 | 0.5714 | 0.1905 | 17 | 531 | 548 | 79.54% | 5 | 80.91s | 24562/28182 |
| Q35 | 7 | 5 | 5 | 22 | 0.2273 | 0.7143 | 0.3448 | 29 | 524 | 553 | 77.52% | 5 | 75.46s | 28316/31934 |
| Q36 | 33 | 21 | 19 | 41 | 0.4634 | 0.5758 | 0.5135 | 31 | 513 | 544 | 77.03% | 5 | 72.45s | 22852/26466 |
| Q37 | 10 | 6 | 5 | 25 | 0.2000 | 0.5000 | 0.2857 | 25 | 343 | 368 | 65.83% | 5 | 59.04s | 19766/23376 |
| Q38 | 17 | 4 | 4 | 25 | 0.1600 | 0.2353 | 0.1905 | 33 | 372 | 405 | 55.92% | 5 | 79.80s | 17094/20710 |
| Q39 | 2 | 0 | 0 | 21 | 0.0000 | 0.0000 | 0.0000 | 33 | 607 | 640 | 72.38% | 5 | 92.80s | 27216/30826 |
| Q40 | 5 | 4 | 4 | 53 | 0.0755 | 0.8000 | 0.1379 | 30 | 423 | 453 | 73.03% | 5 | 78.09s | 27638/31246 |
| Q41 | 5 | 2 | 2 | 26 | 0.0769 | 0.4000 | 0.1290 | 34 | 510 | 544 | 73.49% | 5 | 89.01s | 20234/23860 |
| Q42 | 10 | 3 | 3 | 49 | 0.0612 | 0.3000 | 0.1017 | 42 | 599 | 641 | 62.47% | 5 | 107.73s | 24970/28568 |
| Q43 | 28 | 19 | 19 | 47 | 0.4043 | 0.6786 | 0.5067 | 30 | 209 | 239 | 29.91% | 5 | 68.83s | 18136/21740 |
| Q44 | 25 | 17 | 16 | 49 | 0.3265 | 0.6400 | 0.4324 | 30 | 166 | 196 | 29.39% | 5 | 63.01s | 16420/20026 |
| Q45 | 57 | 38 | 38 | 79 | 0.4810 | 0.6667 | 0.5588 | 28 | 494 | 522 | 81.15% | 5 | 85.35s | 24680/28850 |
| Q46 | 65 | 30 | 29 | 84 | 0.3452 | 0.4462 | 0.3893 | 40 | 568 | 608 | 56.94% | 5 | 85.92s | 20448/24060 |
| Q47 | 4 | 2 | 2 | 26 | 0.0769 | 0.5000 | 0.1333 | 21 | 379 | 400 | 58.14% | 5 | 84.54s | 24330/27914 |
| Q48 | 8 | 4 | 4 | 19 | 0.2105 | 0.5000 | 0.2963 | 20 | 205 | 225 | 40.55% | 5 | 65.00s | 18772/22378 |
| Q49 | 8 | 5 | 5 | 12 | 0.4167 | 0.6250 | 0.5000 | 29 | 441 | 470 | 62.78% | 5 | 78.30s | 23996/27628 |

## GT miss stage distribution

分类采用互斥优先级：已进入 Search/Expand 节点但未越过阈值 → `SELECTOR_FALSE_NEGATIVE`；GT exact normalized title 出现在 unresolved instrumentation → `LOCAL_RESOLVER_UNRESOLVED`；GT 出现在已抓取节点的引用列表但未成为节点 → `CITATION_EXPAND_MISS`；其余 → `CRAWLER_SEARCH_MISS`，其更深层原因仍可能不确定。

| Stage | Count | Share |
|---|---:|---:|
| `CRAWLER_SEARCH_MISS` | 283 | 68.03% |
| `CITATION_EXPAND_MISS` | 68 | 16.35% |
| `LOCAL_RESOLVER_UNRESOLVED` | 35 | 8.41% |
| `SELECTOR_FALSE_NEGATIVE` | 30 | 7.21% |
| `OTHER_UNCERTAIN` | 0 | 0.00% |

主要瓶颈是 Crawler Search：283 个，占 68.03%。有 35 个 GT 具有 local-only resolver 直接漏失证据。

## Serper replay and infrastructure

本轮共执行 248 次 live Serper 请求，HTTP 状态分布为 `{"200": 248}`，并保存 248 份完整 replay。每份记录包含 RealScholarQuery ID、Crawler query、query 序号、请求时间、HTTP 状态、延迟、原始响应、结构化响应和响应 SHA-256；未保存 API key 或请求认证头。

平均/P50/P95/最大单题延迟为 79.95/78.20/108.25/126.80 秒，总墙钟时间 76.51 分钟。最高显存为 38642 MiB，出现在 RealScholarQuery_3；50 题 OOM=0、worker exception=0、failed=0。

## Per-query records and missed GT

### RealScholarQuery_0

```text
QUERY_ID=RealScholarQuery_0
QUERY=Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.
SEED=42
STATUS=PASS
GT_TOTAL=9
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=3
FINAL_RETURNED=10
TP=3
FP=7
FN=6
FINAL_PRECISION=0.3000
FINAL_RECALL=0.3333
FINAL_F1=0.3158
SEARCH_QUERIES=["Effects of dataset size on language model pre-training effectiveness", "Survey papers on large language model pre-training using smaller dataset", "Benefits of limited dataset in pre-training of language models", "Advantages of using smaller datasets in large language model pre-training", "Papers on the effectiveness of smaller datasets in language model pre-training"]
SEARCH_NODES=28
EXPAND_NODES=423
SELECTOR_PROMPTS=451
LOCAL_TITLE_LOOKUPS=1177
LOCAL_TITLE_HITS=840
LOCAL_TITLE_MISSES=336
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=71.37%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=90.826s
PEAK_GPU_MEMORY={"1": 23762, "2": 27374}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| When Less is More: Investigating Data Pruning for Pretraining LLMs at   Scale | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. Data Management For Large Language Models: A Survey / 2 Pretraining of LLM 2.2 Data Quality |
| Deduplicating Training Data Makes Language Models Better | `SELECTOR_FALSE_NEGATIVE` | max score=0.061744; source=Expand SearchFrom:local_paper_db |
| Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Data-Centric AI in the Age of Large Language Models / 4 Knowledge Transfer 4.1 Research Directions: Cost-effective Data Synthesis |
| Automatic Document Selection for Efficient Encoder Pretraining | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Farewell to aimless large-scale pretraining: Influential subset selection for language model | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey of Large Language Models / 4 Pre-training 4.1 Data Collection and Preparation |
| Babyllama-2: Ensemble-distilled models consistently outperform teachers with limited data. | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_1

```text
QUERY_ID=RealScholarQuery_1
QUERY=Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training.

SEED=42
STATUS=PASS
GT_TOTAL=29
CRAWLER_GT_FOUND=18
FINAL_GT_FOUND=17
FINAL_RETURNED=30
TP=17
FP=13
FN=12
FINAL_PRECISION=0.5667
FINAL_RECALL=0.5862
FINAL_F1=0.5763
SEARCH_QUERIES=["Role of pre-training in the development of in-context learning in language models", "Insights into the process of pre-training for in-context learning in language models", "Pre-training methods for in-context learning in language models", "In-context learning in pre-training of large language models", "Survey papers on in-context learning in pre-trained language models"]
SEARCH_NODES=27
EXPAND_NODES=454
SELECTOR_PROMPTS=481
LOCAL_TITLE_LOOKUPS=1504
LOCAL_TITLE_HITS=1104
LOCAL_TITLE_MISSES=396
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=73.40%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=99.611s
PEAK_GPU_MEMORY={"1": 23684, "2": 27318}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Transformers Learn Higher-Order Optimization Methods for In-Context   Learning: A Study with Linear Models | `SELECTOR_FALSE_NEGATIVE` | max score=0.313988; source=Expand SearchFrom:local_paper_db |
| In-context Learning and Induction Heads | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=15; In-context learning and induction heads (14); In-context learning and induction heads. (1) |
| Do pretrained Transformers Learn In-Context by Gradient Descent? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| The mechanistic basis of data dependence and abrupt learning in an   in-context classification task | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Data Generation Perspective to the Mechanism of In-Context Learning / 6 Future Directions |
| Explaining Emergent In-Context Learning as Kernel Regression | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| How Do Nonlinear Transformers Learn and Generalize in In-Context   Learning? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Asymptotic theory of in-context learning by linear attention | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| A Mechanism for Sample-Efficient In-Context Learning for Sparse Retrieval Tasks | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Trained Transformers Learn Linear Models In-Context / 2 Additional Related Work |
| Transformers Learn Nonlinear Features In Context: Nonconvex Mean-field Dynamics on the Attention Landscape | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Language Models ""Grok"" to Copy | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Transformers generalize differently from information stored in context vs in weights. | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=3; Transformers generalize differently from information stored in context vs in weights. (2); Transformers generalize differently from information stored in context vs in weights (1) |
| Investigating the Pre-Training Dynamics of In-Context Learning: Task Recognition vs. Task Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_2

```text
QUERY_ID=RealScholarQuery_2
QUERY=List all papers that use autoregressive transformer to generate videos.
SEED=42
STATUS=PASS
GT_TOTAL=21
CRAWLER_GT_FOUND=15
FINAL_GT_FOUND=15
FINAL_RETURNED=23
TP=15
FP=8
FN=6
FINAL_PRECISION=0.6522
FINAL_RECALL=0.7143
FINAL_F1=0.6818
SEARCH_QUERIES=["Use of autoregressive transformer in video generation papers", "Studies on autoregressive transformer in video creation", "Papers on video generation using autoregressive transformer", "Research on using autoregressive transformers for video editing and composition", "Autoregressive transformer models in video generation research papers"]
SEARCH_NODES=24
EXPAND_NODES=424
SELECTOR_PROMPTS=448
LOCAL_TITLE_LOOKUPS=1376
LOCAL_TITLE_HITS=1154
LOCAL_TITLE_MISSES=217
LOCAL_TITLE_AMBIGUOUS=5
LOCAL_TITLE_HIT_RATE=83.87%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=63.523s
PEAK_GPU_MEMORY={"1": 22532, "2": 26128}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| HARP: Autoregressive Latent Video Prediction with High-Fidelity Image Generator | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Phenaki: Variable length video generation from open domain textual descriptions / 3 Experiments 3.4 Video Encoding |
| iVideoGPT: Interactive VideoGPTs are Scalable World Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Look Outside the Room: Synthesizing A Consistent Long-Term 3D Scene Video from A Single Image | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. A Survey on Long Video Generation: Challenges, Methods, and Prospects / 3 Long Video Generation Paradigms 3.4 Spatial Auto-regressive Models with Temporal AutoRegressive |
| Snap video: Scaled spatiotemporal transformers for text-to-video synthesis | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Pandora: Towards general world model with natural language actions and video states. | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Emu3: Next token prediction is all you need | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_3

```text
QUERY_ID=RealScholarQuery_3
QUERY=I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs. These models should be pre-trained on large-scale datasets, including visual, audio, and audio-visual data. Please exclude survey papers.
SEED=42
STATUS=PASS
GT_TOTAL=42
CRAWLER_GT_FOUND=22
FINAL_GT_FOUND=22
FINAL_RETURNED=60
TP=22
FP=38
FN=20
FINAL_PRECISION=0.3667
FINAL_RECALL=0.5238
FINAL_F1=0.4314
SEARCH_QUERIES=["Research on Large Multimodal Models (LMMs) for integrating visual and textual data", "Foundation models supporting visual and audio inputs", "Multimodal foundation models for visual and audio inputs", "Research on audio-visual pretraining in multimodal foundation models", "Pre-training of multimodal foundation models on large-scale datasets"]
SEARCH_NODES=34
EXPAND_NODES=916
SELECTOR_PROMPTS=950
LOCAL_TITLE_LOOKUPS=2553
LOCAL_TITLE_HITS=1979
LOCAL_TITLE_MISSES=556
LOCAL_TITLE_AMBIGUOUS=18
LOCAL_TITLE_HIT_RATE=77.52%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=126.798s
PEAK_GPU_MEMORY={"1": 32822, "2": 38642}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Fine-grained Audio-Visual Joint Representations for Multimodal Large   Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Foundation Models for Video Understanding: A Survey / 5. Universal Foundational Models (UFMs) 5.1. Generative Pretraining Objective |
| CoAVT: A Cognition-Inspired Unified Audio-Visual-Text Pre-Training Model   for Multimodal Processing | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| video-SALMONN: Speech-Enhanced Audio-Visual Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Gemini: A Family of Highly Capable Multimodal Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=7; Gemini: a family of highly capable multimodal models (7) |
| VITA: Towards Open-Source Interactive Omni Multimodal LLM | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Video Understanding as Machine Translation | `CITATION_EXPAND_MISS` | exact citation occurrences=7; e.g. UniVL: A Unified Video and Language Pre-Training Model for Multimodal Understanding and Generation / 1 Introduction |
| i-Code V2: An Autoregressive Generation Framework over Vision, Language, and Speech Data | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Connecting multi-modal contrastive representations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MIO: A Foundation Model on Multimodal Tokens | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Unified-io 2: Scaling autoregressive multimodal models with vision, language, audio, and action | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. AnyGPT: Unified Multimodal LLM with Discrete Sequence Modeling / 1 Introduction |
| Imagebind: One embedding space to bind them all | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=23; Imagebind: One embedding space to bind them all (23) |
| Ofasys: A multi-modal multi-task learning system for building generalist models. | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. TouchStone: Evaluating Vision-Language Models by Language Models / Related Work 2.2 Vision-Language Models |
| Audioclip: Extending clip to image, text and audio | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=4; Audioclip: Extending clip to image, text and audio (4) |
| Omnibind: Large-scale omni multimodal representation via binding spaces | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| One-peace: Exploring one general representation model toward unlimited modalities | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond / Related Work |
| PG-Video-LLaVA: Pixel Grounding Large Video-Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. A Comprehensive Review of Multimodal Large Language Models: Performance and Challenges Across Different Tasks / III Task Classification of Multimodal Large Language Models III-B Video Tasks |
| Freebind: Free lunch in unified multimodal space via knowledge fusion | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Efficient self-supervised learning with contextualized target representations for vision, speech and language | `CITATION_EXPAND_MISS` | exact citation occurrences=6; e.g. Fast-HuBERT: An Efficient Training Framework for Self-Supervised Speech Representation Learning / 2 Background 2.2 Related Work |
| Extending multi-modal contrastive representations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| From Vision to Audio and Beyond: A Unified Model for Audio-Visual Representation and Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_4

```text
QUERY_ID=RealScholarQuery_4
QUERY=Provide me with all papers that discuss reinforcement learning training for Large Language Model agent tasks.
SEED=42
STATUS=PASS
GT_TOTAL=44
CRAWLER_GT_FOUND=19
FINAL_GT_FOUND=17
FINAL_RETURNED=56
TP=17
FP=39
FN=27
FINAL_PRECISION=0.3036
FINAL_RECALL=0.3864
FINAL_F1=0.3400
SEARCH_QUERIES=["Experiences in training Large Language Model agents using reinforcement learning", "Case studies of Large Language Model agents trained using reinforcement learning", "Reinforcement learning approaches for optimizing Large Language Model agents", "Research on task-agnostic rewards in reinforcement learning training for large language models", "Survey papers on reinforcement learning training for large language models"]
SEARCH_NODES=33
EXPAND_NODES=684
SELECTOR_PROMPTS=717
LOCAL_TITLE_LOOKUPS=1757
LOCAL_TITLE_HITS=1143
LOCAL_TITLE_MISSES=613
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=65.05%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=98.451s
PEAK_GPU_MEMORY={"1": 30720, "2": 34332}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| True Knowledge Comes from Practice: Aligning LLMs with Embodied   Environments via Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Teaching Large Language Models to Reason with Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Language Agents with Reinforcement Learning for Strategic Play in the   Werewolf Game | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. How Far Are We on the Decision-Making of LLMs? Evaluating LLMs’ Gaming Ability in Multi-Agent Environments / 6 Related Work 6.1 Specific Games |
| STARLING: Self-supervised Training of Text-based Reinforcement Learning Agent with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Towards Generalizable Agents in Text-Based Educational Environments: A Study of Integrating RL with LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| WebGPT: Browser-assisted question-answering with human feedback | `SELECTOR_FALSE_NEGATIVE` | max score=0.011713; source=Expand SearchFrom:local_paper_db |
| Mutual Enhancement of Large Language and Reinforcement Learning Models through Bi-Directional Feedback Mechanisms: A Case Study | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LLM Augmented Hierarchical Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Entropy-Regularized Token-Level Policy Optimization for Language Agent Reinforcement | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Building Open-Ended Embodied Agent via Language-Policy Bidirectional Adaptation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RL-GPT: Integrating Reinforcement Learning and Code-as-policy | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Training Language Models to Self-Correct via Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Math-shepherd: Verify and reinforce llms step-by-step without human annotations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Generative job recommendations with large language model | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey on Large Language Models for Recommendation / 4 Generative LLMs for Recommendation 4.2 Tuning Paradigm |
| Reinforcement Learning Problem Solving with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Enhance reasoning for large language models in the game werewolf | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Adarefiner: Refining decisions of language models with adaptive feedback | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Large Language Models as Generalizable Policies for Embodied Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Eureka: Human-Level Reward Design via Coding Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Eureka: Human-level reward design via coding large language models (1) |
| Openagi: When llm meets domain experts | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. A Survey on Large Language Model based Autonomous Agents / 2 LLM-based Autonomous Agent Construction 2.1 Agent Architecture Design |
| Unleashing the Power of Pre-trained Language Models for Offline Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Alpacafarm: A simulation framework for methods that learn from human feedback | `SELECTOR_FALSE_NEGATIVE` | max score=0.448905; source=Expand SearchFrom:local_paper_db |
| Large Language Model-based Human-Agent Collaboration for Complex Task Solving | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Language models are few-shot butlers | `CITATION_EXPAND_MISS` | exact citation occurrences=5; e.g. Adapting LLM Agents Through Communication / 4 Experiments 4.2 Settings |
| How Can LLM Guide RL? A Value-Based Approach | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| AGILE: A Novel Framework of LLM Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_5

```text
QUERY_ID=RealScholarQuery_5
QUERY=Papers that apply RLHF to address the hallucination problem in image and video description.
SEED=42
STATUS=PASS
GT_TOTAL=7
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=4
FINAL_RETURNED=10
TP=4
FP=6
FN=3
FINAL_PRECISION=0.4000
FINAL_RECALL=0.5714
FINAL_F1=0.4706
SEARCH_QUERIES=["Role of RLHF in reducing hallucination in multimodal generation", "Impact of RLHF on hallucination issue in image description", "Use of RLHF in addressing hallucination in video content", "Application of RLHF in video description", "Survey papers on RLHF for image description"]
SEARCH_NODES=35
EXPAND_NODES=480
SELECTOR_PROMPTS=515
LOCAL_TITLE_LOOKUPS=1328
LOCAL_TITLE_HITS=1035
LOCAL_TITLE_MISSES=293
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=77.94%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=76.423s
PEAK_GPU_MEMORY={"1": 19130, "2": 22734}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| ViGoR: Improving Visual Grounding of Large Vision Language Models with Fine-Grained Reward Modeling | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Hallucination of Multimodal Large Language Models: A Survey / 5. Hallucination Mitigation 5.3. Training |
| Dress: Instructing large vision-language models to align and interact with humans via natural language feedback | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Enhancing Image Caption Generation Using Reinforcement Learning with Human Feedback | `SELECTOR_FALSE_NEGATIVE` | max score=0.481732; source=Search SearchFrom:arxiv |

### RealScholarQuery_6

```text
QUERY_ID=RealScholarQuery_6
QUERY=Papers that propose methods based on large language models and evaluate their performance through experiments on the HotPotQA dataset.
SEED=42
STATUS=PASS
GT_TOTAL=24
CRAWLER_GT_FOUND=6
FINAL_GT_FOUND=6
FINAL_RETURNED=30
TP=6
FP=24
FN=18
FINAL_PRECISION=0.2000
FINAL_RECALL=0.2500
FINAL_F1=0.2222
SEARCH_QUERIES=["Proposed methods for HotPotQA using large language models", "Experiments on the HotPotQA dataset for language models", "Survey papers on methods using large language models for HotPotQA", "Research on evaluation methods for Large Language Models on HotPotQA dataset", "Large language model based methods for HotPotQA dataset"]
SEARCH_NODES=19
EXPAND_NODES=334
SELECTOR_PROMPTS=353
LOCAL_TITLE_LOOKUPS=889
LOCAL_TITLE_HITS=716
LOCAL_TITLE_MISSES=173
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=80.54%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=72.325s
PEAK_GPU_MEMORY={"1": 21966, "2": 25592}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| AutoPlan: Automatic Planning of Interactive Decision-Making Tasks With   Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| GenDec: A robust generative Question-decomposition method for Multi-hop   reasoning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open   Domain Multi-Hop Question Answering | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| ReAct: Synergizing Reasoning and Acting in Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=4; ReAct: Synergizing reasoning and acting in language models (3); React: Synergizing reasoning and acting in language models (1) |
| LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| FireAct: Toward Language Agent Fine-tuning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| When Hindsight is Not 20/20: Testing Limits on Reflective Thinking in Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| GenSco: Can Question Decomposition based Passage Alignment improve Question Answering? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| IM-RAG: Multi-Round Retrieval-Augmented Generation Through Learning Inner Monologues | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RAFT: Adapting Language Model to Domain Specific RAG | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. An Empirical Study of Retrieval Augmented Generation with Chain-of-Thought / 1 Introduction |
| Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Learning to Decompose: Hypothetical Question Decomposition Based on   Comparable Texts | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Language Agent Tree Search Unifies Reasoning Acting and Planning in   Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Large Language Models: A Survey / IV How LLMs Are Used and Augmented IV-E LLM Agents |
| Prompting Explicit and Implicit Knowledge for Multi-hop Question   Answering Based on Human Reading Process | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Chain-of-Skills: A Configurable Model for Open-domain Question Answering | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Can Small Language Models Help Large Language Models Reason Better?: LM-Guided Chain-of-Thought | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Chatcot: Tool-augmented chain-of-thought reasoning on chat-based large language models | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. A Survey of Large Language Models / 6 Utilization 6.1 Prompting |

### RealScholarQuery_7

```text
QUERY_ID=RealScholarQuery_7
QUERY=Show me research on the long video description. Here, long videos are defined as those with a duration of at least several minutes.
SEED=42
STATUS=PASS
GT_TOTAL=35
CRAWLER_GT_FOUND=11
FINAL_GT_FOUND=11
FINAL_RETURNED=47
TP=11
FP=36
FN=24
FINAL_PRECISION=0.2340
FINAL_RECALL=0.3143
FINAL_F1=0.2683
SEARCH_QUERIES=["Research on long-duration video description", "Studies on multi-modal language models for long video understanding", "Long video description research papers", "Research on automatic video summarization for long videos", "Survey papers on long video description techniques"]
SEARCH_NODES=32
EXPAND_NODES=555
SELECTOR_PROMPTS=587
LOCAL_TITLE_LOOKUPS=1888
LOCAL_TITLE_HITS=1223
LOCAL_TITLE_MISSES=658
LOCAL_TITLE_AMBIGUOUS=7
LOCAL_TITLE_HIT_RATE=64.78%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=84.980s
PEAK_GPU_MEMORY={"1": 27910, "2": 31542}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Video ReCap: Recursive Captioning of Hour-Long Videos | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MMBench-Video: A Long-Form Multi-Shot Benchmark for Holistic Video Understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Learning To Recognize Procedural Activities with Distant Supervision | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Selective Structured State-Spaces for Long-Form Video Understanding / 4 Experiments 4.4 Comparison with the State-Of-The-Arts |
| HowToCaption: Prompting LLMs to Transform Video Annotations at Scale | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LongVideoBench: A Benchmark for Long-context Interleaved Video-Language Understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Enhancing Long Video Understanding via Hierarchical Event-Based Memory | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DrVideo: Document Retrieval Based Long Video Understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LVBench: An Extreme Long Video Understanding Benchmark | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| World Model on Million-Length Video And Language With Blockwise RingAttention | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Koala: Key frame-conditioned long video-LLM | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MLLM as Video Narrator: Mitigating Modality Imbalance in Video Moment Retrieval | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MLVU: A Comprehensive Benchmark for Multi-Task Long Video Understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Kangaroo: A Powerful Video-Language Model Supporting Long-context Video Input | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LifelongMemory: Leveraging LLMs for Answering Queries in Long-form   Egocentric Videos | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| ShareGPT4Video: Improving Video Understanding and Generation with Better Captions | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LLMs Meet Long Video: Advancing Long Video Comprehension with An Interactive Visual Adapter in LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| VideoAgent: Long-form Video Understanding with Large Language Model as Agent | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Semi-parametric video-grounded text generation | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Self-Chained Image-Language Model for Video Localization and Question Answering / 2 Related Work |
| A simple recipe for contrastively pre-training video-first encoders beyond 16 frames. | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Memory Consolidation Enables Long-Context Video Understanding / 2 Related Work |
| Learning Video Representations from Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=3; Learning video representations from large language models (3) |
| Synopses of movie narratives: a video-language dataset for story understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Mm-narrator: Narrating long-form videos with multimodal in-context learning. | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Video Understanding with Large Language Models: A Survey / 3 Vid-LLMs: Models 3.1 LLM-based Video Agents |
| Videoagent: A memory-augmented multimodal agent for video understanding. | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Streaming dense video captioning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_8

```text
QUERY_ID=RealScholarQuery_8
QUERY=Do you know some papers about using reward shaping methods to train large language model agent.
SEED=42
STATUS=PASS
GT_TOTAL=16
CRAWLER_GT_FOUND=8
FINAL_GT_FOUND=8
FINAL_RETURNED=34
TP=8
FP=26
FN=8
FINAL_PRECISION=0.2353
FINAL_RECALL=0.5000
FINAL_F1=0.3200
SEARCH_QUERIES=["Exploring the use of self-rewarding mechanisms in training large language models", "Research on using small extrinsic rewards for aligning large language models with user intent", "Effectiveness of reward shaping methods in training large language models", "Application of reward shaping in language model agent training", "Reward shaping techniques in large language model training"]
SEARCH_NODES=22
EXPAND_NODES=331
SELECTOR_PROMPTS=353
LOCAL_TITLE_LOOKUPS=971
LOCAL_TITLE_HITS=631
LOCAL_TITLE_MISSES=339
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=64.98%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=84.099s
PEAK_GPU_MEMORY={"1": 18262, "2": 21866}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Beyond Sparse Rewards: Enhancing Reinforcement Learning with Language   Model Critique in Text Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Retroformer: Retrospective Large Language Agents with Policy Gradient   Optimization | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. UltraFeedback: Boosting Language Models with High-quality Feedback / 2 Related Work RLHF for LLMs. |
| Quark: Controllable Text Generation with Reinforced Unlearning | `CITATION_EXPAND_MISS` | exact citation occurrences=9; e.g. The Cringe Loss: Learning what language not to model / 2 Related Work Iterative training of language models |
| Language Reward Modulation for Pretraining Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Auto MC-Reward: Automated Dense Reward Design with Large Language Models for Minecraft | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Token-level Direct Preference Optimization | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Extracting Heuristics from Large Language Models for Reward Shaping in Reinforcement Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Math-shepherd: Verify and reinforce llms step-by-step without human annotations | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Math-shepherd: Verify and reinforce llms step-by-step without human annotations (1) |

### RealScholarQuery_9

```text
QUERY_ID=RealScholarQuery_9
QUERY=Give me papers about how to rank search results by the use of LLM.
SEED=42
STATUS=PASS
GT_TOTAL=39
CRAWLER_GT_FOUND=16
FINAL_GT_FOUND=16
FINAL_RETURNED=39
TP=16
FP=23
FN=23
FINAL_PRECISION=0.4103
FINAL_RECALL=0.4103
FINAL_F1=0.4103
SEARCH_QUERIES=["Ranking mechanisms in Large Language Models", "Application of LLM in search result ranking", "Survey papers on ranking search results with Language Model", "Influence of LLM on search result rankings", "Use of LLM in ranking search results"]
SEARCH_NODES=24
EXPAND_NODES=380
SELECTOR_PROMPTS=404
LOCAL_TITLE_LOOKUPS=1291
LOCAL_TITLE_HITS=876
LOCAL_TITLE_MISSES=395
LOCAL_TITLE_AMBIGUOUS=20
LOCAL_TITLE_HIT_RATE=67.85%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=80.987s
PEAK_GPU_MEMORY={"1": 18326, "2": 21930}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Beyond Yes and No: Improving Zero-Shot LLM Rankers via Scoring   Fine-Grained Relevance Labels | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Large Language Models for Information Retrieval: A Survey / 5 Reranker 5.2 Utilizing LLMs as Unsupervised Rerankers |
| PaRaDe: Passage Ranking using Demonstrations with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| TourRank: Utilizing Large Language Models for Documents Ranking with a Tournament-Inspired Strategy | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RankRAG: Unifying Context Ranking with Retrieval-Augmented Generation in LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LLM-RankFusion: Mitigating Intrinsic Inconsistency in LLM-based Ranking | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Improving Zero-shot LLM Re-Ranker with Risk Minimization | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Consolidating Ranking and Relevance Predictions of Large Language Models through Post-Processing | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Re-Ranking Step by Step: Investigating Pre-Filtering for Re-Ranking with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Large Language Models for Relevance Judgment in Product Search | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PromptReps: Prompting Large Language Models to Generate Dense and Sparse Representations for Zero-Shot Document Retrieval | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Passage-specific Prompt Tuning for Passage Reranking in Question Answering with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MuGI: Enhancing Information Retrieval through Multi-Text Generation Integration with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Discrete Prompt Optimization via Constrained Generation for Zero-shot   Re-ranker | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Large Language Models for Information Retrieval: A Survey / 5 Reranker 5.2 Utilizing LLMs as Unsupervised Rerankers |
| REAR: A Relevance-Aware Retrieval-Augmented Framework for Open-Domain   Question Answering | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Agent4Ranking: Semantic Robust Ranking via Personalized Query Rewriting   Using Multi-agent LLM | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| FIRST: Faster Improved Listwise Reranking with Single Token Decoding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Leveraging LLMs for Unsupervised Dense Retriever Ranking | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Unsupervised Contrast-Consistent Ranking with Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Found in the Middle: Permutation Self-Consistency Improves Listwise Ranking in Large Language Models / 1 Introduction |
| Enhancing Legal Document Retrieval: A Multi-Phase Approach with Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Zero-shot Audio Topic Reranking using Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Cognitive Personalized Search Integrating Large Language Models with an Efficient Memory Mechanism | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Towards More Relevant Product Search Ranking Via Large Language Models: An Empirical Study | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Open-source large language models are strong zero-shot query likelihood models for document ranking | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Large Language Models for Information Retrieval: A Survey / 5 Reranker 5.2 Utilizing LLMs as Unsupervised Rerankers |

### RealScholarQuery_10

```text
QUERY_ID=RealScholarQuery_10
QUERY=Is there any work that analyzes the scaling law of the multi-module models, such as video-text, image-text models?
SEED=42
STATUS=PASS
GT_TOTAL=15
CRAWLER_GT_FOUND=8
FINAL_GT_FOUND=6
FINAL_RETURNED=8
TP=6
FP=2
FN=9
FINAL_PRECISION=0.7500
FINAL_RECALL=0.4000
FINAL_F1=0.5217
SEARCH_QUERIES=["Empirical studies on the scaling laws of text-to-video generation models", "Scaling behavior of multi-modal transformer models in video-text tasks", "Research on scaling law in image-text models", "Analysis of scaling law in video-text models", "Survey papers on scaling law of multi-module models"]
SEARCH_NODES=33
EXPAND_NODES=585
SELECTOR_PROMPTS=618
LOCAL_TITLE_LOOKUPS=1542
LOCAL_TITLE_HITS=1205
LOCAL_TITLE_MISSES=337
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=78.15%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=96.309s
PEAK_GPU_MEMORY={"1": 21466, "2": 25076}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Are Bigger Encoders Always Better in Vision Large Models? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PaLI: A Jointly-Scaled Multilingual Language-Image Model | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Pali: A jointly-scaled multilingual language-image model (1) |
| Scaling Law Hypothesis for Multimodal Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| An Empirical Study of Scaling Instruct-Tuned Large Multimodal Models | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Improved Baselines with Visual Instruction Tuning / 1 Introduction |
| SPHINX-X: Scaling Data and Parameters for a Family of Multi-modal Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Multimodal contrastive learning with limoe: the language-image mixture of experts | `SELECTOR_FALSE_NEGATIVE` | max score=0.453402; source=Expand SearchFrom:local_paper_db |
| Simple open-vocabulary object detection with vision transformers | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. RoboAgent: Generalization and Efficiency in Robot Manipulation via Semantic Augmentations and Action Chunking / 2 Related Work |
| Scaling rectified flow transformers for high-resolution image synthesis | `SELECTOR_FALSE_NEGATIVE` | max score=0.285241; source=Expand SearchFrom:local_paper_db |

### RealScholarQuery_11

```text
QUERY_ID=RealScholarQuery_11
QUERY=Give me all visual-LLM models that are MoE architecture
SEED=42
STATUS=PASS
GT_TOTAL=20
CRAWLER_GT_FOUND=11
FINAL_GT_FOUND=8
FINAL_RETURNED=11
TP=8
FP=3
FN=12
FINAL_PRECISION=0.7273
FINAL_RECALL=0.4000
FINAL_F1=0.5161
SEARCH_QUERIES=["Objectives of visual-LLM models using MoE architecture", "Research on MoE architecture in visual-LLMs", "Multi-Modal Large Language Models with MoE architecture", "Survey papers on visual-LLM models with MoE architecture", "MoE architecture models in visual-LLM"]
SEARCH_NODES=15
EXPAND_NODES=374
SELECTOR_PROMPTS=389
LOCAL_TITLE_LOOKUPS=951
LOCAL_TITLE_HITS=781
LOCAL_TITLE_MISSES=169
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=82.12%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=54.119s
PEAK_GPU_MEMORY={"1": 19204, "2": 22814}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Omni-SMoLA: Boosting Generalist Multimodal Models with Soft Mixture of   Low-rank Experts | `SELECTOR_FALSE_NEGATIVE` | max score=0.396865; source=Expand SearchFrom:local_paper_db |
| CuMo: Scaling Multimodal LLM with Co-Upcycled Mixture-of-Experts | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MoME: Mixture of Multimodal Experts for Generalist Multimodal Large Language Models | `SELECTOR_FALSE_NEGATIVE` | max score=0.494987; source=Search SearchFrom:local_paper_db |
| Solving Token Gradient Conflict in Mixture-of-Experts for Large Vision-Language Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Boosting Continual Learning of Vision-Language Models via   Mixture-of-Experts Adapters | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MoMa: Efficient Early-Fusion Pre-training with Mixture of Modality-Aware Experts | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LLaVA-MoLE: Sparse Mixture of LoRA Experts for Mitigating Data Conflicts   in Instruction Finetuning MLLMs | `SELECTOR_FALSE_NEGATIVE` | max score=0.333624; source=Expand SearchFrom:local_paper_db |
| Mini-Gemini: Mining the Potential of Multi-modality Vision Language   Models | `CITATION_EXPAND_MISS` | exact citation occurrences=7; e.g. Building and better understanding vision-language models: insights and future directions / 2 Analyzing architectural choices in VLMs 2.1 Connecting unimodal pre-trained models |
| MoExtend: Tuning New Experts for Modality and Task Extension | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Scaling Vision-Language Models with Sparse Mixture of Experts | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. A Survey on Mixture of Experts / 6. Applications of Mixture of Experts Models |
| MiniDrive: More Efficient Vision-Language Models with Multi-Level 2D Features as Text Tokens for Autonomous Driving | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LLMBind: A Unified Modality-Task Integration Framework | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_12

```text
QUERY_ID=RealScholarQuery_12
QUERY=What papers discuss the use of transformer architecture in 3d video generation
SEED=42
STATUS=PASS
GT_TOTAL=17
CRAWLER_GT_FOUND=9
FINAL_GT_FOUND=9
FINAL_RETURNED=21
TP=9
FP=12
FN=8
FINAL_PRECISION=0.4286
FINAL_RECALL=0.5294
FINAL_F1=0.4737
SEARCH_QUERIES=["Exploration of transformer architecture for 3D video synthesis", "Transformer architecture application in 3D video creation", "Papers on transformer-based methods in 3D video generation", "Research on 3D video generation using transformer architecture", "Use of transformer model in 3D video production"]
SEARCH_NODES=33
EXPAND_NODES=703
SELECTOR_PROMPTS=736
LOCAL_TITLE_LOOKUPS=1920
LOCAL_TITLE_HITS=1525
LOCAL_TITLE_MISSES=387
LOCAL_TITLE_AMBIGUOUS=8
LOCAL_TITLE_HIT_RATE=79.43%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=93.404s
PEAK_GPU_MEMORY={"1": 29726, "2": 33336}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| TEACH: Temporal Action Composition for 3D Humans | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Bailando: 3D Dance Generation by Actor-Critic GPT with Choreographic   Memory | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. MotionDiffuse: Text-Driven Human Motion Generation with Diffusion Model / 2 Related Work 2.2 Conditional Motion Generation |
| DanceFormer: Music Conditioned 3D Dance Generation with Parametric Motion Transformer | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Breathing Life into Faces: Speech-driven 3D Facial Animation with Natural Head Pose and Detailed Shape | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Director3D: Real-world Camera Trajectory and 3D Scene Generation from Text | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Human4DiT: 360-degree Human Video Generation with 4D Diffusion Transformer | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| AI Choreographer: Music Conditioned 3D Dance Generation with AIST++ | `CITATION_EXPAND_MISS` | exact citation occurrences=9; e.g. GIMO: Gaze-Informed Human Motion Prediction in Context / 4 Gaze-Informed Human Motion Prediction 4.2 Multi-modal Feature Extraction |
| N\"UWA: Visual Synthesis Pre-training for Neural visUal World creAtion | `CITATION_EXPAND_MISS` | exact citation occurrences=9; e.g. NUWA-XL: Diffusion over Diffusion for eXtremely Long Video Generation / 1 Introduction |

### RealScholarQuery_13

```text
QUERY_ID=RealScholarQuery_13
QUERY=Provide papers demonstrating that the self-correction of LLMs does not enhance their performance.
SEED=42
STATUS=PASS
GT_TOTAL=12
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=3
FINAL_RETURNED=4
TP=3
FP=1
FN=9
FINAL_PRECISION=0.7500
FINAL_RECALL=0.2500
FINAL_F1=0.3750
SEARCH_QUERIES=["Research on self-correction mechanisms in LLMs and their impact on performance", "Academic papers on the ineffectiveness of self-correction in LLMs", "Survey papers on self-correction not enhancing LLM performance", "Impact of self-correction on language model performance", "Studies on the limitations of self-correction in language models"]
SEARCH_NODES=22
EXPAND_NODES=358
SELECTOR_PROMPTS=380
LOCAL_TITLE_LOOKUPS=893
LOCAL_TITLE_HITS=658
LOCAL_TITLE_MISSES=234
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=73.68%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=76.800s
PEAK_GPU_MEMORY={"1": 19854, "2": 23458}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Can Large Language Models Really Improve by Self-critiquing Their Own   Plans? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| A Closer Look at the Self-Verification Abilities of Large Language   Models in Logical Reasoning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| SELF-[IN]CORRECT: LLMs Struggle with Discriminating Self-Generated Responses | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| The Counterfeit Conundrum: Can Code Language Models Grasp the Nuances of   Their Incorrect Generations? | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Small Language Models Need Strong Verifiers to Self-Correct Reasoning / 6 Related Work Verifying Reasoning. |
| When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs | `SELECTOR_FALSE_NEGATIVE` | max score=0.456547; source=Search SearchFrom:local_paper_db |
| On the Intrinsic Self-Correction Capability of LLMs: Uncertainty and Latent Concept | `SELECTOR_FALSE_NEGATIVE` | max score=0.163544; source=Expand SearchFrom:local_paper_db |
| Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| GPT-4 Doesn't Know It's Wrong: An Analysis of Iterative Prompting for Reasoning Problems | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; GPT-4 doesn’t know it’s wrong: An analysis of iterative prompting for reasoning problems (1); GPT-4 Doesn’t Know It’s Wrong: An Analysis of Iterative Prompting for Reasoning Problems. (1) |

### RealScholarQuery_14

```text
QUERY_ID=RealScholarQuery_14
QUERY=Find papers that use LLMs or LLM-based agents to automatically write surveys or summaries for multiple scholarly documents.
SEED=42
STATUS=PASS
GT_TOTAL=9
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=5
FINAL_RETURNED=24
TP=5
FP=19
FN=4
FINAL_PRECISION=0.2083
FINAL_RECALL=0.5556
FINAL_F1=0.3030
SEARCH_QUERIES=["Articles on the application of LLM-based agents in multi-document summary", "Research on using language models for automatic synthesis of literature reviews", "Papers on LLM-based agents for writing summaries of scholarly articles", "Survey papers on the use of LLMs in scholarly document summarization", "Use of LLMs in automatic survey writing"]
SEARCH_NODES=34
EXPAND_NODES=530
SELECTOR_PROMPTS=564
LOCAL_TITLE_LOOKUPS=1246
LOCAL_TITLE_HITS=816
LOCAL_TITLE_MISSES=426
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=65.49%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=103.796s
PEAK_GPU_MEMORY={"1": 25482, "2": 29094}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Instruct Large Language Models to Generate Scientific Literature Survey Step by Step | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| vitaLITy 2: Reviewing Academic Literature Using Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| System for systematic literature review using multiple AI agents:   Concept and an empirical evaluation | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Cutting Through the Clutter: The Potential of LLMs for Efficient Filtration in Systematic Literature Reviews / 1 Related Work |
| Leveraging Long-Context Large Language Models for Multi-Document Understanding and Summarization in Enterprise Applications | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_15

```text
QUERY_ID=RealScholarQuery_15
QUERY=Provide papers claiming that reinforcement learning can negatively impact the performance of supervised fine-tuned LLMs.
SEED=42
STATUS=PASS
GT_TOTAL=5
CRAWLER_GT_FOUND=2
FINAL_GT_FOUND=2
FINAL_RETURNED=3
TP=2
FP=1
FN=3
FINAL_PRECISION=0.6667
FINAL_RECALL=0.4000
FINAL_F1=0.5000
SEARCH_QUERIES=["Impact of reinforcement learning on performance of fine-tuned LLMs", "Downsides of reinforcement learning in supervised fine-tuned LLMs", "Effects of reinforcement learning on fine-tuned language models", "Implications of Reinforcement Learning on Supervised Fine-Tuning in Language Models", "Survey papers on negative impacts of reinforcement learning on supervised fine-tuned LLMs"]
SEARCH_NODES=29
EXPAND_NODES=320
SELECTOR_PROMPTS=349
LOCAL_TITLE_LOOKUPS=850
LOCAL_TITLE_HITS=539
LOCAL_TITLE_MISSES=309
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=63.41%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=62.996s
PEAK_GPU_MEMORY={"1": 19470, "2": 23074}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Fundamental Limitations of Alignment in Large Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback / 4 Incorporating RLHF into a Broader Framework for Safer AI 4.1 Frameworks for Better Understanding RLHF |
| Reward Collapse in Aligning Large Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback / 3 Open Problems and Limitations of RLHF 3.3 Challenges with the Policy |
| Vanishing gradients in reinforcement finetuning of language models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_16

```text
QUERY_ID=RealScholarQuery_16
QUERY=Find papers on trigger-free document-level event extraction methods that do not use human-annotated triggers.
SEED=42
STATUS=PASS
GT_TOTAL=8
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=4
FINAL_RETURNED=19
TP=4
FP=15
FN=4
FINAL_PRECISION=0.2105
FINAL_RECALL=0.5000
FINAL_F1=0.2963
SEARCH_QUERIES=["Studies on event extraction techniques without human-annotated triggers", "Research articles on document-level event extraction without triggers", "Survey papers on trigger-free document-level event extraction", "Papers on event extraction methods without triggers", "Document-level event extraction without triggers research papers"]
SEARCH_NODES=24
EXPAND_NODES=203
SELECTOR_PROMPTS=227
LOCAL_TITLE_LOOKUPS=1054
LOCAL_TITLE_HITS=464
LOCAL_TITLE_MISSES=588
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=44.02%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=51.879s
PEAK_GPU_MEMORY={"1": 17702, "2": 21328}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| COFFEE: A Contrastive Oracle-Free Framework for Event Extraction | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Document-Level Multi-Event Extraction with Event Proxy Nodes and Hausdorff Distance Minimization | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RAAT: Relation-Augmented Attention Transformer for Relation Modeling in Document-Level Event Extraction | `SELECTOR_FALSE_NEGATIVE` | max score=0.100000; source=Search SearchFrom:local_paper_db |
| Document-Level Event Extraction via Human-Like Reading Process | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_17

```text
QUERY_ID=RealScholarQuery_17
QUERY=Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.
SEED=42
STATUS=PASS
GT_TOTAL=9
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=3
FINAL_RETURNED=3
TP=3
FP=0
FN=6
FINAL_PRECISION=1.0000
FINAL_RECALL=0.3333
FINAL_F1=0.5000
SEARCH_QUERIES=["Impact of parameter size on the performance of in-context learning versus supervised fine-tuning in large language models", "Why supervised fine-tuned small language models outperform in-context learning in NER", "In-context learning vs supervised fine-tuning in LLMs for information extraction", "Limitations of in-context learning in language models for information extraction", "Performance comparison of in-context learning and supervised fine-tuning in language models for information extraction"]
SEARCH_NODES=30
EXPAND_NODES=403
SELECTOR_PROMPTS=433
LOCAL_TITLE_LOOKUPS=1091
LOCAL_TITLE_HITS=786
LOCAL_TITLE_MISSES=298
LOCAL_TITLE_AMBIGUOUS=7
LOCAL_TITLE_HIT_RATE=72.04%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=82.996s
PEAK_GPU_MEMORY={"1": 17118, "2": 20760}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Intent Detection and Entity Extraction from BioMedical Literature | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MetaIE: Distilling a Meta Model from LLM for All Kinds of Information Extraction Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Exploring the Feasibility of ChatGPT for Event Extraction | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey of Large Language Models / 8 Applications 8.1 LLM for Research Community |
| Guideline Learning for In-context Information Extraction | `SELECTOR_FALSE_NEGATIVE` | max score=0.108310; source=Expand SearchFrom:local_paper_db |
| Pushing the Limits of ChatGPT on NLP Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Looking Right is Sometimes Right: Investigating the Capabilities of Decoder-only LLMs for Sequence Labeling | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_18

```text
QUERY_ID=RealScholarQuery_18
QUERY=Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.
SEED=42
STATUS=PASS
GT_TOTAL=5
CRAWLER_GT_FOUND=1
FINAL_GT_FOUND=1
FINAL_RETURNED=12
TP=1
FP=11
FN=4
FINAL_PRECISION=0.0833
FINAL_RECALL=0.2000
FINAL_F1=0.1176
SEARCH_QUERIES=["Evaluation of LLM-generated text in zero-shot scenarios", "Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text", "Zero-shot detection of LLM-generated content", "Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection"]
SEARCH_NODES=33
EXPAND_NODES=422
SELECTOR_PROMPTS=455
LOCAL_TITLE_LOOKUPS=1320
LOCAL_TITLE_HITS=883
LOCAL_TITLE_MISSES=432
LOCAL_TITLE_AMBIGUOUS=5
LOCAL_TITLE_HIT_RATE=66.89%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=4
LATENCY=76.987s
PEAK_GPU_MEMORY={"1": 20702, "2": 24314}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Zero-Shot Detection of LLM-Generated Text using Token Cohesiveness | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DetectGPT-SC: Improving Detection of Text Generated by Large Language Models through Self-Consistency with Masked Predictions. | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Fighting fire with fire: The dual role of llms in crafting and detecting elusive disinformation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_19

```text
QUERY_ID=RealScholarQuery_19
QUERY=Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.
SEED=42
STATUS=PASS
GT_TOTAL=37
CRAWLER_GT_FOUND=19
FINAL_GT_FOUND=14
FINAL_RETURNED=17
TP=14
FP=3
FN=23
FINAL_PRECISION=0.8235
FINAL_RECALL=0.3784
FINAL_F1=0.5185
SEARCH_QUERIES=["Techniques to mitigate vocabulary watermarking effects on LLM generation", "Impact of vocabulary watermarking on LLMs generation quality", "Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks", "Research on methods to maintain generation quality in LLMs during vocabulary watermarking", "Survey papers on protecting generation quality of LLMs under vocabulary watermarking"]
SEARCH_NODES=21
EXPAND_NODES=223
SELECTOR_PROMPTS=244
LOCAL_TITLE_LOOKUPS=927
LOCAL_TITLE_HITS=531
LOCAL_TITLE_MISSES=394
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=57.28%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=74.206s
PEAK_GPU_MEMORY={"1": 18026, "2": 21640}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| A Resilient and Accessible Distribution-Preserving Watermark for Large   Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| WaterJudge: Quality-Detection Trade-off when Watermarking Large Language   Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Protecting Intellectual Property of Language Generation APIs with   Lexical Watermark | `SELECTOR_FALSE_NEGATIVE` | max score=0.266355; source=Expand SearchFrom:local_paper_db |
| WatME: Towards Lossless Watermarking Through Lexical Redundancy | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Duwak: Dual Watermarks in Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Duwak: Dual Watermarks in Large Language Models. (1) |
| Adaptive Text Watermark for Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| A Watermark for Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=83; A watermark for large language models (54); A Watermark for Large Language Models (21) |
| PostMark: A Robust Blackbox Watermark for Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Embarrassingly Simple Text Watermarks | `SELECTOR_FALSE_NEGATIVE` | max score=0.458000; source=Expand SearchFrom:local_paper_db |
| A Watermark for Low-entropy and Unbiased Generation in Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Topic-Based Watermarks for LLM-Generated Text | `SELECTOR_FALSE_NEGATIVE` | max score=0.220458; source=Search SearchFrom:local_paper_db |
| Watermarking Language Models with Error Correcting Codes | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PersonaMark: Personalized LLM watermarking for model protection and user attribution | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| ModelShield: Adaptive and Robust Watermark against Model Extraction Attack | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Improving the Generation Quality of Watermarked Large Language Models   via Word Importance Scoring | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Watermarking Conditional Text Generation for AI Detection: Unveiling   Challenges and a Semantic-Aware Watermark Remedy | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Copyright Protection in Generative AI: A Technical Perspective / 3 Copyright in Text Generation 3.4 Model Copyright Protection |
| Towards Codable Watermarking for Injecting Multi-bits Information to LLMs | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Less is More: Sparse Watermarking in LLMs with Enhanced Text Quality / 4 Experiments 4.3 Results of Robustness against Attacks |
| Watermarking Text Generated by Black-Box Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=4; Watermarking Text Generated by Black-Box Language Models (2); Watermarking text generated by black-box language models. (1) |
| A Semantic Invariant Robust Watermark for Large Language Models | `SELECTOR_FALSE_NEGATIVE` | max score=0.242661; source=Search SearchFrom:local_paper_db |
| Provably Robust Multi-bit Watermarking for AI-generated Text via Error   Correction Code | `SELECTOR_FALSE_NEGATIVE` | max score=0.184043; source=Expand SearchFrom:local_paper_db |
| Advancing Beyond Identification: Multi-bit Watermark for Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Cross-Attention Watermarking of Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| SemStamp: A Semantic Watermark with Paraphrastic Robustness for Text Generation | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; SEMSTAMP: A semantic watermark with paraphrastic robustness for text generation. (1) |

### RealScholarQuery_20

```text
QUERY_ID=RealScholarQuery_20
QUERY=Find papers supporting the claim that knowledgeable LLMs have sufficient inductive capacity to analyze the relationships between multiple papers and systematically write a survey on them.
SEED=42
STATUS=PASS
GT_TOTAL=4
CRAWLER_GT_FOUND=1
FINAL_GT_FOUND=1
FINAL_RETURNED=6
TP=1
FP=5
FN=3
FINAL_PRECISION=0.1667
FINAL_RECALL=0.2500
FINAL_F1=0.2000
SEARCH_QUERIES=["LLMs and their ability to analyze multiple research papers", "Papers on systematic review writing by AI models", "Scholarly articles on the analysis of multiple papers by LLMs", "Research on the impact of large language models on academic literature review", "Survey papers on inductive capacity of language models"]
SEARCH_NODES=36
EXPAND_NODES=869
SELECTOR_PROMPTS=905
LOCAL_TITLE_LOOKUPS=2058
LOCAL_TITLE_HITS=1247
LOCAL_TITLE_MISSES=807
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=60.59%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=120.139s
PEAK_GPU_MEMORY={"1": 30250, "2": 33862}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Explaining Relationships Among Research Papers | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Instruct Large Language Models to Generate Scientific Literature Survey Step by Step | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| vitaLITy 2: Reviewing Academic Literature Using Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_21

```text
QUERY_ID=RealScholarQuery_21
QUERY=Search for papers related to large language models that demonstrate how the same prompt with different responses can improve the performance of the SFT model.
SEED=42
STATUS=PASS
GT_TOTAL=2
CRAWLER_GT_FOUND=0
FINAL_GT_FOUND=0
FINAL_RETURNED=0
TP=0
FP=0
FN=2
FINAL_PRECISION=0.0000
FINAL_RECALL=0.0000
FINAL_F1=0.0000
SEARCH_QUERIES=["Prompt engineering methods for improving SFT model performance in large language models", "Studies on how different responses to the same prompt affect SFT model", "Survey papers on the use of varied responses to a single prompt in large language models for SFT", "Research on the impact of diverse responses on the performance of SFT models", "Papers on enhancing SFT model performance with different response prompts"]
SEARCH_NODES=34
EXPAND_NODES=413
SELECTOR_PROMPTS=447
LOCAL_TITLE_LOOKUPS=1258
LOCAL_TITLE_HITS=898
LOCAL_TITLE_MISSES=359
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=71.38%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=80.463s
PEAK_GPU_MEMORY={"1": 18444, "2": 21856}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Curry-DPO: Enhancing Alignment using Curriculum Learning &amp;amp; Ranked Preferences | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Relative Preference Optimization: Enhancing LLM Alignment through Contrasting Responses across Identical and Diverse Prompts | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_22

```text
QUERY_ID=RealScholarQuery_22
QUERY=Papers on solving common sense problems in machine translation.
SEED=42
STATUS=PASS
GT_TOTAL=3
CRAWLER_GT_FOUND=1
FINAL_GT_FOUND=1
FINAL_RETURNED=1
TP=1
FP=0
FN=2
FINAL_PRECISION=1.0000
FINAL_RECALL=0.3333
FINAL_F1=0.5000
SEARCH_QUERIES=["Survey papers on common sense problems in machine translation", "Research articles on machine translation and common sense issues", "Improving common sense in machine translation", "Algorithms used in solving common sense problems in machine translation", "Machine translation challenges in commonsense reasoning"]
SEARCH_NODES=30
EXPAND_NODES=316
SELECTOR_PROMPTS=346
LOCAL_TITLE_LOOKUPS=949
LOCAL_TITLE_HITS=565
LOCAL_TITLE_MISSES=384
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=59.54%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=61.561s
PEAK_GPU_MEMORY={"1": 17444, "2": 21064}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Rethinking Human-like Translation Strategy: Integrating Drift-Diffusion   Model with Large Language Models for Machine Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Few-shot learning with multilingual language models. | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Few-shot Learning with Multilingual Language Models (1) |

### RealScholarQuery_23

```text
QUERY_ID=RealScholarQuery_23
QUERY=Show me papers utilizing reinforcement learning to optimize diffusion models for video generation.
SEED=42
STATUS=PASS
GT_TOTAL=2
CRAWLER_GT_FOUND=0
FINAL_GT_FOUND=0
FINAL_RETURNED=1
TP=0
FP=1
FN=2
FINAL_PRECISION=0.0000
FINAL_RECALL=0.0000
FINAL_F1=0.0000
SEARCH_QUERIES=["Use of reinforcement learning in optimizing diffusion models for video production", "Studies on video synthesis using reinforcement learning in diffusion models", "Survey papers on reinforcement learning optimization in video generation", "Research on reinforcement learning techniques in video diffusion models optimization", "Papers on diffusion models for video generation optimized with reinforcement learning"]
SEARCH_NODES=26
EXPAND_NODES=365
SELECTOR_PROMPTS=391
LOCAL_TITLE_LOOKUPS=983
LOCAL_TITLE_HITS=769
LOCAL_TITLE_MISSES=212
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=78.23%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=66.643s
PEAK_GPU_MEMORY={"1": 18216, "2": 21826}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Video Diffusion Alignment via Reward Gradients | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| InstructVideo: Instructing Video Diffusion Models with Human Feedback | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_24

```text
QUERY_ID=RealScholarQuery_24
QUERY=Show me all research papers on machine translation agents.
SEED=42
STATUS=PASS
GT_TOTAL=11
CRAWLER_GT_FOUND=7
FINAL_GT_FOUND=6
FINAL_RETURNED=20
TP=6
FP=14
FN=5
FINAL_PRECISION=0.3000
FINAL_RECALL=0.5455
FINAL_F1=0.3871
SEARCH_QUERIES=["Latest advancements in machine translation agents", "Research on machine learning in machine translation", "Survey papers on machine translation", "Papers on machine translation using agents", "Machine translation agents research papers"]
SEARCH_NODES=31
EXPAND_NODES=513
SELECTOR_PROMPTS=544
LOCAL_TITLE_LOOKUPS=1563
LOCAL_TITLE_HITS=1006
LOCAL_TITLE_MISSES=554
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=64.36%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=108.681s
PEAK_GPU_MEMORY={"1": 23278, "2": 26872}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| LLMs-in-the-loop Part-1: Expert Small AI Models for Bio-Medical Text   Translation | `SELECTOR_FALSE_NEGATIVE` | max score=0.463908; source=Search SearchFrom:local_paper_db |
| Towards Achieving Human Parity on End-to-end Simultaneous Speech   Translation via LLM Agent | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| SiLLM: Large Language Models for Simultaneous Machine Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| A Reinforcement Learning Approach to Interactive-Predictive Neural   Machine Translation | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Active Learning for Interactive Neural Machine Translation of Data Streams / 2 Related work |
| Zero-resource neural machine translation with multi-agent communication game | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Improving Zero-shot Translation with Language-Independent Constraints / 6 Related Work |

### RealScholarQuery_25

```text
QUERY_ID=RealScholarQuery_25
QUERY=Video aesthetics score, using multimodal large models.
SEED=42
STATUS=PASS
GT_TOTAL=1
CRAWLER_GT_FOUND=1
FINAL_GT_FOUND=1
FINAL_RETURNED=4
TP=1
FP=3
FN=0
FINAL_PRECISION=0.2500
FINAL_RECALL=1.0000
FINAL_F1=0.4000
SEARCH_QUERIES=["Large language models in video quality assessment", "Multimodal machine learning for video aesthetics", "Survey papers on video aesthetics score using multimodal models", "Use of multimodal large models in video scoring", "Multimodal large models for video analysis"]
SEARCH_NODES=33
EXPAND_NODES=499
SELECTOR_PROMPTS=532
LOCAL_TITLE_LOOKUPS=1527
LOCAL_TITLE_HITS=988
LOCAL_TITLE_MISSES=536
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=64.70%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=77.698s
PEAK_GPU_MEMORY={"1": 23526, "2": 27166}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

No missed GT.

### RealScholarQuery_26

```text
QUERY_ID=RealScholarQuery_26
QUERY=Scaling Laws for Fine-Grained Mixture of Experts.
SEED=42
STATUS=PASS
GT_TOTAL=2
CRAWLER_GT_FOUND=2
FINAL_GT_FOUND=2
FINAL_RETURNED=6
TP=2
FP=4
FN=0
FINAL_PRECISION=0.3333
FINAL_RECALL=1.0000
FINAL_F1=0.5000
SEARCH_QUERIES=["Optimization of mixture of experts model using scaling laws", "Examination of the impact of parameter increase on performance scaling in Fine-Grained Mixture of Experts", "Influence of mixture of experts on scaling laws", "Scaling laws in fine-grained mixture of experts model", "Survey papers on Scaling Laws for Fine-Grained Mixture of Experts"]
SEARCH_NODES=16
EXPAND_NODES=318
SELECTOR_PROMPTS=334
LOCAL_TITLE_LOOKUPS=994
LOCAL_TITLE_HITS=779
LOCAL_TITLE_MISSES=215
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=78.37%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=60.880s
PEAK_GPU_MEMORY={"1": 19038, "2": 22650}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

No missed GT.

### RealScholarQuery_27

```text
QUERY_ID=RealScholarQuery_27
QUERY=Show me research on rejection sampling finetuning.
SEED=42
STATUS=PASS
GT_TOTAL=9
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=4
FINAL_RETURNED=6
TP=4
FP=2
FN=5
FINAL_PRECISION=0.6667
FINAL_RECALL=0.4444
FINAL_F1=0.5333
SEARCH_QUERIES=["Studies on improving rejection sampling efficiency in fine-tuning", "Rejection sampling fine-tuning in machine learning", "Academic studies on rejection sampling optimization", "Research articles on fine-tuning techniques in rejection sampling", "Survey papers on rejection sampling fine-tuning"]
SEARCH_NODES=25
EXPAND_NODES=222
SELECTOR_PROMPTS=247
LOCAL_TITLE_LOOKUPS=614
LOCAL_TITLE_HITS=373
LOCAL_TITLE_MISSES=241
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=60.75%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=71.467s
PEAK_GPU_MEMORY={"1": 16720, "2": 20334}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Statistical Rejection Sampling Improves Preference Optimization | `SELECTOR_FALSE_NEGATIVE` | max score=0.122886; source=Search SearchFrom:local_paper_db |
| Let AI Entertain You: Increasing User Engagement with Generative AI and   Rejection Sampling | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Xwin-LM: Strong and Scalable Alignment Practice for LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DART-Math: Difficulty-Aware Rejection Tuning for Mathematical   Problem-Solving | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Breaking Language Barriers in Multilingual Mathematical Reasoning:   Insights and Observations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_28

```text
QUERY_ID=RealScholarQuery_28
QUERY=Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.
SEED=42
STATUS=PASS
GT_TOTAL=4
CRAWLER_GT_FOUND=2
FINAL_GT_FOUND=2
FINAL_RETURNED=6
TP=2
FP=4
FN=2
FINAL_PRECISION=0.3333
FINAL_RECALL=0.5000
FINAL_F1=0.4000
SEARCH_QUERIES=["Comparison studies on difficulty levels of different code evaluation datasets", "Code evaluation datasets with mid-level hardness", "Middle difficulty level code evaluation datasets", "Survey papers on code evaluation datasets"]
SEARCH_NODES=28
EXPAND_NODES=404
SELECTOR_PROMPTS=432
LOCAL_TITLE_LOOKUPS=1229
LOCAL_TITLE_HITS=850
LOCAL_TITLE_MISSES=378
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=69.16%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=4
LATENCY=80.227s
PEAK_GPU_MEMORY={"1": 25254, "2": 28870}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLM | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| NaturalCodeBench: Examining Coding Performance Mismatch on HumanEval and   Natural User Prompts | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_29

```text
QUERY_ID=RealScholarQuery_29
QUERY=Research on teaching llms to do math prove and solve IMO level math problems.
SEED=42
STATUS=PASS
GT_TOTAL=8
CRAWLER_GT_FOUND=3
FINAL_GT_FOUND=1
FINAL_RETURNED=14
TP=1
FP=13
FN=7
FINAL_PRECISION=0.0714
FINAL_RECALL=0.1250
FINAL_F1=0.0909
SEARCH_QUERIES=["Machine learning approaches for solving IMO problems", "Advanced techniques to solve IMO level math problems with LLMs", "Methods to teach language models mathematical proof", "Research on solving IMO level math problems using LLMs", "Survey papers on teaching language models mathematics"]
SEARCH_NODES=28
EXPAND_NODES=307
SELECTOR_PROMPTS=335
LOCAL_TITLE_LOOKUPS=1301
LOCAL_TITLE_HITS=892
LOCAL_TITLE_MISSES=408
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=68.56%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=72.096s
PEAK_GPU_MEMORY={"1": 18296, "2": 21900}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| HDFlow: Enhancing LLM Complex Problem-Solving with Hybrid Thinking and   Dynamic Workflows | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Large Language Models for Mathematical Reasoning: Progresses and   Challenges | `SELECTOR_FALSE_NEGATIVE` | max score=0.048757; source=Search SearchFrom:local_paper_db |
| Proving Olympiad Algebraic Inequalities without Human Demonstrations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Accessing GPT-4 level Mathematical Olympiad Solutions via Monte Carlo   Tree Self-refine with LLaMa-3 8B | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Lyra: Orchestrating Dual Correction in Automated Theorem Proving | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. A Survey on Deep Learning for Theorem Proving / 5 Evaluations |
| InfiMM-WebMath-40B: Advancing Multimodal Pre-Training for Enhanced   Mathematical Reasoning | `SELECTOR_FALSE_NEGATIVE` | max score=0.018946; source=Search SearchFrom:local_paper_db |
| Lean-STaR: Learning to Interleave Thinking and Proving | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search / 2 Model Training 2.2 Supervised Fine-tuning |

### RealScholarQuery_30

```text
QUERY_ID=RealScholarQuery_30
QUERY=I would like to find some research papers about test time training topic, in LLM research area.
SEED=42
STATUS=PASS
GT_TOTAL=6
CRAWLER_GT_FOUND=3
FINAL_GT_FOUND=2
FINAL_RETURNED=8
TP=2
FP=6
FN=4
FINAL_PRECISION=0.2500
FINAL_RECALL=0.3333
FINAL_F1=0.2857
SEARCH_QUERIES=["Online learning techniques for test-time training in large language models", "LLM research on test time training", "Advancements in test time training for language models", "Test-time training techniques in large language models", "Survey papers on test time training in language models"]
SEARCH_NODES=27
EXPAND_NODES=533
SELECTOR_PROMPTS=560
LOCAL_TITLE_LOOKUPS=1190
LOCAL_TITLE_HITS=852
LOCAL_TITLE_MISSES=335
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=71.60%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=79.364s
PEAK_GPU_MEMORY={"1": 20562, "2": 23794}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Efficient Test-Time Adaptation of Vision-Language Models | `SELECTOR_FALSE_NEGATIVE` | max score=0.049870; source=Search SearchFrom:local_paper_db |
| On the test-time zero-shot generalization of vision-language models: Do   we really need prompt learning? | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MedAdapter: Efficient Test-Time Adaptation of Large Language Models   towards Medical Reasoning | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Efficient Continual Pre-training by Mitigating the Stability Gap / 5 Evaluation 5.3 Deploying our strategies into the Llama-3 Model |
| Self-Refine: Iterative Refinement with Self-Feedback | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Self-refine: Iterative refinement with self-feedback (1) |

### RealScholarQuery_31

```text
QUERY_ID=RealScholarQuery_31
QUERY=DPO training for large-scale vision-language models.
SEED=42
STATUS=PASS
GT_TOTAL=15
CRAWLER_GT_FOUND=11
FINAL_GT_FOUND=10
FINAL_RETURNED=13
TP=10
FP=3
FN=5
FINAL_PRECISION=0.7692
FINAL_RECALL=0.6667
FINAL_F1=0.7143
SEARCH_QUERIES=["Challenges in DPO training for large-scale vision-language models", "Application of DPO in large-scale vision-language model training", "Comparative studies on DPO and other methods for training large-scale vision-language models", "Effects of DPO training on large-scale vision-language models", "Survey papers on DPO training for vision-language models"]
SEARCH_NODES=23
EXPAND_NODES=443
SELECTOR_PROMPTS=466
LOCAL_TITLE_LOOKUPS=1343
LOCAL_TITLE_HITS=992
LOCAL_TITLE_MISSES=348
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=73.86%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=74.085s
PEAK_GPU_MEMORY={"1": 19842, "2": 23438}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Mitigating Multilingual Hallucination in Large Vision-Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Enhancing Large Vision Language Models with Self-Training on Image   Comprehension | `SELECTOR_FALSE_NEGATIVE` | max score=0.004831; source=Expand SearchFrom:local_paper_db |
| STLLaVA-Med: Self-Training Large Language and Vision Assistant for   Medical Question-Answering | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Multi-Modal Hallucination Control by Visual Information Grounding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Automated Multi-level Preference for MLLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_32

```text
QUERY_ID=RealScholarQuery_32
QUERY=Show me cutting edge research works on neural network based quantum Monte Carlo.
SEED=42
STATUS=PASS
GT_TOTAL=16
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=4
FINAL_RETURNED=11
TP=4
FP=7
FN=12
FINAL_PRECISION=0.3636
FINAL_RECALL=0.2500
FINAL_F1=0.2963
SEARCH_QUERIES=["State-of-the-art research in neural network quantum Monte Carlo", "Survey papers on neural network based quantum Monte Carlo", "Recent advancements in quantum Monte Carlo using neural networks", "Neural network based quantum Monte Carlo papers", "Application of neural networks in quantum Monte Carlo studies"]
SEARCH_NODES=20
EXPAND_NODES=14
SELECTOR_PROMPTS=34
LOCAL_TITLE_LOOKUPS=359
LOCAL_TITLE_HITS=20
LOCAL_TITLE_MISSES=337
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=5.57%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=55.423s
PEAK_GPU_MEMORY={"1": 15082, "2": 18688}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Neural-network quantum state study of the long-range antiferromagnetic   Ising chain | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Universal Performance Gap of Neural Quantum States Applied to the Hofstadter-Bose-Hubbard Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Discovering Quantum Phase Transitions with Fermionic Neural Networks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Ab-initio quantum chemistry with neural-network wavefunctions | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Second-order optimisation strategies for neural network quantum states | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| NetKet 3: Machine Learning Toolbox for Many-Body Quantum Systems | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; NetKet 3: Machine learning toolbox for many-body quantum systems (1) |
| Deep learning quantum Monte Carlo for solids | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Natural Quantum Monte Carlo Computation of Excited States | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Natural quantum monte carlo computation of excited states (2023). (1) |
| Forward Laplacian: A New Computational Framework for Neural   Network-based Variational Monte Carlo | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Solving the nuclear pairing model with neural network quantum states | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Highly Accurate Real-space Electron Densities with Neural Networks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Penalty and auxiliary wave function methods for electronic Excitation in neural network variational Monte Carlo | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_33

```text
QUERY_ID=RealScholarQuery_33
QUERY=Show me some popular papers on generating textual adversarial examples for machine translation.
SEED=42
STATUS=PASS
GT_TOTAL=13
CRAWLER_GT_FOUND=7
FINAL_GT_FOUND=7
FINAL_RETURNED=12
TP=7
FP=5
FN=6
FINAL_PRECISION=0.5833
FINAL_RECALL=0.5385
FINAL_F1=0.5600
SEARCH_QUERIES=["Methods for generating adversarial examples in machine translation", "State-of-the-art techniques for generating adversarial examples in machine translation", "Adversarial example creation in machine translation using textual methods", "Textual adversarial examples in machine translation research papers", "Survey papers on textual adversarial examples in machine translation"]
SEARCH_NODES=22
EXPAND_NODES=206
SELECTOR_PROMPTS=228
LOCAL_TITLE_LOOKUPS=847
LOCAL_TITLE_HITS=575
LOCAL_TITLE_MISSES=271
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=67.89%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=70.875s
PEAK_GPU_MEMORY={"1": 21572, "2": 25194}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| A Targeted Attack on Black-Box Neural Machine Translation with Parallel   Data Poisoning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Targeted Adversarial Attacks against Neural Machine Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Generating Authentic Adversarial Examples beyond Meaning-preserving with   Doubly Round-trip Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| TransFool: An Adversarial Attack against Neural Machine Translation   Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Rethinking Targeted Adversarial Attacks For Neural Machine Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Vision-fused Attack: Advancing Aggressive and Stealthy Adversarial Text   against Neural Machine Translation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_34

```text
QUERY_ID=RealScholarQuery_34
QUERY=Show me research on 3d scene understanding leveraging progress on 3D AIGC foundation models.
SEED=42
STATUS=PASS
GT_TOTAL=7
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=4
FINAL_RETURNED=35
TP=4
FP=31
FN=3
FINAL_PRECISION=0.1143
FINAL_RECALL=0.5714
FINAL_F1=0.1905
SEARCH_QUERIES=["Survey papers on 3D scene understanding with 3D AIGC models", "Research on 3D scene understanding using AIGC", "Advancements in 3D AIGC foundational models for scene understanding", "Application of 3D AIGC foundation models in scene understanding", "Foundation models and their role in 3D scene understanding"]
SEARCH_NODES=17
EXPAND_NODES=531
SELECTOR_PROMPTS=548
LOCAL_TITLE_LOOKUPS=1261
LOCAL_TITLE_HITS=1003
LOCAL_TITLE_MISSES=240
LOCAL_TITLE_AMBIGUOUS=18
LOCAL_TITLE_HIT_RATE=79.54%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=80.911s
PEAK_GPU_MEMORY={"1": 24562, "2": 28182}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| SceneVerse: Scaling 3D Vision-Language Learning for Grounded Scene   Understanding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| 3D-VirtFusion: Synthetic 3D Data Augmentation through Generative Diffusion Models and Controllable Editing | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Bridging the Domain Gap: Self-Supervised 3D Scene Understanding with Foundation Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_35

```text
QUERY_ID=RealScholarQuery_35
QUERY=Give me papers about LLM quantized pretraining.
SEED=42
STATUS=PASS
GT_TOTAL=7
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=5
FINAL_RETURNED=22
TP=5
FP=17
FN=2
FINAL_PRECISION=0.2273
FINAL_RECALL=0.7143
FINAL_F1=0.3448
SEARCH_QUERIES=["Effects of quantization on language model pretraining", "Research on quantization techniques in LLM pretraining", "Methods for quantized pretraining in LLM", "Quantitative pretraining of language models", "Survey papers on LLM quantized pretraining"]
SEARCH_NODES=29
EXPAND_NODES=524
SELECTOR_PROMPTS=553
LOCAL_TITLE_LOOKUPS=1526
LOCAL_TITLE_HITS=1183
LOCAL_TITLE_MISSES=342
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=77.52%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=75.463s
PEAK_GPU_MEMORY={"1": 28316, "2": 31934}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| LoQT: Low-Rank Adapters for Quantized Pretraining | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Q-GaLore: Quantized GaLore with INT4 Projection and Layer-Adaptive Low-Rank Gradients | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_36

```text
QUERY_ID=RealScholarQuery_36
QUERY=Show me research on identity preservation video generation.
SEED=42
STATUS=PASS
GT_TOTAL=33
CRAWLER_GT_FOUND=21
FINAL_GT_FOUND=19
FINAL_RETURNED=41
TP=19
FP=22
FN=14
FINAL_PRECISION=0.4634
FINAL_RECALL=0.5758
FINAL_F1=0.5135
SEARCH_QUERIES=["AI approaches for identity preservation in video editing", "Latest techniques in identity preservation video generation", "Research articles on identity preservation video creation", "Deep learning techniques for identity preservation in video generation", "Survey papers on identity preservation in video generation"]
SEARCH_NODES=31
EXPAND_NODES=513
SELECTOR_PROMPTS=544
LOCAL_TITLE_LOOKUPS=1720
LOCAL_TITLE_HITS=1325
LOCAL_TITLE_MISSES=391
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=77.03%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=72.451s
PEAK_GPU_MEMORY={"1": 22852, "2": 26466}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| MagicPose: Realistic Human Poses and Facial Expressions Retargeting with   Identity-aware Diffusion | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Comprehensive Survey on Human Video Generation: Challenges, Methods, and Insights / VI Pose to Human Video Generation VI-A Single-condition Pose-guided Methods |
| VLOGGER: Multimodal Diffusion for Embodied Avatar Synthesis | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Anchored Diffusion for Video Face Reenactment | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| VITON-DiT: Learning In-the-Wild Video Try-On from Human Dance Videos via   Diffusion Transformers | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| One-Shot Identity-Preserving Portrait Reenactment | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| An Identity-Preserved Framework for Human Motion Transfer | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Infinite-ID: Identity-preserved Personalization via ID-semantics   Decoupling Paradigm | `SELECTOR_FALSE_NEGATIVE` | max score=0.011310; source=Search SearchFrom:local_paper_db |
| StoryDiffusion: Consistent Self-Attention for Long-Range Image and Video   Generation | `SELECTOR_FALSE_NEGATIVE` | max score=0.257143; source=Search SearchFrom:local_paper_db |
| X2Face: A network for controlling face generation by using images,   audio, and pose codes | `CITATION_EXPAND_MISS` | exact citation occurrences=17; e.g. Pose-Controllable Talking Face Generation by Implicitly Modularized Audio-Visual Representation / 2 Related Work |
| Deep Video Portraits | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=12; Deep video portraits (12) |
| Facial Expression Video Generation Based-On Spatio-temporal   Convolutional GAN: FEV-GAN | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MIMAFace: Face Animation via Motion-Identity Modulated Appearance   Feature Learning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DreaMoving: A Human Video Generation Framework based on Diffusion Models | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Comprehensive Survey on Human Video Generation: Challenges, Methods, and Insights / VI Pose to Human Video Generation VI-B Multi-condition Poses-guided Methods |
| Audio-driven High-resolution Seamless Talking Head Video Editing via   StyleGAN | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_37

```text
QUERY_ID=RealScholarQuery_37
QUERY=Give me some papers showing that LLM agents can do schedule planning.
SEED=42
STATUS=PASS
GT_TOTAL=10
CRAWLER_GT_FOUND=6
FINAL_GT_FOUND=5
FINAL_RETURNED=25
TP=5
FP=20
FN=5
FINAL_PRECISION=0.2000
FINAL_RECALL=0.5000
FINAL_F1=0.2857
SEARCH_QUERIES=["Language Model agents and their application in schedule planning", "Use of LLM agents in schedule planning studies", "LLM agents in schedule planning research papers", "Research articles on LLM-based schedule planning", "Survey papers on schedule planning with Language Model agents"]
SEARCH_NODES=25
EXPAND_NODES=343
SELECTOR_PROMPTS=368
LOCAL_TITLE_LOOKUPS=1042
LOCAL_TITLE_HITS=686
LOCAL_TITLE_MISSES=355
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=65.83%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=59.036s
PEAK_GPU_MEMORY={"1": 19766, "2": 23376}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| RoboGPT: an intelligent agent of making embodied long-term decisions for   daily instruction tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Smart Language Agents in Real-World Planning | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Incorporating Large Language Models into Production Systems for Enhanced Task Automation and Flexibility | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RePrompt: Planning by Automatic Prompt Engineering for Large Language   Models Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| AIOS: LLM Agent Operating System | `SELECTOR_FALSE_NEGATIVE` | max score=0.085966; source=Search SearchFrom:local_paper_db |

### RealScholarQuery_38

```text
QUERY_ID=RealScholarQuery_38
QUERY=Show me research on image encoding distributions.
SEED=42
STATUS=PASS
GT_TOTAL=17
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=4
FINAL_RETURNED=25
TP=4
FP=21
FN=13
FINAL_PRECISION=0.1600
FINAL_RECALL=0.2353
FINAL_F1=0.1905
SEARCH_QUERIES=["Analysis of image encoding distributions in machine learning", "Studies on image encoding techniques and their distribution", "Research on binary image compression using probabilistic encoding and decoding", "Survey papers on image encoding distributions", "Investigations on the use of diffusion models for image encoding distributions"]
SEARCH_NODES=33
EXPAND_NODES=372
SELECTOR_PROMPTS=405
LOCAL_TITLE_LOOKUPS=1284
LOCAL_TITLE_HITS=718
LOCAL_TITLE_MISSES=558
LOCAL_TITLE_AMBIGUOUS=8
LOCAL_TITLE_HIT_RATE=55.92%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=79.799s
PEAK_GPU_MEMORY={"1": 17094, "2": 20710}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| BIVA: A Very Deep Hierarchy of Latent Variables for Generative Modeling | `CITATION_EXPAND_MISS` | exact citation occurrences=5; e.g. A Comprehensive Survey of AI-Generated Content (AIGC): A History of Generative AI from GAN to ChatGPT / 4. Generative AI 4.1. Unimodal Models |
| Neural JPEG: End-to-End Image Compression Leveraging a Standard JPEG   Encoder-Decoder | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Learning to Improve Image Compression without Changing the Standard   Decoder | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| End-to-end optimized image compression with competition of prior   distributions | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Latent Space Imaging | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PixelVAE: A Latent Variable Model for Natural Images | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; PixelVAE: A Latent Variable Model for Natural Images (1) |
| Learned Compression of Encoding Distributions | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Second Sight: Using brain-optimized encoding models to align image   distributions with human brain activity | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| CUPID: Contextual Understanding of Prompt-conditioned Image   Distributions | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Distribution prediction for image compression: An experimental   re-compressor for JPEG images | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Bridging Distribution Learning and Image Clustering in High-dimensional   Space | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Compressing Images by Encoding Their Latent Representations with   Relative Entropy Coding | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Learned Compression for Images and Point Clouds | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_39

```text
QUERY_ID=RealScholarQuery_39
QUERY=Help me search for the work related to the synthetic data of large language models. I want to know how to automatically generate large-scale, high-quality, diverse, difficult, and valuable long thought data for learning.
SEED=42
STATUS=PASS
GT_TOTAL=2
CRAWLER_GT_FOUND=0
FINAL_GT_FOUND=0
FINAL_RETURNED=21
TP=0
FP=21
FN=2
FINAL_PRECISION=0.0000
FINAL_RECALL=0.0000
FINAL_F1=0.0000
SEARCH_QUERIES=["Efficient methods for sampling diverse test cases from large language models using synthetic data", "Techniques for generating synthetic data for language model training", "Research on automatic generation of high-quality diverse data for language models", "Methods for generating valuable long thought data for AI learning", "Survey papers on synthetic data for large language models"]
SEARCH_NODES=33
EXPAND_NODES=607
SELECTOR_PROMPTS=640
LOCAL_TITLE_LOOKUPS=1430
LOCAL_TITLE_HITS=1035
LOCAL_TITLE_MISSES=387
LOCAL_TITLE_AMBIGUOUS=8
LOCAL_TITLE_HIT_RATE=72.38%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=92.800s
PEAK_GPU_MEMORY={"1": 27216, "2": 30826}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| MUSTARD: Mastering Uniform Synthesis of Theorem and Proof Data | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale   Synthetic Data | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_40

```text
QUERY_ID=RealScholarQuery_40
QUERY=Could you list research that demonstrates the advantages of Quantization-Aware Training (QAT), which can enable the model to learn better representations for low-bit weights?.
SEED=42
STATUS=PASS
GT_TOTAL=5
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=4
FINAL_RETURNED=53
TP=4
FP=49
FN=1
FINAL_PRECISION=0.0755
FINAL_RECALL=0.8000
FINAL_F1=0.1379
SEARCH_QUERIES=["Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI", "Effects of Quantization-Aware Training on model representations", "Research papers on the impact of Quantization-Aware Training on low-bit weight representations", "Advantages of Quantization-Aware Training in AI", "Survey papers on Quantization-Aware Training benefits"]
SEARCH_NODES=30
EXPAND_NODES=423
SELECTOR_PROMPTS=453
LOCAL_TITLE_LOOKUPS=1342
LOCAL_TITLE_HITS=980
LOCAL_TITLE_MISSES=362
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=73.03%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=78.095s
PEAK_GPU_MEMORY={"1": 27638, "2": 31246}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Low-Rank Quantization-Aware Training for LLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_41

```text
QUERY_ID=RealScholarQuery_41
QUERY=Using synthesis data for scaling up sft data.
SEED=42
STATUS=PASS
GT_TOTAL=5
CRAWLER_GT_FOUND=2
FINAL_GT_FOUND=2
FINAL_RETURNED=26
TP=2
FP=24
FN=3
FINAL_PRECISION=0.0769
FINAL_RECALL=0.4000
FINAL_F1=0.1290
SEARCH_QUERIES=["Exponential growth of training data in NLP through synthetic data", "Applications of generative AI in creating synthetic data for soft target data scaling", "Scaling up SFT data with synthesis data", "Survey paper on usage of synthetic data for scaling up soft target data", "Use of synthetic data in increasing volume of SFT data"]
SEARCH_NODES=34
EXPAND_NODES=510
SELECTOR_PROMPTS=544
LOCAL_TITLE_LOOKUPS=1256
LOCAL_TITLE_HITS=923
LOCAL_TITLE_MISSES=330
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=73.49%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=89.006s
PEAK_GPU_MEMORY={"1": 20234, "2": 23860}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| API-guided Dataset Synthesis to Finetune Large Code Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Skywork-Math: Data Scaling Laws for Mathematical Reasoning in Large Language Models -- The Story Goes On | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| FullAnno: A Data Engine for Enhancing Image Comprehension of MLLMs | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_42

```text
QUERY_ID=RealScholarQuery_42
QUERY=Show me research on how to select frames when doing video understanding.
SEED=42
STATUS=PASS
GT_TOTAL=10
CRAWLER_GT_FOUND=3
FINAL_GT_FOUND=3
FINAL_RETURNED=49
TP=3
FP=46
FN=7
FINAL_PRECISION=0.0612
FINAL_RECALL=0.3000
FINAL_F1=0.1017
SEARCH_QUERIES=["Papers on automated video summary generation using frame selection", "Studies on efficient frame sampling in video comprehension", "Research on temporal sampling strategies for video representation learning", "Optical flow-based methods for key frame selection in video understanding", "Survey papers on frame selection in video understanding"]
SEARCH_NODES=42
EXPAND_NODES=599
SELECTOR_PROMPTS=641
LOCAL_TITLE_LOOKUPS=2081
LOCAL_TITLE_HITS=1300
LOCAL_TITLE_MISSES=772
LOCAL_TITLE_AMBIGUOUS=9
LOCAL_TITLE_HIT_RATE=62.47%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=107.730s
PEAK_GPU_MEMORY={"1": 24970, "2": 28568}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Frame attention networks for facial expression recognition in videos | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Multi-Agent Reinforcement Learning Based Frame Sampling for Effective   Untrimmed Video Recognition | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. View while Moving: Efficient Video Recognition in Long-untrimmed Videos / 1. Introduction |
| BubbleNets: Learning to Select the Guidance Frame in Video Object   Segmentation by Deep Sorting Frames | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Unsupervised video summarization framework using keyframe extraction and   video skimming | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Key Frame Extraction with Attention Based Deep Neural Networks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Koala: Key frame-conditioned long video-LLM | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Online Learnable Keyframe Extraction in Videos and its Application with   Semantic Word Vector in Action Recognition | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_43

```text
QUERY_ID=RealScholarQuery_43
QUERY=AI for Science papers, especially protein design and DPO of antibody design.
SEED=42
STATUS=PASS
GT_TOTAL=28
CRAWLER_GT_FOUND=19
FINAL_GT_FOUND=19
FINAL_RETURNED=47
TP=19
FP=28
FN=9
FINAL_PRECISION=0.4043
FINAL_RECALL=0.6786
FINAL_F1=0.5067
SEARCH_QUERIES=["AI advancements in protein design", "Application of AI in scientific research papers", "Survey papers on protein design using AI", "Research on DPO in antibody design", "AI tools for protein design"]
SEARCH_NODES=30
EXPAND_NODES=209
SELECTOR_PROMPTS=239
LOCAL_TITLE_LOOKUPS=1264
LOCAL_TITLE_HITS=378
LOCAL_TITLE_MISSES=882
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=29.91%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=68.829s
PEAK_GPU_MEMORY={"1": 18136, "2": 21740}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Diffusion Language Models Are Versatile Protein Learners | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| How to Hallucinate Functional Proteins | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. ProGen: Language Modeling for Protein Generation / 2 Related Work |
| Protein Design by Integrating Machine Learning with Quantum Annealing   and Quantum-inspired Optimization | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Decomposed Direct Preference Optimization for Structure-Based Drug   Design | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| A framework for conditional diffusion modelling with applications in motif scaffolding for protein design | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Fast protein backbone generation with SE(3) flow matching | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Fast protein backbone generation with se(3) flow matching (1) |
| Protein Conformation Generation via Force-Guided SE(3) Diffusion Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Generative De Novo Protein Design with Global Context | `CITATION_EXPAND_MISS` | exact citation occurrences=5; e.g. De novo Protein Design Using Geometric Vector Field Networks / 5 Experiments 5.1 Inverse Folding |
| PDB-Struct: A Comprehensive Benchmark for Structure-based Protein Design | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_44

```text
QUERY_ID=RealScholarQuery_44
QUERY=What are the researches that have explored the application of Crypto-based Private Learning in privacy-preserving machine learning?.
SEED=42
STATUS=PASS
GT_TOTAL=25
CRAWLER_GT_FOUND=17
FINAL_GT_FOUND=16
FINAL_RETURNED=49
TP=16
FP=33
FN=9
FINAL_PRECISION=0.3265
FINAL_RECALL=0.6400
FINAL_F1=0.4324
SEARCH_QUERIES=["Research articles on privacy-preserving machine learning using cryptography", "Use of homomorphic encryption in private learning for machine learning", "Research on encryption methods in privacy-preserving machine learning", "Application of cryptographic techniques in private machine learning", "Survey papers on Crypto-based Private Learning in machine learning"]
SEARCH_NODES=30
EXPAND_NODES=166
SELECTOR_PROMPTS=196
LOCAL_TITLE_LOOKUPS=1007
LOCAL_TITLE_HITS=296
LOCAL_TITLE_MISSES=708
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=29.39%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=63.011s
PEAK_GPU_MEMORY={"1": 16420, "2": 20026}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Neural Network Training With Homomorphic Encryption | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. Wildest Dreams: Reproducible Research in Privacy-preserving Neural Network Training / 3. State-of-the-Art Approaches 3.1. Secure Training using HE |
| Efficient Privacy-Preserving KAN Inference Using Homomorphic Encryption | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Blind Faith: Privacy-Preserving Machine Learning using Function   Approximation | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Blind faith: Privacy-preserving machine learning using function approximation (1) |
| Privacy-Preserving Logistic Regression Training on Large Datasets | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| CryptoGCN: Fast and Scalable Homomorphically Encrypted Graph   Convolutional Network Inference | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Decentralised, Collaborative, and Privacy-preserving Machine Learning   for Multi-Hospital Data | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Privacy-Preserving Machine Learning: Methods, Challenges and Directions | `SELECTOR_FALSE_NEGATIVE` | max score=0.008675; source=Search SearchFrom:local_paper_db |
| SHE: A Fast and Accurate Deep Neural Network for Encrypted Data | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; She: A fast and accurate deep neural network for encrypted data (1) |
| Learning in the Dark: Privacy-Preserving Machine Learning using Function   Approximation | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Learning in the dark: Privacy-preserving machine learning using function approximation (1) |

### RealScholarQuery_45

```text
QUERY_ID=RealScholarQuery_45
QUERY=All papers about controllability of video generation.
SEED=42
STATUS=PASS
GT_TOTAL=57
CRAWLER_GT_FOUND=38
FINAL_GT_FOUND=38
FINAL_RETURNED=79
TP=38
FP=41
FN=19
FINAL_PRECISION=0.4810
FINAL_RECALL=0.6667
FINAL_F1=0.5588
SEARCH_QUERIES=["Papers on techniques for controlling video generation", "Studies on the control aspects of video production", "Latest research on controllability of video generation", "Research papers on video generation controllability", "Survey papers on controllability of video generation"]
SEARCH_NODES=28
EXPAND_NODES=494
SELECTOR_PROMPTS=522
LOCAL_TITLE_LOOKUPS=1867
LOCAL_TITLE_HITS=1515
LOCAL_TITLE_MISSES=343
LOCAL_TITLE_AMBIGUOUS=9
LOCAL_TITLE_HIT_RATE=81.15%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=85.350s
PEAK_GPU_MEMORY={"1": 24680, "2": 28850}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Panacea: Panoramic and Controllable Video Generation for Autonomous   Driving | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Cinemo: Consistent and Controllable Image Animation with Motion   Diffusion Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DrivingDiffusion: Layout-Guided multi-view driving scene video   generation with latent diffusion model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DiVE: DiT-based Video Generation with Enhanced Control | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DriveScape: Towards High-Resolution Controllable Multi-View Driving   Video Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| CamCo: Camera-Controllable 3D-Consistent Image-to-Video Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| DreamVideo: High-Fidelity Image-to-Video Generation with Image Retention   and Text Guidance | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MagicDrive: Street View Generation with Diverse 3D Geometry Control | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| FreeTraj: Tuning-Free Trajectory Control in Video Diffusion Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Ctrl-V: Higher Fidelity Video Generation with Bounding-Box Controlled   Object Motion | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MotionCtrl: A Unified and Flexible Motion Controller for Video   Generation | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=18; Motionctrl: A unified and flexible motion controller for video generation (5); Motionctrl: A unified and flexible motion controller for video generation. (13) |
| AMG: Avatar Motion Guided Video Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| ControlNeXt: Powerful and Efficient Control for Image and Video   Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MyGo: Consistent and Controllable Multi-View Driving Video Generation   with Camera Control | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Training-free Camera Control for Video Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MotionClone: Training-Free Motion Cloning for Controllable Video Generation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MagicStick: Controllable Video Editing via Control Handle Transformations | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| VMC: Video Motion Customization using Temporal Attention Adaption for Text-to-Video Diffusion Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MOFA-Video: Controllable Image Animation via Generative Motion Field Adaptions in Frozen Image-to-Video Diffusion Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_46

```text
QUERY_ID=RealScholarQuery_46
QUERY=Show me research on robot decision making and task planning, especially relevant datasets and benchmarks.
SEED=42
STATUS=PASS
GT_TOTAL=65
CRAWLER_GT_FOUND=30
FINAL_GT_FOUND=29
FINAL_RETURNED=84
TP=29
FP=55
FN=36
FINAL_PRECISION=0.3452
FINAL_RECALL=0.4462
FINAL_F1=0.3893
SEARCH_QUERIES=["Benchmarks used in robot decision making research", "Relevant datasets for robot decision making", "Benchmark datasets for robot decision making", "Research on task planning in robotics", "Survey papers on robot decision making"]
SEARCH_NODES=40
EXPAND_NODES=568
SELECTOR_PROMPTS=608
LOCAL_TITLE_LOOKUPS=1556
LOCAL_TITLE_HITS=886
LOCAL_TITLE_MISSES=667
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=56.94%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=85.924s
PEAK_GPU_MEMORY={"1": 20448, "2": 24060}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Describe, Explain, Plan and Select: Interactive Planning with Large   Language Models Enables Open-World Multi-Task Agents | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents (1); Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents. (1) |
| DELTA: Decomposed Efficient Long-Term Robot Task Planning using Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Delta: Decomposed efficient long-term robot task planning using large language models (1) |
| 3D Diffuser Actor: Policy Diffusion with 3D Scene Representations | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; 3D Diffuser Actor: Policy Diffusion with 3D Scene Representations (1) |
| Mapping Instructions to Actions in 3D Environments with Visual Goal   Prediction | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Mapping instructions to actions in 3D environments with visual goal prediction (1) |
| LoHoRavens: A Long-Horizon Language-Conditioned Benchmark for Robotic   Tabletop Manipulation | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RoboGPT: an intelligent agent of making embodied long-term decisions for   daily instruction tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Plan-Seq-Learn: Language Model Guided RL for Solving Long Horizon   Robotics Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PerAct2: Benchmarking and Learning for Robotic Bimanual Manipulation   Tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| LHManip: A Dataset for Long-Horizon Language-Grounded Manipulation Tasks   in Cluttered Tabletop Environments | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| PDDLStream: Integrating Symbolic Planners and Blackbox Samplers via   Optimistic Adaptive Planning | `SELECTOR_FALSE_NEGATIVE` | max score=0.483037; source=Expand SearchFrom:local_paper_db |
| Train Offline, Test Online: A Real Robot Learning Benchmark | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Open X-Embodiment: Robotic Learning Datasets and RT-X Models / IV RT-X Design IV-C Training and inference details |
| RH20T-P: A Primitive-Level Robotic Dataset Towards Composable   Generalization Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| MLDT: Multi-Level Decomposition for Complex Long-Horizon Robotic Task   Planning with Open-Source Large Language Model | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| RH20T: A Comprehensive Robotic Dataset for Learning Diverse Skills in One-Shot | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; Diffusion policy: Visuomotor policy learning via action diffusion (2) |
| RePLan: Robotic Replanning with Perception and Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| SayPlan: Grounding Large Language Models using 3D Scene Graphs for Scalable Robot Task Planning | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; Sayplan: Grounding large language models using 3d scene graphs for scalable robot task planning (2) |
| Scaling Up and Distilling Down: Language-Guided Robot Skill Acquisition | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. Deep Generative Models in Robotics: A Survey on Learning from Multimodal Demonstrations / II Problem Formulation |
| Relevance-driven Decision Making for Safer and More Efficient Human   Robot Collaboration | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| VoxPoser: Composable 3D Value Maps for Robotic Manipulation with   Language Models | `CITATION_EXPAND_MISS` | exact citation occurrences=7; e.g. A Survey of Optimization-based Task and Motion Planning: From Classical To Learning Approaches / V Optimization-based Motion Planning V-C Learning Methods for Motion Planning |
| RLBench: The Robot Learning Benchmark &amp;amp; Learning Environment | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Task and Motion Planning for Execution in the Real | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Grounding LLMs For Robot Task Planning Using Closed-loop State Feedback | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Cognitive Mapping and Planning for Visual Navigation | `CITATION_EXPAND_MISS` | exact citation occurrences=18; e.g. Deep Visual MPC-Policy Learning for Navigation / II Related Work II-C Deep Visual Based Navigation |
| PEORL: Integrating Symbolic Planning and Hierarchical Reinforcement   Learning for Robust Decision-Making | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Toward General-Purpose Robots via Foundation Models: A Survey and Meta-Analysis / 2 Preliminaries 2.1 Ingredients of a Robotic System |
| A framework for training and benchmarking algorithms that schedule robot tasks | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| FetchBench: A Simulation Benchmark for Robot Fetching | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Open-Ended Instructable Embodied Agents with Memory-Augmented Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Open-ended instructable embodied agents with memory-augmented large language models (1) |
| Multi-agent Planning using Visual Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Orbit: A Unified Simulation Framework for Interactive Robot Learning Environments | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| HAZARD Challenge: Embodied Decision Making in Dynamically Changing Environments | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| HumanoidBench: Simulated Humanoid Benchmark for Whole-Body Locomotion and Manipulation | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey of Optimization-based Task and Motion Planning: From Classical To Learning Approaches / VII Future Challenges and Opportunities |
| LoTa-Bench: Benchmarking Language-oriented Task Planners for Embodied Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| HomeRobot: Open-Vocabulary Mobile Manipulation | `CITATION_EXPAND_MISS` | exact citation occurrences=5; e.g. Foundation Models in Robotics: Applications, Challenges, and the Future / III Robotics III-F Open-Vocabulary Robot Navigation and Manipulation |
| Towards End-to-End Embodied Decision Making via Multi-modal Large Language Model: Explorations with GPT4-Vision and Beyond | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_47

```text
QUERY_ID=RealScholarQuery_47
QUERY=How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents.
SEED=42
STATUS=PASS
GT_TOTAL=4
CRAWLER_GT_FOUND=2
FINAL_GT_FOUND=2
FINAL_RETURNED=26
TP=2
FP=24
FN=2
FINAL_PRECISION=0.0769
FINAL_RECALL=0.5000
FINAL_F1=0.1333
SEARCH_QUERIES=["Comparative studies on LLM agent evaluation in financial domain", "Regulatory and industry-standard benchmarks for evaluating LLM agents in finance", "Evaluation metrics for LLM agents in financial tasks", "Benchmarking methods for LLM agents in financial tasks", "Survey papers on evaluation of LLM agents in finance"]
SEARCH_NODES=21
EXPAND_NODES=379
SELECTOR_PROMPTS=400
LOCAL_TITLE_LOOKUPS=1498
LOCAL_TITLE_HITS=871
LOCAL_TITLE_MISSES=626
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=58.14%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=84.543s
PEAK_GPU_MEMORY={"1": 24330, "2": 27914}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| FinBen: A Holistic Financial Benchmark for Large Language Models | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Towards a Realistic Long-Term Benchmark for Open-Web Research Agents | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_48

```text
QUERY_ID=RealScholarQuery_48
QUERY=Papers that explore using large language models for mining factors in stock exchange analysis.
SEED=42
STATUS=PASS
GT_TOTAL=8
CRAWLER_GT_FOUND=4
FINAL_GT_FOUND=4
FINAL_RETURNED=19
TP=4
FP=15
FN=4
FINAL_PRECISION=0.2105
FINAL_RECALL=0.5000
FINAL_F1=0.2963
SEARCH_QUERIES=["Survey papers on large language models in stock exchange analysis", "Use of GPT-3 in stock market trend analysis", "Impact of large language models on stock exchange analysis", "Role of AI and language models in stock prediction", "Application of large language models in stock market analysis"]
SEARCH_NODES=20
EXPAND_NODES=205
SELECTOR_PROMPTS=225
LOCAL_TITLE_LOOKUPS=767
LOCAL_TITLE_HITS=311
LOCAL_TITLE_MISSES=455
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=40.55%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=65.005s
PEAK_GPU_MEMORY={"1": 18772, "2": 22378}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Automate Strategy Finding with LLM in Quant investment | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=12; Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models (3); Can chatgpt forecast stock price movements? return predictability and large language models (7) |
| FinLlama: Financial Sentiment Classification for Algorithmic Trading Applications | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Large Language Model Agent in Financial Trading: A Survey / 4. Evaluation 4.1. Trading Strategy |
| Background-aware Multi-source Fusion Financial Trend Forecasting Mechanism | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |

### RealScholarQuery_49

```text
QUERY_ID=RealScholarQuery_49
QUERY=Can you help me find research papers that explore the use of large vision-language models as agents to automatically play PC games?
SEED=42
STATUS=PASS
GT_TOTAL=8
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=5
FINAL_RETURNED=12
TP=5
FP=7
FN=3
FINAL_PRECISION=0.4167
FINAL_RECALL=0.6250
FINAL_F1=0.5000
SEARCH_QUERIES=["Survey papers on vision-language models as game agents", "Studies on PC game automation using large vision-language models", "Research on Large Multimodal Models (LMMs) and their application in automatic PC game play", "Exploration of large vision-language models as gaming agents", "Use of AI in automated PC game playing"]
SEARCH_NODES=29
EXPAND_NODES=441
SELECTOR_PROMPTS=470
LOCAL_TITLE_LOOKUPS=1166
LOCAL_TITLE_HITS=732
LOCAL_TITLE_MISSES=433
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=62.78%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=78.297s
PEAK_GPU_MEMORY={"1": 23996, "2": 27628}
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

| Missed GT | Stage | Evidence |
|---|---|---|
| Atari-GPT: Investigating the Capabilities of Multimodal Large Language Models as Low-Level Policies for Atari Games | `CRAWLER_SEARCH_MISS` | Absent from Search/Expand nodes, unresolved attempts, and exact visible citations; deeper cause is uncertain. |
| STEVE-1: A Generative Model for Text-to-Behavior in Minecraft | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=1; Steve-1: A generative model for text-to-behavior in minecraft (1) |
| Will GPT-4 Run DOOM? | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey on Large Language Model-Based Game Agents / 2 A Unified Architecture for LLMGAs 2.1 Perception |

## Artifacts

- Machine-readable summary: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/summary.json`
- Per-query results: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00` through `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49`
- Serper replay manifest: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/serper_replay_manifest.json`
- Orchestrator state: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/orchestrator_state.json`
- Official metrics: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/official_metrics.txt`
- Completion audit: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/completion_audit.json`
- Pre-run provenance: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_50Q_BASELINE_SEED_42`
