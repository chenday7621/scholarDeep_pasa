# PaSa Search Query Generation 审计

审计对象：冻结 commit `fe89b48dd36e7438d74622cff1d430a66193222c` 的实际源码、Crawler checkpoint 配置及已有 50Q 输出。本阶段只读取这些文件，没有调用模型或改动 prompt。

## 结论

当前机制是**一次 Crawler 调用中的静态、自回归 multi-query generation**。模型一次输出一段带 `[Search]` 标记的文本，解析器提取其中最多 5 条，再并发请求 Serper。没有“检索第一条 → 看结果 → 生成第二条”的搜索反馈循环。原 prompt 已要求 query 互斥并偏好 survey；不能把它描述成完全没有多样性要求，但也没有约束清单、facet 分配、重复校验或反馈改写的可执行保证。

## 完整调用链与参数

| 环节 | 实际行为 | 源码位置 |
|---|---|---|
| 数据输入 | `data['question']` 成为 `user_query`；`source_meta.published_time` 减 7 天成为截止日期 | [run_paper_agent.py](/home/chenyi/pasa/run_paper_agent.py:44) |
| 参数 | `--search_queries` 默认 5，`--search_papers` 默认 10；分别传给 PaperAgent，同名参数已修复正确 | [CLI 与构造](/home/chenyi/pasa/run_paper_agent.py:35) |
| 模板加载 | 构造函数读取 `agent_prompt.json`，保存 user query 和预算 | [PaperAgent.__init__](/home/chenyi/pasa/paper_agent.py:31) |
| 构造生成输入 | `generate_query.format(user_query=self.user_query).strip()` | [PaperAgent.search](/home/chenyi/pasa/paper_agent.py:132) |
| 模型调用 | 一次 `self.crawler.infer(prompt)`；chat template → tokenizer → `model.generate(max_new_tokens=512)` → 解码字符串 | [Agent.infer](/home/chenyi/pasa/models.py:47) |
| Query 解析 | `re.findall(r"Search\](.*?)\[", ..., re.DOTALL)`，strip 后取 `[:self.search_queries]` | [regex 定义](/home/chenyi/pasa/paper_agent.py:69)、[解析及截断](/home/chenyi/pasa/paper_agent.py:135) |
| 搜索分发 | 按解析数量启动 worker，`queries.pop()` 取查询；实际 HTTP 到达顺序不等于模型生成序号 | [search_paper](/home/chenyi/pasa/paper_agent.py:94) |
| 请求构造 | 追加 `before:YYYY-MM-DD site:arxiv.org`；Serper POST，`num=self.search_papers`、page=1 | [google_search_arxiv_id](/home/chenyi/pasa/utils.py:44) |
| 返回结果 | 从 organic URL 提取现代 arXiv ID，set 去重；跨 query 的已触达 paper ID 再去重、读取论文和打分 | [URL parser](/home/chenyi/pasa/utils.py:73)、[节点构造](/home/chenyi/pasa/paper_agent.py:99) |
| 后续阶段 | `run()` 先 search 一次，再做既定层数 Expand；Expand 的 Crawler 调用用于 section 选择，不是重生成 Serper query | [PaperAgent.run](/home/chenyi/pasa/paper_agent.py:234) |

`search_queries=5` 控制的是**正则解析结果的上限**，不是模型调用次数，不是补足 5 条的循环，也没有作为数字 5 写入生成 prompt。返回少于 5 条就只搜索那些条目，多于 5 条只取前 5 条；源码没有 query 文本去重、非空校验或不足补齐逻辑。论文 ID 去重发生在检索后，不能追回已经消耗的重复查询预算。

正则依赖下一处 `[` 才结束当前捕获；保存的输出通常以 `[StopSearch]` 结束。prompt 本身没有说明这套标记协议。此次 Q18、Q28 的原始输出各只有 4 个可解析 Search 条目，其余 48 题为 5 条，所以保存了 248 次搜索，而非 250。这个事实不能归因为本次 probe 改变生成数量。

## 原始 prompt 与实际模型输入

