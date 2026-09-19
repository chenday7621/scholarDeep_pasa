# QUERY_PLANNER_V1_SEARCH_AB_001

A→B：正式 Search macro recall **20.9770% → 10.7500%**（-10.2270 pp；相对 -48.7532%）；GT 命中 **138 → 80 / 790**；实际 Serper 调用 **248 → 108**。

B 新找回 19 个 GT，丢失 A 原先找到的 77 个 GT；净变化 -58。这些数量均按 (Q, 归一化 GT 标题) 计数。

**生成格式需要单独看待：A 有 0 个 Q、B 有 20 个 Q 没有可解析的 Search query；A/B 含 `[Expand]` 标记的生成分别为 0/24。这些标记只是模型输出文本，没有执行 Expand，也没有改成 Search 后补跑。零 query 的题保留在 50 题 Recall 分母中。**

标题获取也有限制：共有 145 个直接返回 ID 未能取得原生标题，正式标题匹配不会计入它们。该结果包含本次元数据基础设施失败的影响；另附 ID-aware 诊断，A/B 为 164/100 个 GT ID，未用来替代正式指标。

## 一次性固定实验

- 数据：RealScholarQuery-50 Q0–Q49。每 Q 的 A/B 都重新生成并执行真实 Serper；无旧 baseline/PAGE2 搜索结果复用，无本地 Search 响应缓存。
- Checkpoint：`/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler`；同一 Crawler、同一 generation config、同一 GPU、batch_size=1。每次 A/B generate 前均重置 seed=42，PYTHONHASHSEED=42。只传原生 max_new_tokens=512，不覆盖 sampling 参数。
- 原采样参数：do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05。prompt 固定，无多次试验后挑结果或根据 GT 修改 query。
- A 从仓库 `agent_prompt.json` 直接读取完整原始字符串，包括原始空白；B 使用用户指定文本。两组均用原生 chat template 和 `[Search]` parser。
- 原生 parser：`Search\](.*?)\[` + DOTALL，strip 后最多保留前 5 条。未补 query、未因重复而删除 query、未将 `[Expand]` 文本转成 Search。
- 请求：同一 Serper endpoint/凭据；page=1、num=10、site:arxiv.org。source_meta.published_time=20241001，按原脚本减 7 天，因此全部 before:2024-09-24。before 是请求中的搜索操作符，没有额外本地日期过滤。
- 每 Q 先产生 A/B 输出，再按 query 序号交错请求两组。偶数 Q 先 A，奇数 Q 先 B；同文本也分别发真实请求。少 query 组结束后另一组继续，绝不补齐。
- 按相同 query 序号配对的首次请求共有 108 对；开始时间差中位数 1.167s，最大 2.913s。紧邻执行降低时间差异，不能保证搜索索引完全不变。

### A prompt（原生）

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.
User Query: {user_query}
```

### B prompt（固定 V1）

```text
Please generate up to 5 mutually complementary search queries to find relevant papers according to the User Query.

Requirements:

- Preserve important entities, benchmarks, methods, tasks, comparison relations, exclusions, and negations from the user query across the query set.
- If the user query contains an acronym, preserve the original acronym in at least one search query.
- Do not invent datasets, models, methods, benchmarks, or technical mechanisms not supported by the user query.
- Avoid superficial paraphrases or highly redundant queries.
- Generate fewer than 5 queries if additional queries would only be redundant.

