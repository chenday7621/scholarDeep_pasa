# REPRO_LOCAL_ONLY_001 + REPRO_SELECTOR_SERIALIZATION_001

## RealScholarQuery Q0–Q4 fixed-seed reproduction pilot

本报告对应同一份 PaSa 源码、同一组 checkpoint 和统一 `SEED=42` 的一次正式 5-query pilot。Q0→Q4 使用独立 Python 进程串行执行；每题退出并确认物理 GPU 1、2 回落到 0 MiB 后才启动下一题。未运行 Q5 及之后样本。

```text
FIVE_QUERY_FIXED_SEED_PILOT=PASS
SEED=42
READY_FOR_REALSCHOLARQUERY_50=YES
INFRASTRUCTURE_ISSUES=无本次执行失败；Q3物理GPU1峰值39780MiB，距40GB上限较近；固定seed不能冻结实时Serper响应和线程调度，因此尚未证明结果级完全重复
MAIN_RECALL_BOTTLENECK=CRAWLER_SEARCH_MISS (46/74 final misses, 62.16%)
NEXT_STEP_RECOMMENDATION=基础设施已具备按同一代码和seed串行运行50条的条件；若要求多次运行结果完全一致，应先冻结/缓存Serper响应并另行验证线程调度确定性
```

## Execution invariants

- Active patches: `REPRO_LOCAL_ONLY_001`, `REPRO_SELECTOR_SERIALIZATION_001`.
- Seeded sources: `PYTHONHASHSEED`, Python `random`, NumPy, `torch`, `torch.cuda.manual_seed`, and `torch.cuda.manual_seed_all`, all set to 42.
- Official generation configuration was not modified. No deterministic-algorithm switch was enabled.
- Parameters remained `expand_layers=2`, `search_queries=5`, `search_papers=10`, `expand_papers=20`, `threads_num=20`.
- Checkpoints remained `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler` and `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-selector`.
- Every query reported Selector maximum concurrency 1, both Expand layers complete, zero CUDA OOM, zero worker exception, and zero online title requests.
- Worker exception propagation passed a dedicated no-model preflight before the pilot.

## Five-query summary

```text
VALID_QUERIES=5
TOTAL_GT=145
TOTAL_CRAWLER_GT_FOUND=75
TOTAL_FINAL_GT_FOUND=71
MACRO_PRECISION=0.4589
MACRO_RECALL=0.5098
MACRO_F1=0.4813
MICRO_PRECISION=0.4277
MICRO_RECALL=0.4897
MICRO_F1=0.4566
AVG_LATENCY=91.393s
P50_LATENCY=93.906s
MAX_LATENCY=115.983s
TOTAL_SERPER_CALLS=25
AVG_LOCAL_TITLE_HIT_RATE=74.74%
MAX_GPU_MEMORY=physical_1:39780MiB,physical_2:37292MiB,overall:39780MiB
```

`FINAL_RETURNED` 和 Precision/Recall/F1 使用仓库 `metrics.py` 的集合语义：`keep_letters` 标题归一化，`select_score > 0.5` 计入最终返回。官方 `metrics.py` 复算的 Macro Crawler Recall / Precision / Recall 为 `0.5480 / 0.4589 / 0.5098`，与独立计算一致。

| Query | GT | Crawler GT | Final GT | Returned | P | R | F1 | Search | Expand | Selector prompts | Local hit rate | Latency | Peak MiB (GPU1/GPU2) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RealScholarQuery_0 | 9 | 5 | 4 | 12 | 0.3333 | 0.4444 | 0.3810 | 27 | 442 | 469 | 73.78% | 87.250s | 22662/26272 |
| RealScholarQuery_1 | 29 | 19 | 18 | 31 | 0.5806 | 0.6207 | 0.6000 | 23 | 391 | 414 | 73.68% | 93.906s | 23700/27304 |
| RealScholarQuery_2 | 21 | 14 | 14 | 20 | 0.7000 | 0.6667 | 0.6829 | 24 | 419 | 443 | 83.93% | 64.213s | 22612/26226 |
| RealScholarQuery_3 | 42 | 20 | 20 | 51 | 0.3922 | 0.4762 | 0.4301 | 37 | 844 | 881 | 79.48% | 115.983s | 39780/37292 |
| RealScholarQuery_4 | 44 | 17 | 15 | 52 | 0.2885 | 0.3409 | 0.3125 | 35 | 560 | 595 | 62.81% | 95.611s | 21870/25482 |

