# CRAWLER_SEARCH_MISS 离线 root-cause audit

基线 commit：`fe89b48dd36e7438d74622cff1d430a66193222c`。审计单位为 **283 个 (query, normalized GT title) 对**，不是 283 篇全局唯一论文。覆盖全部 50 题的 query 生成与 248 份 Serper 原始响应。

本阶段仅分析本地保存的结果树、smoke instrumentation、Serper replay/raw JSON、RealScholarQuery GT 的标题及 `answer_arxiv_id`、id2paper 和 ZIP metadata。没有运行 Crawler/Selector、没有网络请求、没有修改 baseline 或提交 Git。新文件仅为本报告及同名 JSONL。

## 结论

- **7 个（2.47%）原 Search miss 实际已有同 GT arXiv ID 节点**，属于标题版本/metadata 导致的阶段归因偏差。其中 6 个已被 Selector 选中，1 个分数未过 0.5。
- 其中 **3 个 GT 已出现在本题 Serper organic 返回中**，并成功保留为 Search 节点；它们没有被 URL parser 或 dedup 丢掉。另 4 个通过 Expand 找到。
- 已证实 `SERPER_RETURNED_BUT_DROPPED`：**0**。原始 response 中出现、进入节点、最终标题评测命中是三个不同事件。
- 剩余 **276 个（97.53%）保留 UNDETERMINED**。有证据的 query 缺陷另列为非互斥诊断，不能用相关性填充根因数量。
- Q28 的 4 条 query 全部省略 HumanEval/MBPP/code_contests；Q48 的 5 条全部省略 factor/alpha/mining。这些文本事实可核验，但没有替代 query 的响应，不能证明对应 GT 必然因此漏检。
- 没有 page 2、更多 top-k、替代 query、搜索引擎索引快照，故不能把“本次未返回”改称 SEARCH_TOPK_MISS 或 INDEXABILITY_SOURCE_ISSUE。

## 证据规则与身份匹配

1. 以 baseline `summary.json` 中的 283 条 CRAWLER_SEARCH_MISS 确定范围；GT JSONL 同一行的 answer 与 answer_arxiv_id 按下标对应。arXiv ID 是本次身份关联依据，未联网核验 GT 本身的映射质量。
2. 对全部 248 份响应检查 raw_response_text SHA-256，并验证 JSON 解析结果与 structured_response 完全相同。扫描每一个字符串字段，不只 organic/title：包括 URL、snippet、date、searchParameters 等。JSONL 保存原始字段值、JSON Pointer、response hash 与路径。
3. 匹配 GT ID（带边界，允许版本号）、GT 原标题、同 ID 本地标题；标题检查分别使用 baseline keep_letters 与多次 HTML unescape + Unicode NFKC + 字母数字归一化。完整标题子串提及不自动算作候选返回；必须区分 organic URL/title 与 snippet 引用。
4. 分别标明本题响应和其他题响应。其他题找到论文只能说明它在那一份已保存响应中可见，不能推断本题应当返回。
5. 重建原 URL parser 的 `arxiv.org/(abs|pdf|html)/现代数字ID` 行为，核对 root.touch_ids 与树节点 ID；同 ID 已有节点直接排除“被 dedup 丢失”。集合转序、线程先后与未记录的失败不能从静态树反演。
6. 每个 miss 保留与本题返回标题最接近的 3 个字符串候选（difflib SequenceMatcher，无模型）。相似度不作为论文身份或根因证据；截断标题、未保存别名仍可能不可识别。
7. 同 ID 标题不同但未形成节点，只记录 metadata variant；只有已有同 ID 节点而原标题评测漏失，才确认为 TITLE_METADATA_MISMATCH 主分类。别名引用出现也不能反推出当时选择了该章节或该父节点被扩展。
8. 阴性检查没有导入项目 utils/models，没有使用网络 SDK 或 GPU。标题相似度 ≥0.8 且没有身份命中的唯一候选是 Q31 的 V-DPO（返回 ID 2411.02712），而 GT Mitigating Multilingual Hallucination 的 ID 为 2408.00550；已保存资料没有两者为同文的证据，未将字符串相似误作返回命中。

## 互斥主分类：数量、比例与证据门槛

| 主分类 | 数量 | 占 283 | 判定或未成立原因 |
|---|---:|---:|---|
| `SERPER_RETURNED_BUT_DROPPED` | 0 | 0.00% | 本题 organic 已建立 GT 身份，但 parser/后续节点流程有可见丢失；本次返回的 3 个 GT 均已成为节点。 |
| `QUERY_COVERAGE_MISS` | 0 | 0.00% | 文本缺项有证据，逐 GT 的因果归因无对照；不升级为已确认主因。 |
| `QUERY_REDUNDANCY` | 0 | 0.00% | 查询及结果重复可以测量，无法证明替换后具体哪个 GT 会命中。 |
| `QUERY_TOO_BROAD` | 0 | 0.00% | 部分 query 省略用户限定可观察，但同题其他 query 仍可能覆盖，不能逐 GT 确认因果。 |
| `QUERY_TOO_NARROW` | 0 | 0.00% | 部分 query 引入子题限制可观察，但子题拆分也可能有益，不能逐 GT 确认因果。 |
| `SEARCH_TOPK_MISS` | 0 | 0.00% | 没有 GT 实际排在第 11 名以后或后续页的记录；未返回不等于排名在 top-k 外。 |
| `TITLE_METADATA_MISMATCH` | 7 | 2.47% | GT ID 已在结果节点，GT 与节点标题经原 keep_letters 不相等。 |
| `INDEXABILITY_SOURCE_ISSUE` | 0 | 0.00% | 所有目标 GT 均有数据集提供的现代 arXiv ID；本地缺 metadata 不等于不被搜索引擎索引。 |
| `UNDETERMINED` | 276 | 97.53% | 已完成字段/ID/标题/节点检查，但本地证据不能唯一解释未返回/未到达的原因。 |

零计数类别没有“已证实代表案例”，不编造案例填表。下面列出的 query 问题是真实观测案例，且明确不计入这些类别的已确认根因数量。

## 7 个被原标题分类误归为 Search miss 的真实案例

| JSONL 行 | Query / GT ID | GT 标题 | 实际节点标题 | 来源 / score |
|---:|---|---|---|---|
| 66 | Q7 / 2402.08268 | World Model on Million-Length Video And Language With Blockwise RingAttention | World Model on Million-Length Video And Language With RingAttention | Expand / 0.920180976 |
| 78 | Q8 / 2401.07382 | Beyond Sparse Rewards: Enhancing Reinforcement Learning with Language   Model Critique in Text Generation | DRLC: Reinforcement Learning with Dense Rewards from LLM Critic | Search / 0.979449153 |
| 133 | Q17 / 2401.14556 | Looking Right is Sometimes Right: Investigating the Capabilities of Decoder-only LLMs for Sequence Labeling | Do Not (Always) Look Right: Investigating the Capabilities of Decoder-Based Large Language Models for Sequence Labeling | Expand / 0.201629505 |
| 138 | Q19 / 2310.07710 | A Resilient and Accessible Distribution-Preserving Watermark for Large   Language Models | DiPmark: A Stealthy, Efficient and Resilient Watermark for Large Language Models | Expand / 0.971225321 |
| 140 | Q19 / 2311.09832 | WatME: Towards Lossless Watermarking Through Lexical Redundancy | X-Mark: Towards Lossless Watermarking Through Lexical Redundancy | Search / 0.996722758 |
| 269 | Q46 / 1909.12271 | RLBench: The Robot Learning Benchmark &amp;amp; Learning Environment | RLBench: The Robot Learning Benchmark & Learning Environment | Expand / 0.996485829 |
| 279 | Q47 / 2402.12659 | FinBen: A Holistic Financial Benchmark for Large Language Models | The FinBen: An Holistic Financial Benchmark for Large Language Models | Search / 0.999138951 |

- **JSONL 第 66 行 / Q7 / 2402.08268**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/0.json)，JSON Pointer `/child/Studies on multi-modal language models for long video understanding/0/child/1 Introduction/1`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
- **JSONL 第 78 行 / Q8 / 2401.07382**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/0.json)，JSON Pointer `/child/Effectiveness of reward shaping methods in training large language models/1`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_003.json) `/structured_response/organic/5`，query 序号 3，position=6，parser ID=`2401.07382`；查询原文：Effectiveness of reward shaping methods in training large language models。
- **JSONL 第 133 行 / Q17 / 2401.14556**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/0.json)，JSON Pointer `/child/Why supervised fine-tuned small language models outperform in-context learning in NER/2/child/1 Motivation and significance/9`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
- **JSONL 第 138 行 / Q19 / 2310.07710**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/0.json)，JSON Pointer `/child/Research on methods to maintain generation quality in LLMs during vocabulary watermarking/1/child/4. Watermarking for LLMs 4.2. Watermarking during Logits Generation/1`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
- **JSONL 第 140 行 / Q19 / 2311.09832**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/0.json)，JSON Pointer `/child/Impact of vocabulary watermarking on LLMs generation quality/0`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/8`，query 序号 4，position=9，parser ID=`2311.09832`；查询原文：Impact of vocabulary watermarking on LLMs generation quality。
- **JSONL 第 269 行 / Q46 / 1909.12271**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/0.json)，JSON Pointer `/child/Benchmark datasets for robot decision making/5/child/6 Related Work/16`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
- **JSONL 第 279 行 / Q47 / 2402.12659**：[结果树](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/0.json)，JSON Pointer `/child/Comparative studies on LLM agent evaluation in financial domain/2`；GT/metadata 差异见 JSONL 的 `metadata_title_variants`。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_001.json) `/structured_response/organic/1`，query 序号 5，position=2，parser ID=`2402.12659`；查询原文：Comparative studies on LLM agent evaluation in financial domain。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_001.json) `/structured_response/organic/4`，query 序号 5，position=5，parser ID=`2402.12659`；查询原文：Comparative studies on LLM agent evaluation in financial domain。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/3`，query 序号 4，position=4，parser ID=`2402.12659`；查询原文：Regulatory and industry-standard benchmarks for evaluating LLM agents in finance。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_003.json) `/structured_response/organic/6`，query 序号 3，position=7，parser ID=`2402.12659`；查询原文：Evaluation metrics for LLM agents in financial tasks。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_004.json) `/structured_response/organic/1`，query 序号 2，position=2，parser ID=`2402.12659`；查询原文：Benchmarking methods for LLM agents in financial tasks。
  - [原始响应记录](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_004.json) `/structured_response/organic/6`，query 序号 2，position=7，parser ID=`2402.12659`；查询原文：Benchmarking methods for LLM agents in financial tasks。

这 7 条不用于改写冻结指标。6 条已选中记录的身份识别修复不会新增实际检索结果；另 1 条是“已经找到但 Selector 未选中”，也不是 Search 失败。不能简单把 7/790 当作新增 Recall 收益。

## 283 条的本地覆盖与其他证据

全部已保存响应包含 2425 条 organic，其中 2424 条 URL 可被原正则解析。唯一不可解析项是 Q43 的 `https://arxiv.org/archive/cs` 分类首页，不是某篇 GT 的论文链接。按每题去重后共 1411 个 Search 候选 ID；最终 baseline 有 1,403 个 Search 节点，差额 8 个并非本次 283 个目标 GT 的已识别返回。此处仅用于核对 Search 流程完整性。

| 观测（非互斥） | GT 对数 | 占 283 |
|---|---:|---:|
| GT ID 在 id2paper 中存在 | 260 | 91.87% |
| GT ID 对应 ZIP metadata 可读 | 259 | 91.52% |
| GT ID 缺少本地 id2paper metadata | 23 | 8.13% |
| 同 ID 本地标题不同于 GT | 22 | 7.77% |
| 已知标题别名出现在本题保存的引用中 | 5 | 1.77% |
| 已知标题别名出现在 unresolved instrumentation 中 | 0 | 0.00% |
| GT ID/完整标题别名出现在其他题的响应字段 | 8 | 2.83% |

仅依赖 normalized GT title 反查会漏掉标题版本变化：本次使用数据集自带 ID 关联，比上一阶段只按标题反查更完整。metadata 缺失、别名引用或他题返回都是证据维度，不代表唯一因果分类。

本地标题不同但不一定是主因的记录：Q1/JSONL:3, Q1/JSONL:5, Q4/JSONL:30, Q4/JSONL:34, Q4/JSONL:43, Q5/JSONL:44, Q6/JSONL:54, Q6/JSONL:56, Q7/JSONL:66, Q7/JSONL:71, Q8/JSONL:78, Q9/JSONL:93, Q13/JSONL:122, Q17/JSONL:133, Q19/JSONL:138, Q19/JSONL:140, Q21/JSONL:153, Q28/JSONL:164, Q38/JSONL:214, Q38/JSONL:215, Q46/JSONL:269, Q47/JSONL:279。
已知标题别名可见引用记录：Q7/JSONL:66, Q17/JSONL:133, Q19/JSONL:138, Q19/JSONL:140, Q46/JSONL:269。原始分类只按 GT exact title 扫描，因此不能据其缺证据断言路径不可达。

### 8 个 GT 在其他题原始响应中的直接可见性

以下是观察到的替代查询候选覆盖证据：它排除了“在本次所有响应中都不可见”的说法，但不能证明原 query 缺哪个词才是唯一原因，也不能借用他题 Selector 分数预测本题结果。

| 目标 Query / JSONL 行 | GT | 他题 Query | 实际返回它的查询原文 | replay 字段 |
|---|---|---|---|---|
| Q4 / 33 | Training Language Models to Self-Correct via Reinforcement Learning | Q13 | Research on self-correction mechanisms in LLMs and their impact on performance | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_001.json) `/structured_response/organic/6/link` |
| Q4 / 43 | AGILE: A Novel Framework of LLM Agents | Q37 | Use of LLM agents in schedule planning studies | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/9/link` |
| Q7 / 74 | VideoAgent: Long-form Video Understanding with Large Language Model as Agent | Q42 | Studies on efficient frame sampling in video comprehension | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/8/link` |
| Q21 / 154 | Relative Preference Optimization: Enhancing LLM Alignment through Contrasting Responses across Identical and Diverse Prompts | Q31 | Survey papers on DPO training for vision-language models | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_005.json) `/structured_response/organic/7/link` |
| Q31 / 173 | Automated Multi-level Preference for MLLMs | Q5 | Role of RLHF in reducing hallucination in multimodal generation | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_001.json) `/structured_response/organic/7/link` |
| Q39 / 219 | DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale   Synthetic Data | Q29 | Advanced techniques to solve IMO level math problems with LLMs | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/6/link` |
| Q40 / 220 | Low-Rank Quantization-Aware Training for LLMs | Q35 | Research on quantization techniques in LLM pretraining | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_002.json) `/structured_response/organic/2/link` |
| Q46 / 274 | Multi-agent Planning using Visual Language Models | Q37 | Language Model agents and their application in schedule planning | [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_001.json) `/structured_response/organic/5/link` |

## Query 问题的非互斥诊断统计

这些数目回答“哪些 query 集合有可验证属性，以及有多少待审 GT 位于这些题中”，**不回答多少 miss 已由该属性造成**。关联 GT 数使用全部原 283 条，可能包括已确认的 7 条 metadata 偏差，类别不能相加。

相似度：词法 token 小写、LLM 与 large language model(s) 合并；content token 再去模板词并做有限复数归并。不是 embedding，也不代表完整语义等价。冗余标记必须同时满足 content Jaccard ≥0.8、该对 query 返回 ID Jaccard ≥0.6；阈值是审计操作定义，不是经验证的最优阈值。
可复算定义：token 正则 `[a-z0-9]+`，Jaccard=`|A∩B|/|A∪B|`。content 去词表：`a an the on of for in with and or to by as that how why all some me using use uses used research researches paper papers survey surveys study studies article articles scholarly academic work works technique techniques method methods approach approaches application applications role impact effects effect influence latest recent advancement advancements exploring exploration investigation investigations`。归并表：`models→model, agents→agent, datasets→dataset, transformers→transformer, videos→video, results→result, languages→language, methods→method, rankings→ranking, finetuning→fine tuning, pretraining→pre training`；最后两者作为单个替换后的 token。每条 query 的最终 content_tokens 已保存。

| 观测类别 | Query 数 / 50 | Query 比例 | 关联 GT 数 / 283 | GT 比例 | Query |
|---|---:|---:|---:|---:|---|
| `QUERY_COVERAGE_MISS`（诊断） | 2 | 4.00% | 4 | 1.41% | Q28, Q48 |
| `QUERY_REDUNDANCY`（诊断） | 7 | 14.00% | 42 | 14.84% | Q2, Q9, Q11, Q16, Q26, Q33, Q34 |
| `QUERY_TOO_BROAD`（诊断） | 13 | 26.00% | 108 | 38.16% | Q3, Q4, Q7, Q8, Q9, Q24, Q25, Q27, Q28, Q43, Q45, Q48, Q49 |
| `QUERY_TOO_NARROW`（诊断） | 7 | 14.00% | 55 | 19.43% | Q4, Q19, Q38, Q39, Q42, Q47, Q48 |

248 条生成查询；Q18/Q28 各 4 条，其余各 5 条。同题完全相同文本重复总数：0。每条查询内部先按 ID 去重后共 2258 个候选槽位，按题再次去重为 1411 个 ID；跨查询重复槽位 847（37.51%）。这里的重复不包括一个 query 内不同 URL/版本的重复，也不等于可回收的新增 GT 数。

### QUERY_COVERAGE_MISS 的真实观测案例（非确认根因）

- **Q28**：用户需求：Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.
  - 全部 4 条均未出现用户明确给出的 HumanEval、MBPP、code_contests 三个难度参照名；泛称 mid-level/middle difficulty 仍被保留。
  - query 1：Survey papers on code evaluation datasets
  - query 2：Middle difficulty level code evaluation datasets
  - query 3：Code evaluation datasets with mid-level hardness
  - query 4：Comparison studies on difficulty levels of different code evaluation datasets
  - 关联真实 miss 示例：PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLM，JSONL 第 164 行 / Q28 / 2401.03855。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q48**：用户需求：Papers that explore using large language models for mining factors in stock exchange analysis.
  - 全部 5 条没有 factor/factors、alpha 或 mining；用户明确要求 mining factors。
  - query 1：Application of large language models in stock market analysis
  - query 2：Role of AI and language models in stock prediction
  - query 3：Impact of large language models on stock exchange analysis
  - query 4：Use of GPT-3 in stock market trend analysis
  - query 5：Survey papers on large language models in stock exchange analysis
  - 关联真实 miss 示例：Automate Strategy Finding with LLM in Quant investment，JSONL 第 281 行 / Q48 / 2409.06289。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。

### QUERY_TOO_BROAD 的真实观测案例（非确认根因）

- **Q24**：用户需求：Show me all research papers on machine translation agents.
  - 该条省略 agent；其他条仍保留 agent。
  - query 3：Survey papers on machine translation
  - 关联真实 miss 示例：Towards Achieving Human Parity on End-to-end Simultaneous Speech   Translation via LLM Agent，JSONL 第 158 行 / Q24 / 2407.21646。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q43**：用户需求：AI for Science papers, especially protein design and DPO of antibody design.
  - 该条没有 protein 或 antibody/DPO。
  - query 4：Application of AI in scientific research papers
  - 关联真实 miss 示例：Diffusion Language Models Are Versatile Protein Learners，JSONL 第 230 行 / Q43 / 2402.18567。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q48**：用户需求：Papers that explore using large language models for mining factors in stock exchange analysis.
  - 该条变为泛化的 AI stock prediction，未保留 factor mining。
  - query 2：Role of AI and language models in stock prediction
  - 关联真实 miss 示例：Automate Strategy Finding with LLM in Quant investment，JSONL 第 281 行 / Q48 / 2409.06289。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。

### QUERY_TOO_NARROW 的真实观测案例（非确认根因）

- **Q19**：用户需求：Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.
  - 引入 word embeddings 和 watermarking attacks 子问题，非用户明确限定。
  - query 3：Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks
  - 关联真实 miss 示例：A Resilient and Accessible Distribution-Preserving Watermark for Large   Language Models，JSONL 第 138 行 / Q19 / 2310.07710。该条仍按证据保留 `TITLE_METADATA_MISMATCH`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q42**：用户需求：Show me research on how to select frames when doing video understanding.
  - 引入 optical flow 子方法，用户未限定实现机制。
  - query 2：Optical flow-based methods for key frame selection in video understanding
  - 关联真实 miss 示例：Frame attention networks for facial expression recognition in videos，JSONL 第 224 行 / Q42 / 1907.00193。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q47**：用户需求：How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents.
  - 引入 regulatory/industry-standard，用户未限定基准来源。
  - query 4：Regulatory and industry-standard benchmarks for evaluating LLM agents in finance
  - 关联真实 miss 示例：FinBen: A Holistic Financial Benchmark for Large Language Models，JSONL 第 279 行 / Q47 / 2402.12659。该条仍按证据保留 `TITLE_METADATA_MISMATCH`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q48**：用户需求：Papers that explore using large language models for mining factors in stock exchange analysis.
  - 该条限定 GPT-3，用户未限定模型系列。
  - query 4：Use of GPT-3 in stock market trend analysis
  - 关联真实 miss 示例：Automate Strategy Finding with LLM in Quant investment，JSONL 第 281 行 / Q48 / 2409.06289。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。

### QUERY_REDUNDANCY 的真实观测案例（非确认根因）

- **Q11**：用户需求：Give me all visual-LLM models that are MoE architecture
  - query 1：MoE architecture models in visual-LLM；query 4：Research on MoE architecture in visual-LLMs。content Jaccard=0.800，response ID Jaccard=0.800，共享 ID 数=8。
  - 关联真实 miss 示例：CuMo: Scaling Multimodal LLM with Co-Upcycled Mixture-of-Experts，JSONL 第 106 行 / Q11 / 2405.05949。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q26**：用户需求：Scaling Laws for Fine-Grained Mixture of Experts.
  - query 1：Survey papers on Scaling Laws for Fine-Grained Mixture of Experts；query 2：Scaling laws in fine-grained mixture of experts model。content Jaccard=0.857，response ID Jaccard=0.750，共享 ID 数=6。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。
- **Q2**：用户需求：List all papers that use autoregressive transformer to generate videos.
  - query 3：Papers on video generation using autoregressive transformer；query 5：Use of autoregressive transformer in video generation papers。content Jaccard=1.000，response ID Jaccard=0.727，共享 ID 数=8。
  - 关联真实 miss 示例：iVideoGPT: Interactive VideoGPTs are Scalable World Models，JSONL 第 10 行 / Q2 / 2405.15223。该条仍按证据保留 `UNDETERMINED`；不能由 query 属性推导可恢复性。
  - 证据：[Crawler 原始输出](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/smoke_report.json)；对应 replay 路径见该题逐条查询及 JSONL。

### SEARCH_TOPK_MISS、INDEXABILITY_SOURCE_ISSUE 与 UNDETERMINED 边界

真实未确定案例：Q0 的 **Automatic Document Selection for Efficient Encoder Pretraining**（ID 2210.10951，JSONL 第 1 行 / Q0 / 2210.10951），本地 metadata 存在，本题已保存响应没有可识别返回，也没有同 ID 节点。这不能证明它排在第 11 名，也不能证明它未被索引；因此两类均不赋值。

## 全部 50 题 query 审计

每题给出原始用户需求、生成顺序、实际请求参数、词法重复与响应重复统计，以及限定/覆盖审阅。原始生成文本保存在 JSONL 的 query_audit.raw_generation（Q25/Q26 无目标 miss，完整信息保留在本报告）。

### Q0 — 5 queries / 2 target misses

用户需求：Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.

文本完全重复：0；content Jaccard 均值/最大值：0.491/0.833；跨查询重复 ID 槽位：22/50（44.00%）；survey 查询数：1。

审阅：保留 smaller/limited dataset、LM pre-training；多条重述同一目标，未展开 pruning/selection/distillation 等方法。后者是 GT 方法词差异，不足以证明必须如此生成 query。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Papers on the effectiveness of smaller datasets in language model pre-training | 10 / 10 | `q=Papers on the effectiveness of smaller datasets in language model pre-training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_005.json) |
| 2 | Advantages of using smaller datasets in large language model pre-training | 10 / 10 | `q=Advantages of using smaller datasets in large language model pre-training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_004.json) |
| 3 | Benefits of limited dataset in pre-training of language models | 10 / 10 | `q=Benefits of limited dataset in pre-training of language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_003.json) |
| 4 | Survey papers on large language model pre-training using smaller dataset | 10 / 10 | `q=Survey papers on large language model pre-training using smaller dataset before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_002.json) |
| 5 | Effects of dataset size on language model pre-training effectiveness | 10 / 10 | `q=Effects of dataset size on language model pre-training effectiveness before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=0.833，response ID Jaccard=0.333。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q1 — 5 queries / 7 target misses

