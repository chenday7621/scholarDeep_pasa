# PAGE2_SEARCH_PROBE_001

**原审计 276 个未解释 miss 中，page2 找回 35 个，recovery rate=12.6812%。**248 条原查询均完成 HTTP 200 响应；本次只增加 page2，没有调用模型或修改冻结产物。

## 实验与口径

每条请求完整复制对应 baseline 的 q 字符串，包括 `before:2024-09-24 site:arxiv.org`；保持 Serper、num=10，只将 page=1 改成 page=2。所有新 attempt/replay 写到独立目录：`/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911`。按生成序号关联，不按原并发请求到达顺序关联。

身份匹配只使用 GT 提供的 arXiv ID 与 organic URL 的原 parser 输出；不把 snippet 中提及、模糊标题或其他题结果计入本题返回。每个 GT 在同题多条 query 命中只计一次，所有命中证据均保留。

下表给出三个独立口径，避免把 276 子集的 recovery、全量 Search recall 与 baseline Crawler/Selector 指标混为一谈。PAGE2_RECOVERY_RATE 的分母为各口径中 page1 未命中的 GT；目标子集恰为 276。

| 口径 | 分母 | PAGE1_GT_RECALL | PAGE1_PLUS_PAGE2_GT_RECALL | NEW_GT_FROM_PAGE2 | PAGE2_RECOVERY_RATE |
|---|---:|---:|---:|---:|---:|
| unexplained_276 | 276 | 0/276 = 0.0000% | 35/276 = 12.6812% | 35 | 35/276 = 12.6812% |
| all_normalized_GT_790 | 790 | 157/790 = 19.8734% | 220/790 = 27.8481% | 63 | 63/633 = 9.9526% |
| all_arxiv_ID_791 | 791 | 157/791 = 19.8483% | 220/791 = 27.8129% | 63 | 63/634 = 9.9369% |

**新增分母核查：**Q45 的 Panacea+（2408.07605）与 Panacea（2311.16813）归一化标题相同，但对应两个不同 GT ID，并非仅空格不同。保持冻结文件不动；790 口径仍沿用原标题分组，同时补充 791 个 (query,ID) 口径。这里的 ID 辅助 Search 覆盖率不是重新计算后的官方 title-based baseline。

## 276 个 miss 中哪些题收益最大

| Query | 原未解释 miss | page2 新增 GT | recovery rate |
|---|---:|---:|---:|
| Q19 | 10 | 4 | 40.0000% |
| Q1 | 7 | 2 | 28.5714% |
| Q3 | 10 | 2 | 20.0000% |
| Q7 | 18 | 2 | 11.1111% |
| Q9 | 19 | 2 | 10.5263% |
| Q11 | 7 | 2 | 28.5714% |
| Q32 | 10 | 2 | 20.0000% |
| Q4 | 20 | 1 | 5.0000% |
| Q6 | 14 | 1 | 7.1429% |
| Q10 | 4 | 1 | 25.0000% |
| Q13 | 5 | 1 | 20.0000% |
| Q16 | 3 | 1 | 33.3333% |
| Q21 | 2 | 1 | 50.0000% |
| Q23 | 2 | 1 | 50.0000% |
| Q24 | 2 | 1 | 50.0000% |
| Q27 | 4 | 1 | 25.0000% |
| Q30 | 1 | 1 | 100.0000% |
| Q33 | 6 | 1 | 16.6667% |
| Q34 | 3 | 1 | 33.3333% |
| Q36 | 8 | 1 | 12.5000% |
| Q40 | 1 | 1 | 100.0000% |
| Q41 | 3 | 1 | 33.3333% |
| Q43 | 6 | 1 | 16.6667% |
| Q45 | 18 | 1 | 5.5556% |
| Q46 | 20 | 1 | 5.0000% |
| Q48 | 2 | 1 | 50.0000% |

## 对 Top-10 瓶颈的判断

观测到 35/276 个原未解释 miss 在相同查询的新 page2 响应中出现，说明加深检索对这部分样本确有候选覆盖价值。不过大多数目标仍未找回，当前证据不支持“Top-10 太浅是这 276 个漏失的主要解释”。