## Per-query details and GT misses

### RealScholarQuery_0

```text
QUERY_ID=RealScholarQuery_0
QUERY=Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.
SEED=42
STATUS=PASS
GT_TOTAL=9
CRAWLER_GT_FOUND=5
FINAL_GT_FOUND=4
FINAL_RETURNED=12
TP=4
FP=8
FN=5
FINAL_PRECISION=0.3333
FINAL_RECALL=0.4444
FINAL_F1=0.3810
SEARCH_QUERIES=5
SEARCH_NODES=27
EXPAND_NODES=442
SELECTOR_PROMPTS=469
LOCAL_TITLE_LOOKUPS=1110
LOCAL_TITLE_HITS=819
LOCAL_TITLE_MISSES=289
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=73.78%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=87.250s
PEAK_GPU_MEMORY=physical_1:22662MiB,physical_2:26272MiB
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

Crawler generated search queries:

- `Effects of dataset size on language model pre-training effectiveness`
- `Survey papers on large language model pre-training using smaller dataset`
- `Benefits of limited dataset in pre-training of language models`
- `Advantages of using smaller datasets in large language model pre-training`
- `Papers on the effectiveness of smaller datasets in language model pre-training`

| Missed GT | Stage | Evidence |
|---|---|---|
| When Less is More: Investigating Data Pruning for Pretraining LLMs at   Scale | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. Data Management For Large Language Models: A Survey / 2 Pretraining of LLM 2.2 Data Quality |
| Deduplicating Training Data Makes Language Models Better | `SELECTOR_FALSE_NEGATIVE` | max score=0.061744; source=Expand SearchFrom:local_paper_db |
| Automatic Document Selection for Efficient Encoder Pretraining | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Farewell to aimless large-scale pretraining: Influential subset selection for language model | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey of Large Language Models / 4 Pre-training 4.1 Data Collection and Preparation |
| Babyllama-2: Ensemble-distilled models consistently outperform teachers with limited data. | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |

### RealScholarQuery_1

```text
QUERY_ID=RealScholarQuery_1
QUERY=Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training.
SEED=42
STATUS=PASS
GT_TOTAL=29
CRAWLER_GT_FOUND=19
FINAL_GT_FOUND=18
FINAL_RETURNED=31
TP=18
FP=13
FN=11
FINAL_PRECISION=0.5806
FINAL_RECALL=0.6207
FINAL_F1=0.6000
SEARCH_QUERIES=5
SEARCH_NODES=23
EXPAND_NODES=391
SELECTOR_PROMPTS=414
LOCAL_TITLE_LOOKUPS=1273
LOCAL_TITLE_HITS=938
LOCAL_TITLE_MISSES=333
LOCAL_TITLE_AMBIGUOUS=2
LOCAL_TITLE_HIT_RATE=73.68%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=93.906s
PEAK_GPU_MEMORY=physical_1:23700MiB,physical_2:27304MiB
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

Crawler generated search queries:

- `Role of pre-training in the development of in-context learning in language models`
- `Insights into the process of pre-training for in-context learning in language models`
- `Pre-training methods for in-context learning in language models`
- `In-context learning in pre-training of large language models`
- `Survey papers on in-context learning in pre-trained language models`