User Query: {user_query}
```

## 正式评测口径

- 沿用冻结 `utils.keep_letters`：仅保留 Unicode 字母并转小写；标题完全相等才算命中，不使用 fuzzy/alias/embedding，也不按 GT ID 替代正式匹配。原始 791 条标注归一化为 790 个 (Q,title) GT；碰撞按冻结规则保留，不修 evaluator。
- 只对 Serper organic URL 经原生正则解析得到的 arXiv IDs 评测。ID 正则保持原样：`arxiv.org/(abs|pdf|html)/(\d{4}\.\d+)`；不从 snippet 或站外链接补候选。
- 候选标题使用未改动的原生 `search_paper_by_arxiv_id`：本地 ZIP 记录优先，缺失时仅按已返回 ID 查询原生 arXiv 元数据。同一 ID 在 A/B 使用共享标题快照。没有标题搜索、引用搜索或新候选补充；未解析到标题的 ID 不用 GT/Serper 展示标题替代。
- **SEARCH_RECALL 为 macro**：50 个逐 Q recall 的平均值。MICRO_SEARCH_RECALL 为总命中 GT / 790。
- **SEARCH_RECALL_PER_CALL = 命中 GT 数 / 实际 Serper HTTP 尝试次数**，单位为 GT/调用，不是百分比，也不是 recall 再除调用数。失败尝试计入成本；另列 logical calls。
- unique candidates 同时报告：全组跨 Q 去重 ID 数、逐 Q 去重后求和的 (Q,ID) 数。后者与逐题评测/候选处理量更接近。
- 用原始 `metrics.py` 对 Search-only 候选树复算，A/B macro recall 与独立汇总均一致。验证树中的 select_score=0 仅为满足文件结构；未运行 Selector，其余 Selector/ranking 输出不作实验指标。

## A/B 总体结果

| 指标 | A：Baseline | B：V1 |
|---|---:|---:|
| TOTAL_GT | 790 | 790 |
| SEARCH_GT_FOUND | 138 | 80 |
| SEARCH_RECALL（正式 macro） | 20.9770% | 10.7500% |
| MICRO_SEARCH_RECALL | 17.4684% | 10.1266% |
| SEARCH_RECALL_PER_CALL（GT/调用） | 0.556452 | 0.740741 |
| Serper calls（HTTP attempts） | 248 | 108 |
| Logical Search calls / queries | 248 | 108 |
| Unique candidate arXiv IDs（全组去重） | 1143 | 675 |
| Unique candidates（逐 Q 去重后求和） | 1440 | 746 |
| 成功取得标题的全组 ID 数 | 1034 | 592 |
| 未取得标题的全组 ID 数 | 109 | 83 |
| 无可解析 query 的 Q 数 | 0 | 20 |
| 空 query / 未 EOS 生成数 | 0 / 0 | 0 / 0 |

Macro 绝对变化 **-10.2270 pp**，相对变化 **-48.7532%**。Micro 绝对变化 **-7.3418 pp**，相对变化 **-42.0290%**。

| GT 分组 | 数量 |
|---|---:|
| B 新找回、A 未找到 | 19 |
| A 找到、B 丢失 | 77 |
| 两组都找到 | 61 |
| 两组都没找到 | 633 |

逐题 Recall：提升 8 题、下降 28 题、持平 14 题。

格式可用性的描述性分解：B 无可解析 query 的 20 题，A 命中 54 个 GT，B 命中 0；其余 30 题，A/B 命中 84/80。这只是分解完整结果，没有从正式 50 题指标中剔除格式失败，也不能据此推断修复格式后的效果。

## Query 数量、重复与结果 overlap

A query 数量分布：`{'5': 48, '4': 2}`；B：`{'4': 19, '0': 20, '3': 10, '2': 1}`。

| 指标 | A | B |
|---|---:|---:|
| 规范化后完全重复 query 对 | 0 | 0 |
| 词集合 Jaccard≥0.85 的近重复 query 对 | 0 | 0 |
| 同题不同 query 之间重复的 ID occurrences | 891 | 287 |
| 各题 query 对返回 ID Jaccard 的平均值 | 0.220772 | 0.124949 |

重复 query 使用小写字母数字 token 序列精确比较；近重复只作词面诊断。ID overlap 矩阵及每对重叠 ID 保存在 JSON 的 per_query[].groups.A/B.query_overlap 中。少于 2 条 query 的题其 overlap 均值记为 0，因此该汇总也受零 query/少 query 影响，不单独视作质量改善。

## Recall 提升与下降最大的 Q

### 提升最大

| Q | GT | A 命中 / Recall | B 命中 / Recall | Δ Recall | B 新增 / 丢失 |
|---|---:|---|---|---|---|
| Q21 | 2 | 0 / 0.0000% | 1 / 50.0000% | +50.0000 pp | 1 / 0 |
| Q16 | 8 | 2 / 25.0000% | 3 / 37.5000% | +12.5000 pp | 2 / 1 |
| Q48 | 8 | 1 / 12.5000% | 2 / 25.0000% | +12.5000 pp | 1 / 0 |
| Q49 | 8 | 0 / 0.0000% | 1 / 12.5000% | +12.5000 pp | 1 / 0 |
| Q0 | 9 | 0 / 0.0000% | 1 / 11.1111% | +11.1111 pp | 1 / 0 |

### 下降最大

| Q | GT | A 命中 / Recall | B 命中 / Recall | Δ Recall | B 新增 / 丢失 |
|---|---:|---|---|---|---|
| Q26 | 2 | 2 / 100.0000% | 0 / 0.0000% | -100.0000 pp | 0 / 2 |
| Q14 | 9 | 5 / 55.5556% | 0 / 0.0000% | -55.5556 pp | 0 / 5 |
| Q30 | 6 | 3 / 50.0000% | 0 / 0.0000% | -50.0000 pp | 0 / 3 |
| Q34 | 7 | 3 / 42.8571% | 0 / 0.0000% | -42.8571 pp | 0 / 3 |
| Q40 | 5 | 2 / 40.0000% | 0 / 0.0000% | -40.0000 pp | 0 / 2 |

## Q0–Q49 逐题结果

| Q | GT | A queries/calls | B queries/calls | A found | B found | A Recall | B Recall | Δ | 新增/丢失 | A/B candidates |
|---|---:|---|---|---:|---:|---|---|---|---|---|
| Q0 | 9 | 5/5 | 4/4 | 0 | 1 | 0.0000% | 11.1111% | +11.1111 pp | 1/0 | 29/22 |
| Q1 | 29 | 5/5 | 0/0 | 5 | 0 | 17.2414% | 0.0000% | -17.2414 pp | 0/5 | 29/0 |
| Q2 | 21 | 5/5 | 3/3 | 3 | 3 | 14.2857% | 14.2857% | +0.0000 pp | 0/0 | 23/15 |
| Q3 | 42 | 5/5 | 0/0 | 3 | 0 | 7.1429% | 0.0000% | -7.1429 pp | 0/3 | 38/0 |
| Q4 | 44 | 5/5 | 0/0 | 3 | 0 | 6.8182% | 0.0000% | -6.8182 pp | 0/3 | 36/0 |
| Q5 | 7 | 5/5 | 3/3 | 1 | 1 | 14.2857% | 14.2857% | +0.0000 pp | 0/0 | 33/21 |
| Q6 | 24 | 5/5 | 2/2 | 1 | 0 | 4.1667% | 0.0000% | -4.1667 pp | 0/1 | 20/12 |
| Q7 | 35 | 5/5 | 0/0 | 3 | 0 | 8.5714% | 0.0000% | -8.5714 pp | 0/3 | 32/0 |
| Q8 | 16 | 5/5 | 4/4 | 5 | 5 | 31.2500% | 31.2500% | +0.0000 pp | 0/0 | 32/27 |
| Q9 | 39 | 5/5 | 0/0 | 6 | 0 | 15.3846% | 0.0000% | -15.3846 pp | 0/6 | 24/0 |
| Q10 | 15 | 5/5 | 3/3 | 3 | 4 | 20.0000% | 26.6667% | +6.6667 pp | 1/0 | 36/25 |
| Q11 | 20 | 5/5 | 4/4 | 4 | 6 | 20.0000% | 30.0000% | +10.0000 pp | 2/0 | 17/18 |
| Q12 | 17 | 5/5 | 0/0 | 3 | 0 | 17.6471% | 0.0000% | -17.6471 pp | 0/3 | 28/0 |
| Q13 | 12 | 5/5 | 0/0 | 3 | 0 | 25.0000% | 0.0000% | -25.0000 pp | 0/3 | 22/0 |
| Q14 | 9 | 5/5 | 0/0 | 5 | 0 | 55.5556% | 0.0000% | -55.5556 pp | 0/5 | 40/0 |
| Q15 | 5 | 5/5 | 3/3 | 1 | 1 | 20.0000% | 20.0000% | +0.0000 pp | 0/0 | 33/24 |
| Q16 | 8 | 5/5 | 3/3 | 2 | 3 | 25.0000% | 37.5000% | +12.5000 pp | 2/1 | 20/19 |
| Q17 | 9 | 5/5 | 0/0 | 2 | 0 | 22.2222% | 0.0000% | -22.2222 pp | 0/2 | 32/0 |
| Q18 | 5 | 4/4 | 0/0 | 1 | 0 | 20.0000% | 0.0000% | -20.0000 pp | 0/1 | 31/0 |
| Q19 | 37 | 5/5 | 3/3 | 4 | 4 | 10.8108% | 10.8108% | +0.0000 pp | 1/1 | 22/17 |
| Q20 | 4 | 5/5 | 0/0 | 1 | 0 | 25.0000% | 0.0000% | -25.0000 pp | 0/1 | 36/0 |
| Q21 | 2 | 5/5 | 4/4 | 0 | 1 | 0.0000% | 50.0000% | +50.0000 pp | 1/0 | 31/28 |
| Q22 | 3 | 5/5 | 4/4 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 31/33 |
| Q23 | 2 | 5/5 | 4/4 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 25/17 |
| Q24 | 11 | 5/5 | 3/3 | 4 | 3 | 36.3636% | 27.2727% | -9.0909 pp | 0/1 | 33/27 |
| Q25 | 1 | 5/5 | 0/0 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 32/0 |
| Q26 | 2 | 5/5 | 0/0 | 2 | 0 | 100.0000% | 0.0000% | -100.0000 pp | 0/2 | 14/0 |
| Q27 | 9 | 5/5 | 3/3 | 4 | 3 | 44.4444% | 33.3333% | -11.1111 pp | 0/1 | 25/19 |
| Q28 | 4 | 4/4 | 3/3 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 28/23 |
| Q29 | 8 | 5/5 | 4/4 | 3 | 2 | 37.5000% | 25.0000% | -12.5000 pp | 0/1 | 28/34 |
| Q30 | 6 | 5/5 | 0/0 | 3 | 0 | 50.0000% | 0.0000% | -50.0000 pp | 0/3 | 26/0 |
| Q31 | 15 | 5/5 | 0/0 | 3 | 0 | 20.0000% | 0.0000% | -20.0000 pp | 0/3 | 20/0 |
| Q32 | 16 | 5/5 | 4/4 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 23/18 |
| Q33 | 13 | 5/5 | 4/4 | 5 | 5 | 38.4615% | 38.4615% | +0.0000 pp | 0/0 | 27/18 |
| Q34 | 7 | 5/5 | 0/0 | 3 | 0 | 42.8571% | 0.0000% | -42.8571 pp | 0/3 | 23/0 |
| Q35 | 7 | 5/5 | 0/0 | 2 | 0 | 28.5714% | 0.0000% | -28.5714 pp | 0/2 | 29/0 |
| Q36 | 33 | 5/5 | 4/4 | 9 | 7 | 27.2727% | 21.2121% | -6.0606 pp | 1/3 | 30/28 |
| Q37 | 10 | 5/5 | 0/0 | 3 | 0 | 30.0000% | 0.0000% | -30.0000 pp | 0/3 | 24/0 |
| Q38 | 17 | 5/5 | 4/4 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 36/37 |
| Q39 | 2 | 5/5 | 4/4 | 0 | 0 | 0.0000% | 0.0000% | +0.0000 pp | 0/0 | 34/30 |
| Q40 | 5 | 5/5 | 0/0 | 2 | 0 | 40.0000% | 0.0000% | -40.0000 pp | 0/2 | 27/0 |
| Q41 | 5 | 5/5 | 4/4 | 2 | 2 | 40.0000% | 40.0000% | +0.0000 pp | 0/0 | 29/24 |
| Q42 | 10 | 5/5 | 4/4 | 2 | 1 | 20.0000% | 10.0000% | -10.0000 pp | 0/1 | 46/37 |
| Q43 | 28 | 5/5 | 3/3 | 6 | 3 | 21.4286% | 10.7143% | -10.7143 pp | 1/4 | 32/23 |
| Q44 | 25 | 5/5 | 4/4 | 6 | 5 | 24.0000% | 20.0000% | -4.0000 pp | 1/2 | 30/30 |
| Q45 | 57 | 5/5 | 4/4 | 11 | 9 | 19.2982% | 15.7895% | -3.5088 pp | 3/5 | 28/22 |
| Q46 | 65 | 5/5 | 4/4 | 7 | 8 | 10.7692% | 12.3077% | +1.5385 pp | 3/2 | 36/39 |
| Q47 | 4 | 5/5 | 0/0 | 1 | 0 | 25.0000% | 0.0000% | -25.0000 pp | 0/1 | 23/0 |
| Q48 | 8 | 5/5 | 4/4 | 1 | 2 | 12.5000% | 25.0000% | +12.5000 pp | 1/0 | 20/24 |
| Q49 | 8 | 5/5 | 4/4 | 0 | 1 | 0.0000% | 12.5000% | +12.5000 pp | 1/0 | 37/35 |

## Q18、Q28、Q43、Q48 详细结果

### Q18

Original Question: Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

GT=5；Recall delta=-20.0000 pp；B 新增=0，B 丢失=1。

**A 组**：queries=4，实际 Serper calls=4，unique candidates=31，GT found=1/5，Recall=20.0000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection | 8 | 2308.10792, 2312.08725, 2312.10302, 2401.01335, 2406.08660, 2408.03562, 2408.06663, 2408.13296 |
| 2 | Zero-shot detection of LLM-generated content | 10 | 2301.11305, 2306.05540, 2310.05103, 2310.05130, 2310.05165, 2310.14724, 2401.12070, 2405.04286, 2405.16133, 2410.13966 |
| 3 | Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text | 9 | 2303.07205, 2308.10792, 2310.14724, 2402.09282, 2405.10523, 2406.08660, 2406.17633, 2408.13296, 2507.05157 |
| 4 | Evaluation of LLM-generated text in zero-shot scenarios | 10 | 2305.13242, 2307.11729, 2309.13205, 2310.14724, 2312.01044, 2401.12070, 2401.17390, 2402.01383, 2405.04793, 2405.10516 |

原始模型输出：

```text
[Search]Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection
[Search]Zero-shot detection of LLM-generated content
[Search]Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
[Search]Evaluation of LLM-generated text in zero-shot scenarios
[StopSearch]
```

**B 组**：queries=0，实际 Serper calls=0，unique candidates=0，GT found=0/5，Recall=0.0000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| — | 无可解析 Search query；未补跑 | 0 | — |

原始模型输出：

```text
[Expand]Performance comparison between LLMs and supervised fine-tuned small classification models
[Expand]Academic studies on zero-shot detection of LLM-generated text
[StopExpand]
```

GT 命中明细（仅冻结标题匹配）：

| GT 原始标题 | arXiv ID | A | B | 分组 |
|---|---|---|---|---|
| MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark | 2310.13606 | 未找到 | 未找到 | both_missed |
| Who Wrote This? The Key to Zero-Shot LLM-Generated Text Detection Is GECScore | 2405.04286 | 找到 | 未找到 | B_lost |
| Zero-Shot Detection of LLM-Generated Text using Token Cohesiveness | 2409.16914 | 未找到 | 未找到 | both_missed |
| DetectGPT-SC: Improving Detection of Text Generated by Large Language Models through Self-Consistency with Masked Predictions. | 2310.14479 | 未找到 | 未找到 | both_missed |
| Fighting fire with fire: The dual role of llms in crafting and detecting elusive disinformation | 2310.15515 | 未找到 | 未找到 | both_missed |

### Q28

Original Question: Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

GT=4；Recall delta=+0.0000 pp；B 新增=0，B 丢失=0。

**A 组**：queries=4，实际 Serper calls=4，unique candidates=28，GT found=0/4，Recall=0.0000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | Survey papers on code evaluation datasets | 9 | 2107.03374, 2305.01210, 2311.10372, 2312.15223, 2402.18041, 2406.00515, 2406.12655, 2408.16498, 2410.01837 |
| 2 | Middle difficulty level code evaluation datasets | 9 | 2308.12950, 2311.10372, 2312.14852, 2403.04814, 2403.07974, 2404.06041, 2406.00515, 2407.21579, 2409.09054 |
| 3 | Code evaluation datasets with mid-level hardness | 10 | 2109.14430, 2203.01439, 2205.04980, 2305.12945, 2401.10491, 2402.08100, 2402.10176, 2402.19450, 2407.00981, 2407.09424 |
| 4 | Comparison studies on difficulty levels of different code evaluation datasets | 9 | 2311.10372, 2312.14852, 2402.17168, 2403.07974, 2406.12655, 2407.21579, 2408.05715, 2408.16498, 2409.09054 |

原始模型输出：

```text
[Search]Survey papers on code evaluation datasets
[Search]Middle difficulty level code evaluation datasets
[Search]Code evaluation datasets with mid-level hardness
[Search]Comparison studies on difficulty levels of different code evaluation datasets
[StopSearch]
```

**B 组**：queries=3，实际 Serper calls=3，unique candidates=23，GT found=0/4，Recall=0.0000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | Middle difficulty level code evaluation datasets | 9 | 2308.12950, 2311.10372, 2312.14852, 2403.04814, 2403.07974, 2404.06041, 2406.00515, 2407.21579, 2409.09054 |
| 2 | Comparison of code evaluation datasets hardness | 10 | 1312.4986, 1903.05503, 2205.04980, 2302.02104, 2308.09658, 2401.10491, 2402.10176, 2402.19450, 2407.00981, 2407.09424 |
| 3 | Academic articles on mid-level hardness code evaluation datasets | 10 | 1812.09510, 2203.01439, 2205.04980, 2302.02104, 2401.10491, 2402.10176, 2402.19450, 2403.12503, 2407.09424, 2407.13054 |

原始模型输出：

```text
[Search]Middle difficulty level code evaluation datasets
[Search]Comparison of code evaluation datasets hardness
[Search]Academic articles on mid-level hardness code evaluation datasets
[StopSearch]
```

GT 命中明细（仅冻结标题匹配）：

| GT 原始标题 | arXiv ID | A | B | 分组 |
|---|---|---|---|---|
| PythonSaga: Redefining the Benchmark to Evaluate Code Generating LLM | 2401.03855 | 未找到 | 未找到 | both_missed |
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | 2310.06770 | 未找到 | 未找到 | both_missed |
| CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution | 2401.03065 | 未找到 | 未找到 | both_missed |
| NaturalCodeBench: Examining Coding Performance Mismatch on HumanEval and   Natural User Prompts | 2405.04520 | 未找到 | 未找到 | both_missed |

### Q43

Original Question: AI for Science papers, especially protein design and DPO of antibody design.

GT=28；Recall delta=-10.7143 pp；B 新增=1，B 丢失=4。

**A 组**：queries=5，实际 Serper calls=5，unique candidates=32，GT found=6/28，Recall=21.4286%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | AI tools for protein design | 10 | 2104.04883, 2201.07338, 2202.01079, 2302.04611, 2310.09685, 2312.06297, 2402.04268, 2402.10516, 2405.01983, 2407.03154 |
| 2 | Research on DPO in antibody design | 6 | 2006.01174, 2012.15585, 2210.08270, 2403.04187, 2403.16576, 2406.10833 |
| 3 | Survey papers on protein design using AI | 8 | 2109.13754, 2201.07338, 2310.09685, 2402.04268, 2402.08703, 2402.10516, 2407.03154, 2408.11363 |
| 4 | Application of AI in scientific research papers | 9 | 1802.07228, 2304.10578, 2306.06699, 2307.10265, 2311.11175, 2312.09843, 2402.08565, 2404.01268, 2408.06292 |
| 5 | AI advancements in protein design | 7 | 2204.10673, 2211.16742, 2312.00080, 2402.04268, 2402.10516, 2408.11363, 2408.17241 |

原始模型输出：

```text
[Search]AI tools for protein design
[Search]Research on DPO in antibody design
[Search]Survey papers on protein design using AI
[Search]Application of AI in scientific research papers
[Search]AI advancements in protein design
[StopSearch]
```

**B 组**：queries=3，实际 Serper calls=3，unique candidates=23，GT found=3/28，Recall=10.7143%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | AI techniques in protein design | 8 | 2007.08383, 2201.07338, 2201.12459, 2203.00854, 2209.12643, 2312.06297, 2402.04268, 2402.10516 |
| 2 | Research on DPO in antibody design | 6 | 2006.01174, 2012.15585, 2210.08270, 2403.04187, 2403.16576, 2406.10833 |
| 3 | Application of AI in scientific research papers | 9 | 1802.07228, 2304.10578, 2306.06699, 2307.10265, 2311.11175, 2312.09843, 2402.08565, 2404.01268, 2408.06292 |

原始模型输出：

```text
[Search]AI techniques in protein design
[Search]Research on DPO in antibody design
[Search]Application of AI in scientific research papers
[StopSearch]
```

GT 命中明细（仅冻结标题匹配）：

| GT 原始标题 | arXiv ID | A | B | 分组 |
|---|---|---|---|---|
| Generative AI for Controllable Protein Sequence Design: A Survey | 2402.10516 | 找到 | 找到 | both_found |
| Graph Denoising Diffusion for Inverse Protein Folding | 2306.16819 | 未找到 | 未找到 | both_missed |
| Protein Design with Guided Discrete Diffusion | 2305.20009 | 未找到 | 未找到 | both_missed |
| Fold2Seq: A Joint Sequence(1D)-Fold(3D) Embedding-based Generative Model<br>  for Protein Design | 2106.13058 | 未找到 | 未找到 | both_missed |
| Diffusion Language Models Are Versatile Protein Learners | 2402.18567 | 未找到 | 未找到 | both_missed |
| Protein structure generation via folding diffusion | 2209.15611 | 未找到 | 未找到 | both_missed |
| A Text-guided Protein Design Framework | 2302.04611 | 找到 | 未找到 | B_lost |
| Protein Structure and Sequence Generation with Equivariant Denoising<br>  Diffusion Probabilistic Models | 2205.15019 | 未找到 | 未找到 | both_missed |
| Protein sequence design with deep generative models | 2104.04457 | 未找到 | 未找到 | both_missed |
| How to Hallucinate Functional Proteins | 1903.00458 | 未找到 | 未找到 | both_missed |
| PiFold: Toward effective and efficient protein inverse folding | 2209.12643 | 未找到 | 找到 | B_new |
| ProGen: Language Modeling for Protein Generation | 2004.03497 | 未找到 | 未找到 | both_missed |
| Protein Design by Integrating Machine Learning with Quantum Annealing   and Quantum-inspired Optimization | 2407.07177 | 未找到 | 未找到 | both_missed |
| Decomposed Direct Preference Optimization for Structure-Based Drug   Design | 2407.13981 | 未找到 | 未找到 | both_missed |
| A framework for conditional diffusion modelling with applications in motif scaffolding for protein design | 2312.09236 | 未找到 | 未找到 | both_missed |
| Fast protein backbone generation with SE(3) flow matching | 2310.05297 | 未找到 | 未找到 | both_missed |
| SE(3) diffusion model with application to protein backbone generation | 2302.02277 | 未找到 | 未找到 | both_missed |
| AlphaDesign: A graph protein design method and benchmark on AlphaFoldDB | 2202.01079 | 找到 | 未找到 | B_lost |
| Structure-informed Language Models Are Protein Designers | 2302.01649 | 未找到 | 未找到 | both_missed |
| Preference optimization of protein language models as a multi-objective<br>  binder design paradigm | 2403.04187 | 未找到 | 未找到 | both_missed |
| Deep Generative Modeling for Protein Design | 2109.13754 | 找到 | 未找到 | B_lost |
| Antigen-Specific Antibody Design via Direct Energy-based Preference<br>  Optimization | 2403.16576 | 找到 | 找到 | both_found |
| Protein Conformation Generation via Force-Guided SE(3) Diffusion Models | 2403.14088 | 未找到 | 未找到 | both_missed |
| Generative De Novo Protein Design with Global Context | 2204.10673 | 未找到 | 未找到 | both_missed |
| Leveraging Deep Generative Model For Computational Protein Design And Optimization | 2408.17241 | 未找到 | 未找到 | both_missed |
| PDB-Struct: A Comprehensive Benchmark for Structure-based Protein Design | 2312.00080 | 找到 | 未找到 | B_lost |
| Controllable Protein Design with Language Models | 2201.07338 | 未找到 | 未找到 | both_missed |
| Generative artificial intelligence for de novo protein design | 2310.09685 | 未找到 | 未找到 | both_missed |

### Q48

Original Question: Papers that explore using large language models for mining factors in stock exchange analysis.

GT=8；Recall delta=+12.5000 pp；B 新增=1，B 丢失=0。

**A 组**：queries=5，实际 Serper calls=5，unique candidates=20，GT found=1/8，Recall=12.5000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | Application of large language models in stock market analysis | 10 | 2303.17564, 2311.10723, 2401.11641, 2402.03659, 2406.10811, 2406.11903, 2407.18103, 2407.18957, 2408.06361, 2409.08281 |
| 2 | Role of AI and language models in stock prediction | 8 | 2304.07619, 2401.01487, 2401.11641, 2402.03659, 2404.05101, 2407.18103, 2407.18957, 2409.08281 |
| 3 | Impact of large language models on stock exchange analysis | 10 | 2303.17564, 2401.11641, 2402.03659, 2406.10811, 2406.11903, 2406.19966, 2407.18103, 2407.18957, 2408.06361, 2409.08281 |
| 4 | Use of GPT-3 in stock market trend analysis | 10 | 2307.13617, 2309.17322, 2311.06273, 2401.11641, 2402.06698, 2404.05101, 2406.11903, 2407.18957, 2409.08281, 2412.19245 |
| 5 | Survey papers on large language models in stock exchange analysis | 9 | 1908.10063, 2303.17564, 2311.10723, 2401.11641, 2402.03659, 2406.10811, 2406.11903, 2408.06361, 2409.08281 |

原始模型输出：

```text
[Search]Application of large language models in stock market analysis
[Search]Role of AI and language models in stock prediction
[Search]Impact of large language models on stock exchange analysis
[Search]Use of GPT-3 in stock market trend analysis
[Search]Survey papers on large language models in stock exchange analysis
[StopSearch]
```

**B 组**：queries=4，实际 Serper calls=4，unique candidates=24，GT found=2/8，Recall=25.0000%。

| Query # | 实际生成 query | 返回 unique ID 数 | IDs |
|---|---|---:|---|
| 1 | Investigations on the use of large language models for predictive modeling in stock markets | 10 | 2401.11641, 2402.03659, 2402.06689, 2402.06698, 2404.07452, 2406.10811, 2406.11903, 2406.19966, 2407.18103, 2409.08281 |
| 2 | Extraction of factors influencing stock exchange using large language models | 9 | 2402.03659, 2404.07452, 2406.10811, 2406.11903, 2406.19966, 2407.18957, 2408.06361, 2409.06289, 2409.08281 |
| 3 | Role of AI and NLP in stock market prediction | 9 | 2107.09055, 2208.13564, 2304.14544, 2309.00136, 2401.01487, 2401.11641, 2407.02236, 2407.03689, 2409.08281 |
| 4 | Application of GPT-2 model in stock market prediction | 8 | 2304.07619, 2308.16771, 2311.06273, 2402.03659, 2402.06698, 2404.05101, 2407.18957, 2409.08281 |

原始模型输出：

```text
[Search]Investigations on the use of large language models for predictive modeling in stock markets
[Search]Extraction of factors influencing stock exchange using large language models
[Search]Role of AI and NLP in stock market prediction
[Search]Application of GPT-2 model in stock market prediction
[StopSearch]
```

GT 命中明细（仅冻结标题匹配）：

| GT 原始标题 | arXiv ID | A | B | 分组 |
|---|---|---|---|---|
| Unveiling the Potential of Sentiment: Can Large Language Models Predict Chinese Stock Price Movements? | 2306.14222 | 未找到 | 未找到 | both_missed |
| Automate Strategy Finding with LLM in Quant investment | 2409.06289 | 未找到 | 找到 | B_new |
| LLMFactor: Extracting Profitable Factors through Prompts for Explainable Stock Movement Prediction | 2406.10811 | 找到 | 找到 | both_found |
| Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models | 2304.07619 | 未找到 | 未找到 | both_missed |
| Linking microblogging sentiments to stock price movement: An application of GPT-4 | 2308.16771 | 未找到 | 未找到 | both_missed |
| Alpha-GPT: Human-AI Interactive Alpha Mining for Quantitative Investment | 2308.00016 | 未找到 | 未找到 | both_missed |
| FinLlama: Financial Sentiment Classification for Algorithmic Trading Applications | 2403.12285 | 未找到 | 未找到 | both_missed |
| Background-aware Multi-source Fusion Financial Trend Forecasting Mechanism | 2407.00904 | 未找到 | 未找到 | both_missed |

## ID-aware diagnostic（不替代正式指标）

直接使用数据标注的 GT arXiv IDs 对 Search URL ID 做匹配。Q45 的归一化标题碰撞仍保持冻结处理；ID 口径有 791 个 (Q,ID)，正式标题口径为 790。诊断差异可能来自标题写法或元数据失败，不将 ID 命中自动补进正式结果。

| 指标 | A | B |
|---|---:|---:|
| GT IDs | 791 | 791 |
| Found GT IDs | 164 | 100 |
| Micro ID recall | 20.7332% | 12.6422% |
| Macro ID recall | 24.7565% | 13.2837% |
| 按 annotated ID 找到的归一化 GT 组 | 164 | 100 |

## 运行时间与请求健康

- 实验执行 UTC：2026-09-14T02:51:09.993979+00:00 → 2026-09-14T04:31:33.170496+00:00；总实验 wall time **6023.18s（100.39 分钟）**，包括加载、生成、搜索、元数据/评测及两执行阶段之间的等待。
- 生成+Search 阶段：688.26s；元数据+评测阶段：5243.41s。
- 报告生成 UTC：2026-09-14T07:40:49.969904+00:00；从实验启动到本次报告落盘共 289.67 分钟，其中评测结束后到报告生成的间隔为 189.28 分钟。此间隔不计为 Search/元数据实际运行时间。
- Serper HTTP attempts：A 248，B 108，合计 356。失败 attempts A/B=0/0；最终失败 logical calls=0/0；429=0/0。
- HTTP status：A `{'200': 248}`；B `{'200': 108}`。每条逻辑请求最多 3 次；固定 15/60 秒 connect/read timeout、1/2 秒 backoff，Retry-After 最长 30 秒；这些基础设施参数 A/B 一致。
- 标题元数据（A/B 共用）：1371 个直接 Search ID，成功解析 1226；原生 arXiv 元数据 HTTP 请求 585，429=376。这些不是 Serper calls，也不增加候选。
- 元数据 HTTP/传输状态分布：`{'429': 376, '503': 11, 'None': 196, '200': 2}`；None 表示没有收到 HTTP 响应，具体异常类型保存在逐请求记录中。
- 元数据未解析 IDs：1311.6877, 1406.7536, 1610.05683, 1802.07228, 1804.11238, 1902.09483, 1904.06145, 1904.10251, 1909.08593, 1910.10939, 1912.10514, 2010.05316, 2012.12989, 2012.15585, 2101.06125, 2101.06317, 2112.07491, 2112.13677, 2201.07338, 2201.12459, 2202.11027, 2204.12966, 2205.02886, 2205.07877, 2206.03066, 2206.14307, 2207.07810, 2207.10882, 2208.13564, 2209.13435, 2210.16493, 2211.06318, 2301.03505, 2301.13331, 2302.00599, 2302.03954, 2302.11449, 2303.03846, 2303.09014, 2304.05977, 2304.10578, 2304.14544, 2305.03394, 2305.11461, 2305.14239, 2305.17888, 2305.18086, 2305.18505, 2306.01694, 2306.05171, 2306.06699, 2306.13176, 2307.02502, 2307.07515, 2307.08214, 2307.10265, 2307.10930, 2307.13617, 2308.16771, 2309.00136, 2309.02352, 2310.00300, 2310.05492, 2310.06489, 2310.09685, 2310.10669, 2311.06273, 2311.06329, 2312.15216, 2312.15223, 2401.01483, 2402.06698, 2402.07681, 2402.08115, 2402.09402, 2402.11014, 2402.15809, 2402.18571, 2403.00157, 2403.03643, 2403.04187, 2403.06735, 2403.10075, 2403.11287, 2403.13000, 2404.05159, 2404.07981, 2404.13191, 2405.01466, 2405.03111, 2405.06695, 2405.09161, 2405.09589, 2405.10516, 2405.11804, 2405.16579, 2406.01017, 2406.04216, 2406.06027, 2406.06254, 2406.06699, 2406.07259, 2406.09170, 2406.10305, 2406.10361, 2406.11176, 2406.19413, 2407.00707, 2407.02048, 2407.02236, 2407.04383, 2407.12693, 2407.16965, 2407.17699, 2407.17902, 2407.17915, 2408.00764, 2408.05795, 2408.06292, 2408.11646, 2408.11822, 2408.15950, 2408.16498, 2408.17241, 2409.00031, 2409.00089, 2409.00398, 2409.04600, 2409.12917, 2412.09248, 2412.18819, 2412.19245, 2501.01793, 2506.04133, 2506.19408, 2506.20918, 2507.05157, 2507.16971, 2508.05289, 2509.05390, 2510.04950, 2510.07290, 2510.14179, 2606.10392, 2607.07162。未解析造成的正式标题覆盖限制与 ID diagnostic 均已保留。

## 复核与边界

- 原始响应、payload、HTTP status、UTC/latency、返回 ID/标题、每个 GT 的 A/B 证据和增失分组都保存在 JSON。每次 HTTP attempt 另有独立文件，可检查未改写的响应。
- 冻结源码/配置、baseline 文件和既有实验文件已做前后 SHA-256 校验；原始 metrics.py 验证结果在 provenance.official_evaluator_verification。
- 此结果比较的是固定 prompt 的一次 seed=42 Search-only 测量，包含模型是否遵守原生 Search 格式的影响。少量 query 与低成本不自动等于更好；per-call 与总 Recall 必须一起看。
- 同一 before 日期不能冻结搜索引擎索引或排序；A/B 请求紧邻且交错，但仍不是完全静态检索环境。
- 没有运行 Citation Expand、Selector、完整 PaSa；没有 facet/acronym expansion 模块，没有外部 LLM，没有 page2、prompt 调优或 GT-based query 修改，没有 Git commit。实验到此结束，未继续修改 V1。

输出：`QUERY_PLANNER_V1_SEARCH_AB_001.json`、`QUERY_PLANNER_V1_SEARCH_AB_001.md`；独立运行/评测脚本及请求证据在 `query_planner_v1_search_ab_001/`。
