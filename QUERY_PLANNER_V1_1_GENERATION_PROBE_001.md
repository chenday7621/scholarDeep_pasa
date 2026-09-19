# QUERY_PLANNER_V1_1_GENERATION_PROBE_001

A/B Search parse success：**50/50 → 50/50**；非 Search action 题数：**0 → 0**；总 query 数：**248 → 247**。

本轮只检验单次固定 seed 的输出格式与词面重复情况。是否更好地保留实体、benchmark、比较及否定条件，是否引入无依据的具体名称，均等待人工审核；不使用 GT，不宣称语义质量提升或检索 Recall。

## 固定实验与边界

- Q0–Q49，只解码 RealScholarQuery-50 原始 question 字段。每题 A 后紧邻生成 B，各一次，共 100 次；没有重采样或筛选结果。

- checkpoint：`/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler`；物理 GPU 1（NVIDIA A100-PCIE-40GB），batch_size=1。A/B 每次 generate 前重置 seed=42，进程 PYTHONHASHSEED=42，max_new_tokens=512。

- 两组使用同一原生 chat template、tokenizer 和 checkpoint generation config；仅传原生 max_new_tokens，不改 sampling。do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05。

- A 直接读取原生 agent_prompt.json；两组均沿用原生推理的外层 strip。B 固定为用户指定 V1.1 文本。原生 parser `Search\](.*?)\[` + DOTALL，strip 后最多前 5 条。没有补齐、去重、修复格式或将 Expand 改写为 Search。

- 仅以本地文件加载 Crawler；HF 离线模式及 Python 网络审计钩子禁止 Internet socket / DNS。未调用 Search、Serper、Expand、Selector、外部 LLM/API 或元数据查询。

- baseline、源码、先前 V1 Search 实验及配置前后哈希一致。独立脚本不导入 PaSa 主流程。未更改 checkpoint、baseline、evaluator；未提交 Git。

- 未加入 facet planner、acronym expansion、constraint extraction JSON 或 repair model。

### A prompt（原始模板）

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.
User Query: {user_query}
```

### B prompt（固定 V1.1 模板）

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.

Keep explicit important entities, benchmarks, methods, comparison relations, exclusions, and negations from the User Query in the search queries. Avoid introducing unsupported specific models, datasets, methods, or benchmarks.

Please return only [Search] queries followed by [StopSearch].

User Query: {user_query}
```

## 统计口径

- Parse success 指原生 parser 在该题解析出至少一条 query；零 query 题保留在 50 题分母。另列严格格式指标，以区分“可解析”与“仅含 Search 条目且以 StopSearch 结束”。

- 非 Search action 统计原始输出中除 Search / StopSearch 外的 action 形括号标记，同时报告涉及题数和标记次数；未知标记并不自动证明真正执行了动作。本实验不会执行任何生成动作。

- exact duplicate query 数按同题完全相同字符串的多余条目 sum(count−1) 计算；另列配对数。大小写或标点不同不算 exact。

- Token 使用小写 ASCII 字母数字集合，标点与下划线分词，不移除停用词、不词干化。Jaccard ≥ 0.85 计为高相似；near-duplicate 排除 exact。只比较同题的最终 queries，不跨题计重复。

- 同时报告所有 query pair 的汇总平均 Jaccard，以及有至少两条 query 的题等权平均；没有 pair 的题不人为记零。阈值和分析代码在生成前固定。词面相似只能作为重复诊断，不能判断语义冗余或信息覆盖。

## Q0–Q49 逐题机械统计