| Missed GT | Stage | Evidence |
|---|---|---|
| Transformers Learn Higher-Order Optimization Methods for In-Context   Learning: A Study with Linear Models | `SELECTOR_FALSE_NEGATIVE` | max score=0.313988; source=Expand SearchFrom:local_paper_db |
| In-context Learning and Induction Heads | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=12; In-context learning and induction heads (11); In-context learning and induction heads. (1) |
| Do pretrained Transformers Learn In-Context by Gradient Descent? | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| The mechanistic basis of data dependence and abrupt learning in an   in-context classification task | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Data Generation Perspective to the Mechanism of In-Context Learning / 6 Future Directions |
| Explaining Emergent In-Context Learning as Kernel Regression | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| How Do Nonlinear Transformers Learn and Generalize in In-Context   Learning? | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Asymptotic theory of in-context learning by linear attention | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| A Mechanism for Sample-Efficient In-Context Learning for Sparse Retrieval Tasks | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Trained Transformers Learn Linear Models In-Context / 2 Additional Related Work |
| Transformers Learn Nonlinear Features In Context: Nonconvex Mean-field Dynamics on the Attention Landscape | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Language Models ""Grok"" to Copy | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Transformers generalize differently from information stored in context vs in weights. | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; Transformers generalize differently from information stored in context vs in weights. (2) |

### RealScholarQuery_2

```text
QUERY_ID=RealScholarQuery_2
QUERY=List all papers that use autoregressive transformer to generate videos.
SEED=42
STATUS=PASS
GT_TOTAL=21
CRAWLER_GT_FOUND=14
FINAL_GT_FOUND=14
FINAL_RETURNED=20
TP=14
FP=6
FN=7
FINAL_PRECISION=0.7000
FINAL_RECALL=0.6667
FINAL_F1=0.6829
SEARCH_QUERIES=5
SEARCH_NODES=24
EXPAND_NODES=419
SELECTOR_PROMPTS=443
LOCAL_TITLE_LOOKUPS=1369
LOCAL_TITLE_HITS=1149
LOCAL_TITLE_MISSES=214
LOCAL_TITLE_AMBIGUOUS=6
LOCAL_TITLE_HIT_RATE=83.93%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=64.213s
PEAK_GPU_MEMORY=physical_1:22612MiB,physical_2:26226MiB
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

Crawler generated search queries:

- `Use of autoregressive transformer in video generation papers`
- `Studies on autoregressive transformer in video creation`
- `Papers on video generation using autoregressive transformer`
- `Research on using autoregressive transformers for video editing and composition`
- `Autoregressive transformer models in video generation research papers`

| Missed GT | Stage | Evidence |
|---|---|---|
| HARP: Autoregressive Latent Video Prediction with High-Fidelity Image Generator | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Phenaki: Variable length video generation from open domain textual descriptions / 3 Experiments 3.4 Video Encoding |
| iVideoGPT: Interactive VideoGPTs are Scalable World Models | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Axial Attention in Multidimensional Transformers | `CITATION_EXPAND_MISS` | exact citation occurrences=7; e.g. Towards End-to-End Generative Modeling of Long Videos with Memory-Efficient Bidirectional Transformers / 3 Memory-efficient Bidirectional Transformer 3.1 Encoder Architecture |
| Look Outside the Room: Synthesizing A Consistent Long-Term 3D Scene Video from A Single Image | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. A Survey on Long Video Generation: Challenges, Methods, and Prospects / 3 Long Video Generation Paradigms 3.4 Spatial Auto-regressive Models with Temporal AutoRegressive |
| Snap video: Scaled spatiotemporal transformers for text-to-video synthesis | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Pandora: Towards general world model with natural language actions and video states. | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Emu3: Next token prediction is all you need | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |

### RealScholarQuery_3

```text
QUERY_ID=RealScholarQuery_3
QUERY=I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs. These models should be pre-trained on large-scale datasets, including visual, audio, and audio-visual data. Please exclude survey papers.
SEED=42
STATUS=PASS
GT_TOTAL=42
CRAWLER_GT_FOUND=20
FINAL_GT_FOUND=20
FINAL_RETURNED=51
TP=20
FP=31
FN=22
FINAL_PRECISION=0.3922
FINAL_RECALL=0.4762
FINAL_F1=0.4301
SEARCH_QUERIES=5
SEARCH_NODES=37
EXPAND_NODES=844
SELECTOR_PROMPTS=881
LOCAL_TITLE_LOOKUPS=2213
LOCAL_TITLE_HITS=1759
LOCAL_TITLE_MISSES=438
LOCAL_TITLE_AMBIGUOUS=16
LOCAL_TITLE_HIT_RATE=79.48%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=115.983s
PEAK_GPU_MEMORY=physical_1:39780MiB,physical_2:37292MiB
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