用户需求：Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training.

文本完全重复：0；content Jaccard 均值/最大值：0.581/0.857；跨查询重复 ID 槽位：23/50（46.00%）；survey 查询数：1。

审阅：保留 pre-training 与 in-context learning；mechanism/dynamics/理论解释多以 insights/role 泛述，未拆分梯度下降或 kernel 等机制。不能仅由 GT 方法名缺失判因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on in-context learning in pre-trained language models | 10 / 10 | `q=Survey papers on in-context learning in pre-trained language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_005.json) |
| 2 | In-context learning in pre-training of large language models | 10 / 10 | `q=In-context learning in pre-training of large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_004.json) |
| 3 | Pre-training methods for in-context learning in language models | 10 / 10 | `q=Pre-training methods for in-context learning in language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_003.json) |
| 4 | Insights into the process of pre-training for in-context learning in language models | 10 / 10 | `q=Insights into the process of pre-training for in-context learning in language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_002.json) |
| 5 | Role of pre-training in the development of in-context learning in language models | 10 / 10 | `q=Role of pre-training in the development of in-context learning in language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=0.857，response ID Jaccard=0.429。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q2 — 5 queries / 4 target misses

用户需求：List all papers that use autoregressive transformer to generate videos.

文本完全重复：0；content Jaccard 均值/最大值：0.623/1.000；跨查询重复 ID 槽位：24/48（50.00%）；survey 查询数：0。

审阅：4 条紧贴 autoregressive transformer/video generation；另 1 条转到 editing/composition。没有完全丢失用户核心主题。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Autoregressive transformer models in video generation research papers | 10 / 9 | `q=Autoregressive transformer models in video generation research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on using autoregressive transformers for video editing and composition | 10 / 10 | `q=Research on using autoregressive transformers for video editing and composition before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_004.json) |
| 3 | Papers on video generation using autoregressive transformer | 10 / 10 | `q=Papers on video generation using autoregressive transformer before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on autoregressive transformer in video creation | 10 / 10 | `q=Studies on autoregressive transformer in video creation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_002.json) |
| 5 | Use of autoregressive transformer in video generation papers | 10 / 9 | `q=Use of autoregressive transformer in video generation papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=1.000，response ID Jaccard=0.727。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q3 — 5 queries / 10 target misses

用户需求：I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs. These models should be pre-trained on large-scale datasets, including visual, audio, and audio-visual data. Please exclude survey papers.

文本完全重复：0；content Jaccard 均值/最大值：0.358/0.714；跨查询重复 ID 槽位：11/45（24.44%）；survey 查询数：0。

审阅：4 条覆盖 visual/audio 或 multimodal pretraining；visual/textual 一条漂移。未显式编码 exclude surveys、visual/audio/audio-visual 三种数据来源的完整组合。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Pre-training of multimodal foundation models on large-scale datasets | 7 / 5 | `q=Pre-training of multimodal foundation models on large-scale datasets before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on audio-visual pretraining in multimodal foundation models | 10 / 10 | `q=Research on audio-visual pretraining in multimodal foundation models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_004.json) |
| 3 | Multimodal foundation models for visual and audio inputs | 10 / 10 | `q=Multimodal foundation models for visual and audio inputs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_003.json) |
| 4 | Foundation models supporting visual and audio inputs | 10 / 10 | `q=Foundation models supporting visual and audio inputs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_002.json) |
| 5 | Research on Large Multimodal Models (LMMs) for integrating visual and textual data | 10 / 10 | `q=Research on Large Multimodal Models (LMMs) for integrating visual and textual data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 3，content Jaccard=0.714，response ID Jaccard=0.333。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q4 — 5 queries / 20 target misses

用户需求：Provide me with all papers that discuss reinforcement learning training for Large Language Model agent tasks.

文本完全重复：0；content Jaccard 均值/最大值：0.489/0.667；跨查询重复 ID 槽位：17/50（34.00%）；survey 查询数：1。

审阅：3 条明确 LLM agents + RL；另有泛 RL survey 和 task-agnostic rewards 子题。agent 在整个 query 集合中没有丢失。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on reinforcement learning training for large language models | 10 / 10 | `q=Survey papers on reinforcement learning training for large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on task-agnostic rewards in reinforcement learning training for large language models | 10 / 10 | `q=Research on task-agnostic rewards in reinforcement learning training for large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_004.json) |
| 3 | Reinforcement learning approaches for optimizing Large Language Model agents | 10 / 10 | `q=Reinforcement learning approaches for optimizing Large Language Model agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_003.json) |
| 4 | Case studies of Large Language Model agents trained using reinforcement learning | 10 / 10 | `q=Case studies of Large Language Model agents trained using reinforcement learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_002.json) |
| 5 | Experiences in training Large Language Model agents using reinforcement learning | 10 / 10 | `q=Experiences in training Large Language Model agents using reinforcement learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 5，content Jaccard=0.667，response ID Jaccard=0.053。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q5 — 5 queries / 1 target misses

用户需求：Papers that apply RLHF to address the hallucination problem in image and video description.

文本完全重复：0；content Jaccard 均值/最大值：0.295/0.600；跨查询重复 ID 槽位：14/49（28.57%）；survey 查询数：1。

审阅：image/video/RLHF 均有分配，部分条保留 hallucination；没有证据表明整个需求被遗漏。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on RLHF for image description | 10 / 10 | `q=Survey papers on RLHF for image description before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_005.json) |
| 2 | Application of RLHF in video description | 10 / 10 | `q=Application of RLHF in video description before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_004.json) |
| 3 | Use of RLHF in addressing hallucination in video content | 10 / 10 | `q=Use of RLHF in addressing hallucination in video content before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_003.json) |
| 4 | Impact of RLHF on hallucination issue in image description | 10 / 10 | `q=Impact of RLHF on hallucination issue in image description before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_002.json) |
| 5 | Role of RLHF in reducing hallucination in multimodal generation | 10 / 9 | `q=Role of RLHF in reducing hallucination in multimodal generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 4，content Jaccard=0.600，response ID Jaccard=0.000。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q6 — 5 queries / 14 target misses

用户需求：Papers that propose methods based on large language models and evaluate their performance through experiments on the HotPotQA dataset.

文本完全重复：0；content Jaccard 均值/最大值：0.395/0.667；跨查询重复 ID 槽位：31/50（62.00%）；survey 查询数：1。

审阅：每条都保留 HotPotQA；LLM methods/experiments/evaluation 有交叠。未点名 RAG/decomposition/planning 不能单独判定 coverage miss。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Large language model based methods for HotPotQA dataset | 10 / 10 | `q=Large language model based methods for HotPotQA dataset before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on evaluation methods for Large Language Models on HotPotQA dataset | 10 / 10 | `q=Research on evaluation methods for Large Language Models on HotPotQA dataset before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on methods using large language models for HotPotQA | 10 / 10 | `q=Survey papers on methods using large language models for HotPotQA before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_003.json) |
| 4 | Experiments on the HotPotQA dataset for language models | 10 / 10 | `q=Experiments on the HotPotQA dataset for language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_002.json) |
| 5 | Proposed methods for HotPotQA using large language models | 10 / 10 | `q=Proposed methods for HotPotQA using large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=0.667，response ID Jaccard=0.429。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q7 — 5 queries / 19 target misses

用户需求：Show me research on the long video description. Here, long videos are defined as those with a duration of at least several minutes.

文本完全重复：0；content Jaccard 均值/最大值：0.458/1.000；跨查询重复 ID 槽位：10/42（23.81%）；survey 查询数：1。

审阅：description 与 understanding/summarization 混合；保留 long/long-duration，但没有 several minutes 数值界限。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on long video description techniques | 10 / 8 | `q=Survey papers on long video description techniques before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on automatic video summarization for long videos | 10 / 9 | `q=Research on automatic video summarization for long videos before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_004.json) |
| 3 | Long video description research papers | 10 / 9 | `q=Long video description research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on multi-modal language models for long video understanding | 10 / 8 | `q=Studies on multi-modal language models for long video understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_002.json) |
| 5 | Research on long-duration video description | 10 / 8 | `q=Research on long-duration video description before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=1.000，response ID Jaccard=0.214。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q8 — 5 queries / 5 target misses

用户需求：Do you know some papers about using reward shaping methods to train large language model agent.

文本完全重复：0；content Jaccard 均值/最大值：0.252/0.800；跨查询重复 ID 槽位：14/36（38.89%）；survey 查询数：0。

审阅：3 条保留 reward shaping，其中 1 条含 agent；另有 self-rewarding 和 extrinsic reward alignment，主题有漂移但没有整体遗漏。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Reward shaping techniques in large language model training | 10 / 9 | `q=Reward shaping techniques in large language model training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_005.json) |
| 2 | Application of reward shaping in language model agent training | 10 / 10 | `q=Application of reward shaping in language model agent training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_004.json) |
| 3 | Effectiveness of reward shaping methods in training large language models | 10 / 10 | `q=Effectiveness of reward shaping methods in training large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on using small extrinsic rewards for aligning large language models with user intent | 7 / 4 | `q=Research on using small extrinsic rewards for aligning large language models with user intent before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_002.json) |
| 5 | Exploring the use of self-rewarding mechanisms in training large language models | 7 / 3 | `q=Exploring the use of self-rewarding mechanisms in training large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=0.800，response ID Jaccard=0.583。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q9 — 5 queries / 19 target misses

用户需求：Give me papers about how to rank search results by the use of LLM.

文本完全重复：0；content Jaccard 均值/最大值：0.584/1.000；跨查询重复 ID 槽位：15/39（38.46%）；survey 查询数：1。

审阅：4 条保留 search-result ranking；1 条只有 ranking mechanisms。多条同义重述，未显式 reranking/passages，但不能由此证明漏检原因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Use of LLM in ranking search results | 10 / 9 | `q=Use of LLM in ranking search results before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_005.json) |
| 2 | Influence of LLM on search result rankings | 10 / 8 | `q=Influence of LLM on search result rankings before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on ranking search results with Language Model | 10 / 10 | `q=Survey papers on ranking search results with Language Model before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_003.json) |
| 4 | Application of LLM in search result ranking | 10 / 7 | `q=Application of LLM in search result ranking before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_002.json) |
| 5 | Ranking mechanisms in Large Language Models | 7 / 5 | `q=Ranking mechanisms in Large Language Models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.308。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q10 — 5 queries / 4 target misses

用户需求：Is there any work that analyzes the scaling law of the multi-module models, such as video-text, image-text models?

文本完全重复：0；content Jaccard 均值/最大值：0.360/0.571；跨查询重复 ID 槽位：13/46（28.26%）；survey 查询数：1。

审阅：image-text/video-text/multimodal scaling 都被覆盖；部分 query 聚焦 text-to-video 或 transformer 子类。multi-module 原词也保留。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on scaling law of multi-module models | 10 / 9 | `q=Survey papers on scaling law of multi-module models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_005.json) |
| 2 | Analysis of scaling law in video-text models | 10 / 9 | `q=Analysis of scaling law in video-text models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on scaling law in image-text models | 10 / 9 | `q=Research on scaling law in image-text models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_003.json) |
| 4 | Scaling behavior of multi-modal transformer models in video-text tasks | 10 / 10 | `q=Scaling behavior of multi-modal transformer models in video-text tasks before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_002.json) |
| 5 | Empirical studies on the scaling laws of text-to-video generation models | 10 / 9 | `q=Empirical studies on the scaling laws of text-to-video generation models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 3，content Jaccard=0.571，response ID Jaccard=0.200。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q11 — 5 queries / 7 target misses

用户需求：Give me all visual-LLM models that are MoE architecture

文本完全重复：0；content Jaccard 均值/最大值：0.667/1.000；跨查询重复 ID 槽位：29/44（65.91%）；survey 查询数：1。

审阅：全部保留 visual/multimodal LLM 与 MoE；没有整体关键概念缺失。模型架构别名未展开属于后续假设。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | MoE architecture models in visual-LLM | 10 / 9 | `q=MoE architecture models in visual-LLM before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_005.json) |
| 2 | Survey papers on visual-LLM models with MoE architecture | 10 / 8 | `q=Survey papers on visual-LLM models with MoE architecture before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_004.json) |
| 3 | Multi-Modal Large Language Models with MoE architecture | 10 / 8 | `q=Multi-Modal Large Language Models with MoE architecture before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on MoE architecture in visual-LLMs | 10 / 9 | `q=Research on MoE architecture in visual-LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_002.json) |
| 5 | Objectives of visual-LLM models using MoE architecture | 10 / 10 | `q=Objectives of visual-LLM models using MoE architecture before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.308。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q12 — 5 queries / 5 target misses

用户需求：What papers discuss the use of transformer architecture in 3d video generation

文本完全重复：0；content Jaccard 均值/最大值：0.524/0.667；跨查询重复 ID 槽位：10/43（23.26%）；survey 查询数：0。

审阅：全部保留 3D/video/transformer；多条同义重述。GT 中 motion/dance/animation 未被展开，但用户本身也未列这些子类。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Use of transformer model in 3D video production | 10 / 9 | `q=Use of transformer model in 3D video production before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on 3D video generation using transformer architecture | 7 / 5 | `q=Research on 3D video generation using transformer architecture before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_004.json) |
| 3 | Papers on transformer-based methods in 3D video generation | 10 / 10 | `q=Papers on transformer-based methods in 3D video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_003.json) |
| 4 | Transformer architecture application in 3D video creation | 10 / 10 | `q=Transformer architecture application in 3D video creation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_002.json) |
| 5 | Exploration of transformer architecture for 3D video synthesis | 10 / 9 | `q=Exploration of transformer architecture for 3D video synthesis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 3，content Jaccard=0.667，response ID Jaccard=0.000。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q13 — 5 queries / 5 target misses

用户需求：Provide papers demonstrating that the self-correction of LLMs does not enhance their performance.

文本完全重复：0；content Jaccard 均值/最大值：0.379/0.667；跨查询重复 ID 槽位：24/46（52.17%）；survey 查询数：1。

审阅：包含 ineffectiveness、limitations、not enhancing 等负面结论，也有中性的 impact 查询；没有丢失整个否定方向。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Studies on the limitations of self-correction in language models | 10 / 9 | `q=Studies on the limitations of self-correction in language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_005.json) |
| 2 | Impact of self-correction on language model performance | 10 / 10 | `q=Impact of self-correction on language model performance before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on self-correction not enhancing LLM performance | 10 / 9 | `q=Survey papers on self-correction not enhancing LLM performance before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_003.json) |
| 4 | Academic papers on the ineffectiveness of self-correction in LLMs | 10 / 9 | `q=Academic papers on the ineffectiveness of self-correction in LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_002.json) |
| 5 | Research on self-correction mechanisms in LLMs and their impact on performance | 10 / 9 | `q=Research on self-correction mechanisms in LLMs and their impact on performance before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.667，response ID Jaccard=0.267。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q14 — 5 queries / 3 target misses

用户需求：Find papers that use LLMs or LLM-based agents to automatically write surveys or summaries for multiple scholarly documents.

文本完全重复：0；content Jaccard 均值/最大值：0.159/0.375；跨查询重复 ID 槽位：3/37（8.11%）；survey 查询数：2。

审阅：覆盖 automatic survey、literature review、multi-document summary、LLM agents；enterprise/scientific 等 GT 场景不能倒推必须添加。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Use of LLMs in automatic survey writing | 10 / 10 | `q=Use of LLMs in automatic survey writing before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_005.json) |
| 2 | Survey papers on the use of LLMs in scholarly document summarization | 7 / 4 | `q=Survey papers on the use of LLMs in scholarly document summarization before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_004.json) |
| 3 | Papers on LLM-based agents for writing summaries of scholarly articles | 10 / 9 | `q=Papers on LLM-based agents for writing summaries of scholarly articles before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on using language models for automatic synthesis of literature reviews | 7 / 5 | `q=Research on using language models for automatic synthesis of literature reviews before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_002.json) |
| 5 | Articles on the application of LLM-based agents in multi-document summary | 10 / 9 | `q=Articles on the application of LLM-based agents in multi-document summary before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=0.375，response ID Jaccard=0.125。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q15 — 5 queries / 1 target misses

用户需求：Provide papers claiming that reinforcement learning can negatively impact the performance of supervised fine-tuned LLMs.

文本完全重复：0；content Jaccard 均值/最大值：0.472/0.667；跨查询重复 ID 槽位：19/48（39.58%）；survey 查询数：1。

审阅：至少两条保留 negative/downsides，其他条较中性；RL/SFT/LLM 均覆盖。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on negative impacts of reinforcement learning on supervised fine-tuned LLMs | 10 / 10 | `q=Survey papers on negative impacts of reinforcement learning on supervised fine-tuned LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_005.json) |
| 2 | Implications of Reinforcement Learning on Supervised Fine-Tuning in Language Models | 10 / 10 | `q=Implications of Reinforcement Learning on Supervised Fine-Tuning in Language Models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_004.json) |
| 3 | Effects of reinforcement learning on fine-tuned language models | 10 / 9 | `q=Effects of reinforcement learning on fine-tuned language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_003.json) |
| 4 | Downsides of reinforcement learning in supervised fine-tuned LLMs | 10 / 9 | `q=Downsides of reinforcement learning in supervised fine-tuned LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_002.json) |
| 5 | Impact of reinforcement learning on performance of fine-tuned LLMs | 10 / 10 | `q=Impact of reinforcement learning on performance of fine-tuned LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 4，content Jaccard=0.667，response ID Jaccard=0.188。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q16 — 5 queries / 3 target misses

用户需求：Find papers on trigger-free document-level event extraction methods that do not use human-annotated triggers.

文本完全重复：0；content Jaccard 均值/最大值：0.545/1.000；跨查询重复 ID 槽位：24/48（50.00%）；survey 查询数：1。

审阅：trigger-free/without triggers/document-level 均出现，human-annotated 有单独 query；核心要求得到覆盖。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Document-level event extraction without triggers research papers | 10 / 10 | `q=Document-level event extraction without triggers research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_005.json) |
| 2 | Papers on event extraction methods without triggers | 10 / 10 | `q=Papers on event extraction methods without triggers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on trigger-free document-level event extraction | 10 / 9 | `q=Survey papers on trigger-free document-level event extraction before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_003.json) |
| 4 | Research articles on document-level event extraction without triggers | 10 / 9 | `q=Research articles on document-level event extraction without triggers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_002.json) |
| 5 | Studies on event extraction techniques without human-annotated triggers | 10 / 10 | `q=Studies on event extraction techniques without human-annotated triggers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 4，content Jaccard=1.000，response ID Jaccard=0.727。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q17 — 5 queries / 4 target misses

用户需求：Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

文本完全重复：0；content Jaccard 均值/最大值：0.359/0.538；跨查询重复 ID 槽位：19/49（38.78%）；survey 查询数：0。