| Q | A/B queries | A/B 非 Search action 标记次数 | A/B exact 重复条目 | A/B 高相似 pairs | A/B 平均 Jaccard |
|---|---:|---:|---:|---:|---:|
| Q0 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3870/0.4545 |
| Q1 | 5/5 | 0/0 | 0/0 | 0/0 | 0.5260/0.5463 |
| Q2 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3574/0.3761 |
| Q3 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3072/0.3413 |
| Q4 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3696/0.3955 |
| Q5 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2643/0.2258 |
| Q6 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4565/0.2620 |
| Q7 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3350/0.2740 |
| Q8 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2786/0.3406 |
| Q9 | 5/4 | 0/0 | 0/0 | 0/0 | 0.2262/0.2738 |
| Q10 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3145/0.3676 |
| Q11 | 5/4 | 0/0 | 0/0 | 0/0 | 0.3465/0.4143 |
| Q12 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3260/0.2679 |
| Q13 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3016/0.2589 |
| Q14 | 5/5 | 0/0 | 0/0 | 0/0 | 0.1958/0.1734 |
| Q15 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4438/0.4547 |
| Q16 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4136/0.2900 |
| Q17 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3745/0.3671 |
| Q18 | 4/4 | 0/0 | 0/0 | 0/0 | 0.2390/0.1794 |
| Q19 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3041/0.3872 |
| Q20 | 5/5 | 0/0 | 0/0 | 0/0 | 0.1617/0.1332 |
| Q21 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2027/0.1804 |
| Q22 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3521/0.2570 |
| Q23 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4011/0.3830 |
| Q24 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3919/0.3000 |
| Q25 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2504/0.2910 |
| Q26 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4257/0.3409 |
| Q27 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3814/0.2887 |
| Q28 | 4/5 | 0/0 | 0/0 | 0/0 | 0.3265/0.3559 |
| Q29 | 5/5 | 0/0 | 0/0 | 0/0 | 0.1017/0.1139 |
| Q30 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4553/0.4712 |
| Q31 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4576/0.4342 |
| Q32 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3996/0.3795 |
| Q33 | 5/5 | 0/0 | 0/0 | 0/0 | 0.4209/0.4889 |
| Q34 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3792/0.2746 |
| Q35 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2095/0.2899 |
| Q36 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3747/0.4167 |
| Q37 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3097/0.2499 |
| Q38 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2258/0.2675 |
| Q39 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2204/0.2264 |
| Q40 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3204/0.2283 |
| Q41 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2111/0.2607 |
| Q42 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2269/0.3918 |
| Q43 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2239/0.2391 |
| Q44 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2754/0.2859 |
| Q45 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3743/0.3291 |
| Q46 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2554/0.2409 |
| Q47 | 5/5 | 0/0 | 0/0 | 0/0 | 0.2824/0.3169 |
| Q48 | 5/5 | 0/0 | 0/0 | 0/0 | 0.3454/0.1804 |
| Q49 | 5/5 | 0/0 | 0/0 | 0/0 | 0.1925/0.2371 |

## 非 Search action 与高相似证据

A：非 Search 标记分布 `{}`；无 query 题：无。

A 无达到阈值的 query pair。

B：非 Search 标记分布 `{}`；无 query 题：无。

B 无达到阈值的 query pair。

## 运行与复核

- 生成阶段 UTC：2026-09-14T08:03:22.259349+00:00 → 2026-09-14T08:07:37.155288+00:00；wall time 254.83s（4.25 分钟，包括 checkpoint 哈希、加载与落盘）。

- 网络钩子阻止了 1 次事件：`['socket.__new__']`。这是 socket 创建阶段的拒绝，不是成功的网络请求；未记录调用栈，无法归因到具体库。生成次数 100；原始记录位于 `query_planner_v1_1_generation_probe_001/raw_generations/`。

- JSON 保存完整 prompt、token IDs、原始输出、解析结果、seed、时间、运行配置、checkpoint 与源码哈希，以及每个 pair 的统计。人工审核表覆盖全部 50 题，中文翻译仅用于审核。独立复核证据保存在 `query_planner_v1_1_generation_probe_001/validation.json`。

## 最终统计与重点原始输出

| 指标 | A：Baseline | B：V1.1 |
|---|---:|---:|
| Search parse success（题数 / 50） | 50 | 50 |
| 无 Search query 题数 | 0 | 0 |
| 严格 Search 格式题数 | 50 | 50 |
| 非 Search action 题数 | 0 | 0 |
| 非 Search action 标记出现次数 | 0 | 0 |
| 含 Expand / StopExpand 题数 | 0 | 0 |
| 总 query 数 | 248 | 247 |
| 每题 query 数分布 | {"4": 2, "5": 48} | {"4": 3, "5": 47} |
| 空 query 数 | 0 | 0 |
| exact duplicate query 数（重复条目） | 0 | 0 |
| exact duplicate pair 数 | 0 | 0 |
| 高相似 pair 数（Jaccard ≥ 0.85，含 exact） | 0 | 0 |
| near-duplicate pair 数（排除 exact） | 0 | 0 |
| 全部题内 pair 数 | 492 | 488 |
| 平均 pairwise token Jaccard（所有 pair） | 0.319038 | 0.310582 |
| 平均 pairwise token Jaccard（有 pair 的题等权） | 0.318457 | 0.310068 |
| 未以 EOS 结束的生成数 | 0 | 0 |
| 超过原生 5 条上限的生成数 | 0 | 8 |

B 有 8 题生成超过 5 条 Search query（Q0、Q4、Q7、Q20、Q38、Q42、Q44、Q45），原生截取前共 257 条，最终保留 247 条。A 截取前后均为 248 条。超出上限的 10 条仍完整保存于 JSON 的原始输出、all_parsed_queries 和 discarded_queries；上表及人工表的 query 指标均按最终前 5 条计算。

以下保留本次实际生成文本及原生解析结果，供人工检查。单个 seed 的格式成功率并不能证明跨 seed 稳定；词面重复指标也不能单独证明 query 质量提高。

### Q18

Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

检查是否正常输出 [Search]，而非 [Expand]。

文本核查：本次 B 正常生成 4 条 [Search] 并以 [StopSearch] 结束，未出现 Expand 标记。

**A：Baseline**

```text
[Search]Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection
[Search]Zero-shot detection of LLM-generated content
[Search]Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
[Search]Evaluation of LLM-generated text in zero-shot scenarios
[StopSearch]
```