Crawler generated search queries:

- `Research on Large Multimodal Models (LMMs) for integrating visual and textual data`
- `Foundation models supporting visual and audio inputs`
- `Multimodal foundation models for visual and audio inputs`
- `Research on audio-visual pretraining in multimodal foundation models`
- `Pre-training of multimodal foundation models on large-scale datasets`

| Missed GT | Stage | Evidence |
|---|---|---|
| CoAVT: A Cognition-Inspired Unified Audio-Visual-Text Pre-Training Model   for Multimodal Processing | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| video-SALMONN: Speech-Enhanced Audio-Visual Large Language Models | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Gemini: A Family of Highly Capable Multimodal Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=4; Gemini: a family of highly capable multimodal models (4) |
| VITA: Towards Open-Source Interactive Omni Multimodal LLM | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Video Understanding as Machine Translation | `CITATION_EXPAND_MISS` | exact citation occurrences=7; e.g. UniVL: A Unified Video and Language Pre-Training Model for Multimodal Understanding and Generation / 1 Introduction |
| i-Code V2: An Autoregressive Generation Framework over Vision, Language, and Speech Data | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| OPT: Omni-Perception Pre-Trainer for Cross-Modal Understanding and Generation | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. Large-scale Multi-Modal Pre-trained Models: A Comprehensive Survey / 3 Multi-Modal Pre-training 3.4 Pre-training Objectives |
| Connecting multi-modal contrastive representations | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| MIO: A Foundation Model on Multimodal Tokens | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Unified-io 2: Scaling autoregressive multimodal models with vision, language, audio, and action | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. AnyGPT: Unified Multimodal LLM with Discrete Sequence Modeling / 1 Introduction |
| Imagebind: One embedding space to bind them all | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=23; Imagebind: One embedding space to bind them all (22); ImageBind: One embedding space to bind them all (1) |
| Ofasys: A multi-modal multi-task learning system for building generalist models. | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. TouchStone: Evaluating Vision-Language Models by Language Models / Related Work 2.2 Vision-Language Models |
| Audioclip: Extending clip to image, text and audio | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=5; Audioclip: Extending clip to image, text and audio (5) |
| Audio-Visual LLM for Video Understanding | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Omnibind: Large-scale omni multimodal representation via binding spaces | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Onellm: One framework to align all modalities with language | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| VideoLLaMA 2: Advancing spatial-temporal modeling and audio understanding in video-llms | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. A Comprehensive Review of Multimodal Large Language Models: Performance and Challenges Across Different Tasks / III Task Classification of Multimodal Large Language Models III-B Video Tasks |
| One-peace: Exploring one general representation model toward unlimited modalities | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond / Related Work |
| Freebind: Free lunch in unified multimodal space via knowledge fusion | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Efficient self-supervised learning with contextualized target representations for vision, speech and language | `CITATION_EXPAND_MISS` | exact citation occurrences=2; e.g. Fast-HuBERT: An Efficient Training Framework for Self-Supervised Speech Representation Learning / 2 Background 2.2 Related Work |
| Extending multi-modal contrastive representations | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| From Vision to Audio and Beyond: A Unified Model for Audio-Visual Representation and Generation | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |

### RealScholarQuery_4