审阅：ICL vs supervised fine-tuning、small model、information extraction、NER 得到覆盖；未点名 RE/EE，但 information extraction 作为上位概念仍保留。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Performance comparison of in-context learning and supervised fine-tuning in language models for information extraction | 10 / 10 | `q=Performance comparison of in-context learning and supervised fine-tuning in language models for information extraction before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_005.json) |
| 2 | Limitations of in-context learning in language models for information extraction | 10 / 10 | `q=Limitations of in-context learning in language models for information extraction before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_004.json) |
| 3 | In-context learning vs supervised fine-tuning in LLMs for information extraction | 10 / 10 | `q=In-context learning vs supervised fine-tuning in LLMs for information extraction before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_003.json) |
| 4 | Why supervised fine-tuned small language models outperform in-context learning in NER | 10 / 9 | `q=Why supervised fine-tuned small language models outperform in-context learning in NER before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_002.json) |
| 5 | Impact of parameter size on the performance of in-context learning versus supervised fine-tuning in large language models | 10 / 10 | `q=Impact of parameter size on the performance of in-context learning versus supervised fine-tuning in large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=0.538，response ID Jaccard=0.429。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q18 — 4 queries / 4 target misses

用户需求：Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

文本完全重复：0；content Jaccard 均值/最大值：0.273/0.444；跨查询重复 ID 槽位：7/40（17.50%）；survey 查询数：0。

审阅：仅生成 4 条；zero-shot/detection/LLM-generated text 与 supervised comparison 均覆盖；不能据少 1 条推断哪个 GT 本可命中。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection | 10 / 10 | `q=Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_004.json) |
| 2 | Zero-shot detection of LLM-generated content | 10 / 10 | `q=Zero-shot detection of LLM-generated content before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_003.json) |
| 3 | Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text | 10 / 10 | `q=Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_002.json) |
| 4 | Evaluation of LLM-generated text in zero-shot scenarios | 10 / 10 | `q=Evaluation of LLM-generated text in zero-shot scenarios before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=0.444，response ID Jaccard=0.111。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q19 — 5 queries / 12 target misses

用户需求：Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.

文本完全重复：0；content Jaccard 均值/最大值：0.466/0.714；跨查询重复 ID 槽位：28/49（57.14%）；survey 查询数：1。

审阅：多数条保留 watermarking/generation quality；word embeddings/attacks 为额外子问题。词汇水印的各方法名未出现不构成独立因果证据。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on protecting generation quality of LLMs under vocabulary watermarking | 10 / 9 | `q=Survey papers on protecting generation quality of LLMs under vocabulary watermarking before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on methods to maintain generation quality in LLMs during vocabulary watermarking | 10 / 10 | `q=Research on methods to maintain generation quality in LLMs during vocabulary watermarking before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_004.json) |
| 3 | Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks | 10 / 10 | `q=Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_003.json) |
| 4 | Impact of vocabulary watermarking on LLMs generation quality | 10 / 10 | `q=Impact of vocabulary watermarking on LLMs generation quality before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_002.json) |
| 5 | Techniques to mitigate vocabulary watermarking effects on LLM generation | 10 / 10 | `q=Techniques to mitigate vocabulary watermarking effects on LLM generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 4，content Jaccard=0.714，response ID Jaccard=0.462。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q20 — 5 queries / 3 target misses

用户需求：Find papers supporting the claim that knowledgeable LLMs have sufficient inductive capacity to analyze the relationships between multiple papers and systematically write a survey on them.

文本完全重复：0；content Jaccard 均值/最大值：0.094/0.333；跨查询重复 ID 槽位：10/46（21.74%）；survey 查询数：1。

审阅：multiple papers/analysis/systematic review/inductive capacity 有分配；主要词义保留，部分 query 使用 AI 而非 LLM。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on inductive capacity of language models | 10 / 10 | `q=Survey papers on inductive capacity of language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on the impact of large language models on academic literature review | 10 / 8 | `q=Research on the impact of large language models on academic literature review before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_004.json) |
| 3 | Scholarly articles on the analysis of multiple papers by LLMs | 10 / 9 | `q=Scholarly articles on the analysis of multiple papers by LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_003.json) |
| 4 | Papers on systematic review writing by AI models | 10 / 9 | `q=Papers on systematic review writing by AI models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_002.json) |
| 5 | LLMs and their ability to analyze multiple research papers | 10 / 10 | `q=LLMs and their ability to analyze multiple research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=0.333，response ID Jaccard=0.357。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q21 — 5 queries / 2 target misses

用户需求：Search for papers related to large language models that demonstrate how the same prompt with different responses can improve the performance of the SFT model.

文本完全重复：0；content Jaccard 均值/最大值：0.272/0.333；跨查询重复 ID 槽位：10/44（22.73%）；survey 查询数：1。

审阅：保留 same prompt/different responses/SFT，另有 prompt engineering 和 different response prompts 的关系模糊化；核心关系至少在一条明确保留。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Papers on enhancing SFT model performance with different response prompts | 10 / 10 | `q=Papers on enhancing SFT model performance with different response prompts before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on the impact of diverse responses on the performance of SFT models | 10 / 10 | `q=Research on the impact of diverse responses on the performance of SFT models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on the use of varied responses to a single prompt in large language models for SFT | 7 / 4 | `q=Survey papers on the use of varied responses to a single prompt in large language models for SFT before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on how different responses to the same prompt affect SFT model | 10 / 10 | `q=Studies on how different responses to the same prompt affect SFT model before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_002.json) |
| 5 | Prompt engineering methods for improving SFT model performance in large language models | 10 / 10 | `q=Prompt engineering methods for improving SFT model performance in large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.333，response ID Jaccard=0.053。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q22 — 5 queries / 1 target misses

用户需求：Papers on solving common sense problems in machine translation.

文本完全重复：0；content Jaccard 均值/最大值：0.466/0.714；跨查询重复 ID 槽位：20/50（40.00%）；survey 查询数：1。

审阅：全部保留 machine translation 与 common sense/commonsense；没有整体概念遗漏。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Machine translation challenges in commonsense reasoning | 10 / 10 | `q=Machine translation challenges in commonsense reasoning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_005.json) |
| 2 | Algorithms used in solving common sense problems in machine translation | 10 / 10 | `q=Algorithms used in solving common sense problems in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_004.json) |
| 3 | Improving common sense in machine translation | 10 / 10 | `q=Improving common sense in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_003.json) |
| 4 | Research articles on machine translation and common sense issues | 10 / 10 | `q=Research articles on machine translation and common sense issues before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_002.json) |
| 5 | Survey papers on common sense problems in machine translation | 10 / 10 | `q=Survey papers on common sense problems in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 5，content Jaccard=0.714，response ID Jaccard=0.111。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q23 — 5 queries / 2 target misses

用户需求：Show me papers utilizing reinforcement learning to optimize diffusion models for video generation.

文本完全重复：0；content Jaccard 均值/最大值：0.555/0.714；跨查询重复 ID 槽位：21/47（44.68%）；survey 查询数：1。

审阅：RL、diffusion、video generation 均覆盖；多条为重述。未出现 human feedback/reward gradients 只构成术语扩展候选。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Papers on diffusion models for video generation optimized with reinforcement learning | 10 / 9 | `q=Papers on diffusion models for video generation optimized with reinforcement learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on reinforcement learning techniques in video diffusion models optimization | 10 / 9 | `q=Research on reinforcement learning techniques in video diffusion models optimization before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on reinforcement learning optimization in video generation | 10 / 10 | `q=Survey papers on reinforcement learning optimization in video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on video synthesis using reinforcement learning in diffusion models | 10 / 10 | `q=Studies on video synthesis using reinforcement learning in diffusion models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_002.json) |
| 5 | Use of reinforcement learning in optimizing diffusion models for video production | 10 / 9 | `q=Use of reinforcement learning in optimizing diffusion models for video production before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=0.714，response ID Jaccard=0.267。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q24 — 5 queries / 2 target misses

用户需求：Show me all research papers on machine translation agents.

文本完全重复：0；content Jaccard 均值/最大值：0.717/1.000；跨查询重复 ID 槽位：16/47（34.04%）；survey 查询数：1。

审阅：3 条保留 agents，2 条退化为 general MT/ML in MT；speech/simultaneous 等未展开不能确认为 GT 漏检原因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Machine translation agents research papers | 10 / 10 | `q=Machine translation agents research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_005.json) |
| 2 | Papers on machine translation using agents | 10 / 8 | `q=Papers on machine translation using agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on machine translation | 10 / 9 | `q=Survey papers on machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on machine learning in machine translation | 10 / 10 | `q=Research on machine learning in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_002.json) |
| 5 | Latest advancements in machine translation agents | 10 / 10 | `q=Latest advancements in machine translation agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.500。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q25 — 5 queries / 0 target misses

用户需求：Video aesthetics score, using multimodal large models.

文本完全重复：0；content Jaccard 均值/最大值：0.295/0.667；跨查询重复 ID 槽位：14/47（29.79%）；survey 查询数：1。

审阅：aesthetics 在部分条保留，另有 quality/analysis/scoring 泛化；本题没有目标 283 中的 miss，仍完整审计 query 集。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Multimodal large models for video analysis | 10 / 8 | `q=Multimodal large models for video analysis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_005.json) |
| 2 | Use of multimodal large models in video scoring | 10 / 9 | `q=Use of multimodal large models in video scoring before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on video aesthetics score using multimodal models | 10 / 10 | `q=Survey papers on video aesthetics score using multimodal models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_003.json) |
| 4 | Multimodal machine learning for video aesthetics | 10 / 10 | `q=Multimodal machine learning for video aesthetics before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_002.json) |
| 5 | Large language models in video quality assessment | 10 / 10 | `q=Large language models in video quality assessment before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.667，response ID Jaccard=0.308。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q26 — 5 queries / 0 target misses

用户需求：Scaling Laws for Fine-Grained Mixture of Experts.

文本完全重复：0；content Jaccard 均值/最大值：0.539/0.857；跨查询重复 ID 槽位：22/38（57.89%）；survey 查询数：1。

审阅：scaling law/fine-grained/MoE 在部分条完整保留，另有参数扩展子类；本题没有目标 miss。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on Scaling Laws for Fine-Grained Mixture of Experts | 9 / 7 | `q=Survey papers on Scaling Laws for Fine-Grained Mixture of Experts before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_005.json) |
| 2 | Scaling laws in fine-grained mixture of experts model | 10 / 7 | `q=Scaling laws in fine-grained mixture of experts model before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_004.json) |
| 3 | Influence of mixture of experts on scaling laws | 10 / 7 | `q=Influence of mixture of experts on scaling laws before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_003.json) |
| 4 | Examination of the impact of parameter increase on performance scaling in Fine-Grained Mixture of Experts | 10 / 9 | `q=Examination of the impact of parameter increase on performance scaling in Fine-Grained Mixture of Experts before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_002.json) |
| 5 | Optimization of mixture of experts model using scaling laws | 10 / 8 | `q=Optimization of mixture of experts model using scaling laws before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.857，response ID Jaccard=0.750。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q27 — 5 queries / 4 target misses

用户需求：Show me research on rejection sampling finetuning.

文本完全重复：0；content Jaccard 均值/最大值：0.554/1.000；跨查询重复 ID 槽位：20/45（44.44%）；survey 查询数：1。

审阅：部分条是 rejection sampling finetuning，部分只讨论 sampling optimization 或反向关系；主题覆盖不均。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on rejection sampling fine-tuning | 10 / 8 | `q=Survey papers on rejection sampling fine-tuning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_005.json) |
| 2 | Research articles on fine-tuning techniques in rejection sampling | 10 / 9 | `q=Research articles on fine-tuning techniques in rejection sampling before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_004.json) |
| 3 | Academic studies on rejection sampling optimization | 10 / 10 | `q=Academic studies on rejection sampling optimization before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_003.json) |
| 4 | Rejection sampling fine-tuning in machine learning | 10 / 8 | `q=Rejection sampling fine-tuning in machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_002.json) |
| 5 | Studies on improving rejection sampling efficiency in fine-tuning | 10 / 10 | `q=Studies on improving rejection sampling efficiency in fine-tuning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.545。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q28 — 4 queries / 2 target misses

用户需求：Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

文本完全重复：0；content Jaccard 均值/最大值：0.446/0.500；跨查询重复 ID 槽位：10/38（26.32%）；survey 查询数：1。

审阅：仅 4 条；保留 middle difficulty，全部缺少 HumanEval/MBPP/code_contests 明确参照。这是可直接核验的命名约束遗漏，非已证明的检索因果。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on code evaluation datasets | 10 / 9 | `q=Survey papers on code evaluation datasets before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_004.json) |
| 2 | Middle difficulty level code evaluation datasets | 10 / 9 | `q=Middle difficulty level code evaluation datasets before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_003.json) |
| 3 | Code evaluation datasets with mid-level hardness | 10 / 10 | `q=Code evaluation datasets with mid-level hardness before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_002.json) |
| 4 | Comparison studies on difficulty levels of different code evaluation datasets | 10 / 10 | `q=Comparison studies on difficulty levels of different code evaluation datasets before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.500，response ID Jaccard=0.200。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q29 — 5 queries / 3 target misses

用户需求：Research on teaching llms to do math prove and solve IMO level math problems.

文本完全重复：0；content Jaccard 均值/最大值：0.149/0.625；跨查询重复 ID 槽位：14/42（33.33%）；survey 查询数：1。

审阅：math proof 与 IMO 问题均有分支，部分条泛化 machine learning；未观察到整个需求缺失。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on teaching language models mathematics | 10 / 8 | `q=Survey papers on teaching language models mathematics before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on solving IMO level math problems using LLMs | 10 / 8 | `q=Research on solving IMO level math problems using LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_004.json) |
| 3 | Methods to teach language models mathematical proof | 10 / 10 | `q=Methods to teach language models mathematical proof before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_003.json) |
| 4 | Advanced techniques to solve IMO level math problems with LLMs | 10 / 8 | `q=Advanced techniques to solve IMO level math problems with LLMs before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_002.json) |
| 5 | Machine learning approaches for solving IMO problems | 10 / 8 | `q=Machine learning approaches for solving IMO problems before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=0.625，response ID Jaccard=0.455。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q30 — 5 queries / 1 target misses

用户需求：I would like to find some research papers about test time training topic, in LLM research area.

文本完全重复：0；content Jaccard 均值/最大值：0.608/1.000；跨查询重复 ID 槽位：19/46（41.30%）；survey 查询数：1。

审阅：全部保留 test-time training 和 LM/LLM；online learning 作为子题。GT 含 vision-language 与用户 LLM 边界，不能据此认定 query 错误。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on test time training in language models | 10 / 10 | `q=Survey papers on test time training in language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_005.json) |
| 2 | Test-time training techniques in large language models | 10 / 8 | `q=Test-time training techniques in large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_004.json) |
| 3 | Advancements in test time training for language models | 10 / 10 | `q=Advancements in test time training for language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_003.json) |
| 4 | LLM research on test time training | 10 / 9 | `q=LLM research on test time training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_002.json) |
| 5 | Online learning techniques for test-time training in large language models | 10 / 9 | `q=Online learning techniques for test-time training in large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=1.000，response ID Jaccard=0.176。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q31 — 5 queries / 4 target misses

用户需求：DPO training for large-scale vision-language models.

文本完全重复：0；content Jaccard 均值/最大值：0.761/1.000；跨查询重复 ID 槽位：21/44（47.73%）；survey 查询数：1。

审阅：DPO 与 vision-language 均保留，条目按 challenges/effects/comparison 重述；没有整体概念缺失。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on DPO training for vision-language models | 10 / 10 | `q=Survey papers on DPO training for vision-language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_005.json) |
| 2 | Effects of DPO training on large-scale vision-language models | 10 / 10 | `q=Effects of DPO training on large-scale vision-language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_004.json) |
| 3 | Comparative studies on DPO and other methods for training large-scale vision-language models | 7 / 5 | `q=Comparative studies on DPO and other methods for training large-scale vision-language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_003.json) |
| 4 | Application of DPO in large-scale vision-language model training | 10 / 9 | `q=Application of DPO in large-scale vision-language model training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_002.json) |
| 5 | Challenges in DPO training for large-scale vision-language models | 10 / 10 | `q=Challenges in DPO training for large-scale vision-language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=1.000，response ID Jaccard=0.462。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q32 — 5 queries / 10 target misses

用户需求：Show me cutting edge research works on neural network based quantum Monte Carlo.

文本完全重复：0；content Jaccard 均值/最大值：0.654/1.000；跨查询重复 ID 槽位：18/41（43.90%）；survey 查询数：1。

审阅：全部保留 neural network/quantum Monte Carlo；recent/state-of-the-art 也出现。只是 CS/arXiv 搜索条件不足以证明这些 GT 不可索引。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Application of neural networks in quantum Monte Carlo studies | 10 / 10 | `q=Application of neural networks in quantum Monte Carlo studies before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_005.json) |
| 2 | Neural network based quantum Monte Carlo papers | 10 / 9 | `q=Neural network based quantum Monte Carlo papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_004.json) |
| 3 | Recent advancements in quantum Monte Carlo using neural networks | 7 / 4 | `q=Recent advancements in quantum Monte Carlo using neural networks before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_003.json) |
| 4 | Survey papers on neural network based quantum Monte Carlo | 10 / 10 | `q=Survey papers on neural network based quantum Monte Carlo before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_002.json) |
| 5 | State-of-the-art research in neural network quantum Monte Carlo | 10 / 8 | `q=State-of-the-art research in neural network quantum Monte Carlo before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=1.000，response ID Jaccard=0.000。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q33 — 5 queries / 6 target misses

用户需求：Show me some popular papers on generating textual adversarial examples for machine translation.

文本完全重复：0；content Jaccard 均值/最大值：0.587/1.000；跨查询重复 ID 槽位：25/50（50.00%）；survey 查询数：1。

审阅：machine translation/adversarial/textual 均覆盖；popular 被替换成 state-of-the-art，具体攻击方法未拆分只是候选方向。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on textual adversarial examples in machine translation | 10 / 10 | `q=Survey papers on textual adversarial examples in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_005.json) |
| 2 | Textual adversarial examples in machine translation research papers | 10 / 10 | `q=Textual adversarial examples in machine translation research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_004.json) |
| 3 | Adversarial example creation in machine translation using textual methods | 10 / 10 | `q=Adversarial example creation in machine translation using textual methods before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_003.json) |
| 4 | State-of-the-art techniques for generating adversarial examples in machine translation | 10 / 10 | `q=State-of-the-art techniques for generating adversarial examples in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_002.json) |
| 5 | Methods for generating adversarial examples in machine translation | 10 / 10 | `q=Methods for generating adversarial examples in machine translation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.667。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q34 — 5 queries / 3 target misses

用户需求：Show me research on 3d scene understanding leveraging progress on 3D AIGC foundation models.

文本完全重复：0；content Jaccard 均值/最大值：0.673/0.833；跨查询重复 ID 槽位：16/34（47.06%）；survey 查询数：1。

审阅：3D scene understanding 与 AIGC/foundation models 均有覆盖；没有整体概念缺失。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Foundation models and their role in 3D scene understanding | 7 / 4 | `q=Foundation models and their role in 3D scene understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_005.json) |
| 2 | Application of 3D AIGC foundation models in scene understanding | 10 / 8 | `q=Application of 3D AIGC foundation models in scene understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_004.json) |
| 3 | Advancements in 3D AIGC foundational models for scene understanding | 10 / 7 | `q=Advancements in 3D AIGC foundational models for scene understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on 3D scene understanding using AIGC | 10 / 7 | `q=Research on 3D scene understanding using AIGC before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_002.json) |
| 5 | Survey papers on 3D scene understanding with 3D AIGC models | 10 / 8 | `q=Survey papers on 3D scene understanding with 3D AIGC models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 5，content Jaccard=0.833，response ID Jaccard=0.455。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q35 — 5 queries / 2 target misses

用户需求：Give me papers about LLM quantized pretraining.

文本完全重复：0；content Jaccard 均值/最大值：0.383/1.000；跨查询重复 ID 槽位：17/47（36.17%）；survey 查询数：1。

审阅：4 条保留 quantization/quantized；1 条把 quantized 写成 Quantitative pretraining，这是字面概念漂移，其他条仍正确。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on LLM quantized pretraining | 10 / 9 | `q=Survey papers on LLM quantized pretraining before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_005.json) |
| 2 | Quantitative pretraining of language models | 10 / 10 | `q=Quantitative pretraining of language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_004.json) |
| 3 | Methods for quantized pretraining in LLM | 10 / 10 | `q=Methods for quantized pretraining in LLM before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_003.json) |
| 4 | Research on quantization techniques in LLM pretraining | 10 / 8 | `q=Research on quantization techniques in LLM pretraining before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_002.json) |
| 5 | Effects of quantization on language model pretraining | 10 / 10 | `q=Effects of quantization on language model pretraining before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 3，content Jaccard=1.000，response ID Jaccard=0.118。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q36 — 5 queries / 8 target misses

用户需求：Show me research on identity preservation video generation.

文本完全重复：0；content Jaccard 均值/最大值：0.584/1.000；跨查询重复 ID 槽位：19/50（38.00%）；survey 查询数：1。

审阅：保留 identity preservation/video generation；editing 为子题，未枚举 reenactment/talking-head/try-on 不足以判因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on identity preservation in video generation | 10 / 10 | `q=Survey papers on identity preservation in video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_005.json) |
| 2 | Deep learning techniques for identity preservation in video generation | 10 / 10 | `q=Deep learning techniques for identity preservation in video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_004.json) |
| 3 | Research articles on identity preservation video creation | 10 / 10 | `q=Research articles on identity preservation video creation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_003.json) |
| 4 | Latest techniques in identity preservation video generation | 10 / 10 | `q=Latest techniques in identity preservation video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_002.json) |
| 5 | AI approaches for identity preservation in video editing | 10 / 10 | `q=AI approaches for identity preservation in video editing before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 4，content Jaccard=1.000，response ID Jaccard=0.250。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q37 — 5 queries / 4 target misses

用户需求：Give me some papers showing that LLM agents can do schedule planning.

文本完全重复：0；content Jaccard 均值/最大值：0.543/1.000；跨查询重复 ID 槽位：16/41（39.02%）；survey 查询数：1。