page1 是 2026-09-10 的冻结结果，page2 在 2026-09-11 获取。固定 before 日期不等于固定搜索索引或排序；没有同步重取 page1。因此这是固定请求参数的增量 probe，不能将新 page2 的 nominal rank 11–20 严格等同于 baseline 当时的 11–20，也不能彻底排除时间变化。没有请求 page3 或更深结果，剩余 miss 不能据此全部归咎 query generation。

没有获取新论文全文、没有 Selector/Expand，所以找回数只表示 Search 候选覆盖，不是最终 Recall/F1 的实测提升。扩大 top-k 会增加候选处理成本；不能将本次额外 248 次 API 请求的结果作为每题 ≤5×Top10 的公平 planner A/B。

## 请求完整性

- 成功逻辑请求：248/248；HTTP 状态分布：`{'None': 6, '200': 248}`。
- 总记录 attempts：254；transport failures：6。初次沙箱阻止与后续 TLS/连接失败均保留，成功结果从不重请求；失败请求是否已到服务器不可知，不把它们算成 HTTP 200。
- page2 organic=2470；可解析 arXiv ID occurrences=2463；同一原查询的 page1/page2 ID 重合累计=248（去除每页内部重复后）。
- 每条保存 query/QID/生成序号、payload、HTTP、时间、latency、raw 文本与原 bytes base64、parsed IDs、raw/bytes/file SHA-256。响应 searchParameters.page=2 及 q 均核验。
- 冻结输入 363 个文件 hash 复核未变；manifest：`/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/frozen_inputs_before.json`。

## 按 RealScholarQuery 的完整统计

| Query | queries | GT组 | page1 GT | page1+page2 GT | 全GT新增 | 目标miss | 目标找回 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q0 | 5 | 9 | 0 | 0 | 0 | 2 | 0 |
| Q1 | 5 | 29 | 5 | 8 | 3 | 7 | 2 |
| Q2 | 5 | 21 | 6 | 9 | 3 | 4 | 0 |
| Q3 | 5 | 42 | 3 | 8 | 5 | 10 | 2 |
| Q4 | 5 | 44 | 2 | 5 | 3 | 20 | 1 |
| Q5 | 5 | 7 | 2 | 2 | 0 | 1 | 0 |
| Q6 | 5 | 24 | 2 | 4 | 2 | 14 | 1 |
| Q7 | 5 | 35 | 3 | 5 | 2 | 18 | 2 |
| Q8 | 5 | 16 | 5 | 5 | 0 | 4 | 0 |
| Q9 | 5 | 39 | 5 | 8 | 3 | 19 | 2 |
| Q10 | 5 | 15 | 3 | 4 | 1 | 4 | 1 |
| Q11 | 5 | 20 | 4 | 7 | 3 | 7 | 2 |
| Q12 | 5 | 17 | 5 | 5 | 0 | 5 | 0 |
| Q13 | 5 | 12 | 3 | 5 | 2 | 5 | 1 |
| Q14 | 5 | 9 | 4 | 5 | 1 | 3 | 0 |
| Q15 | 5 | 5 | 1 | 1 | 0 | 1 | 0 |
| Q16 | 5 | 8 | 2 | 4 | 2 | 3 | 1 |
| Q17 | 5 | 9 | 2 | 2 | 0 | 3 | 0 |
| Q18 | 4 | 5 | 1 | 1 | 0 | 4 | 0 |
| Q19 | 5 | 37 | 8 | 14 | 6 | 10 | 4 |
| Q20 | 5 | 4 | 1 | 1 | 0 | 3 | 0 |
| Q21 | 5 | 2 | 0 | 1 | 1 | 2 | 1 |
| Q22 | 5 | 3 | 0 | 0 | 0 | 1 | 0 |
| Q23 | 5 | 2 | 0 | 1 | 1 | 2 | 1 |
| Q24 | 5 | 11 | 5 | 6 | 1 | 2 | 1 |
| Q25 | 5 | 1 | 0 | 0 | 0 | 0 | 0 |
| Q26 | 5 | 2 | 2 | 2 | 0 | 0 | 0 |
| Q27 | 5 | 9 | 5 | 6 | 1 | 4 | 1 |
| Q28 | 4 | 4 | 0 | 0 | 0 | 2 | 0 |
| Q29 | 5 | 8 | 3 | 4 | 1 | 3 | 0 |
| Q30 | 5 | 6 | 3 | 4 | 1 | 1 | 1 |
| Q31 | 5 | 15 | 4 | 4 | 0 | 4 | 0 |
| Q32 | 5 | 16 | 4 | 6 | 2 | 10 | 2 |
| Q33 | 5 | 13 | 3 | 5 | 2 | 6 | 1 |
| Q34 | 5 | 7 | 1 | 3 | 2 | 3 | 1 |
| Q35 | 5 | 7 | 2 | 2 | 0 | 2 | 0 |
| Q36 | 5 | 33 | 8 | 10 | 2 | 8 | 1 |
| Q37 | 5 | 10 | 4 | 4 | 0 | 4 | 0 |
| Q38 | 5 | 17 | 0 | 0 | 0 | 11 | 0 |
| Q39 | 5 | 2 | 0 | 0 | 0 | 2 | 0 |
| Q40 | 5 | 5 | 4 | 5 | 1 | 1 | 1 |
| Q41 | 5 | 5 | 2 | 3 | 1 | 3 | 1 |
| Q42 | 5 | 10 | 2 | 2 | 0 | 6 | 0 |
| Q43 | 5 | 28 | 10 | 13 | 3 | 6 | 1 |
| Q44 | 5 | 25 | 6 | 9 | 3 | 4 | 0 |
| Q45 | 5 | 57 | 12 | 15 | 3 | 18 | 1 |
| Q46 | 5 | 65 | 6 | 7 | 1 | 20 | 1 |
| Q47 | 5 | 4 | 2 | 2 | 0 | 1 | 0 |
| Q48 | 5 | 8 | 2 | 3 | 1 | 2 | 1 |
| Q49 | 5 | 8 | 0 | 0 | 0 | 1 | 0 |