```text
QUERY_ID=RealScholarQuery_4
QUERY=Provide me with all papers that discuss reinforcement learning training for Large Language Model agent tasks.
SEED=42
STATUS=PASS
GT_TOTAL=44
CRAWLER_GT_FOUND=17
FINAL_GT_FOUND=15
FINAL_RETURNED=52
TP=15
FP=37
FN=29
FINAL_PRECISION=0.2885
FINAL_RECALL=0.3409
FINAL_F1=0.3125
SEARCH_QUERIES=5
SEARCH_NODES=35
EXPAND_NODES=560
SELECTOR_PROMPTS=595
LOCAL_TITLE_LOOKUPS=1608
LOCAL_TITLE_HITS=1010
LOCAL_TITLE_MISSES=595
LOCAL_TITLE_AMBIGUOUS=3
LOCAL_TITLE_HIT_RATE=62.81%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=95.611s
PEAK_GPU_MEMORY=physical_1:21870MiB,physical_2:25482MiB
CUDA_OOM_COUNT=0
WORKER_EXCEPTION_COUNT=0
```

Crawler generated search queries:

- `Experiences in training Large Language Model agents using reinforcement learning`
- `Case studies of Large Language Model agents trained using reinforcement learning`
- `Reinforcement learning approaches for optimizing Large Language Model agents`
- `Research on task-agnostic rewards in reinforcement learning training for large language models`
- `Survey papers on reinforcement learning training for large language models`

| Missed GT | Stage | Evidence |
|---|---|---|
| True Knowledge Comes from Practice: Aligning LLMs with Embodied   Environments via Reinforcement Learning | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Teaching Large Language Models to Reason with Reinforcement Learning | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Language Agents with Reinforcement Learning for Strategic Play in the   Werewolf Game | `CITATION_EXPAND_MISS` | exact citation occurrences=4; e.g. How Far Are We on the Decision-Making of LLMs? Evaluating LLMs’ Gaming Ability in Multi-Agent Environments / 6 Related Work 6.1 Specific Games |
| STARLING: Self-supervised Training of Text-based Reinforcement Learning Agent with Large Language Models | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Towards Generalizable Agents in Text-Based Educational Environments: A Study of Integrating RL with LLMs | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| WebGPT: Browser-assisted question-answering with human feedback | `SELECTOR_FALSE_NEGATIVE` | max score=0.011713; source=Expand SearchFrom:local_paper_db |
| Mutual Enhancement of Large Language and Reinforcement Learning Models through Bi-Directional Feedback Mechanisms: A Case Study | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| LLM Augmented Hierarchical Agents | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Entropy-Regularized Token-Level Policy Optimization for Language Agent Reinforcement | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Building Open-Ended Embodied Agent via Language-Policy Bidirectional Adaptation | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| RL-GPT: Integrating Reinforcement Learning and Code-as-policy | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Training Language Models to Self-Correct via Reinforcement Learning | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Math-shepherd: Verify and reinforce llms step-by-step without human annotations | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Generative job recommendations with large language model | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Survey on Large Language Models for Recommendation / 4 Generative LLMs for Recommendation 4.2 Tuning Paradigm |
| Reinforcement Learning Problem Solving with Large Language Models | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Enhance reasoning for large language models in the game werewolf | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Adarefiner: Refining decisions of language models with adaptive feedback | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Large Language Models as Generalizable Policies for Embodied Tasks | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Lagr-seq: Language-guided reinforcement learning with sample-efficient querying. | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Eureka: Human-Level Reward Design via Coding Large Language Models | `LOCAL_RESOLVER_UNRESOLVED` | exact unresolved lookup count=2; Eureka: Human-level reward design via coding large language models (2) |
| Openagi: When llm meets domain experts | `CITATION_EXPAND_MISS` | exact citation occurrences=3; e.g. A Survey on Large Language Model based Autonomous Agents / 2 LLM-based Autonomous Agent Construction 2.1 Agent Architecture Design |
| Unleashing the Power of Pre-trained Language Models for Offline Reinforcement Learning | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Reason for future, act for now: A principled framework for autonomous llm agents with provable sample efficiency | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Alpacafarm: A simulation framework for methods that learn from human feedback | `SELECTOR_FALSE_NEGATIVE` | max score=0.448905; source=Expand SearchFrom:local_paper_db |
| Large Language Model-based Human-Agent Collaboration for Complex Task Solving | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| Language models are few-shot butlers | `CITATION_EXPAND_MISS` | exact citation occurrences=1; e.g. A Systematic Survey of Text Worlds as Embodied Natural Language Environments / 6 Contemporary Focus Areas 6.3 Hybrid 3D-Text Environments |
| How Can LLM Guide RL? A Value-Based Approach | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |
| AGILE: A Novel Framework of LLM Agents | `CRAWLER_SEARCH_MISS` | absent from Search/Expand nodes, unresolved attempts, and exact visible citation titles; deeper cause uncertain |