审阅：5 条围绕 LLM agent/schedule planning 重述；是否存在召回浪费需结合真实结果交叠指标。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on schedule planning with Language Model agents | 10 / 8 | `q=Survey papers on schedule planning with Language Model agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_005.json) |
| 2 | Research articles on LLM-based schedule planning | 10 / 9 | `q=Research articles on LLM-based schedule planning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_004.json) |
| 3 | LLM agents in schedule planning research papers | 10 / 7 | `q=LLM agents in schedule planning research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_003.json) |
| 4 | Use of LLM agents in schedule planning studies | 10 / 8 | `q=Use of LLM agents in schedule planning studies before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_002.json) |
| 5 | Language Model agents and their application in schedule planning | 10 / 9 | `q=Language Model agents and their application in schedule planning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 4，content Jaccard=1.000，response ID Jaccard=0.364。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q38 — 5 queries / 11 target misses

用户需求：Show me research on image encoding distributions.

文本完全重复：0；content Jaccard 均值/最大值：0.337/0.600；跨查询重复 ID 槽位：11/44（25.00%）；survey 查询数：1。

审阅：原始需求 image encoding distributions 本身宽泛；部分 query 收窄为 binary compression/diffusion，无资料可唯一确定用户意图。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Investigations on the use of diffusion models for image encoding distributions | 10 / 10 | `q=Investigations on the use of diffusion models for image encoding distributions before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_005.json) |
| 2 | Survey papers on image encoding distributions | 10 / 10 | `q=Survey papers on image encoding distributions before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on binary image compression using probabilistic encoding and decoding | 7 / 4 | `q=Research on binary image compression using probabilistic encoding and decoding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on image encoding techniques and their distribution | 10 / 10 | `q=Studies on image encoding techniques and their distribution before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_002.json) |
| 5 | Analysis of image encoding distributions in machine learning | 10 / 10 | `q=Analysis of image encoding distributions in machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.600，response ID Jaccard=0.000。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q39 — 5 queries / 2 target misses

用户需求：Help me search for the work related to the synthetic data of large language models. I want to know how to automatically generate large-scale, high-quality, diverse, difficult, and valuable long thought data for learning.

文本完全重复：0；content Jaccard 均值/最大值：0.171/0.333；跨查询重复 ID 槽位：17/50（34.00%）；survey 查询数：1。

审阅：long thought 被一条保留，diverse/high-quality 被其他条保留；difficult 未显式出现，test cases 为额外子题；不凭 GT 中 theorem proving 倒推必需词。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on synthetic data for large language models | 10 / 10 | `q=Survey papers on synthetic data for large language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_005.json) |
| 2 | Methods for generating valuable long thought data for AI learning | 10 / 10 | `q=Methods for generating valuable long thought data for AI learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on automatic generation of high-quality diverse data for language models | 10 / 10 | `q=Research on automatic generation of high-quality diverse data for language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_003.json) |
| 4 | Techniques for generating synthetic data for language model training | 10 / 10 | `q=Techniques for generating synthetic data for language model training before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_002.json) |
| 5 | Efficient methods for sampling diverse test cases from large language models using synthetic data | 10 / 10 | `q=Efficient methods for sampling diverse test cases from large language models using synthetic data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 5，content Jaccard=0.333，response ID Jaccard=0.333。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q40 — 5 queries / 1 target misses

用户需求：Could you list research that demonstrates the advantages of Quantization-Aware Training (QAT), which can enable the model to learn better representations for low-bit weights?.

文本完全重复：0；content Jaccard 均值/最大值：0.431/0.571；跨查询重复 ID 槽位：19/49（38.78%）；survey 查询数：1。

审阅：QAT/representations/low-bit/advantages 均覆盖；与 PTQ 比较是合理子题，不能判为漏失根因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on Quantization-Aware Training benefits | 10 / 10 | `q=Survey papers on Quantization-Aware Training benefits before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_005.json) |
| 2 | Advantages of Quantization-Aware Training in AI | 10 / 10 | `q=Advantages of Quantization-Aware Training in AI before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_004.json) |
| 3 | Research papers on the impact of Quantization-Aware Training on low-bit weight representations | 10 / 10 | `q=Research papers on the impact of Quantization-Aware Training on low-bit weight representations before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_003.json) |
| 4 | Effects of Quantization-Aware Training on model representations | 10 / 10 | `q=Effects of Quantization-Aware Training on model representations before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_002.json) |
| 5 | Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI | 10 / 9 | `q=Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 5，content Jaccard=0.571，response ID Jaccard=0.118。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q41 — 5 queries / 3 target misses

用户需求：Using synthesis data for scaling up sft data.

文本完全重复：0；content Jaccard 均值/最大值：0.226/0.500；跨查询重复 ID 槽位：13/47（27.66%）；survey 查询数：1。

审阅：2 条将 SFT 展开为 soft target data，属于可见的错误/歧义展开；另有 2 条保留 SFT，不能认定整个 query 集合没有 SFT。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Use of synthetic data in increasing volume of SFT data | 10 / 10 | `q=Use of synthetic data in increasing volume of SFT data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_005.json) |
| 2 | Survey paper on usage of synthetic data for scaling up soft target data | 10 / 8 | `q=Survey paper on usage of synthetic data for scaling up soft target data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_004.json) |
| 3 | Scaling up SFT data with synthesis data | 10 / 10 | `q=Scaling up SFT data with synthesis data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_003.json) |
| 4 | Applications of generative AI in creating synthetic data for soft target data scaling | 10 / 9 | `q=Applications of generative AI in creating synthetic data for soft target data scaling before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_002.json) |
| 5 | Exponential growth of training data in NLP through synthetic data | 10 / 10 | `q=Exponential growth of training data in NLP through synthetic data before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 4，content Jaccard=0.500，response ID Jaccard=0.545。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q42 — 5 queries / 6 target misses

用户需求：Show me research on how to select frames when doing video understanding.

文本完全重复：0；content Jaccard 均值/最大值：0.239/0.500；跨查询重复 ID 槽位：3/45（6.67%）；survey 查询数：1。

审阅：frame/keyframe/temporal sampling/video understanding 都有分支；optical flow 额外收窄一条，无法证明降低总体召回。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on frame selection in video understanding | 10 / 10 | `q=Survey papers on frame selection in video understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_005.json) |
| 2 | Optical flow-based methods for key frame selection in video understanding | 10 / 10 | `q=Optical flow-based methods for key frame selection in video understanding before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on temporal sampling strategies for video representation learning | 7 / 5 | `q=Research on temporal sampling strategies for video representation learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on efficient frame sampling in video comprehension | 10 / 10 | `q=Studies on efficient frame sampling in video comprehension before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_002.json) |
| 5 | Papers on automated video summary generation using frame selection | 10 / 10 | `q=Papers on automated video summary generation using frame selection before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=0.500，response ID Jaccard=0.053。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q43 — 5 queries / 6 target misses

用户需求：AI for Science papers, especially protein design and DPO of antibody design.

文本完全重复：0；content Jaccard 均值/最大值：0.377/1.000；跨查询重复 ID 槽位：9/39（23.08%）；survey 查询数：1。

审阅：protein design 和 antibody DPO 分别覆盖，1 条泛到 AI scientific research；未展开具体生成架构不能直接判因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | AI tools for protein design | 10 / 10 | `q=AI tools for protein design before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on DPO in antibody design | 5 / 5 | `q=Research on DPO in antibody design before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_004.json) |
| 3 | Survey papers on protein design using AI | 10 / 8 | `q=Survey papers on protein design using AI before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_003.json) |
| 4 | Application of AI in scientific research papers | 10 / 9 | `q=Application of AI in scientific research papers before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_002.json) |
| 5 | AI advancements in protein design | 10 / 7 | `q=AI advancements in protein design before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=1.000，response ID Jaccard=0.250。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q44 — 5 queries / 4 target misses

用户需求：What are the researches that have explored the application of Crypto-based Private Learning in privacy-preserving machine learning?.

文本完全重复：0；content Jaccard 均值/最大值：0.385/0.667；跨查询重复 ID 槽位：20/50（40.00%）；survey 查询数：1。

审阅：cryptography/private ML 保留，homomorphic encryption 有子题；未写 MPC 等不能证明未覆盖这些 GT。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on Crypto-based Private Learning in machine learning | 10 / 10 | `q=Survey papers on Crypto-based Private Learning in machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_005.json) |
| 2 | Application of cryptographic techniques in private machine learning | 10 / 10 | `q=Application of cryptographic techniques in private machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on encryption methods in privacy-preserving machine learning | 10 / 10 | `q=Research on encryption methods in privacy-preserving machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_003.json) |
| 4 | Use of homomorphic encryption in private learning for machine learning | 10 / 10 | `q=Use of homomorphic encryption in private learning for machine learning before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_002.json) |
| 5 | Research articles on privacy-preserving machine learning using cryptography | 10 / 10 | `q=Research articles on privacy-preserving machine learning using cryptography before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=0.667，response ID Jaccard=0.538。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q45 — 5 queries / 18 target misses

用户需求：All papers about controllability of video generation.

文本完全重复：0；content Jaccard 均值/最大值：0.517/1.000；跨查询重复 ID 槽位：18/46（39.13%）；survey 查询数：1。

审阅：controllability/video generation 在 4 条保留，1 条泛化到 video production；camera/motion/layout 等 GT 子方向未显式分解。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on controllability of video generation | 10 / 9 | `q=Survey papers on controllability of video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_005.json) |
| 2 | Research papers on video generation controllability | 10 / 9 | `q=Research papers on video generation controllability before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_004.json) |
| 3 | Latest research on controllability of video generation | 10 / 9 | `q=Latest research on controllability of video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on the control aspects of video production | 10 / 9 | `q=Studies on the control aspects of video production before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_002.json) |
| 5 | Papers on techniques for controlling video generation | 10 / 10 | `q=Papers on techniques for controlling video generation before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 2，content Jaccard=1.000，response ID Jaccard=0.125。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q46 — 5 queries / 21 target misses

用户需求：Show me research on robot decision making and task planning, especially relevant datasets and benchmarks.

文本完全重复：0；content Jaccard 均值/最大值：0.362/0.750；跨查询重复 ID 槽位：8/48（16.67%）；survey 查询数：1。

审阅：decision making、task planning、datasets、benchmarks 都有分支；dataset/benchmark 条可能高度交叠，需以响应计算验证。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on robot decision making | 10 / 9 | `q=Survey papers on robot decision making before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on task planning in robotics | 10 / 9 | `q=Research on task planning in robotics before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_004.json) |
| 3 | Benchmark datasets for robot decision making | 10 / 10 | `q=Benchmark datasets for robot decision making before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_003.json) |
| 4 | Relevant datasets for robot decision making | 10 / 10 | `q=Relevant datasets for robot decision making before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_002.json) |
| 5 | Benchmarks used in robot decision making research | 10 / 10 | `q=Benchmarks used in robot decision making research before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 1 与 5，content Jaccard=0.750，response ID Jaccard=0.056。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q47 — 5 queries / 2 target misses

用户需求：How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents.

文本完全重复：0；content Jaccard 均值/最大值：0.344/0.571；跨查询重复 ID 槽位：27/48（56.25%）；survey 查询数：1。

审阅：全部保留 LLM agent/finance/evaluation；regulatory 一条额外收窄。FinBen 的匹配必须检查 GT ID 和标题版本，不能按措辞归因。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Survey papers on evaluation of LLM agents in finance | 10 / 10 | `q=Survey papers on evaluation of LLM agents in finance before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_005.json) |
| 2 | Benchmarking methods for LLM agents in financial tasks | 10 / 9 | `q=Benchmarking methods for LLM agents in financial tasks before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_004.json) |
| 3 | Evaluation metrics for LLM agents in financial tasks | 10 / 10 | `q=Evaluation metrics for LLM agents in financial tasks before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_003.json) |
| 4 | Regulatory and industry-standard benchmarks for evaluating LLM agents in finance | 10 / 10 | `q=Regulatory and industry-standard benchmarks for evaluating LLM agents in finance before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_002.json) |
| 5 | Comparative studies on LLM agent evaluation in financial domain | 10 / 9 | `q=Comparative studies on LLM agent evaluation in financial domain before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 3，content Jaccard=0.571，response ID Jaccard=0.462。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q48 — 5 queries / 2 target misses

用户需求：Papers that explore using large language models for mining factors in stock exchange analysis.

文本完全重复：0；content Jaccard 均值/最大值：0.360/1.000；跨查询重复 ID 槽位：28/48（58.33%）；survey 查询数：1。

审阅：整体保留 finance/stocks/LLM，却全部丢失 factor/alpha/mining 任务词；GPT-3 是额外限定。两个 GT 是否受影响仍需区分局部 metadata 证据。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Application of large language models in stock market analysis | 10 / 10 | `q=Application of large language models in stock market analysis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_005.json) |
| 2 | Role of AI and language models in stock prediction | 10 / 9 | `q=Role of AI and language models in stock prediction before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_004.json) |
| 3 | Impact of large language models on stock exchange analysis | 10 / 10 | `q=Impact of large language models on stock exchange analysis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_003.json) |
| 4 | Use of GPT-3 in stock market trend analysis | 10 / 10 | `q=Use of GPT-3 in stock market trend analysis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_002.json) |
| 5 | Survey papers on large language models in stock exchange analysis | 10 / 9 | `q=Survey papers on large language models in stock exchange analysis before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 3 与 5，content Jaccard=1.000，response ID Jaccard=0.583。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

### Q49 — 5 queries / 1 target misses

用户需求：Can you help me find research papers that explore the use of large vision-language models as agents to automatically play PC games?

文本完全重复：0；content Jaccard 均值/最大值：0.265/0.571；跨查询重复 ID 槽位：9/38（23.68%）；survey 查询数：1。

审阅：PC games/VLM agents 在多条保留，1 条退化为 AI game playing；不能依据 Atari/PC 边界猜测标注对错。

| 序号 | Crawler 生成查询 | organic / 唯一 ID | 请求参数与 replay |
|---:|---|---:|---|
| 1 | Use of AI in automated PC game playing | 10 / 10 | `q=Use of AI in automated PC game playing before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_005.json) |
| 2 | Exploration of large vision-language models as gaming agents | 7 / 6 | `q=Exploration of large vision-language models as gaming agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on Large Multimodal Models (LMMs) and their application in automatic PC game play | 3 / 3 | `q=Research on Large Multimodal Models (LMMs) and their application in automatic PC game play before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on PC game automation using large vision-language models | 10 / 9 | `q=Studies on PC game automation using large vision-language models before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_002.json) |
| 5 | Survey papers on vision-language models as game agents | 10 / 10 | `q=Survey papers on vision-language models as game agents before:2024-09-24 site:arxiv.org`; num=10, page=1; [replay](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_001.json) |

最相似词项对：query 2 与 5，content Jaccard=0.571，response ID Jaccard=0.231。完整 pairwise 表见对应 JSONL 的 query_audit.pairwise_similarity。

## 283 条逐项索引

完整逐项证据：[CRAWLER_SEARCH_MISS_AUDIT.jsonl](/home/chenyi/pasa/CRAWLER_SEARCH_MISS_AUDIT.jsonl)。JSONL 一行对应一个原 baseline miss；表中“其他题可见”不作为本题返回。每行保存所有同题响应路径、全字段命中证据、同 ID 节点、touch_ids、标题变体、别名引用、最近标题候选和 query 审计。