解析结果：

1. Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection
2. Zero-shot detection of LLM-generated content
3. Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
4. Evaluation of LLM-generated text in zero-shot scenarios

**B：V1.1**

```text
[Search]Performance of LLMs in zero-shot text detection
[Search]Comparison between LLMs and supervised fine-tuned small classification models
[Search]Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
[Search]Zero-shot detection of LLM-generated content
[StopSearch]
```

解析结果：

1. Performance of LLMs in zero-shot text detection
2. Comparison between LLMs and supervised fine-tuned small classification models
3. Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
4. Zero-shot detection of LLM-generated content

### Q28

Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

检查 HumanEval、MBPP、code_contests，以及更难／更容易的比较关系是否保留。

文本核查：本次 A/B 均未出现 HumanEval、MBPP、code_contests 这三个名称。B 实际生成 5 条，但数量不代表保留了难度比较关系。

**A：Baseline**

```text
[Search]Survey papers on code evaluation datasets
[Search]Middle difficulty level code evaluation datasets
[Search]Code evaluation datasets with mid-level hardness
[Search]Comparison studies on difficulty levels of different code evaluation datasets
[StopSearch]
```

解析结果：

1. Survey papers on code evaluation datasets
2. Middle difficulty level code evaluation datasets
3. Code evaluation datasets with mid-level hardness
4. Comparison studies on difficulty levels of different code evaluation datasets

**B：V1.1**

```text
[Search]Survey papers on code evaluation datasets
[Search]Research papers on mid-level hardness code evaluation datasets
[Search]Comparison of difficulty levels in code evaluation datasets
[Search]Evaluating the difficulty level of code evaluation datasets
[Search]Middle difficulty code evaluation datasets
[StopSearch]
```

解析结果：

1. Survey papers on code evaluation datasets
2. Research papers on mid-level hardness code evaluation datasets
3. Comparison of difficulty levels in code evaluation datasets
4. Evaluating the difficulty level of code evaluation datasets
5. Middle difficulty code evaluation datasets

### Q43

AI for Science papers, especially protein design and DPO of antibody design.

检查是否同时覆盖 protein design 和 antibody design / DPO。

文本核查：B 出现 protein design、antibody design 和 DPO，也产生了 “Decoding Protein Optimization”。这里只记录模型实际文本，该展开的正确性留给人工审核。

**A：Baseline**

```text
[Search]AI tools for protein design
[Search]Research on DPO in antibody design
[Search]Survey papers on protein design using AI
[Search]Application of AI in scientific research papers
[Search]AI advancements in protein design
[StopSearch]
```

解析结果：

1. AI tools for protein design
2. Research on DPO in antibody design
3. Survey papers on protein design using AI
4. Application of AI in scientific research papers
5. AI advancements in protein design

**B：V1.1**

```text
[Search]AI techniques used in protein design
[Search]Research on DPO application in antibody design
[Search]Survey papers on AI in protein design
[Search]Papers on Decoding Protein Optimization in antibody design
[Search]Application of AI for scientific research
[StopSearch]
```

解析结果：

1. AI techniques used in protein design
2. Research on DPO application in antibody design
3. Survey papers on AI in protein design
4. Papers on Decoding Protein Optimization in antibody design
5. Application of AI for scientific research

### Q48

Papers that explore using large language models for mining factors in stock exchange analysis.

检查是否保留 factor mining，而非退化为普通 stock prediction。

文本核查：B 出现 factor identification / factor mining，同时出现原问题未提及的 GPT-2、BERT-based。factor mining 所在 query 使用 machine learning；是否保留了原问题要求的大语言模型与因子挖掘之间的关系，留给人工审核。

**A：Baseline**

```text
[Search]Application of large language models in stock market analysis
[Search]Role of AI and language models in stock prediction
[Search]Impact of large language models on stock exchange analysis
[Search]Use of GPT-3 in stock market trend analysis
[Search]Survey papers on large language models in stock exchange analysis
[StopSearch]
```

解析结果：

1. Application of large language models in stock market analysis
2. Role of AI and language models in stock prediction
3. Impact of large language models on stock exchange analysis
4. Use of GPT-3 in stock market trend analysis
5. Survey papers on large language models in stock exchange analysis

**B：V1.1**

```text
[Search]Investigations on the use of GPT-2 model for stock market prediction and factor identification
[Search]Use of AI and NLP in stock market analysis
[Search]Application of BERT-based language models in stock market sentiment analysis
[Search]Survey papers on stock exchange analysis using large language models
[Search]Role of machine learning in stock exchange factor mining
[StopSearch]
```

解析结果：

1. Investigations on the use of GPT-2 model for stock market prediction and factor identification
2. Use of AI and NLP in stock market analysis
3. Application of BERT-based language models in stock market sentiment analysis
4. Survey papers on stock exchange analysis using large language models
5. Role of machine learning in stock exchange factor mining

实验到此停止。等待人工审核后，再决定是否进入 Serper Search A/B；本轮没有运行 Search。