## GT miss stage distribution

分类采用互斥优先级：已抓取但最终未选中 → Selector false negative；出现 exact unresolved lookup → local resolver unresolved；在已抓取论文的引用列表中发现 exact GT 但没有形成节点 → Citation Expand miss；其余未在 Search、Expand、unresolved 或可见引用中出现的 GT → Crawler Search miss，后续深层原因仍不确定。

| Stage | Count | Share of 74 misses |
|---|---:|---:|
| `CRAWLER_SEARCH_MISS` | 46 | 62.16% |
| `CITATION_EXPAND_MISS` | 18 | 24.32% |
| `LOCAL_RESOLVER_UNRESOLVED` | 6 | 8.11% |
| `SELECTOR_FALSE_NEGATIVE` | 4 | 5.41% |
| `OTHER_UNCERTAIN` | 0 | 0.00% |

Search/Crawler 覆盖是主要瓶颈：46 个 GT 在初始 Search 中没有出现，也没有在本次已抓取树的 exact citation、unresolved 日志或 Expand 节点中找到。另有 18 个 GT 明确出现在某个已抓取论文的引用列表中但没有形成节点，说明 section/depth/父节点覆盖使 Citation Expand 未能恢复它们。

6 个 GT 有直接 local-only 影响证据：citation title 已被 lookup，normalized title 与 GT 精确一致，但本地 resolver 返回 unresolved 并跳过。4 个 GT 已进入 Crawler 集合，但被 `select_score <= 0.5` 删除。

## Q3, serialization, and GPU lifecycle

Q3 在 seed 42 下完整完成两层 Expand：Search nodes=37，Expand nodes=844，Selector prompts=881，最大单 batch=114 prompts。Selector 最大并发始终为 1，CUDA OOM=0，worker exception=0。峰值为物理 GPU 1 39780 MiB、GPU 2 37292 MiB。

所有五题开始前和结束后，物理 GPU 1、2 均为 0 MiB，因此没有跨 query 显存累积。不过 Q3 的 GPU 1 峰值达到 39780 MiB，约为标称 40960 MiB 的 97.1%，后续 50-query 仍应保留当前逐题停止门禁。

## Reproducibility assessment

固定 seed 已覆盖代码中明确的 Python、NumPy 和 Torch RNG，且 Crawler/Selector generation 配置未改变。该设置足以定义一个统一的 seed/config baseline，但本次只执行了一轮，不能据此声称结果级完全可重复。实时 Serper 返回可能随时间变化；Search 和 Expand 仍使用多线程，候选到达与去重顺序可能受调度影响；本次也按要求没有启用 deterministic algorithms。

因此，当前基础设施可以进入一次正式 50-query 串行运行；若目标是随后重跑得到完全相同的论文集合与分数，还需先冻结 Serper 响应，并单独验证剩余线程调度和 CUDA 算子的确定性。

## Artifacts

- Machine-readable summary: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-fixed-seed-42-20260910/fixed_seed_summary.json`
- Orchestrator state: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-fixed-seed-42-20260910/orchestrator_state.json`
- Official metrics output: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-fixed-seed-42-20260910/official_metrics.txt`
- Per-query outputs/logs: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-fixed-seed-42-20260910/q0` through `q4`
- Pre-run metadata: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_5Q_FIXED_SEED_42/pre_run_metadata.json`
- Pre-run git diff: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_5Q_FIXED_SEED_42/git_diff_before.patch`
- Input hashes: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_5Q_FIXED_SEED_42/input_hashes.txt`