| JSONL 行 | Query | GT ID | GT 标题 | 主分类 | 同题 organic / 同 ID 节点 / 他题字段可见 |
|---:|---|---|---|---|---|
| 1 | Q0 | 2210.10951 | Automatic Document Selection for Efficient Encoder Pretraining | UNDETERMINED | 0 / 0 / 否 |
| 2 | Q0 | 2409.17312 | Babyllama-2: Ensemble-distilled models consistently outperform teachers with limited data. | UNDETERMINED | 0 / 0 / 否 |
| 3 | Q1 | 2310.08540 | Do pretrained Transformers Learn In-Context by Gradient Descent? | UNDETERMINED | 0 / 0 / 否 |
| 4 | Q1 | 2305.12766 | Explaining Emergent In-Context Learning as Kernel Regression | UNDETERMINED | 0 / 0 / 否 |
| 5 | Q1 | 2402.15607 | How Do Nonlinear Transformers Learn and Generalize in In-Context   Learning? | UNDETERMINED | 0 / 0 / 否 |
| 6 | Q1 | 2405.11751 | Asymptotic theory of in-context learning by linear attention | UNDETERMINED | 0 / 0 / 否 |
| 7 | Q1 | 2402.01258 | Transformers Learn Nonlinear Features In Context: Nonconvex Mean-field Dynamics on the Attention Landscape | UNDETERMINED | 0 / 0 / 否 |
| 8 | Q1 | 2409.09281 | Language Models ""Grok"" to Copy | UNDETERMINED | 0 / 0 / 否 |
| 9 | Q1 | 2406.14022 | Investigating the Pre-Training Dynamics of In-Context Learning: Task Recognition vs. Task Learning | UNDETERMINED | 0 / 0 / 否 |
| 10 | Q2 | 2405.15223 | iVideoGPT: Interactive VideoGPTs are Scalable World Models | UNDETERMINED | 0 / 0 / 否 |
| 11 | Q2 | 2402.14797 | Snap video: Scaled spatiotemporal transformers for text-to-video synthesis | UNDETERMINED | 0 / 0 / 否 |
| 12 | Q2 | 2406.09455 | Pandora: Towards general world model with natural language actions and video states. | UNDETERMINED | 0 / 0 / 否 |
| 13 | Q2 | 2409.18869 | Emu3: Next token prediction is all you need | UNDETERMINED | 0 / 0 / 否 |
| 14 | Q3 | 2401.12264 | CoAVT: A Cognition-Inspired Unified Audio-Visual-Text Pre-Training Model   for Multimodal Processing | UNDETERMINED | 0 / 0 / 否 |
| 15 | Q3 | 2406.15704 | video-SALMONN: Speech-Enhanced Audio-Visual Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 16 | Q3 | 2408.05211 | VITA: Towards Open-Source Interactive Omni Multimodal LLM | UNDETERMINED | 0 / 0 / 否 |
| 17 | Q3 | 2305.12311 | i-Code V2: An Autoregressive Generation Framework over Vision, Language, and Speech Data | UNDETERMINED | 0 / 0 / 否 |
| 18 | Q3 | 2305.14381 | Connecting multi-modal contrastive representations | UNDETERMINED | 0 / 0 / 否 |
| 19 | Q3 | 2409.17692 | MIO: A Foundation Model on Multimodal Tokens | UNDETERMINED | 0 / 0 / 否 |
| 20 | Q3 | 2407.11895 | Omnibind: Large-scale omni multimodal representation via binding spaces | UNDETERMINED | 0 / 0 / 否 |
| 21 | Q3 | 2405.04883 | Freebind: Free lunch in unified multimodal space via knowledge fusion | UNDETERMINED | 0 / 0 / 否 |
| 22 | Q3 | 2310.08884 | Extending multi-modal contrastive representations | UNDETERMINED | 0 / 0 / 否 |
| 23 | Q3 | 2409.19132 | From Vision to Audio and Beyond: A Unified Model for Audio-Visual Representation and Generation | UNDETERMINED | 0 / 0 / 否 |
| 24 | Q4 | 2401.14151 | True Knowledge Comes from Practice: Aligning LLMs with Embodied   Environments via Reinforcement Learning | UNDETERMINED | 0 / 0 / 否 |
| 25 | Q4 | 2403.04642 | Teaching Large Language Models to Reason with Reinforcement Learning | UNDETERMINED | 0 / 0 / 否 |
| 26 | Q4 | 2406.05872 | STARLING: Self-supervised Training of Text-based Reinforcement Learning Agent with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 27 | Q4 | 2404.18978 | Towards Generalizable Agents in Text-Based Educational Environments: A Study of Integrating RL with LLMs | UNDETERMINED | 0 / 0 / 否 |
| 28 | Q4 | 2401.06603 | Mutual Enhancement of Large Language and Reinforcement Learning Models through Bi-Directional Feedback Mechanisms: A Case Study | UNDETERMINED | 0 / 0 / 否 |
| 29 | Q4 | 2311.05596 | LLM Augmented Hierarchical Agents | UNDETERMINED | 0 / 0 / 否 |
| 30 | Q4 | 2402.06700 | Entropy-Regularized Token-Level Policy Optimization for Language Agent Reinforcement | UNDETERMINED | 0 / 0 / 否 |
| 31 | Q4 | 2401.00006 | Building Open-Ended Embodied Agent via Language-Policy Bidirectional Adaptation | UNDETERMINED | 0 / 0 / 否 |
| 32 | Q4 | 2402.19299 | RL-GPT: Integrating Reinforcement Learning and Code-as-policy | UNDETERMINED | 0 / 0 / 否 |
| 33 | Q4 | 2409.12917 | Training Language Models to Self-Correct via Reinforcement Learning | UNDETERMINED | 0 / 0 / 是 |
| 34 | Q4 | 2312.08935 | Math-shepherd: Verify and reinforce llms step-by-step without human annotations | UNDETERMINED | 0 / 0 / 否 |
| 35 | Q4 | 2404.18638 | Reinforcement Learning Problem Solving with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 36 | Q4 | 2405.15383 | Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search | UNDETERMINED | 0 / 0 / 否 |
| 37 | Q4 | 2402.02330 | Enhance reasoning for large language models in the game werewolf | UNDETERMINED | 0 / 0 / 否 |
| 38 | Q4 | 2309.17176 | Adarefiner: Refining decisions of language models with adaptive feedback | UNDETERMINED | 0 / 0 / 否 |
| 39 | Q4 | 2310.17722 | Large Language Models as Generalizable Policies for Embodied Tasks | UNDETERMINED | 0 / 0 / 否 |
| 40 | Q4 | 2310.20587 | Unleashing the Power of Pre-trained Language Models for Offline Reinforcement Learning | UNDETERMINED | 0 / 0 / 否 |
| 41 | Q4 | 2402.12914 | Large Language Model-based Human-Agent Collaboration for Complex Task Solving | UNDETERMINED | 0 / 0 / 否 |
| 42 | Q4 | 2402.16181 | How Can LLM Guide RL? A Value-Based Approach | UNDETERMINED | 0 / 0 / 否 |
| 43 | Q4 | 2405.14751 | AGILE: A Novel Framework of LLM Agents | UNDETERMINED | 0 / 0 / 是 |
| 44 | Q5 | 2311.10081 | Dress: Instructing large vision-language models to align and interact with humans via natural language feedback | UNDETERMINED | 0 / 0 / 否 |
| 45 | Q6 | 2305.15064 | AutoPlan: Automatic Planning of Interactive Decision-Making Tasks With   Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 46 | Q6 | 2402.11166 | GenDec: A robust generative Question-decomposition method for Multi-hop   reasoning | UNDETERMINED | 0 / 0 / 否 |
| 47 | Q6 | 2403.12393 | Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open   Domain Multi-Hop Question Answering | UNDETERMINED | 0 / 0 / 否 |
| 48 | Q6 | 2406.15319 | LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs | UNDETERMINED | 0 / 0 / 否 |
| 49 | Q6 | 2310.05915 | FireAct: Toward Language Agent Fine-tuning | UNDETERMINED | 0 / 0 / 否 |
| 50 | Q6 | 2404.09129 | When Hindsight is Not 20/20: Testing Limits on Reflective Thinking in Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 51 | Q6 | 2407.10245 | GenSco: Can Question Decomposition based Passage Alignment improve Question Answering? | UNDETERMINED | 0 / 0 / 否 |
| 52 | Q6 | 2405.13021 | IM-RAG: Multi-Round Retrieval-Augmented Generation Through Learning Inner Monologues | UNDETERMINED | 0 / 0 / 否 |
| 53 | Q6 | 2407.13101 | Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach | UNDETERMINED | 0 / 0 / 否 |
| 54 | Q6 | 2210.16865 | Learning to Decompose: Hypothetical Question Decomposition Based on   Comparable Texts | UNDETERMINED | 0 / 0 / 否 |
| 55 | Q6 | 2310.04406 | Language Agent Tree Search Unifies Reasoning Acting and Planning in   Language Models | UNDETERMINED | 0 / 0 / 否 |
| 56 | Q6 | 2402.19350 | Prompting Explicit and Implicit Knowledge for Multi-hop Question   Answering Based on Human Reading Process | UNDETERMINED | 0 / 0 / 否 |
| 57 | Q6 | 2305.03130 | Chain-of-Skills: A Configurable Model for Open-domain Question Answering | UNDETERMINED | 0 / 0 / 否 |
| 58 | Q6 | 2404.03414 | Can Small Language Models Help Large Language Models Reason Better?: LM-Guided Chain-of-Thought | UNDETERMINED | 0 / 0 / 否 |
| 59 | Q7 | 2402.13250 | Video ReCap: Recursive Captioning of Hour-Long Videos | UNDETERMINED | 0 / 0 / 否 |
| 60 | Q7 | 2406.14515 | MMBench-Video: A Long-Form Multi-Shot Benchmark for Holistic Video Understanding | UNDETERMINED | 0 / 0 / 否 |
| 61 | Q7 | 2310.04900 | HowToCaption: Prompting LLMs to Transform Video Annotations at Scale | UNDETERMINED | 0 / 0 / 否 |
| 62 | Q7 | 2407.15754 | LongVideoBench: A Benchmark for Long-context Interleaved Video-Language Understanding | UNDETERMINED | 0 / 0 / 否 |
| 63 | Q7 | 2409.06299 | Enhancing Long Video Understanding via Hierarchical Event-Based Memory | UNDETERMINED | 0 / 0 / 否 |
| 64 | Q7 | 2406.12846 | DrVideo: Document Retrieval Based Long Video Understanding | UNDETERMINED | 0 / 0 / 否 |
| 65 | Q7 | 2406.08035 | LVBench: An Extreme Long Video Understanding Benchmark | UNDETERMINED | 0 / 0 / 否 |
| 66 | Q7 | 2402.08268 | World Model on Million-Length Video And Language With Blockwise RingAttention | TITLE_METADATA_MISMATCH | 0 / 1 / 否 |
| 67 | Q7 | 2404.04346 | Koala: Key frame-conditioned long video-LLM | UNDETERMINED | 0 / 0 / 否 |
| 68 | Q7 | 2406.17880 | MLLM as Video Narrator: Mitigating Modality Imbalance in Video Moment Retrieval | UNDETERMINED | 0 / 0 / 否 |
| 69 | Q7 | 2406.04264 | MLVU: A Comprehensive Benchmark for Multi-Task Long Video Understanding | UNDETERMINED | 0 / 0 / 否 |
| 70 | Q7 | 2408.15542 | Kangaroo: A Powerful Video-Language Model Supporting Long-context Video Input | UNDETERMINED | 0 / 0 / 否 |
| 71 | Q7 | 2312.05269 | LifelongMemory: Leveraging LLMs for Answering Queries in Long-form   Egocentric Videos | UNDETERMINED | 0 / 0 / 否 |
| 72 | Q7 | 2406.04325 | ShareGPT4Video: Improving Video Understanding and Generation with Better Captions | UNDETERMINED | 0 / 0 / 否 |
| 73 | Q7 | 2402.13546 | LLMs Meet Long Video: Advancing Long Video Comprehension with An Interactive Visual Adapter in LLMs | UNDETERMINED | 0 / 0 / 否 |
| 74 | Q7 | 2403.10517 | VideoAgent: Long-form Video Understanding with Large Language Model as Agent | UNDETERMINED | 0 / 0 / 是 |
| 75 | Q7 | 2203.05711 | Synopses of movie narratives: a video-language dataset for story understanding | UNDETERMINED | 0 / 0 / 否 |
| 76 | Q7 | 2403.11481 | Videoagent: A memory-augmented multimodal agent for video understanding. | UNDETERMINED | 0 / 0 / 否 |
| 77 | Q7 | 2404.01297 | Streaming dense video captioning | UNDETERMINED | 0 / 0 / 否 |
| 78 | Q8 | 2401.07382 | Beyond Sparse Rewards: Enhancing Reinforcement Learning with Language   Model Critique in Text Generation | TITLE_METADATA_MISMATCH | 1 / 1 / 否 |
| 79 | Q8 | 2308.12270 | Language Reward Modulation for Pretraining Reinforcement Learning | UNDETERMINED | 0 / 0 / 否 |
| 80 | Q8 | 2312.09238 | Auto MC-Reward: Automated Dense Reward Design with Large Language Models for Minecraft | UNDETERMINED | 0 / 0 / 否 |
| 81 | Q8 | 2404.11999 | Token-level Direct Preference Optimization | UNDETERMINED | 0 / 0 / 否 |
| 82 | Q8 | 2405.15194 | Extracting Heuristics from Large Language Models for Reward Shaping in Reinforcement Learning | UNDETERMINED | 0 / 0 / 否 |
| 83 | Q9 | 2310.14408 | PaRaDe: Passage Ranking using Demonstrations with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 84 | Q9 | 2406.11678 | TourRank: Utilizing Large Language Models for Documents Ranking with a Tournament-Inspired Strategy | UNDETERMINED | 0 / 0 / 否 |
| 85 | Q9 | 2407.02485 | RankRAG: Unifying Context Ranking with Retrieval-Augmented Generation in LLMs | UNDETERMINED | 0 / 0 / 否 |
| 86 | Q9 | 2406.00231 | LLM-RankFusion: Mitigating Intrinsic Inconsistency in LLM-based Ranking | UNDETERMINED | 0 / 0 / 否 |
| 87 | Q9 | 2406.13331 | Improving Zero-shot LLM Re-Ranker with Risk Minimization | UNDETERMINED | 0 / 0 / 否 |
| 88 | Q9 | 2404.11791 | Consolidating Ranking and Relevance Predictions of Large Language Models through Post-Processing | UNDETERMINED | 0 / 0 / 否 |
| 89 | Q9 | 2406.18740 | Re-Ranking Step by Step: Investigating Pre-Filtering for Re-Ranking with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 90 | Q9 | 2406.00247 | Large Language Models for Relevance Judgment in Product Search | UNDETERMINED | 0 / 0 / 否 |
| 91 | Q9 | 2404.18424 | PromptReps: Prompting Large Language Models to Generate Dense and Sparse Representations for Zero-Shot Document Retrieval | UNDETERMINED | 0 / 0 / 否 |
| 92 | Q9 | 2405.20654 | Passage-specific Prompt Tuning for Passage Reranking in Question Answering with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 93 | Q9 | 2401.06311 | MuGI: Enhancing Information Retrieval through Multi-Text Generation Integration with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 94 | Q9 | 2402.17497 | REAR: A Relevance-Aware Retrieval-Augmented Framework for Open-Domain   Question Answering | UNDETERMINED | 0 / 0 / 否 |
| 95 | Q9 | 2312.15450 | Agent4Ranking: Semantic Robust Ranking via Personalized Query Rewriting   Using Multi-agent LLM | UNDETERMINED | 0 / 0 / 否 |
| 96 | Q9 | 2406.15657 | FIRST: Faster Improved Listwise Reranking with Single Token Decoding | UNDETERMINED | 0 / 0 / 否 |
| 97 | Q9 | 2402.04853 | Leveraging LLMs for Unsupervised Dense Retriever Ranking | UNDETERMINED | 0 / 0 / 否 |
| 98 | Q9 | 2403.18093 | Enhancing Legal Document Retrieval: A Multi-Phase Approach with Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 99 | Q9 | 2309.07606 | Zero-shot Audio Topic Reranking using Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 100 | Q9 | 2402.10548 | Cognitive Personalized Search Integrating Large Language Models with an Efficient Memory Mechanism | UNDETERMINED | 0 / 0 / 否 |
| 101 | Q9 | 2409.17460 | Towards More Relevant Product Search Ranking Via Large Language Models: An Empirical Study | UNDETERMINED | 0 / 0 / 否 |
| 102 | Q10 | 2408.11039 | Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model | UNDETERMINED | 0 / 0 / 否 |
| 103 | Q10 | 2408.00620 | Are Bigger Encoders Always Better in Vision Large Models? | UNDETERMINED | 0 / 0 / 否 |
| 104 | Q10 | 2409.06754 | Scaling Law Hypothesis for Multimodal Model | UNDETERMINED | 0 / 0 / 否 |
| 105 | Q10 | 2402.05935 | SPHINX-X: Scaling Data and Parameters for a Family of Multi-modal Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 106 | Q11 | 2405.05949 | CuMo: Scaling Multimodal LLM with Co-Upcycled Mixture-of-Experts | UNDETERMINED | 0 / 0 / 否 |
| 107 | Q11 | 2406.19905 | Solving Token Gradient Conflict in Mixture-of-Experts for Large Vision-Language Model | UNDETERMINED | 0 / 0 / 否 |
| 108 | Q11 | 2403.11549 | Boosting Continual Learning of Vision-Language Models via   Mixture-of-Experts Adapters | UNDETERMINED | 0 / 0 / 否 |
| 109 | Q11 | 2407.21770 | MoMa: Efficient Early-Fusion Pre-training with Mixture of Modality-Aware Experts | UNDETERMINED | 0 / 0 / 否 |
| 110 | Q11 | 2408.03511 | MoExtend: Tuning New Experts for Modality and Task Extension | UNDETERMINED | 0 / 0 / 否 |
| 111 | Q11 | 2409.07267 | MiniDrive: More Efficient Vision-Language Models with Multi-Level 2D Features as Text Tokens for Autonomous Driving | UNDETERMINED | 0 / 0 / 否 |
| 112 | Q11 | 2402.14891 | LLMBind: A Unified Modality-Task Integration Framework | UNDETERMINED | 0 / 0 / 否 |
| 113 | Q12 | 2209.04066 | TEACH: Temporal Action Composition for 3D Humans | UNDETERMINED | 0 / 0 / 否 |
| 114 | Q12 | 2103.10206 | DanceFormer: Music Conditioned 3D Dance Generation with Parametric Motion Transformer | UNDETERMINED | 0 / 0 / 否 |
| 115 | Q12 | 2310.20240 | Breathing Life into Faces: Speech-driven 3D Facial Animation with Natural Head Pose and Detailed Shape | UNDETERMINED | 0 / 0 / 否 |
| 116 | Q12 | 2406.17601 | Director3D: Real-world Camera Trajectory and 3D Scene Generation from Text | UNDETERMINED | 0 / 0 / 否 |
| 117 | Q12 | 2405.17405 | Human4DiT: 360-degree Human Video Generation with 4D Diffusion Transformer | UNDETERMINED | 0 / 0 / 否 |
| 118 | Q13 | 2310.08118 | Can Large Language Models Really Improve by Self-critiquing Their Own   Plans? | UNDETERMINED | 0 / 0 / 否 |
| 119 | Q13 | 2311.07954 | A Closer Look at the Self-Verification Abilities of Large Language   Models in Logical Reasoning | UNDETERMINED | 0 / 0 / 否 |
| 120 | Q13 | 2404.04298 | SELF-[IN]CORRECT: LLMs Struggle with Discriminating Self-Generated Responses | UNDETERMINED | 0 / 0 / 否 |
| 121 | Q13 | 2402.08115 | On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks | UNDETERMINED | 0 / 0 / 否 |
| 122 | Q13 | 2402.11436 | Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement | UNDETERMINED | 0 / 0 / 否 |
| 123 | Q14 | 2408.07884 | Instruct Large Language Models to Generate Scientific Literature Survey Step by Step | UNDETERMINED | 0 / 0 / 否 |
| 124 | Q14 | 2408.13450 | vitaLITy 2: Reviewing Academic Literature Using Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 125 | Q14 | 2409.18454 | Leveraging Long-Context Large Language Models for Multi-Document Understanding and Summarization in Enterprise Applications | UNDETERMINED | 0 / 0 / 否 |
| 126 | Q15 | 2310.20703 | Vanishing gradients in reinforcement finetuning of language models | UNDETERMINED | 0 / 0 / 否 |
| 127 | Q16 | 2303.14452 | COFFEE: A Contrastive Oracle-Free Framework for Event Extraction | UNDETERMINED | 0 / 0 / 否 |
| 128 | Q16 | 2305.18926 | Document-Level Multi-Event Extraction with Event Proxy Nodes and Hausdorff Distance Minimization | UNDETERMINED | 0 / 0 / 否 |
| 129 | Q16 | 2202.03092 | Document-Level Event Extraction via Human-Like Reading Process | UNDETERMINED | 0 / 0 / 否 |
| 130 | Q17 | 2404.03598 | Intent Detection and Entity Extraction from BioMedical Literature | UNDETERMINED | 0 / 0 / 否 |
| 131 | Q17 | 2404.00457 | MetaIE: Distilling a Meta Model from LLM for All Kinds of Information Extraction Tasks | UNDETERMINED | 0 / 0 / 否 |
| 132 | Q17 | 2306.09719 | Pushing the Limits of ChatGPT on NLP Tasks | UNDETERMINED | 0 / 0 / 否 |
| 133 | Q17 | 2401.14556 | Looking Right is Sometimes Right: Investigating the Capabilities of Decoder-only LLMs for Sequence Labeling | TITLE_METADATA_MISMATCH | 0 / 1 / 否 |
| 134 | Q18 | 2310.13606 | MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark | UNDETERMINED | 0 / 0 / 否 |
| 135 | Q18 | 2409.16914 | Zero-Shot Detection of LLM-Generated Text using Token Cohesiveness | UNDETERMINED | 0 / 0 / 否 |
| 136 | Q18 | 2310.14479 | DetectGPT-SC: Improving Detection of Text Generated by Large Language Models through Self-Consistency with Masked Predictions. | UNDETERMINED | 0 / 0 / 否 |
| 137 | Q18 | 2310.15515 | Fighting fire with fire: The dual role of llms in crafting and detecting elusive disinformation | UNDETERMINED | 0 / 0 / 否 |
| 138 | Q19 | 2310.07710 | A Resilient and Accessible Distribution-Preserving Watermark for Large   Language Models | TITLE_METADATA_MISMATCH | 0 / 1 / 否 |
| 139 | Q19 | 2403.19548 | WaterJudge: Quality-Detection Trade-off when Watermarking Large Language   Models | UNDETERMINED | 0 / 0 / 否 |
| 140 | Q19 | 2311.09832 | WatME: Towards Lossless Watermarking Through Lexical Redundancy | TITLE_METADATA_MISMATCH | 1 / 1 / 否 |
| 141 | Q19 | 2401.13927 | Adaptive Text Watermark for Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 142 | Q19 | 2406.14517 | PostMark: A Robust Blackbox Watermark for Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 143 | Q19 | 2405.14604 | A Watermark for Low-entropy and Unbiased Generation in Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 144 | Q19 | 2406.10281 | Watermarking Language Models with Error Correcting Codes | UNDETERMINED | 0 / 0 / 否 |
| 145 | Q19 | 2409.09739 | PersonaMark: Personalized LLM watermarking for model protection and user attribution | UNDETERMINED | 0 / 0 / 否 |
| 146 | Q19 | 2405.02365 | ModelShield: Adaptive and Robust Watermark against Model Extraction Attack | UNDETERMINED | 0 / 0 / 否 |
| 147 | Q19 | 2311.09668 | Improving the Generation Quality of Watermarked Large Language Models   via Word Importance Scoring | UNDETERMINED | 0 / 0 / 否 |
| 148 | Q19 | 2308.00221 | Advancing Beyond Identification: Multi-bit Watermark for Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 149 | Q19 | 2401.06829 | Cross-Attention Watermarking of Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 150 | Q20 | 2402.13426 | Explaining Relationships Among Research Papers | UNDETERMINED | 0 / 0 / 否 |
| 151 | Q20 | 2408.07884 | Instruct Large Language Models to Generate Scientific Literature Survey Step by Step | UNDETERMINED | 0 / 0 / 否 |
| 152 | Q20 | 2408.13450 | vitaLITy 2: Reviewing Academic Literature Using Large Language Models | UNDETERMINED | 0 / 0 / 否 |
| 153 | Q21 | 2403.07230 | Curry-DPO: Enhancing Alignment using Curriculum Learning &amp;amp; Ranked Preferences | UNDETERMINED | 0 / 0 / 否 |
| 154 | Q21 | 2402.10958 | Relative Preference Optimization: Enhancing LLM Alignment through Contrasting Responses across Identical and Diverse Prompts | UNDETERMINED | 0 / 0 / 是 |
| 155 | Q22 | 2402.10699 | Rethinking Human-like Translation Strategy: Integrating Drift-Diffusion   Model with Large Language Models for Machine Translation | UNDETERMINED | 0 / 0 / 否 |
| 156 | Q23 | 2407.08737 | Video Diffusion Alignment via Reward Gradients | UNDETERMINED | 0 / 0 / 否 |
| 157 | Q23 | 2312.12490 | InstructVideo: Instructing Video Diffusion Models with Human Feedback | UNDETERMINED | 0 / 0 / 否 |
| 158 | Q24 | 2407.21646 | Towards Achieving Human Parity on End-to-end Simultaneous Speech   Translation via LLM Agent | UNDETERMINED | 0 / 0 / 否 |
| 159 | Q24 | 2402.13036 | SiLLM: Large Language Models for Simultaneous Machine Translation | UNDETERMINED | 0 / 0 / 否 |
| 160 | Q27 | 2312.12457 | Let AI Entertain You: Increasing User Engagement with Generative AI and   Rejection Sampling | UNDETERMINED | 0 / 0 / 否 |
| 161 | Q27 | 2405.20335 | Xwin-LM: Strong and Scalable Alignment Practice for LLMs | UNDETERMINED | 0 / 0 / 否 |
| 162 | Q27 | 2407.13690 | DART-Math: Difficulty-Aware Rejection Tuning for Mathematical   Problem-Solving | UNDETERMINED | 0 / 0 / 否 |
| 163 | Q27 | 2310.20246 | Breaking Language Barriers in Multilingual Mathematical Reasoning:   Insights and Observations | UNDETERMINED | 0 / 0 / 否 |
| 164 | Q28 | 2401.03855 | PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLM | UNDETERMINED | 0 / 0 / 否 |
| 165 | Q28 | 2405.04520 | NaturalCodeBench: Examining Coding Performance Mismatch on HumanEval and   Natural User Prompts | UNDETERMINED | 0 / 0 / 否 |
| 166 | Q29 | 2409.17433 | HDFlow: Enhancing LLM Complex Problem-Solving with Hybrid Thinking and   Dynamic Workflows | UNDETERMINED | 0 / 0 / 否 |
| 167 | Q29 | 2406.14219 | Proving Olympiad Algebraic Inequalities without Human Demonstrations | UNDETERMINED | 0 / 0 / 否 |
| 168 | Q29 | 2406.07394 | Accessing GPT-4 level Mathematical Olympiad Solutions via Monte Carlo   Tree Self-refine with LLaMa-3 8B | UNDETERMINED | 0 / 0 / 否 |
| 169 | Q30 | 2405.02266 | On the test-time zero-shot generalization of vision-language models: Do   we really need prompt learning? | UNDETERMINED | 0 / 0 / 否 |
| 170 | Q31 | 2408.00550 | Mitigating Multilingual Hallucination in Large Vision-Language Models | UNDETERMINED | 0 / 0 / 否 |
| 171 | Q31 | 2406.19973 | STLLaVA-Med: Self-Training Large Language and Vision Assistant for   Medical Question-Answering | UNDETERMINED | 0 / 0 / 否 |
| 172 | Q31 | 2403.14003 | Multi-Modal Hallucination Control by Visual Information Grounding | UNDETERMINED | 0 / 0 / 否 |
| 173 | Q31 | 2405.11165 | Automated Multi-level Preference for MLLMs | UNDETERMINED | 0 / 0 / 是 |
| 174 | Q32 | 2308.09709 | Neural-network quantum state study of the long-range antiferromagnetic   Ising chain | UNDETERMINED | 0 / 0 / 否 |
| 175 | Q32 | 2405.01981 | Universal Performance Gap of Neural Quantum States Applied to the Hofstadter-Bose-Hubbard Model | UNDETERMINED | 0 / 0 / 否 |
| 176 | Q32 | 2202.05183 | Discovering Quantum Phase Transitions with Fermionic Neural Networks | UNDETERMINED | 0 / 0 / 否 |
| 177 | Q32 | 2208.12590 | Ab-initio quantum chemistry with neural-network wavefunctions | UNDETERMINED | 0 / 0 / 否 |
| 178 | Q32 | 2401.17550 | Second-order optimisation strategies for neural network quantum states | UNDETERMINED | 0 / 0 / 否 |
| 179 | Q32 | 2407.00707 | Deep learning quantum Monte Carlo for solids | UNDETERMINED | 0 / 0 / 否 |
| 180 | Q32 | 2307.08214 | Forward Laplacian: A New Computational Framework for Neural   Network-based Variational Monte Carlo | UNDETERMINED | 0 / 0 / 否 |
| 181 | Q32 | 2211.04614 | Solving the nuclear pairing model with neural network quantum states | UNDETERMINED | 0 / 0 / 否 |
| 182 | Q32 | 2409.01306 | Highly Accurate Real-space Electron Densities with Neural Networks | UNDETERMINED | 0 / 0 / 否 |
| 183 | Q32 | 2311.17595 | Penalty and auxiliary wave function methods for electronic Excitation in neural network variational Monte Carlo | UNDETERMINED | 0 / 0 / 否 |
| 184 | Q33 | 2011.00675 | A Targeted Attack on Black-Box Neural Machine Translation with Parallel   Data Poisoning | UNDETERMINED | 0 / 0 / 否 |
| 185 | Q33 | 2303.01068 | Targeted Adversarial Attacks against Neural Machine Translation | UNDETERMINED | 0 / 0 / 否 |
| 186 | Q33 | 2204.08689 | Generating Authentic Adversarial Examples beyond Meaning-preserving with   Doubly Round-trip Translation | UNDETERMINED | 0 / 0 / 否 |
| 187 | Q33 | 2302.00944 | TransFool: An Adversarial Attack against Neural Machine Translation   Models | UNDETERMINED | 0 / 0 / 否 |
| 188 | Q33 | 2407.05319 | Rethinking Targeted Adversarial Attacks For Neural Machine Translation | UNDETERMINED | 0 / 0 / 否 |
| 189 | Q33 | 2409.05021 | Vision-fused Attack: Advancing Aggressive and Stealthy Adversarial Text   against Neural Machine Translation | UNDETERMINED | 0 / 0 / 否 |
| 190 | Q34 | 2401.09340 | SceneVerse: Scaling 3D Vision-Language Learning for Grounded Scene   Understanding | UNDETERMINED | 0 / 0 / 否 |
| 191 | Q34 | 2408.13788 | 3D-VirtFusion: Synthetic 3D Data Augmentation through Generative Diffusion Models and Controllable Editing | UNDETERMINED | 0 / 0 / 否 |
| 192 | Q34 | 2305.08776 | Bridging the Domain Gap: Self-Supervised 3D Scene Understanding with Foundation Models | UNDETERMINED | 0 / 0 / 否 |
| 193 | Q35 | 2405.16528 | LoQT: Low-Rank Adapters for Quantized Pretraining | UNDETERMINED | 0 / 0 / 否 |
| 194 | Q35 | 2407.08296 | Q-GaLore: Quantized GaLore with INT4 Projection and Layer-Adaptive Low-Rank Gradients | UNDETERMINED | 0 / 0 / 否 |
| 195 | Q36 | 2403.08764 | VLOGGER: Multimodal Diffusion for Embodied Avatar Synthesis | UNDETERMINED | 0 / 0 / 否 |
| 196 | Q36 | 2407.15153 | Anchored Diffusion for Video Face Reenactment | UNDETERMINED | 0 / 0 / 否 |
| 197 | Q36 | 2405.18326 | VITON-DiT: Learning In-the-Wild Video Try-On from Human Dance Videos via   Diffusion Transformers | UNDETERMINED | 0 / 0 / 否 |
| 198 | Q36 | 2004.12452 | One-Shot Identity-Preserving Portrait Reenactment | UNDETERMINED | 0 / 0 / 否 |
| 199 | Q36 | 2204.06862 | An Identity-Preserved Framework for Human Motion Transfer | UNDETERMINED | 0 / 0 / 否 |
| 200 | Q36 | 2210.11182 | Facial Expression Video Generation Based-On Spatio-temporal   Convolutional GAN: FEV-GAN | UNDETERMINED | 0 / 0 / 否 |
| 201 | Q36 | 2409.15179 | MIMAFace: Face Animation via Motion-Identity Modulated Appearance   Feature Learning | UNDETERMINED | 0 / 0 / 否 |
| 202 | Q36 | 2407.05577 | Audio-driven High-resolution Seamless Talking Head Video Editing via   StyleGAN | UNDETERMINED | 0 / 0 / 否 |
| 203 | Q37 | 2311.15649 | RoboGPT: an intelligent agent of making embodied long-term decisions for   daily instruction tasks | UNDETERMINED | 0 / 0 / 否 |
| 204 | Q37 | 2407.19667 | Smart Language Agents in Real-World Planning | UNDETERMINED | 0 / 0 / 否 |
| 205 | Q37 | 2407.08550 | Incorporating Large Language Models into Production Systems for Enhanced Task Automation and Flexibility | UNDETERMINED | 0 / 0 / 否 |
| 206 | Q37 | 2406.11132 | RePrompt: Planning by Automatic Prompt Engineering for Large Language   Models Agents | UNDETERMINED | 0 / 0 / 否 |
| 207 | Q38 | 2201.11795 | Neural JPEG: End-to-End Image Compression Leveraging a Standard JPEG   Encoder-Decoder | UNDETERMINED | 0 / 0 / 否 |
| 208 | Q38 | 2009.12927 | Learning to Improve Image Compression without Changing the Standard   Decoder | UNDETERMINED | 0 / 0 / 否 |
| 209 | Q38 | 2111.09172 | End-to-end optimized image compression with competition of prior   distributions | UNDETERMINED | 0 / 0 / 否 |
| 210 | Q38 | 2407.07052 | Latent Space Imaging | UNDETERMINED | 0 / 0 / 否 |
| 211 | Q38 | 2406.13059 | Learned Compression of Encoding Distributions | UNDETERMINED | 0 / 0 / 否 |
| 212 | Q38 | 2306.00927 | Second Sight: Using brain-optimized encoding models to align image   distributions with human brain activity | UNDETERMINED | 0 / 0 / 否 |
| 213 | Q38 | 2406.07699 | CUPID: Contextual Understanding of Prompt-conditioned Image   Distributions | UNDETERMINED | 0 / 0 / 否 |
| 214 | Q38 | 2310.10517 | Distribution prediction for image compression: An experimental   re-compressor for JPEG images | UNDETERMINED | 0 / 0 / 否 |
| 215 | Q38 | 2308.15667 | Bridging Distribution Learning and Image Clustering in High-dimensional   Space | UNDETERMINED | 0 / 0 / 否 |
| 216 | Q38 | 2010.01185 | Compressing Images by Encoding Their Latent Representations with   Relative Entropy Coding | UNDETERMINED | 0 / 0 / 否 |
| 217 | Q38 | 2409.08376 | Learned Compression for Images and Point Clouds | UNDETERMINED | 0 / 0 / 否 |
| 218 | Q39 | 2402.08957 | MUSTARD: Mastering Uniform Synthesis of Theorem and Proof Data | UNDETERMINED | 0 / 0 / 否 |
| 219 | Q39 | 2405.14333 | DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale   Synthetic Data | UNDETERMINED | 0 / 0 / 是 |
| 220 | Q40 | 2406.06385 | Low-Rank Quantization-Aware Training for LLMs | UNDETERMINED | 0 / 0 / 是 |
| 221 | Q41 | 2408.08343 | API-guided Dataset Synthesis to Finetune Large Code Models | UNDETERMINED | 0 / 0 / 否 |
| 222 | Q41 | 2407.08348 | Skywork-Math: Data Scaling Laws for Mathematical Reasoning in Large Language Models -- The Story Goes On | UNDETERMINED | 0 / 0 / 否 |
| 223 | Q41 | 2409.13540 | FullAnno: A Data Engine for Enhancing Image Comprehension of MLLMs | UNDETERMINED | 0 / 0 / 否 |
| 224 | Q42 | 1907.00193 | Frame attention networks for facial expression recognition in videos | UNDETERMINED | 0 / 0 / 否 |
| 225 | Q42 | 1903.11779 | BubbleNets: Learning to Select the Guidance Frame in Video Object   Segmentation by Deep Sorting Frames | UNDETERMINED | 0 / 0 / 否 |
| 226 | Q42 | 1910.04792 | Unsupervised video summarization framework using keyframe extraction and   video skimming | UNDETERMINED | 0 / 0 / 否 |
| 227 | Q42 | 2306.13176 | Key Frame Extraction with Attention Based Deep Neural Networks | UNDETERMINED | 0 / 0 / 否 |
| 228 | Q42 | 2404.04346 | Koala: Key frame-conditioned long video-LLM | UNDETERMINED | 0 / 0 / 否 |
| 229 | Q42 | 2009.12434 | Online Learnable Keyframe Extraction in Videos and its Application with   Semantic Word Vector in Action Recognition | UNDETERMINED | 0 / 0 / 否 |
| 230 | Q43 | 2402.18567 | Diffusion Language Models Are Versatile Protein Learners | UNDETERMINED | 0 / 0 / 否 |
| 231 | Q43 | 2407.07177 | Protein Design by Integrating Machine Learning with Quantum Annealing   and Quantum-inspired Optimization | UNDETERMINED | 0 / 0 / 否 |
| 232 | Q43 | 2407.13981 | Decomposed Direct Preference Optimization for Structure-Based Drug   Design | UNDETERMINED | 0 / 0 / 否 |
| 233 | Q43 | 2312.09236 | A framework for conditional diffusion modelling with applications in motif scaffolding for protein design | UNDETERMINED | 0 / 0 / 否 |
| 234 | Q43 | 2403.14088 | Protein Conformation Generation via Force-Guided SE(3) Diffusion Models | UNDETERMINED | 0 / 0 / 否 |
| 235 | Q43 | 2312.00080 | PDB-Struct: A Comprehensive Benchmark for Structure-based Protein Design | UNDETERMINED | 0 / 0 / 否 |
| 236 | Q44 | 2409.07751 | Efficient Privacy-Preserving KAN Inference Using Homomorphic Encryption | UNDETERMINED | 0 / 0 / 否 |
| 237 | Q44 | 2406.13221 | Privacy-Preserving Logistic Regression Training on Large Datasets | UNDETERMINED | 0 / 0 / 否 |
| 238 | Q44 | 2209.11904 | CryptoGCN: Fast and Scalable Homomorphically Encrypted Graph   Convolutional Network Inference | UNDETERMINED | 0 / 0 / 否 |
| 239 | Q44 | 2402.00205 | Decentralised, Collaborative, and Privacy-preserving Machine Learning   for Multi-Hospital Data | UNDETERMINED | 0 / 0 / 否 |
| 240 | Q45 | 2311.16813,2408.07605 | Panacea: Panoramic and Controllable Video Generation for Autonomous   Driving | UNDETERMINED | 0 / 0 / 否 |
| 241 | Q45 | 2407.15642 | Cinemo: Consistent and Controllable Image Animation with Motion   Diffusion Models | UNDETERMINED | 0 / 0 / 否 |
| 242 | Q45 | 2310.07771 | DrivingDiffusion: Layout-Guided multi-view driving scene video   generation with latent diffusion model | UNDETERMINED | 0 / 0 / 否 |
| 243 | Q45 | 2409.01595 | DiVE: DiT-based Video Generation with Enhanced Control | UNDETERMINED | 0 / 0 / 否 |
| 244 | Q45 | 2409.05463 | DriveScape: Towards High-Resolution Controllable Multi-View Driving   Video Generation | UNDETERMINED | 0 / 0 / 否 |
| 245 | Q45 | 2406.02509 | CamCo: Camera-Controllable 3D-Consistent Image-to-Video Generation | UNDETERMINED | 0 / 0 / 否 |
| 246 | Q45 | 2312.03018 | DreamVideo: High-Fidelity Image-to-Video Generation with Image Retention   and Text Guidance | UNDETERMINED | 0 / 0 / 否 |
| 247 | Q45 | 2310.02601 | MagicDrive: Street View Generation with Diverse 3D Geometry Control | UNDETERMINED | 0 / 0 / 否 |
| 248 | Q45 | 2406.16863 | FreeTraj: Tuning-Free Trajectory Control in Video Diffusion Models | UNDETERMINED | 0 / 0 / 否 |
| 249 | Q45 | 2406.05630 | Ctrl-V: Higher Fidelity Video Generation with Bounding-Box Controlled   Object Motion | UNDETERMINED | 0 / 0 / 否 |
| 250 | Q45 | 2409.01502 | AMG: Avatar Motion Guided Video Generation | UNDETERMINED | 0 / 0 / 否 |
| 251 | Q45 | 2408.06070 | ControlNeXt: Powerful and Efficient Control for Image and Video   Generation | UNDETERMINED | 0 / 0 / 否 |
| 252 | Q45 | 2409.06189 | MyGo: Consistent and Controllable Multi-View Driving Video Generation   with Camera Control | UNDETERMINED | 0 / 0 / 否 |
| 253 | Q45 | 2406.10126 | Training-free Camera Control for Video Generation | UNDETERMINED | 0 / 0 / 否 |
| 254 | Q45 | 2406.05338 | MotionClone: Training-Free Motion Cloning for Controllable Video Generation | UNDETERMINED | 0 / 0 / 否 |
| 255 | Q45 | 2312.03047 | MagicStick: Controllable Video Editing via Control Handle Transformations | UNDETERMINED | 0 / 0 / 否 |
| 256 | Q45 | 2312.00845 | VMC: Video Motion Customization using Temporal Attention Adaption for Text-to-Video Diffusion Models | UNDETERMINED | 0 / 0 / 否 |
| 257 | Q45 | 2405.20222 | MOFA-Video: Controllable Image Animation via Generative Motion Field Adaptions in Frozen Image-to-Video Diffusion Model | UNDETERMINED | 0 / 0 / 否 |
| 258 | Q46 | 2310.12020 | LoHoRavens: A Long-Horizon Language-Conditioned Benchmark for Robotic   Tabletop Manipulation | UNDETERMINED | 0 / 0 / 否 |
| 259 | Q46 | 2311.15649 | RoboGPT: an intelligent agent of making embodied long-term decisions for   daily instruction tasks | UNDETERMINED | 0 / 0 / 否 |
| 260 | Q46 | 2405.01534 | Plan-Seq-Learn: Language Model Guided RL for Solving Long Horizon   Robotics Tasks | UNDETERMINED | 0 / 0 / 否 |
| 261 | Q46 | 2406.02523 | RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots | UNDETERMINED | 0 / 0 / 否 |
| 262 | Q46 | 2407.00278 | PerAct2: Benchmarking and Learning for Robotic Bimanual Manipulation   Tasks | UNDETERMINED | 0 / 0 / 否 |
| 263 | Q46 | 2312.12036 | LHManip: A Dataset for Long-Horizon Language-Grounded Manipulation Tasks   in Cluttered Tabletop Environments | UNDETERMINED | 0 / 0 / 否 |
| 264 | Q46 | 2403.19622 | RH20T-P: A Primitive-Level Robotic Dataset Towards Composable   Generalization Agents | UNDETERMINED | 0 / 0 / 否 |
| 265 | Q46 | 2403.18760 | MLDT: Multi-Level Decomposition for Complex Long-Horizon Robotic Task   Planning with Open-Source Large Language Model | UNDETERMINED | 0 / 0 / 否 |
| 266 | Q46 | 2307.00595 | RH20T: A Comprehensive Robotic Dataset for Learning Diverse Skills in One-Shot | UNDETERMINED | 0 / 0 / 否 |
| 267 | Q46 | 2401.04157 | RePLan: Robotic Replanning with Perception and Language Models | UNDETERMINED | 0 / 0 / 否 |
| 268 | Q46 | 2409.13998 | Relevance-driven Decision Making for Safer and More Efficient Human   Robot Collaboration | UNDETERMINED | 0 / 0 / 否 |
| 269 | Q46 | 1909.12271 | RLBench: The Robot Learning Benchmark &amp;amp; Learning Environment | TITLE_METADATA_MISMATCH | 0 / 1 / 否 |
| 270 | Q46 | 2406.03641 | Task and Motion Planning for Execution in the Real | UNDETERMINED | 0 / 0 / 否 |
| 271 | Q46 | 2402.08546 | Grounding LLMs For Robot Task Planning Using Closed-loop State Feedback | UNDETERMINED | 0 / 0 / 否 |
| 272 | Q46 | 2408.16844 | A framework for training and benchmarking algorithms that schedule robot tasks | UNDETERMINED | 0 / 0 / 否 |
| 273 | Q46 | 2406.11793 | FetchBench: A Simulation Benchmark for Robot Fetching | UNDETERMINED | 0 / 0 / 否 |
| 274 | Q46 | 2408.05478 | Multi-agent Planning using Visual Language Models | UNDETERMINED | 0 / 0 / 是 |
| 275 | Q46 | 2301.04195 | Orbit: A Unified Simulation Framework for Interactive Robot Learning Environments | UNDETERMINED | 0 / 0 / 否 |
| 276 | Q46 | 2401.12975 | HAZARD Challenge: Embodied Decision Making in Dynamically Changing Environments | UNDETERMINED | 0 / 0 / 否 |
| 277 | Q46 | 2402.08178 | LoTa-Bench: Benchmarking Language-oriented Task Planners for Embodied Agents | UNDETERMINED | 0 / 0 / 否 |
| 278 | Q46 | 2310.02071 | Towards End-to-End Embodied Decision Making via Multi-modal Large Language Model: Explorations with GPT4-Vision and Beyond | UNDETERMINED | 0 / 0 / 否 |
| 279 | Q47 | 2402.12659 | FinBen: A Holistic Financial Benchmark for Large Language Models | TITLE_METADATA_MISMATCH | 6 / 1 / 否 |
| 280 | Q47 | 2409.14913 | Towards a Realistic Long-Term Benchmark for Open-Web Research Agents | UNDETERMINED | 0 / 0 / 否 |
| 281 | Q48 | 2409.06289 | Automate Strategy Finding with LLM in Quant investment | UNDETERMINED | 0 / 0 / 否 |
| 282 | Q48 | 2407.00904 | Background-aware Multi-source Fusion Financial Trend Forecasting Mechanism | UNDETERMINED | 0 / 0 / 否 |
| 283 | Q49 | 2408.15950 | Atari-GPT: Investigating the Capabilities of Multimodal Large Language Models as Low-Level Policies for Atari Games | UNDETERMINED | 0 / 0 / 否 |