## 每个找回 GT 的全部原查询与 replay 证据

position 为 Serper 返回的页内位置；nominal 为 10+页内数组下标+1。同一 GT 多次命中不重复计入恢复数。

| Q / 原audit行 | GT / ID | 原query序号及文本 | position / nominal | replay |
|---|---|---|---|---|
| Q1 / 4 | Explaining Emergent In-Context Learning as Kernel Regression / 2305.12766 | 4: Insights into the process of pre-training for in-context learning in language models | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q01/s04/attempt_001.json) `/structured_response/organic/8` |
| Q1 / 9 | Investigating the Pre-Training Dynamics of In-Context Learning: Task Recognition vs. Task Learning / 2406.14022 | 4: Insights into the process of pre-training for in-context learning in language models | 1 / 11 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q01/s04/attempt_001.json) `/structured_response/organic/0` |
| Q1 / 9 | Investigating the Pre-Training Dynamics of In-Context Learning: Task Recognition vs. Task Learning / 2406.14022 | 5: Role of pre-training in the development of in-context learning in language models | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q01/s05/attempt_001.json) `/structured_response/organic/6` |
| Q3 / 14 | CoAVT: A Cognition-Inspired Unified Audio-Visual-Text Pre-Training Model   for Multimodal Processing / 2401.12264 | 2: Research on audio-visual pretraining in multimodal foundation models | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q03/s02/attempt_001.json) `/structured_response/organic/8` |
| Q3 / 16 | VITA: Towards Open-Source Interactive Omni Multimodal LLM / 2408.05211 | 3: Multimodal foundation models for visual and audio inputs | 5 / 15 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q03/s03/attempt_001.json) `/structured_response/organic/4` |
| Q4 / 35 | Reinforcement Learning Problem Solving with Large Language Models / 2404.18638 | 3: Reinforcement learning approaches for optimizing Large Language Model agents | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q04/s03/attempt_001.json) `/structured_response/organic/6` |
| Q6 / 48 | LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs / 2406.15319 | 1: Large language model based methods for HotPotQA dataset | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q06/s01/attempt_001.json) `/structured_response/organic/8` |
| Q6 / 48 | LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs / 2406.15319 | 4: Experiments on the HotPotQA dataset for language models | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q06/s04/attempt_001.json) `/structured_response/organic/9` |
| Q6 / 48 | LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs / 2406.15319 | 5: Proposed methods for HotPotQA using large language models | 8 / 18 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q06/s05/attempt_001.json) `/structured_response/organic/7` |
| Q7 / 69 | MLVU: A Comprehensive Benchmark for Multi-Task Long Video Understanding / 2406.04264 | 5: Research on long-duration video description | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q07/s05/attempt_001.json) `/structured_response/organic/6` |
| Q7 / 74 | VideoAgent: Long-form Video Understanding with Large Language Model as Agent / 2403.10517 | 4: Studies on multi-modal language models for long video understanding | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q07/s04/attempt_001.json) `/structured_response/organic/9` |
| Q9 / 85 | RankRAG: Unifying Context Ranking with Retrieval-Augmented Generation in LLMs / 2407.02485 | 4: Application of LLM in search result ranking | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q09/s04/attempt_001.json) `/structured_response/organic/8` |
| Q9 / 97 | Leveraging LLMs for Unsupervised Dense Retriever Ranking / 2402.04853 | 1: Use of LLM in ranking search results | 8 / 18 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q09/s01/attempt_001.json) `/structured_response/organic/7` |
| Q10 / 103 | Are Bigger Encoders Always Better in Vision Large Models? / 2408.00620 | 2: Analysis of scaling law in video-text models | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q10/s02/attempt_001.json) `/structured_response/organic/9` |
| Q11 / 106 | CuMo: Scaling Multimodal LLM with Co-Upcycled Mixture-of-Experts / 2405.05949 | 1: MoE architecture models in visual-LLM | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q11/s01/attempt_001.json) `/structured_response/organic/9` |
| Q11 / 106 | CuMo: Scaling Multimodal LLM with Co-Upcycled Mixture-of-Experts / 2405.05949 | 4: Research on MoE architecture in visual-LLMs | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q11/s04/attempt_001.json) `/structured_response/organic/2` |
| Q11 / 109 | MoMa: Efficient Early-Fusion Pre-training with Mixture of Modality-Aware Experts / 2407.21770 | 3: Multi-Modal Large Language Models with MoE architecture | 4 / 14 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q11/s03/attempt_001.json) `/structured_response/organic/3` |
| Q13 / 121 | On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks / 2402.08115 | 1: Studies on the limitations of self-correction in language models | 8 / 18 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q13/s01/attempt_001.json) `/structured_response/organic/7` |
| Q16 / 128 | Document-Level Multi-Event Extraction with Event Proxy Nodes and Hausdorff Distance Minimization / 2305.18926 | 1: Document-level event extraction without triggers research papers | 5 / 15 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q16/s01/attempt_001.json) `/structured_response/organic/4` |
| Q19 / 139 | WaterJudge: Quality-Detection Trade-off when Watermarking Large Language   Models / 2403.19548 | 2: Research on methods to maintain generation quality in LLMs during vocabulary watermarking | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q19/s02/attempt_001.json) `/structured_response/organic/8` |
| Q19 / 141 | Adaptive Text Watermark for Large Language Models / 2401.13927 | 5: Techniques to mitigate vocabulary watermarking effects on LLM generation | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q19/s05/attempt_001.json) `/structured_response/organic/8` |
| Q19 / 145 | PersonaMark: Personalized LLM watermarking for model protection and user attribution / 2409.09739 | 1: Survey papers on protecting generation quality of LLMs under vocabulary watermarking | 4 / 14 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q19/s01/attempt_001.json) `/structured_response/organic/3` |
| Q19 / 147 | Improving the Generation Quality of Watermarked Large Language Models   via Word Importance Scoring / 2311.09668 | 4: Impact of vocabulary watermarking on LLMs generation quality | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q19/s04/attempt_001.json) `/structured_response/organic/2` |
| Q21 / 154 | Relative Preference Optimization: Enhancing LLM Alignment through Contrasting Responses across Identical and Diverse Prompts / 2402.10958 | 4: Studies on how different responses to the same prompt affect SFT model | 4 / 14 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q21/s04/attempt_001.json) `/structured_response/organic/3` |
| Q23 / 157 | InstructVideo: Instructing Video Diffusion Models with Human Feedback / 2312.12490 | 1: Papers on diffusion models for video generation optimized with reinforcement learning | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q23/s01/attempt_001.json) `/structured_response/organic/8` |
| Q23 / 157 | InstructVideo: Instructing Video Diffusion Models with Human Feedback / 2312.12490 | 2: Research on reinforcement learning techniques in video diffusion models optimization | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q23/s02/attempt_001.json) `/structured_response/organic/6` |
| Q23 / 157 | InstructVideo: Instructing Video Diffusion Models with Human Feedback / 2312.12490 | 5: Use of reinforcement learning in optimizing diffusion models for video production | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q23/s05/attempt_001.json) `/structured_response/organic/6` |
| Q24 / 159 | SiLLM: Large Language Models for Simultaneous Machine Translation / 2402.13036 | 1: Machine translation agents research papers | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q24/s01/attempt_001.json) `/structured_response/organic/6` |
| Q24 / 159 | SiLLM: Large Language Models for Simultaneous Machine Translation / 2402.13036 | 2: Papers on machine translation using agents | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q24/s02/attempt_001.json) `/structured_response/organic/2` |
| Q24 / 159 | SiLLM: Large Language Models for Simultaneous Machine Translation / 2402.13036 | 2: Papers on machine translation using agents | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q24/s02/attempt_001.json) `/structured_response/organic/6` |
| Q24 / 159 | SiLLM: Large Language Models for Simultaneous Machine Translation / 2402.13036 | 5: Latest advancements in machine translation agents | 9 / 19 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q24/s05/attempt_001.json) `/structured_response/organic/8` |
| Q27 / 161 | Xwin-LM: Strong and Scalable Alignment Practice for LLMs / 2405.20335 | 4: Rejection sampling fine-tuning in machine learning | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q27/s04/attempt_001.json) `/structured_response/organic/9` |
| Q27 / 161 | Xwin-LM: Strong and Scalable Alignment Practice for LLMs / 2405.20335 | 5: Studies on improving rejection sampling efficiency in fine-tuning | 6 / 16 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q27/s05/attempt_001.json) `/structured_response/organic/5` |
| Q30 / 169 | On the test-time zero-shot generalization of vision-language models: Do   we really need prompt learning? / 2405.02266 | 2: Test-time training techniques in large language models | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q30/s02/attempt_001.json) `/structured_response/organic/2` |
| Q32 / 177 | Ab-initio quantum chemistry with neural-network wavefunctions / 2208.12590 | 2: Neural network based quantum Monte Carlo papers | 5 / 15 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q32/s02/attempt_001.json) `/structured_response/organic/4` |
| Q32 / 177 | Ab-initio quantum chemistry with neural-network wavefunctions / 2208.12590 | 5: State-of-the-art research in neural network quantum Monte Carlo | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q32/s05/attempt_001.json) `/structured_response/organic/9` |
| Q32 / 179 | Deep learning quantum Monte Carlo for solids / 2407.00707 | 1: Application of neural networks in quantum Monte Carlo studies | 7 / 17 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q32/s01/attempt_001.json) `/structured_response/organic/6` |
| Q32 / 179 | Deep learning quantum Monte Carlo for solids / 2407.00707 | 5: State-of-the-art research in neural network quantum Monte Carlo | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q32/s05/attempt_001.json) `/structured_response/organic/2` |
| Q33 / 188 | Rethinking Targeted Adversarial Attacks For Neural Machine Translation / 2407.05319 | 3: Adversarial example creation in machine translation using textual methods | 2 / 12 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q33/s03/attempt_001.json) `/structured_response/organic/1` |
| Q33 / 188 | Rethinking Targeted Adversarial Attacks For Neural Machine Translation / 2407.05319 | 5: Methods for generating adversarial examples in machine translation | 5 / 15 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q33/s05/attempt_001.json) `/structured_response/organic/4` |
| Q34 / 192 | Bridging the Domain Gap: Self-Supervised 3D Scene Understanding with Foundation Models / 2305.08776 | 1: Foundation models and their role in 3D scene understanding | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q34/s01/attempt_001.json) `/structured_response/organic/2` |
| Q36 / 200 | Facial Expression Video Generation Based-On Spatio-temporal   Convolutional GAN: FEV-GAN / 2210.11182 | 2: Deep learning techniques for identity preservation in video generation | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q36/s02/attempt_001.json) `/structured_response/organic/9` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs / 2406.06385 | 2: Advantages of Quantization-Aware Training in AI | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q40/s02/attempt_001.json) `/structured_response/organic/2` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs / 2406.06385 | 3: Research papers on the impact of Quantization-Aware Training on low-bit weight representations | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q40/s03/attempt_001.json) `/structured_response/organic/2` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs / 2406.06385 | 3: Research papers on the impact of Quantization-Aware Training on low-bit weight representations | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q40/s03/attempt_001.json) `/structured_response/organic/9` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs / 2406.06385 | 5: Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI | 3 / 13 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q40/s05/attempt_001.json) `/structured_response/organic/2` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs / 2406.06385 | 5: Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q40/s05/attempt_001.json) `/structured_response/organic/9` |
| Q41 / 222 | Skywork-Math: Data Scaling Laws for Mathematical Reasoning in Large Language Models -- The Story Goes On / 2407.08348 | 3: Scaling up SFT data with synthesis data | 4 / 14 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q41/s03/attempt_001.json) `/structured_response/organic/3` |
| Q43 / 235 | PDB-Struct: A Comprehensive Benchmark for Structure-based Protein Design / 2312.00080 | 3: Survey papers on protein design using AI | 2 / 12 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q43/s03/attempt_001.json) `/structured_response/organic/1` |
| Q45 / 240 | Panacea+: Panoramic and Controllable Video Generation for Autonomous   Driving / 2408.07605 | 2: Research papers on video generation controllability | 10 / 20 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q45/s02/attempt_001.json) `/structured_response/organic/9` |
| Q46 / 262 | PerAct2: Benchmarking and Learning for Robotic Bimanual Manipulation   Tasks / 2407.00278 | 5: Benchmarks used in robot decision making research | 8 / 18 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q46/s05/attempt_001.json) `/structured_response/organic/7` |
| Q48 / 281 | Automate Strategy Finding with LLM in Quant investment / 2409.06289 | 1: Application of large language models in stock market analysis | 1 / 11 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q48/s01/attempt_001.json) `/structured_response/organic/0` |
| Q48 / 281 | Automate Strategy Finding with LLM in Quant investment / 2409.06289 | 5: Survey papers on large language models in stock exchange analysis | 6 / 16 | [replay](/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911/q48/s05/attempt_001.json) `/structured_response/organic/5` |

完整的 276 条逐 GT 阴性/阳性记录、全部 790 组/791 ID 统计及 248 条请求索引见 [PAGE2_SEARCH_PROBE_001.json](/home/chenyi/pasa/PAGE2_SEARCH_PROBE_001.json)。所有新 replay 均独立保存，冻结 baseline/audit 保持原样。

## Raw response 边界补查

2470 个 organic 中有 7 个不符合当前 URL parser：Q5/s3 的 5 个 Google redirect、Q23/s3 的旧式 ID `cs/9605103`、Q29/s1 的分类目录页。逐项复核未建立额外目标 GT 命中；Q5 redirect 标题显式出现的 `2312.00849` 已在其他可解析结果中覆盖，不增加计数。没有跟随重定向或另发网络请求。对全部 276 个目标逐题检索 organic 原始字段中的 GT ID，未发现“字段里有目标 ID、但未被已计数 URL 证据覆盖”的遗漏；详情保存在 JSON 的 `raw_response_edge_audit`。Q43/s2 返回空 organic，保留为一次有效空结果，未补搜。