原始 `generate_query`，完整引用自 [agent_prompt.json](/home/chenyi/pasa/agent_prompt.json:2)：

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.
User Query: {user_query}
```

`Agent.infer` 传入一个 user message，但 checkpoint 的 [tokenizer_config.json](/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler/tokenizer_config.json) 中 chat template 额外插入固定 system 文本。因此实际序列结构是：

```text
<|im_start|>system
You are an elite researcher in the field of AI.<|im_end|>
<|im_start|>user
{上面的原始 prompt，替入完整用户问题}<|im_end|>
<|im_start|>assistant
```

模型可见：固定 AI researcher system 角色、互斥查询/survey 指令、完整用户问题。模型不可见：GT titles/IDs、id2paper、论文库、任何 Serper 结果、之前的独立检索轨迹、`search_queries=5` 参数以及程序计算的 before/site 后缀。用户问题自身若有时间或来源要求，仍作为用户文本可见；这里只说程序追加的固定搜索条件不进入此 prompt。

GT 虽被写入 `root.extra['answer']` 用于结果/评测，但生成输入只格式化 `self.user_query`，没有读取该字段。[GT 挂载位置](/home/chenyi/pasa/run_paper_agent.py:61)。本报告也没有利用 GT 反向设计 query。

代码中的 `sample=False` 不等于 greedy：它只是不覆盖 sampling 参数。实际 [generation_config.json](/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler/generation_config.json) 保存 `do_sample=true, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.05`；调用另设 `max_new_tokens=512`。`apply_chat_template(tokenize=False, max_length=992)` 后实际 tokenizer 调用没有 truncation 参数，因此不能仅凭 992 宣称输入被截成 992 tokens。本阶段未更改或执行这些设置。

## 当前 prompt 显式要求了什么

| 能力 | 原始 prompt / 实现证据 | 判定 |
|---|---|---|
| Query diversity | “mutually exclusive queries” | 有自然语言要求，未验证实际语义互斥 |
| Query 间避免重复 | 同一互斥要求可表达此意图 | 有弱指令；没有独立禁止重复规则、相似度筛选或重生成 |
| Constraint preservation | 仅一般性要求根据 User Query 搜索 | 没有枚举实体、关系、比较、否定或逐项保留约束 |
| Facet decomposition | 没有 facet 清单或查询职责 | 未显式要求；模型有时自行分出角度 |
| Synonym / terminology expansion | 没有术语或同义表达指令 | 未显式要求；输出可能自行换词 |
| Broad / narrow 分配 | 偏好 survey | 没有宽窄组合策略；survey 偏好不等于自适应 broadening |
| Retrieval feedback | 全部 query 先生成，再发起搜索 | 没有 |

自回归生成的后续 query token 能看到同一段响应中更早的 query token，所以不能说“模型完全看不到前一条 query”。但它看到的是已生成文本前缀，而不是执行前一条搜索后返回的论文。静态 multi-query 与 iterative query evolution 的区分就在这里。

## 与冻结 50Q audit 对照的真实案例

以下文本直接来自冻结 smoke/replay；序号均为模型生成顺序。相似度沿用冻结审计的内容 token 和返回 ID 集合 Jaccard。只证明观测行为，不把查询缺陷直接等同为某篇 GT 的因果漏失。

### Q10：较好的多角度生成

用户原文：

> Is there any work that analyzes the scaling law of the multi-module models, such as video-text, image-text models?

| 序号 | 实际 query | baseline replay |
|---|---|---|
| 1 | Survey papers on scaling law of multi-module models | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_005.json) |
| 2 | Analysis of scaling law in video-text models | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_004.json) |
| 3 | Research on scaling law in image-text models | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_003.json) |
| 4 | Scaling behavior of multi-modal transformer models in video-text tasks | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_002.json) |
| 5 | Empirical studies on the scaling laws of text-to-video generation models | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/serper_replay/serper_001.json) |

第 2、3 条分别对应用户举出的 video-text / image-text；第 4、5 条进一步触及 transformer 和生成任务。第 2/3 条返回 ID Jaccard=0.20，第 4/5 条=0，说明确实获得不同候选。后两条也含模型自行扩展的内容，这不是全面覆盖或最优 Recall 的证明。

原始模型输出：[smoke_report.json](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q10/attempt_001/smoke_report.json)，字段 `crawler_raw_search_output` / `crawler_generated_search_queries`；GT 数据集第 11 行的 `question` 可核验用户原文。

### Q2：Query redundancy

用户原文：

> List all papers that use autoregressive transformer to generate videos.

| 序号 | 实际 query | baseline replay |
|---|---|---|
| 1 | Autoregressive transformer models in video generation research papers | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_005.json) |
| 2 | Research on using autoregressive transformers for video editing and composition | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_004.json) |
| 3 | Papers on video generation using autoregressive transformer | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_003.json) |
| 4 | Studies on autoregressive transformer in video creation | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_002.json) |
| 5 | Use of autoregressive transformer in video generation papers | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/serper_replay/serper_001.json) |

第 3、5 条主要是同一核心词的重排。冻结内容 token Jaccard=1.00，返回 ID 交集 8、并集 11，Jaccard=0.7273。即使 prompt 已要求互斥，仍实际消耗两条高度重合的搜索预算。

原始模型输出：[smoke_report.json](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q02/attempt_001/smoke_report.json)，字段 `crawler_raw_search_output` / `crawler_generated_search_queries`；GT 数据集第 3 行的 `question` 可核验用户原文。

### Q28：关键 benchmark 比较约束遗漏

用户原文：

> Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

| 序号 | 实际 query | baseline replay |
|---|---|---|
| 1 | Survey papers on code evaluation datasets | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_004.json) |
| 2 | Middle difficulty level code evaluation datasets | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_003.json) |
| 3 | Code evaluation datasets with mid-level hardness | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_002.json) |
| 4 | Comparison studies on difficulty levels of different code evaluation datasets | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/serper_replay/serper_001.json) |

用户提供 HumanEval、MBPP、code_contests 三个命名基准及相对难度关系；四条生成 query 均没有这些名称，也没有“比前两者更难、比后者更容易”的完整关系。mid-level hardness 是保留下来的概括，不能代替用户的比较锚点。这是问题文本与输出的可直接验证差异，不是根据漏失论文倒推的词。

原始模型输出：[smoke_report.json](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q28/attempt_001/smoke_report.json)，字段 `crawler_raw_search_output` / `crawler_generated_search_queries`；GT 数据集第 29 行的 `question` 可核验用户原文。

### Q48：factor / mining 约束遗漏

用户原文：

> Papers that explore using large language models for mining factors in stock exchange analysis.

| 序号 | 实际 query | baseline replay |
|---|---|---|
| 1 | Application of large language models in stock market analysis | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_005.json) |
| 2 | Role of AI and language models in stock prediction | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_004.json) |
| 3 | Impact of large language models on stock exchange analysis | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_003.json) |
| 4 | Use of GPT-3 in stock market trend analysis | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_002.json) |
| 5 | Survey papers on large language models in stock exchange analysis | [raw/structured](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/serper_replay/serper_001.json) |

用户任务是用 LLM mining factors；五条 query 均无 factor 或 mining，集中在泛 stock analysis/prediction/trend。第 4 条还自行收窄为 GPT-3，用户没有限定该模型。可证实任务概念丢失和额外限定，尚不能仅凭此证明替换 query 就会找回某个 GT。

原始模型输出：[smoke_report.json](/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q48/attempt_001/smoke_report.json)，字段 `crawler_raw_search_output` / `crawler_generated_search_queries`；GT 数据集第 49 行的 `question` 可核验用户原文。

## 归因边界与 page2 结果的对应

冻结 [CRAWLER_SEARCH_MISS_AUDIT.md](/home/chenyi/pasa/CRAWLER_SEARCH_MISS_AUDIT.md) 的 283 条中，7 条为 TITLE_METADATA_MISMATCH，276 条为 UNDETERMINED。冻结 query 诊断在 Q28/Q48 标记可验证的需求遗漏；高冗余阈值（content Jaccard≥0.8 且 response ID Jaccard≥0.6）命中 Q2、Q9、Q11、Q16、Q26、Q33、Q34。过宽/过窄标记是输出与需求关系的诊断，不是对全部 miss 作已证实因果分类。

本次 [PAGE2_SEARCH_PROBE_001.md](/home/chenyi/pasa/PAGE2_SEARCH_PROBE_001.md) 中，原 query 不变的 page2 找回 35/276（12.6812%）；其余 241 个未在本次 page2 出现。因此搜索深度有可观测增量，但尚无证据说明它解释了目标漏失的多数。反过来，也不能将剩余 241 条全部判为 query generation 错误：索引、时间变化、来源、超过第 20 名等仍未排除。

当前源码已经具备“根据问题一次生成多个 query + 互斥意图 + survey 偏好 + 固定来源/截止日期后处理”。缺少可验证的结构化约束保留、受预算控制的 facet/表达组合、语义冗余选择以及检索反馈驱动的 query 演化。候选机制与证据边界另见 [QUERY_PLANNER_CANDIDATES.md](/home/chenyi/pasa/QUERY_PLANNER_CANDIDATES.md)；这里不提出或替换新 prompt。