## 验证与输入来源

校验：283 行与 baseline 目标集合一一对应；50 题查询数量覆盖；248 份 raw hash/structured JSON 一致；主分类数量之和为 283；已确认 metadata 偏差均有同 GT ID 节点且原标题归一化不等；返回候选可追踪至 organic 位置及 parser ID。输入清单生成后、报告完成时再次复算全部 hash，确认文件未变。

下列清单是本次读取的数据文件 SHA-256；包括本地 ZIP，完整结果树及 replay。查询时的 API 凭据未读取或写入审计文件。

<details><summary>完整输入 SHA-256 清单</summary>

```json
{
  "/home/chenyi/pasa/data/RealScholarQuery/test.jsonl": "b3b570411ce2399ce4ea145ba9b2d3d0048b248030edeeb44ba95a7e9dc575c2",
  "/home/chenyi/pasa/data/paper_database/cs_paper_2nd.zip": "0bfbd6df2378da872d01544b74e5403cc91e1aa80fafa9fa3a674b2c62c4b8b7",
  "/home/chenyi/pasa/data/paper_database/id2paper.json": "dcbabaf06021dfc25fb97585a7066845fa6ba3a4d477aa155351841a700b74d5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/0.json": "dc54a082e2217c8d8ec986c04a3643f14bc242430801b320484f2bcd5909f2f3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_001.json": "d35644202cb51ec745c92f9110bd60487043845a68c86da94eda0fc821084e31",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_002.json": "becb6eba0526d04fdcf4ef467953b94d44880b5ed443da31af8d4643bb6fa07a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_003.json": "fde15ae1b3eb6044c30c9c81d321395034dff255fe69871ca9645ecabaf66a54",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_004.json": "916b8d41a4f2f81f21fc476d2547ab46b6dec3ab96727671c15d53adb45e5d12",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/serper_replay/serper_005.json": "76bcc7a6b2948dac63a03657a2ceb17f81302058b5bd5ea340220ac359abf64e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00/attempt_001/smoke_report.json": "f58984b4aafffc5115cbc21019474ebc26a9e6bb95998ad3d908a4a4f1dee824",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/0.json": "d965a4752b528b1faaed03e002811cd21fac62b5d393d16fd14dc8f2edd7a517",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_001.json": "c8da127be629dae5a2559478da6ea2fdf5935e9dc2b6b922e2913c4b6b5a942c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_002.json": "4460438ab9eb3f4dbeffccd4ab18494ef4cc5453791d4b32321723e8bd0c46e9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_003.json": "a9a01962d120e8e5b225dc90292e76be924cae96741ab02723d79d453c028074",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_004.json": "b7814aaea1a990eaf65830e6a80c032d62d5ed7a79916be5aca38b4b4afc4fea",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/serper_replay/serper_005.json": "4ea1793536a6cf8dfa26217e381da956871e42fbf245c0f647261970dde6d4bb",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q01/attempt_001/smoke_report.json": "b7fbee471b206cc2c1727114569498be30298595b0eb818a0b00da089d017f78",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/0.json": "d340ed798ee4dc90cb5d61b084b700d7919c64645339f122850ca5e1fea4082f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_001.json": "d4c191a75601149c4d2079f6a8a78c17c769b1f30837b09661ee7804777fb4bd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_002.json": "8b511c20cb4e2d7cd221e83efb67cff2ea2440436cf3a7ffa89c649a7ae1b30f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_003.json": "d94865b951efba9c386b56f3487d24931ceae8af7f9c01a83ad09db72b0176de",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_004.json": "112f328b174a5b0d5925a78b0c2b193b5b73d49bb7ef81bc82c207a1a5851593",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_005.json": "a2dba75aea14d71f54fd5816290b34ae227b01875556620896bfb6eb1c97c76e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/smoke_report.json": "23efb922d82e2b2c608157eb7a1499ac2b4de941dcfaba71b2027a238b6846f1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/0.json": "04aca1f157d4594d5a9c1d0a9b7764cca809e4bb054dae0b0781a84d80b69e62",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_001.json": "bc746fa7d8f6f8cb36dd9c14f33ca90b5a60b696a1ba9e8f6e488dfb65d12d9f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_002.json": "46d28ca1b7f89f2c23f82a8def5c66252701c108ff524f354ad193685e736cce",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_003.json": "1d029e08cbe0078636d1df8f075375f2fb4304571f612f87a386e0b53d2920b9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_004.json": "0fa44a0860837cfc4a8cf068415f65a523557343f9c98dda81ff268c9f6ff0be",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/serper_replay/serper_005.json": "3107a02337bfd7c5283b94c59233674652334e38e599968a726cf173a8a5e205",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q03/attempt_001/smoke_report.json": "acf15d3fbd11cc34b3344653f97a6bb4d26bd72162a7044c288ba4e7a9fa2a96",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/0.json": "6e5b8941e74a5fcc04c11ba0f490247995d6eb0ccec73244856f4f75bf6d28df",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_001.json": "21ffbccd9ee1eba406437fdb0fd21d19e1913118b295a08de38ee1abe3e4f854",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_002.json": "54dd0a3f868af03a67228a8f3bac808f2eb51be1ff1ac1c41da62b66f41d6435",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_003.json": "b346870aa10541116067c68476c0addcca6ae085f03b63ab3ca7a59072aaa718",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_004.json": "4d23e6f3d4e2afd69ba8b6afb223f1f10bc3216fcf9ecf0d68bc6af4b22d64fe",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/serper_replay/serper_005.json": "70e30abad814f384619765600aece8eb011e5d0b269900f9ed0f6efdb84bc0d6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q04/attempt_001/smoke_report.json": "617a3095fdc79a53ac758bc6dea7ad41ce8c8a26fdd0f588a3918317d8db312a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/0.json": "f0b5bd37da88a3eefd428cdf81016bb84e93f5730cfaf9e2cd9839e3ee3d0a0c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_001.json": "31363030a3db380487392f9d78bf76ca7e976780b7879ddb5faa5eb8b16be124",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_002.json": "6b6c275b8f0f290611ed9d8be7a7397054353c3ad35353f9a6d1751d1b7ae596",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_003.json": "8f0cd680db78072c35a112f1ab8adc8017c322060a6b3615626ee678ba8e8533",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_004.json": "844db6af60939529c0610ae6500d6e95b8de9f6276f6e95bb0b0a050581fc4eb",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/serper_replay/serper_005.json": "6c4315253a91ff142a79ed5144543b4cff9ffcaa2ee7d9f3c179b7e8f1d47347",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q05/attempt_001/smoke_report.json": "833b8159d4f7f8a096a83786d31ad46923f91e8375fa631f258a422c8aac39fa",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/0.json": "12970bd408f557ae04fa871fa53c4b70df157508175d46f44a39c911e7100cf6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_001.json": "5ad2eb2b1890dbdc4ac799ab62e46434d32312985e6168775c0d0fcc3f80e57a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_002.json": "17b379898785bce59e1e04c9c1379d94e38bd1676590d6893a6dd3306bb24dab",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_003.json": "3155638cb9e91056e256f138efadcafa30ebd26abd3c71cf094528c60838acfe",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_004.json": "cdbab268a69476dcb2fa34f99bbf748d0a3879e98e3233932c64483da25fae88",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/serper_replay/serper_005.json": "a7858588cdd493ef040d667f89abca3900d6cb065398f43757fc1009cf0ca6fd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q06/attempt_001/smoke_report.json": "cf8f8ce14d9476b378f5b6a7c832f7929e6e1b09528b9aa9b5ecbcad09a46c14",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/0.json": "96e6d0df8ad08e651ad7e832c2f522956b402e9c3cada202449426bd1a34ba9e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_001.json": "2d5f29db260e82e301f71c41b5c2902d17adf40e94299041ea5140325063bb43",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_002.json": "5adc2cf4faaf0ecafd785c0690fcfd3e9e8d183d3a4bd9571f8ff4caa42a00c4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_003.json": "563e479e250c65654c924e835874c0c2e799f2f652a61c79f33db16bcbd51131",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_004.json": "418b92953935afab92a96458cd2d8aaa00167246ed3866a9e93ad20bc92729cd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/serper_replay/serper_005.json": "9faa57dabf17ef2ca862a0bc7d7edb53ff98504d5f5d693a4df81a3bf04a0713",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q07/attempt_001/smoke_report.json": "ff09bc564d40500449dd4588c381148b500eff22129dd9862ccda0b13c5329ad",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/0.json": "8754b91cf0da9f75a73aa6fbf0fb06d94371e62278bf11ed98c77fcdd2360d63",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_001.json": "094f481cec43328583f4666ecc543e0b1c82fe1afad52c6f7de5ea8adfb7c8c8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_002.json": "1256383a6bfa279f45624d93488ec41b4d5e3b4d5caf0bf86c4d41f85a85471e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_003.json": "a58ad94bde7c177d39624c80e43ac8bbd29bba3468f9efe17a5d42211069c4e9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_004.json": "711b833640a15359f72176ac3a4393e9fad1957a80073ad3693f5e47c79cf106",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/serper_replay/serper_005.json": "4b50612ed3652e9897f5b4b8ebf1fe40363dc750a6ca7d89b0a93ce27bbdca88",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q08/attempt_001/smoke_report.json": "9cebb6006b63280b1deea6b2351f7b6f1f87b91e95322bba33188c7116856ee2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/0.json": "5ccef8cf3356a7c7826fe00b9675bd94aa20b25b1a09602d071fdc86956d3bdb",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_001.json": "0a7292140bff31bd5319d2428354218453c4bcfc248f710bc0d26c8f40ee4a5d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_002.json": "11dcb8b945e5df1ede37cf7747ca664dd5b7a759cbe7c9c404b1f92a5d85ece0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_003.json": "5355e2d5e843f09cdbe98c21d8910764a854f8ab5266410d6bb3462dc6c3865b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_004.json": "f1173a05674faed28c52f1d0f44104c0dc9029e3d9fb31161256fa3603eaf5c2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/serper_replay/serper_005.json": "31417805f6631adfc188b229ca18b51ed14fb0c92c614496e578f99a8ab4515a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q09/attempt_001/smoke_report.json": "ff316ee2285089b8567651db3cb4558e56c9f7c5e9754473b9de7409b4de6f76",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/0.json": "14971e9473b302217af624da80c7e9b0b31c0d26b64b1f8af2ac3d606284d2b5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_001.json": "e9b8b4e3c3b5d65050cd4933b236e5d169773a079d642e31d03b7ea3c356e6a8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_002.json": "48837b06cd75991b0673d34509bef2f2ab8b82226430ee909bdd3792e4486c97",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_003.json": "3b5a717929669676586598886906ac14053a0e19d2af907188a3e8af43eb23f0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_004.json": "443ec42c941a308ac20c9adc42eb46cac898ebe6034035c4f28224f945ae7d1d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_005.json": "08801db5ccb257dc3e7bd9e19d7a1ece816d29e295803c5cb9abeefafcd6a27f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/smoke_report.json": "d360613ffeaf537c437b5c6f3e9071169a83dbd05ae8ad1edada95453c7f4509",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/0.json": "5756ae5d409ff4cf0a7e405321eb6d79629df4bfbf724e38e74ef4a9fb8b87e9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_001.json": "98f81cb9c3dd0267610bb40ea3814f17f87bf6b2d8f79710d094fca5ef951b47",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_002.json": "d8506de0e8825ecc8c7f72ff4922e234b84fedca8c0b5bc08d831971ab153274",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_003.json": "fd122af6bf9ce5f24d12958e8124eed56b769aefeaac30b60844d0872925e4b6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_004.json": "88f665ff933c81611a5384bcedb0035adf6561d9c324fb8e3cb906283145d7a6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/serper_replay/serper_005.json": "6b73299ae777445eec36e21346253fa625301df697303ab578aaffdc45690843",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q11/attempt_001/smoke_report.json": "3fe2728053106fae94092ed3547042837e73fd5ecc2137224f23d2232210244c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/0.json": "be60a2d629fab370b771d1e0dd78bfad4555b583f02e23fba75bc77b541b6751",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_001.json": "7d7dabbf43b5dca96cc751ac80792454ca55fa18994d0495fb7783d75e3e7724",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_002.json": "ea215a3794dc60439e8ce1da70068be2863d4b9042ed89474cf1320dc439be7f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_003.json": "3d8aada7e3035f01a479d579ce5c9d696d8f1fb02e63e94adf5bee5a457a03ce",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_004.json": "bbd9722602e5b6159bc7d8df3da4a9d51d7311c200d0c0b9da8a6313e9735d3b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/serper_replay/serper_005.json": "cbea3e14e04feaa1e51f588b5c8fe97f93a17aa8cbca1cd4b19552446aad29a0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q12/attempt_001/smoke_report.json": "0a1d9dcf532a4a1a5448b5117f8eae5f9632fdf7f73c1bbb582b8e41a69dbccb",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/0.json": "83eadc5860ffe8373d456ec0ea16c6ea343ab78f8efcf286bdcb54497e1bbc78",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_001.json": "bda78b27eb0d3c5858a484020c1aeeff8d6ec836cc630f39390b6fbe17d5b939",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_002.json": "8c990650b7b20a6cad4ad3e8ebc1b7ee095cc370cf88b232e71e679670bc06f5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_003.json": "9377c61fa61e7c6355ff07adb78041af0e11b78fd44d034c2f404e9f1769d569",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_004.json": "ac5a7bc02ef4a6072d5977d026c0c8d2df100dd97163727c081616166e517a8b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/serper_replay/serper_005.json": "4cdf0ab0ad8544594037744f4592db855a401defbbea074b90f20e4e3a271793",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q13/attempt_001/smoke_report.json": "8df4e7ba15a925ef344237988deabe9ec5dc851aedf3cff5f9c58c9c870eebbc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/0.json": "dcdf5c5891d3f0613bf04317e5958d304a2d1de241b4a83daac95989ec7db875",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_001.json": "ba335dcabd7bf88859ae6558fd289feaf3e4751d6ad52c7733462fdff0a2bcfd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_002.json": "61e1788cee30e536dcff6cf0592fdec3c9a77af3a43b97ac3e016575d0332e08",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_003.json": "9027396284372421eaab1e7fb62007de522787ce82dc0525480b377d191cd2c5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_004.json": "e185bea65c4f711c4ca6886dbde7bed9e3a5241e53eccc1daa070d9545b35676",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/serper_replay/serper_005.json": "743a5757bd5fdab29616438375eb2b170883f519c95d9693bc38b9810aafafb4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q14/attempt_001/smoke_report.json": "beae72a9403f6aaf3a4f673822e91eaa50ac4f82706399899b886326b5c79a76",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/0.json": "ff52ba351ec42483080343afd5d26f425b2410e89a6e72bc806fd9a002bc6078",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_001.json": "1f5aaed5ffaf15e6ab129b49fc223d6b52d367bbee06f543361daa3f43952318",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_002.json": "fdb78e6cd6a3ba6e5b50215ec8b4301d59b961ea573a624ceffb8bda7e5d0d39",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_003.json": "4522d2bd98a902ba732dbaef16e35117d61a448b39d488c8238654580c7b6118",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_004.json": "d25869f742e8c1775786b6c78326f40bd1245cf9261df07d7fe066929ecea983",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/serper_replay/serper_005.json": "5ca88eb4359238b57bfae68f76fd03bcf3e62d7cd6cd0f9a9ddb2f5a4e134acc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q15/attempt_001/smoke_report.json": "69a679e4a905671a75d05f136eba1a4cf52314a9dd0c0b98dc1a086eb770eda1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/0.json": "d86aa16a3490858e030315dde7a53b5462fa0c020b01ecac53d17662480c5826",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_001.json": "a7715ac6c4c60ddcb894a2ee2feebb09ab7f118eaa09cca23d13ada21ae409d3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_002.json": "f187d49a0ab0d2f1964c1652d3558e2200fa78deb1b0c275d0e27bfed9b8256a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_003.json": "26ac0cea0de83fc9c03cfc691043a3a95f19f7412374a52125c1e48e3c15bee4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_004.json": "b87834fb3b4693b03eaedba192fba10f5f7607fb47ae4c9ae4ffcaa3c34a441e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/serper_replay/serper_005.json": "48e0c043a5e19687b9d7bb903b8aadce1759abfab1a2d1289dfd9d1c9959f080",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q16/attempt_001/smoke_report.json": "9fd11c1b9b1e01769120985dad3d93bca8574b45b7b7b91bd2908457ebde7046",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/0.json": "88e9cd4c702f0b08d4b9f3f08fa390860bf869722bafa569bcd8d7c82c5874c0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_001.json": "ebc76f3e2f61337f2169d3978da9cf2ae8612ae1417a24c8308592613b1f803b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_002.json": "c01839fff4d02b2370bfd5f9a41cab331de3c92ccb91768cd2fcb6a2d10e5a2d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_003.json": "b8966777980a54ea56886328633963429d6579f2966430e8c8686645bd7190f2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_004.json": "b1300d034e2aa7d076bbf16a5dc4832a7d7d94fe765dbc90938304f5fb624283",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/serper_replay/serper_005.json": "23f764f75f3ad80185ffa1500f88be598e5768eed2af2a69ebbebb2cf3c7edd7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q17/attempt_001/smoke_report.json": "e3e039c11dfb4b8911aa25a59ce302b3ac5bc127f244c55bf528402ccec49815",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/0.json": "81de11938843b0dbb518373609d2f154319ce1b552f5e518c2784120c7211dc5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_001.json": "e39a7effc1b1ffa76beba4c4a73c3da0a97e19153de02dd1915abc82540d4a01",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_002.json": "5e803651c4e18f4d4de5bcd21659f57a3f166e73ffb7d15005bc568a6f8b55dc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_003.json": "46352df353db12b943559ed4e607f99a685a8482544d82f482ce99c9465fa99e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/serper_replay/serper_004.json": "eb3808673114ced64318167bfaa39c1f1f8f9205abcb98786ea6bbfa60457403",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q18/attempt_001/smoke_report.json": "92484e79ea91f99afff26a9367f7af05024e2f5d8c22519eae28f852efa6ca59",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/0.json": "308be0a6cba92dfa948ca2cb94f840d4d7ea234c0b566d9e51a6bb2fb8a15d8e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_001.json": "832f7dc89ef442bcf04c2f85e78f691454dfbf5b5d25717e0cc4df92023307da",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_002.json": "44adb71d405753fa6080e401c02b923137987527d6bc5d398335de1663427a0c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_003.json": "a536cea4a3dbc2a63853f4adf8ad5b43d52cab88ae1dbd8f772b73b478f66cd6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_004.json": "c4685558823d477ac9e3032cd6cdc09a4152bb4b7beeffcb8ba198fe31e88bf0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/serper_replay/serper_005.json": "360411a2d8bcce1f215364c4d9ff9e9e62bd1f85b1fe8f1e4924aff6c4aa3380",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q19/attempt_001/smoke_report.json": "cfc664e5e737709ef540a1536f9ba8d3a1ffb8f7e97b7f6579a6c10e2830c42a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/0.json": "d07eb23f128bc61472b48915239961b8a86f79c0721ffe7abf74f7cf0fa6b571",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_001.json": "43c77039e835863f773dabfa9757e892326225ea20d10e453154887149a907a9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_002.json": "c1b110968f7b86fc1f5ce153e1127a8ee0ea28415407b372f87dee3cac3e8b53",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_003.json": "b764c4542aaa13725c0225d588c11e5ffdf4038c89f79b4f0b7ebd9f98c54797",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_004.json": "f93e1a820e35c57e0a12bfbaf2228d2dd2a23b181e2a416a943f7af62fb8d53d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/serper_replay/serper_005.json": "c7cf445bfa5ff1a5759da92f46a1e5df6b619fcb66862ad78a070ab833954655",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q20/attempt_001/smoke_report.json": "575cf222b8a8e7ed8a0a09b44e1b7014f0525a17999a48e9b6513e26536033a8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/0.json": "4735f86b2e3773e3cac0adbae1b9aa3eab3cb4f359860cfe5d23b10403d8bc7a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_001.json": "09c4907c19fa44dbf914f8eaf66f4c76c62b9ff5efa06e3a80e2803e349705a4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_002.json": "c03a970b54391ef04ec95bf5ef69a41fb23b65ef98a8c6dd0238756fee2ecc2b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_003.json": "01835d909832ab9dbb71dbbdfbd1d1e93cad842fe5e1df2226af1cd41179f733",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_004.json": "b6d96c3cd6f228489aabdc202eee3898606fbf22f05a093ffa201f4a3ca8c72f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/serper_replay/serper_005.json": "543e6e849b58a9c89882b22f2ed21069cc8bdcfa1376a6a2324ba9436f5001a2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q21/attempt_001/smoke_report.json": "3c351c758aaa5133cf269625dd4af51941c92b1067e9137809f2b582d5aa7227",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/0.json": "dc91778078381b0e857cfc40b5a4082d27221b9a8ee2e134a37b74a0b563b63d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_001.json": "f1e5d67688cdb5cfa7bbf89824d9d4b62c9066d435709971a05e76c42c6c7c9c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_002.json": "9a78f5801fe1de920487e003801360d165bdd95c67da6c4d9532292cf8ceb237",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_003.json": "1ecd00f933f17ebd076ddac8f8390139efadd18a1ee74c0829730c059622f4a8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_004.json": "7c7cabc85ccbf5c238383102b4686a96acdef88b71eb724121b9c7ec2956f6f8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/serper_replay/serper_005.json": "1379f3ab4c9df5a7813781a508db539db24afcfa134cfec4f35f777148b10c3f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q22/attempt_001/smoke_report.json": "5234f7a71ea965a999f820cb6cf806fe400df22f044e326b444c60c5a0f00cd3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/0.json": "af7efa3a94dd66497b0cab37967103317d7d19cc8340bcc14bf8c082793ac46e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_001.json": "5b04dfab2d3ff1d1078f074dce61a59cd0f4a5842ee8d6c053f8d05834252c63",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_002.json": "d87d455597d311245d3febffe56526ec55b709c317159d958804e345a0de1585",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_003.json": "a2867baf722358e86d30ba5b5ea87e53daab46cc626d3665cb40d53649aecf37",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_004.json": "b8d2e3617c9bcf9cc60a587260335a3f9ad0ac399060bb11ee275a411cedcbb2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/serper_replay/serper_005.json": "1890f38bc4cd3c437f7a7abd7e6f5ff55132e39c788ff37a7f5cb5ab484f52b6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q23/attempt_001/smoke_report.json": "e1bdfe2e4f0e3c6e13b0a296e70dafee25246dc1aef8ed97e173717da8e04895",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/0.json": "9965342f5e2cbc98e20a4fe399cb979fb22bdaee63d7420d10440129b902132f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_001.json": "bffaa929ac434bb5b48c9a120917be5bde3a566bd1a3d5f93b11c0096cf4cf56",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_002.json": "039ab0c721449a50afd0dba97395df436b9750f8f27d083c732dd46690913c30",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_003.json": "53d213c01ed20484d907b7415aa6e92520d5748e8c75e79962d52ab3a7bd5a8e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_004.json": "c638c2c6d637388095abb02d4a0d67659cb037df27770a78fd7ced022e73170c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/serper_replay/serper_005.json": "7b1c609695405aa08dcedc680d073a15437135530a11500a548094eac85a149e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q24/attempt_001/smoke_report.json": "b4dc4dc71d2c8a3b5589565c3c5ba4702863c31e8539067a5d95d433c6501518",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/0.json": "22a30077e4f9d3d324685a84588846f19cf89288da54ab1ee5e9f3ed6a1be093",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_001.json": "6d63a50f2ca2e7eaab596853adbbf0cdfb0fe6c720e8ceb59af07634f3b6f156",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_002.json": "491e056246b95131905920426c5209454339df19fa9deb8d17495ffe0002c7ac",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_003.json": "f013821cf8778654741ef6fcb42d7c5547b2d711d4268396583c34c2e563a9bc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_004.json": "9dc3b950eeea73993fd5c935baee21ab01277f73d716e5cc6420d3208740d998",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/serper_replay/serper_005.json": "1eb117691afff44fee1fb1a641ed802810456143b444bc1b9c2a9faae218d1b7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q25/attempt_001/smoke_report.json": "cf013417ad3ee305d38dadb2983df0e515f95dd247c6a4f5bc617b03db306f05",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/0.json": "ed5e9c98df763fae1e13067c2b48e8aa1a001d122988d2ac895ee7e0d61b04c7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_001.json": "00765e00479b23f40441932d9efade4c2ff5b7b5f540e5876e0d9d9263bd8c85",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_002.json": "a42071b1e417881314ff43b6686278021bd128a898522616e8199aa5b6438d27",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_003.json": "9499f6cfec55d25bed346881b9aafa36b051d080aeaca920ad79ae62c069ecf4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_004.json": "96d0e9c4830982cda2637c72f187a5222648fc20b93c491954264cf24afcd66b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/serper_replay/serper_005.json": "3117b3477c0c4b375cbd45a503bcfde63d11dda1b52c0d8cd5df3737017757a4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q26/attempt_001/smoke_report.json": "c2d52c3d206ebb3ff966a9b50d889728bac6cc48f986bf7ae914250fab4baf27",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/0.json": "18c4efe68c4e0e12235d7b9a8b9d781668aaafefa12e0734e54a3b9f16da1694",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_001.json": "54de0ef60aa12f4b4c1cb8b0fd30d5d350f71229fb95c197adb8d13967a18bbd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_002.json": "563edd75300e4b1c9ec595ed02c00eb950a59ddcc574161d5d179342073f075a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_003.json": "d02ec8fae61f89b7db4b6c2599fb3da3204d578bdeab6265d468d5fc9ade605a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_004.json": "0a7070d811d152d0bc735a94aaec635cc9f61cf74fb6d13c5bab8c3110758d05",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/serper_replay/serper_005.json": "bf6aee14075b0603b4be6cfcad3ddbeea8fc1457039b9dadf6a7981724657057",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q27/attempt_001/smoke_report.json": "a9944ea15640bb75e2a4a77f00cabb788ee79afc3757b730d701570c14417e6f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/0.json": "e8916b7b01b31f3bfbe7e9b70baabf7d56347c47824f900039e182119e555127",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_001.json": "502b494b6a3d91ea9bfce1c4bf9540934ba7923728452d7d19804e5ec57aec0d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_002.json": "189078726f2d3513f073e6cf6da7ecb006089aded6a84f267e156800f161c0bc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_003.json": "e3c67f3013e27e68558f8d2b2a883e1fdeeccbd100b8791464ca540f3a2570ce",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_004.json": "2501f904ec6884af8bfd6538013053c1606d20ac305886a2055a7ab32887055a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/smoke_report.json": "f21d89d18cc2c0324bcd6841bb0d59198f5c049cc962c3e518480d5cd03ff83d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/0.json": "54c19474db9e771a286d4f2037fe6c02e728c0bb2c5cb642d9b6c8611ef7ce55",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_001.json": "d424366a13de6854db39ea54ed0cc94ddff83516e68653263232dc35fa09fb0e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_002.json": "5c3623de2a7a9bc3feb3292abe49e399534b31030439ebc2fbdeffe00cb0b54b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_003.json": "b0a86253d9951f3cda068c59433a48e554bbe634e66f488e87dd9a8806f296f9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_004.json": "45a5671b1ed967a1569b5a370150f9e12d45eddbba1c43be029bbb99a05d9906",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/serper_replay/serper_005.json": "69f6c75b05ca70d652c67fa8bf3cd7e8e82ec6472142238abf92b504ae281ecf",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q29/attempt_001/smoke_report.json": "cdb176b9c25133ddd4cb694716565083a85586f5b04dab2325716b4cc5c0ac8c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/0.json": "7d986271ce245062d51a37d2ce13e5f26ddd2a53e4b09be338f63ef04fc2b1a7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_001.json": "1d710dc8bc345c738feccf15aecb433ef90b0d8c2b2eff03645f57f65bd337a5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_002.json": "54d488d5211e30fa88294ddc470fa548ff4b1a9fd5e92dca2c42a3a28987460e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_003.json": "f879146058b33e7948e453c4861e2772fab79385c079db3daf2b30b57955d79e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_004.json": "3173aa514f7b0f233d6644628123ad4c2b8e44205dac34322230cf5aa490185a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/serper_replay/serper_005.json": "8ce3f7ca8af5a249607fcccf787af15cbef6409874bec2990438462d5a471bde",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q30/attempt_001/smoke_report.json": "5d608528e38fa00245659e3d671dae8b79f6ee8a0aeac87c2b60f07c3b5ecb2b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/0.json": "f188914fdc4f898dee064e2db87647f4989946098eaa3b24ac31c9478ecb71f3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_001.json": "01bb683e2a4bb2a29d508dab439a62481fe3f01cdce583de3620ab2a19fadc47",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_002.json": "6eb2d5def65277eb35ac4d822696724cc395b982e0d70571b435c7956612c00c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_003.json": "a1ce6e2ef738712b95b0302e4b79fd87dcb8ce08866d4fba8036755823acb4f1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_004.json": "a86ba2b5a8ff6ab13cbc1e894618157adba8511d0a924c848652b659fbf2010c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/serper_replay/serper_005.json": "3e8df112e2c3f9dc42ae5f1c9eac6978338ae013314752ac14b05715dc5be280",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q31/attempt_001/smoke_report.json": "e08a3aa2248cc3b629de57de74dddbe494cd28b950b2754535ffdc0ad66362e7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/0.json": "b2c0bc838937edccc58aae7d3c88078e194e2d913600c9fd9714d0591f2f2727",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_001.json": "460c465a5321ef1f1d3aee2ded811221ee6abddfdafd79d0fc52470d4756fcb9",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_002.json": "f014e9ca7d3a24fb3f66c50e3932f7c5dd462dd41b3dabcf03a3b643a61bcfa3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_003.json": "1b815f62e49465626dbbd8cf2406b22b6afac7e25e094416142a256bf4ac7e10",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_004.json": "5dffe37d3100291a4729b032ccbe1ef3bc06e19687b92d98761fd7f7eca1f9db",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/serper_replay/serper_005.json": "b1083f220b198c4f554ec212469ee11ad65d975c5143b2f1e92b7d1b5c46939f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q32/attempt_001/smoke_report.json": "ba0a2b6e21ac1aafa2a5b9ef1f35aba32b9a20b394c2cfd9b52b5e2c8246fa5e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/0.json": "9479e0f762ded6407ca6154d392b82012977b4482e538afde65819e8d4bd55cc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_001.json": "d4f2061e7d1eb43db4a0b5f687aaeac3d2622b877f88e6538a44afb0ac5a8d13",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_002.json": "a566600512f9e7155764ccfb6a5546a89eb6202703f287f68d26941e5ede52fc",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_003.json": "c9ec79d9710036c06993f97de9c32e05c6c66501776c13afb83e247501464857",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_004.json": "9b38e1449806193ccc31c87d82f33872cfdc81e07a19ba5f3ea9a0e6ae84476b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/serper_replay/serper_005.json": "d1c68a9bdf97a851b2990d64844bf1563c9ce2932f7d04ef37c0eb704c7a1f1e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q33/attempt_001/smoke_report.json": "a7235f4ddbc1f581ebcb173bf5097a68c217a9978c65d0b9dc32eac011ad3f06",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/0.json": "fc5a2577d47a61d9a1507c2125dbcbe126de9bfec182113cb3e320e1edd6a571",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_001.json": "47e2e616a44218dc84943307706213a8021e6ee12b22243cdbba581995fe940d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_002.json": "dc75a4c40544e83fddbf1c3382ac468fe28903772f3ead325aa29ea972661f1f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_003.json": "8e13cebe9ace4ce1b0a9e38b427cb4c581b0337e36524b5aeb214a2a42f4d4a1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_004.json": "f94554557c39343533bef31936425a39a1bb9a8957f393ccf526e715b607a7cf",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/serper_replay/serper_005.json": "373828e3d2c446ebfb22c5f77bbd5237cbab89db42e62b110941ebcc325a2291",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q34/attempt_001/smoke_report.json": "19fbd8a3b17c29bf5d314e0418c0821c90dcda90f9a4af0a010dd41dc05ae804",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/0.json": "a540d8eb010e490064856917637b1a538aad1f3c51c8f4a2885cbbcc84159b46",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_001.json": "cd7fe4b42c9d097a850519d99ad20fc9a88e5e62584ef282a1e5933819bd98d0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_002.json": "e24d090e0198335bc4caf6cb196c11153e7608a4dc85009f9ca159b372e2bf5f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_003.json": "f280cb7a33bce6040f531ad57a61c10d2cbd5bf28d6a2050e6cc96c01d13dcc6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_004.json": "30e4dc37e0fe66c2db6d7451b72487aca2d2307aefbed1fc4d4d98dbbe047a8a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/serper_replay/serper_005.json": "ab91f8048791e15270549a95ec56d5798352f14728b4e8c0da32c0dbb1a644e8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q35/attempt_001/smoke_report.json": "aceaeb4db6f0867f7a3786ffc1f29b88a915dd16c82d203ca06e93b8c6ffa61f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/0.json": "af712ddef63a03452d9c0074408100807582197a88d3238ef6821bacad025dd5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_001.json": "038eb974bb97ecb35170f31216bd886a9287a8e95370d324d9c1159123a55e2f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_002.json": "f4b6b319846727964be1604a70fd6c8058d999f13db9fca7716b6cc384656520",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_003.json": "5dfc7ebee4ac1b5836e53edcd735d9bc94e0b5fd474c8489f1756928e53b2d7a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_004.json": "644e39518b2526c57407b651c4c7aa10ccd8e0f5625b77f3b4a4c4dd50dd372d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/serper_replay/serper_005.json": "ccb4685bad9d1b8e0c0b524266310baf39d3decc280b66747e3f20bbb7ab5e96",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q36/attempt_001/smoke_report.json": "9cc011a319737fdc3341d53ae571dda028e882e3a97c6ceaf4d602318725217f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/0.json": "d689205f4ffee95bff7bde97c5f1b5a2fe37af2dea950f4261c01406511d78c1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_001.json": "56da6266c58c3fbef33db8e546f70bc328f830d38c16ee5bc7334562c3856a44",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_002.json": "212f94781c107b0a2b3e74c612ee2b9e5ba361defa2d2ddb80937276aa1ce011",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_003.json": "654b69a8a8927aef8f70c4dd6a8ed963548e5cd9bfd8bd2e52e3db9fbabc531b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_004.json": "5838f0bbee6f610da5078543f3f577096e667403a47f743725271dd995824fc2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/serper_replay/serper_005.json": "0091788c5da07ae2687dd344c1efc73a2da636cde40a132c7e06a798dba45058",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q37/attempt_001/smoke_report.json": "8197449a247360f64250585a94da9d07a73f30f3cd1b0c523ad8d81501b6dde6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/0.json": "c081cd7679fdc836059ecc7bce28d640e645fa484cdb2703ec99463408cd605b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_001.json": "68db992b8fc3062bd3b1e2f0721ec59f30e382c3ad7ad0ca8769f67bb21cb5ed",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_002.json": "8b6a36a2a8ce80e34497cc245cea5ac141d524a7fa122bf76d1ee7e9b4e33069",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_003.json": "e95d3509596d7261030a9f15036b5975323cdaf694fe1d87365d4321d34c6166",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_004.json": "56e74324c13ed289ddc7b9c1950b9bec9f3c164e1e55f9a963bc2217cde0c9b4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/serper_replay/serper_005.json": "ebc2ec324218773902070e58e4f79a8184568f271a25e03614b3148f4b8a2be7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q38/attempt_001/smoke_report.json": "536eb2697cacac7e2e7f334bf7b67f21396b7b873bb1e948f71f4288f45abad0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/0.json": "e1b9e3661b43f1442ca7537f23bfbbf07c54f75b5036ebeb8c330d741c94bf6c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_001.json": "59e7cbe913c6dad688952619233080154e2c102990fe6e715d4b61c2cce24630",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_002.json": "aae5eb74129b4e7cc5ccc1d72562dc734f0ec5a379970220006a2bb94e8d7c09",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_003.json": "5e70bcd746d06086bf37cae57b4b95770bfc0ac60f4607306acef8d9a5d1e501",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_004.json": "2dca57d477105d24facc99a800359f46ed4e7c0dd2dc9889d442fde0578e6ce2",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/serper_replay/serper_005.json": "e35eadab087a77a223b08639dbd9f63feff3d0a4f8b60ee9777eb191464f7333",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q39/attempt_001/smoke_report.json": "e0b89bffa7f9867d8e3a516f7d58ea2fec089952fd58a3fc9696133be55f9032",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/0.json": "3d5099f79d68d76f1d04816756b58dc93dd58207b7527707d2c31889907d3b8c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_001.json": "a66445e1384c25e3c784bced5b2ca731bcf9e925bcccd0ab6adc9c81a0d169c7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_002.json": "076ad6481d02f5ec3ab562be27dddd1e32d1e90e116f249e8f7e87fd675ec5a1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_003.json": "fd1495a863a0624a99217eeed991b5e0bb210fd2d502e6620ba8da327ef8cfdf",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_004.json": "ed3071a8cb8539187f8a8c5213024b904897e3ca472c5bb567d511f6d9d51872",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/serper_replay/serper_005.json": "eccd1555304dea6396ccee191911dba6d5a308d08c2b134c60b043ab19e24466",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q40/attempt_001/smoke_report.json": "38de1fbb0499bdfac41c3c8d3abbd332cf31c89dd81e0aca71ef8d009819c910",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/0.json": "818fe993a1f1c5384c26b660117eaf5b23c15ba248ee3613b8e2a922985aae5f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_001.json": "9ab18567a39e8d8d93784c888a9761ddb89bf5f8218d08a62ca4d3dc91d4b854",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_002.json": "67b7cc3427ee52222769a63595f267d4f0e3645201070b2d77ba1068c474c764",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_003.json": "1caf16f9ed5dbf98023e43414b9ecce49b3979e8811dc2ca89b33d8f90e49385",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_004.json": "5f1b897fcb0359bfb059c1acdd938a673b2a731a6c7e827c0663c65eef824d3d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/serper_replay/serper_005.json": "289bea95de68850a903096337243f15d6d5aad70da358c29418b16310a051783",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q41/attempt_001/smoke_report.json": "778661a26f63d5840c4d8b7be0ba3bbd36d5afd1a36e072d1b2830d2571ceff4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/0.json": "f744a80fcd5fae0a34d60ba21b4caedd43cffc349ff68454a90990edeccca9ac",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_001.json": "b244980d52537019247a5774e38b53f7ab3c5936be48db3d7204f4a1f7475562",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_002.json": "0d6f47594db9bd3935afc08bed1f143d13645f9c9922e09c53909e7568a1c70a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_003.json": "1c8d96cc4a82454c3beac4fa904736046f69625bdb752cbeb7a8f150bccfa8b6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_004.json": "ea31f68decc5791e16ea19d4b939e44c7fd3a6d40d5a03b84310f1d803e10b1c",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/serper_replay/serper_005.json": "bc21f0d5dfee00ec2e7e60c194e56bc9c779259b533024a0fd1426f0abbeee5f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q42/attempt_001/smoke_report.json": "3403b1dc0b6eab03735f385b9d0c47b34f901fc6b4fe0cf5c1fb0cc1dad6c85f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/0.json": "96b946542e3f530b4bc17955613051612351902a8ad840e63b865f294af6fd33",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_001.json": "c46438f2c9ad7d16619402a5a9be322b8f971275576bfeabe0ecfcd795fe0d3f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_002.json": "ab26dd3eeaf46cf53dc641f6b8a3591474c9958942b1261ae0acc3f445ce7d7a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_003.json": "82719ba548397dab08c27c8e4886a021f9dcc2b66b391ed0aea8735755f88f1a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_004.json": "d825cecdd055416dbe9dd6c48b312b4222ed84c4e12c6ef60620d0c3acb76375",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/serper_replay/serper_005.json": "1744958c2f12cf16188c51b07d02470f72481feba56a1257e8c53d92b4ca322e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q43/attempt_001/smoke_report.json": "6c0f4c78a20e5b7f7599fde1457c865d5f386dd12a8245804ab54ac54975c38e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/0.json": "e2065b09301142b5bb4fc37b54fa09c896695f35512f1488aebd4564a3833d2e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_001.json": "8d277bb79f1532bbd07565724f1b0262a64526638730f32073acd9ea5ef69f62",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_002.json": "3bab1f20ce89e251ea3ddef056bc229ea11ce58e8db7bef0afc4239a7e030689",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_003.json": "d235ab1802f58262c833d8ac1ea5d9ef85def0e12549d9582b79d4b6179b3bf8",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_004.json": "c1cb9574b0dd47a7df0b2f3f3741aed07c7bd423c92200d8c821c0d01775237e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/serper_replay/serper_005.json": "15db7b516163de4f75070f2523947f1e18352af2cf6fc2e49e5561862e17153f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q44/attempt_001/smoke_report.json": "9ed6a6636e20369299d83faed0e2e3f4e9b157f0ac4e2c340e6b5c8f789f5389",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/0.json": "5f0bfcff0631a28a8674595e1bcf3b86562355cdda43e95bf27a1e6bc8936a97",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_001.json": "5d0b958f3b87e2904793aa5daca612b865feef329299476a8209e5f8eb32cd2a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_002.json": "b34ac5db5d4940927a1ab3aff666bf7acb1097ae70df5f00b11c1616f255197b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_003.json": "102e5008c5b2da7b81c105a329ffe27c92d34552b898f3cfdbb3760cf13fc86e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_004.json": "c74267e255387b1e3ef501b66ca65f163d949eb7b8d0b4e8116747cf2c1174c3",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/serper_replay/serper_005.json": "a96a5feba37a22a510c5491c4a17d0c9f1b9973a6f372164ebc0484f2fc73221",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q45/attempt_001/smoke_report.json": "16a3829cb3909aaa37b250f8680c3e32ffae7d5104a36283313fece4e109f35b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/0.json": "be2e77ef0ac4964548eea123f4afcf4c6a89660d9c986485371c53488f5baa8a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_001.json": "499b9e1e1a357367f77b09097f40ddc37b6496e2bc2b22803a44b3f4b4e23292",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_002.json": "0d7d1884167e98ee39b9c110d42d6c046b92ec9116d34bd9b8737d639383bc5f",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_003.json": "5a2bcda0ec67464d041f389177a7511aacb93e9d899cc7639113999434c83c0b",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_004.json": "4f07f43fefbc7b56020b89b3420f300cd7a86836b857e15399cf25d52f72ff68",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/serper_replay/serper_005.json": "5080eaf200651091b2e2aafe80a5c7a6c92203fdbca1654bfa9681ba37bcd6bf",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q46/attempt_001/smoke_report.json": "cee8084d3f107392702d84fd70aa45858eb6aef50c3721324b53917b7c9f8ebd",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/0.json": "599507194befe25933622b32ab44c182a8db85b11e381c4d24be51fc370b2241",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_001.json": "0a7a03c3d68bf8bb54130f044f1b82f2d3f3ef6b826167a8fca9bb0789b582e5",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_002.json": "ff83e3126e24922a54b917dd4ab441413989c7df555b87bc34bea27436e487b0",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_003.json": "c475ce9c3c96704c13350a49b667f0b53c60be1a607c57a3d2090ae27b4d69f1",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_004.json": "0ca506b520be06ff5040b8e270c13d8afe73d0b1d23de04d8a9b88038546b340",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/serper_replay/serper_005.json": "b948424f671d6fbcb2aea95d86be02b2e9bab1eefcd4d57b81f97085c533bd88",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q47/attempt_001/smoke_report.json": "9845a56d39ba1f7f4d84dd7bfe1ec43f74f8be92bb7f981973a0a54529252627",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/0.json": "50e42711d14755f29e5b693a6bf837e797b3b607c9856141094030362f2f2d72",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_001.json": "d9de290725e7ef59e5bb8939c0fcb0b8bf3618962718c9e43c1fac0f2b72f07e",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_002.json": "5490297a474b2f0e1b19881bcff678908fe149193f8aa8adc262217cb48d2752",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_003.json": "2f925eedd734ad702d617b36e63f85fff8d8340f353db329190838b641fb58a7",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_004.json": "aa4336ffb60351d298f802124b3be6d99f3e211982c072b607cde97a424c8fbf",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_005.json": "e9b210e337779e288f8e00dad0ca53c817771e75994fe55b40793db2fd80d99d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/smoke_report.json": "79a57747cf8837e5db922215ea281a071e90aa74c385d8badd42eedc9faee793",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/0.json": "2fe7eab59f6cdbfb12d6ace115a082446846eea642b8c01c7fcfd26003aa84e6",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_001.json": "512312d9a53668ff2f605002432c80aba38b4f22685534e8b0c8d4207824702d",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_002.json": "5662f6c96b110eb79cf1f2ff1ad6f7d85c6baaea92930299e1d6de09cfd608b4",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_003.json": "c64886b6701955b972406898dd5e950504fe8c72ac1ae1a23f3cf833623d2f1a",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_004.json": "546f99d47bef23735245d41118b6cae2ba58e7ea1649126f408a373276eaa515",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/serper_replay/serper_005.json": "9a743f468ee36be5b033c4b3e6b9344651cfde376a80aa1c3257d39bc7221085",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q49/attempt_001/smoke_report.json": "17c7e20716fee354965607e6a4ea88b5e5055784f2f6f5740e63698f9c796553",
  "/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/summary.json": "1dfee0130a74963c7be9105c785d6f939d9442974feeeb7ecc82c78d32ddc190"
}
```

</details>

## 优化候选排序：潜在 Recall 收益 / 成本 / 风险（本阶段均未实现）

排序依据为证据强度、可解释的影响范围及成本/风险，不声称已测得新策略 Recall。表中的“涉及 miss”只是待验证集合，不能当作预计恢复数或相加；真实新增 Recall 的下界均为 0。

| 优先级 | 候选 | 潜在收益与证据 | 实现成本 | 风险 |
|---:|---|---|---|---|
| 1 | 增设基于 GT ID 的诊断评测及阶段归因，保留冻结 title 指标 | 已确认 7 个阶段误判，其中 6 个实际上已选中；实际检索 Recall 增量为 0，但能避免把评测偏差当成检索优化收益 | 低，利用已有 GT ID/节点 | 低至中；需处理重复 ID、版本和 GT 映射问题，不可直接替换官方标题口径 |
| 2 | 验证 query 关键约束保留（Q28、Q48） | 涉及 4 个原 miss；Q28 两篇本地摘要提及 HumanEval/MBPP，Q48 Automate Strategy Finding 摘要明确 alpha mining/factors；现有返回没有对应候选，恢复数量未知 | 低至中 | 中；测试集定向调词可能过拟合，应抽象成通用约束保留规则并用独立数据验证 |
| 3 | 从其他题已返回 GT 的查询中提取可泛化检索分面 | 8 个目标 GT 已在其他题响应直接可见；它们是有实证的候选覆盖机会。只有这 8 个全部在原题形成并正确匹配节点，才对应 Crawler micro recall 的 8/790≈1.01 个百分点条件增量；最终 Recall 未知 | 中，先审查任务对应关系 | 中；他题查询可能改变任务范围，必须避免用 GT 标题硬编码 query |
| 4 | 对高重复查询对验证替换/分面检索 | 7 题满足查询+响应双重冗余阈值，涉及 42 个原 miss；存在 847 个全量跨查询重复 ID 槽位，但这些槽位不等于新增 GT | 中，需要新的受控响应才能验证 | 中；去重可能损失有用的重复召回/排序信号，旧 replay 不能评价新 query |
| 5 | 评估更大 top-k/分页 | 当前没有深排名响应，潜在收益未知；只能作为新的受控实验，不能把 276 个未确定样本全记作预计可恢复 GT | 中至高，增加 API/论文获取/Selector 负载 | 高于前项；运行成本、显存和扩展路径均改变，需保留序列化与失败门控 |
| 6 | 评估 ID–标题别名用于 resolver | 22 条有 metadata 标题差异，但 0 条属于“尚无同 ID 节点且已知别名在可见引用里”；本组尚未确认能由 resolver alias 新增召回的案例，低于 query 方向 | 中 | 中；错误合并污染身份，部分差异只需诊断评测处理 |
| 7 | 扩展索引/非 arXiv 来源 | 本次所有目标均有 GT arXiv ID，没有确认 source/indexability 根因；暂无可量化收益，优先级低 | 高 | 高；来源身份映射、评测口径和获取链路都扩大 |

针对 parser/dedup，本次没有确认的 returned-but-dropped 案例，不建议以本审计为依据优先改写。Q35 的 Quantitative、Q41 的 soft target data 以及其他宽窄漂移可作为 query 质量检查样例，但同题仍有正确查询，不能承诺修复后的 Recall 收益。
