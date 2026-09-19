# ACRONYM_EXPANSION_PROBE_002

**独立离线 A/B 实验。所有 expansion 均仅作为模型实际产生的待审核词组；人工审核前不计算、不宣称 expansion accuracy。**

## 数据与隔离

直接复用 `/home/chenyi/pasa/ACRONYM_EXPANSION_PROBE_001.json` 的 29 个样本、14 种缩写，涉及 23 个原始问题。每样本 A/B 各 5 次，共 290 次真实独立生成。

只投影 query_id、original_question、acronym、原始 mention 和已有中文翻译；001 的模型输出、候选答案和人工标签不进入本次 prompt 或检测规则。未重新筛选样本，未读取 GT title/paper、miss audit 或搜索结果。同一问题中的多个 acronym 仍单独计样本，以不同 seed 独立生成，未复用其他样本输出。

仅加载指定本地 Crawler；禁止 Internet socket/DNS，开启 HF offline 和 local_files_only。没有执行 Serper、Selector、Expand、真实搜索或 PaSa 主流程；原生文件只读解析。未修改 baseline、Query Planner、checkpoint 或主流程，未写 SFT 数据，未提交 Git。

## 原生 A/B 设置

A 组原始 prompt：

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.
User Query: {user_query}
```

B 组 = A 组的完整 prompt + 一个换行 + 以下指令；没有添加目标 acronym 参数、JSON 要求、planner、facet 或 constraint 机制：

```text
For acronyms in the user query, always preserve the original acronym. When you are confident about its full form, you may also use the full form together with the acronym in one of the search queries. Do not guess.
```

原生解析逻辑从 `paper_agent.py` 的 AST 读取并按原方式使用：`re.findall('Search\\](.*?)\\[', raw_output, flags=re.DOTALL)`，逐条 strip 后取前 5 条。保留全部匹配、原始文本和被截去部分，不补全缺失标记、不修复格式、不去重、不执行任何 query。

Checkpoint：`/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler`。文件 SHA-256、prompt、chat template 后的输入、每次 seed、token IDs、软件版本和原生代码指纹保存在 JSON provenance。

沿用 checkpoint generation config：do_sample=true，temperature=0.7，top_p=0.8，top_k=20，repetition_penalty=1.05；max_new_tokens=512。use_cache=true 仅启用 KV 缓存。batch_size=1，与原生单问题生成方式一致；原始问题不截断。

seed = 2026091300 + sample_index × 10 + run_number − 1。每个样本的 5 个 seed 不同；145 个样本/轮次 seed 互不相同；同一轮 A/B 配对使用相同 seed。两个条件都重新调用 generate，无聊天历史，也不将 A 输出提供给 B。

运行于 NVIDIA A100-PCIE-40GB（物理 GPU 1），torch 2.5.1+cu124，transformers 4.47.0.dev0；UTC 2026-09-12T16:52:49.263998+00:00 至 2026-09-12T17:03:41.218454+00:00。保护文件前后指纹一致：True。

## 指标定义与限制

- 主统计单位是 sample × run，每组分母固定 145；正常解析指原生解析得到至少 1 条 query 且最终列表无空 query。格式失败不会从分母消失。另报告整个输出严格匹配 `[Search]…[StopSearch]` 的比例。
- Retention：最终前 5 条 query 至少一条包含目标缩写，忽略大小写并允许复数 s，采用完整词边界。另给出原文大小写/词形的严格匹配。
- Expansion Attempt：**疑似展开的词面代理率**，检测模型实际输出中首字母与缩写匹配的连续词组；允许跳过连接词、混合连字符及内嵌大写缩写。没有预置任何标准全称。只保留原文真实出现的候选子串与位置，不补写全称。
- 这只是可复现的候选检测：会漏掉不按首字母构成的全称，也可能把恰好首字母匹配的普通词组列为候选。不能把候选率当作确认的展开意图或正确率。来自原始 question 的已有全称也计入宽口径，并单独标记来源；不是新增知识的证明。
- 本次实际存在这种歧义：`learning in language models`、`limitations in language models` 在跳过连接词 in 后也会匹配 LLM。它们是原始输出中的真实词组，但模型没有明确声称这是 LLM 的全称。保留这些命中供审核，不把它们自动判为“错误展开”，也不删除后重新选择统计规则。下文所有 attempt / 共现数字必须按此代理口径解读。
- 共现：同一条最终 query 同时含目标缩写和疑似展开。不同 query 分别出现不算共现。
- 重复：同一 run 的最终列表内，先比较规范化 token 序列完全相同，再列出 token-set Jaccard ≥0.85 的近重复；候选全称替换回缩写后相同的 query 对另列为复核线索，不能据此断言 B 指令导致重复或两种表达语义等价。
- 多 acronym 的同一个 original question 会被重复计入样本，LLM 样本较多；结果是本次固定语料、prompt 和 5 次采样的描述性比较，不提供总体可靠性或准确率推断。

## A/B 自动统计

| 指标 | A | B |
|---|---:|---:|
| Search query 正常解析率 | 145/145 (100.00%) | 145/145 (100.00%) |
| 严格原生格式率 | 145/145 (100.00%) | 145/145 (100.00%) |
| Acronym Retention Rate | 127/145 (87.59%) | 127/145 (87.59%) |
| 原文大小写/词形严格保留率 | 118/145 (81.38%) | 116/145 (80.00%) |
| Expansion Attempt Rate（疑似，词面代理） | 29/145 (20.00%) | 34/145 (23.45%) |
| Acronym + full-form 共现率（疑似，词面代理） | 0/145 (0.00%) | 0/145 (0.00%) |
| 出现原问题未包含的疑似展开词组 | 24/145 (16.55%) | 29/145 (20.00%) |
| 含规范化重复 query 的输出 | 0/145 (0.00%) | 0/145 (0.00%) |
| 含近重复 query 的输出 | 2/145 (1.38%) | 0/145 (0.00%) |
| 候选全称替换为缩写后重复的输出 | 0/145 (0.00%) | 0/145 (0.00%) |
| 含非 Search 动作标记的输出 | 0/145 (0.00%) | 0/145 (0.00%) |
| 触发原生前 5 条截取的输出 | 0/145 (0.00%) | 0/145 (0.00%) |
| 最终 query 总数 | 718 | 702 |
| 出现疑似展开的样本数 | 11/29 | 12/29 |
| 达上限且未 EOS 的输出 | 0 | 0 |
| 空 query 数 | 0 | 0 |
| 未被原生正则提取的 [Search] 标记数 | 0 | 0 |

合并 A/B 后共有 15/29 个样本至少产生一次疑似展开。仅以成功解析输出为分母的补充指标保存在 JSON 的 summary.A/B.rates_among_parsed_runs。

### 配对运行的指标变化

| 指标 | A/B 均出现 | 仅 A | 仅 B | 均未出现 |
|---|---:|---:|---:|---:|
| Search query 正常解析率 | 145 | 0 | 0 | 0 |
| Acronym Retention Rate | 125 | 2 | 2 | 16 |
| Expansion Attempt Rate（疑似，词面代理） | 22 | 7 | 12 | 104 |
| Acronym + full-form 共现率（疑似，词面代理） | 0 | 0 | 0 | 145 |

这些差异只表示指标是否出现，不是人工表中“更好/相同/更差”的自动标签。

### 每样本 5 次结果

五位字符串从左到右对应 Run 1–5：1=该指标出现，0=未出现；“展开”和“共现”均是疑似词面指标。

| Sample | A 解析 | B 解析 | A 保留 | B 保留 | A 展开 | B 展开 | A 共现 | B 共现 |
|---|---|---|---|---|---|---|---|---|
| Q5:RLHF | 11111 | 11111 | 11111 | 11111 | 00000 | 00001 | 00000 | 00000 |
| Q9:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q11:LLM | 11111 | 11111 | 11111 | 11111 | 11101 | 11100 | 00000 | 00000 |
| Q11:MoE | 11111 | 11111 | 11111 | 11111 | 00000 | 00011 | 00000 | 00000 |
| Q13:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q14:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q15:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q17:LLM | 11111 | 11111 | 11111 | 11110 | 01111 | 11111 | 00000 | 00000 |
| Q17:NER | 11111 | 11111 | 11011 | 11110 | 00000 | 00000 | 00000 | 00000 |
| Q17:RE | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 | 00000 | 00000 |
| Q17:EE | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 | 00000 | 00000 |
| Q18:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 01000 | 00000 | 00000 |
| Q19:LLM | 11111 | 11111 | 11111 | 11111 | 10010 | 00000 | 00000 | 00000 |
| Q20:LLM | 11111 | 11111 | 11111 | 11111 | 00010 | 00000 | 00000 | 00000 |
| Q21:SFT | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q28:MBPP | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 | 00000 | 00000 |
| Q29:LLM | 11111 | 11111 | 11111 | 11111 | 10010 | 10110 | 00000 | 00000 |
| Q29:IMO | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q30:LLM | 11111 | 11111 | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 |
| Q31:DPO | 11111 | 11111 | 11111 | 11111 | 10000 | 00000 | 00000 | 00000 |
| Q34:AIGC | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q35:LLM | 11111 | 11111 | 11111 | 11111 | 01010 | 11111 | 00000 | 00000 |
| Q37:LLM | 11111 | 11111 | 11111 | 11111 | 00101 | 01100 | 00000 | 00000 |
| Q40:QAT | 11111 | 11111 | 10111 | 10111 | 11111 | 11111 | 00000 | 00000 |
| Q41:SFT | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q43:AI | 11111 | 11111 | 11111 | 11111 | 00000 | 10000 | 00000 | 00000 |
| Q43:DPO | 11111 | 11111 | 11011 | 11111 | 00100 | 01000 | 00000 | 00000 |
| Q47:LLM | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |
| Q49:PC | 11111 | 11111 | 11111 | 11111 | 00000 | 00000 | 00000 | 00000 |

## 模型实际产生的疑似展开：待人工审核

只列出生成 query 中实际出现的候选词组；此表不预填 Gold，也不自动判正确、错误或可疑程度。疑似表示词面检测命中。问题本身已有的词组用“原问题已有”标记。

| Sample | 组 | 实际候选词组 | 原问题已有 | 位置（Run / Query，1 起） |
|---|---|---|---|---|
| Q5:RLHF | B | Reinforcement Learning HUMAN Feedback | 否 | R5/Q4 |
| Q11:LLM | A | Large Language Models | 否 | R1/Q3, R2/Q4, R3/Q1, R5/Q4 |
| Q11:LLM | B | Large Language Models | 否 | R1/Q5, R2/Q3, R3/Q4 |
| Q11:MoE | B | Mixture-of-experts | 否 | R4/Q5, R5/Q4 |
| Q17:LLM | A | learning in language models | 否 | R2/Q2, R3/Q3, R3/Q5, R4/Q2, R5/Q1 |
| Q17:LLM | A | large language models | 否 | R4/Q5 |
| Q17:LLM | B | learning in language models | 否 | R1/Q4, R4/Q3, R5/Q1 |
| Q17:LLM | B | limitations in language models | 否 | R2/Q1, R3/Q2 |
| Q18:LLM | B | learning in language model | 否 | R2/Q3 |
| Q19:LLM | A | Large Language Models | 否 | R1/Q5 |
| Q19:LLM | A | large language models | 否 | R4/Q5 |
| Q20:LLM | A | large language models | 否 | R4/Q2 |
| Q29:LLM | A | large language models | 否 | R1/Q5, R4/Q5 |
| Q29:LLM | B | Large Language Models | 否 | R1/Q2, R1/Q4, R3/Q2 |
| Q29:LLM | B | large language models | 否 | R4/Q1 |
| Q30:LLM | A | large language models | 否 | R1/Q4, R1/Q5, R2/Q3, R2/Q4, R3/Q5, R4/Q4, R5/Q2 |
| Q30:LLM | A | Large Language Models | 否 | R2/Q5 |
| Q30:LLM | B | large language models | 否 | R1/Q5, R2/Q5, R3/Q5, R4/Q4, R4/Q5, R5/Q2, R5/Q3 |
| Q30:LLM | B | Large Language Models | 否 | R3/Q4 |
| Q31:DPO | A | Differentiable privacy objectives | 否 | R1/Q4 |
| Q35:LLM | A | Large Language Model | 否 | R2/Q4 |
| Q35:LLM | A | large language models | 否 | R4/Q4 |
| Q35:LLM | B | large language models | 否 | R1/Q2, R4/Q2, R5/Q3, R5/Q5 |
| Q35:LLM | B | Large Language Model | 否 | R1/Q4, R2/Q4, R4/Q5 |
| Q35:LLM | B | large language model | 否 | R3/Q4, R5/Q4 |
| Q37:LLM | A | Large Language Model | 否 | R3/Q5, R5/Q5 |
| Q37:LLM | B | Large Language Model | 否 | R2/Q5 |
| Q37:LLM | B | Large Language Models | 否 | R3/Q5 |
| Q40:QAT | A | Quantization-Aware Training | 是 | R1/Q1, R1/Q2, R1/Q3, R1/Q5, R2/Q1, R2/Q2, R2/Q3, R2/Q4, R2/Q5, R3/Q1, R3/Q2, R3/Q3, R3/Q4, R4/Q1, R4/Q2, R4/Q3, R4/Q4, R5/Q1, R5/Q2, R5/Q3, R5/Q4 |
| Q40:QAT | B | Quantization-Aware Training | 是 | R1/Q1, R1/Q2, R1/Q3, R2/Q1, R2/Q2, R2/Q3, R2/Q4, R2/Q5, R3/Q1, R3/Q2, R3/Q3, R3/Q4, R4/Q1, R4/Q3, R4/Q4, R5/Q1, R5/Q2, R5/Q3, R5/Q4 |
| Q40:QAT | B | quantization-aware training | 是 | R1/Q5 |
| Q43:AI | B | Artificial Intelligence | 否 | R1/Q5 |
| Q43:DPO | A | Deep Potential Optimization | 否 | R3/Q5 |
| Q43:DPO | B | drug-protein optimization | 否 | R2/Q3 |

## 格式与重复明细

- Q17:NER / A / Run 3：近重复 query 索引（0 起）=[{"query_indices": [1, 3], "token_set_jaccard": 0.9090909090909091}]。
- Q17:NER / A / Run 5：近重复 query 索引（0 起）=[{"query_indices": [1, 3], "token_set_jaccard": 0.9090909090909091}]。

## 文件与人工审核

- `ACRONYM_EXPANSION_PROBE_002.json`：全部 prompt、seed、原始输出、所有/最终 queries、候选证据、解析及重复指标、provenance。
- `ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW.md`：29 个样本及中文翻译，A/B 各 5 次全部 queries；人工 gold、组内判断、组间比较和 Notes 留空。
- 独立脚本位于 `acronym_expansion_probe_002/`；检测规则在推理前固定，哈希已核对。没有进行重试挑选或修改 prompt 后重新采样。

## 最后总结

- A/B Search query 解析率：A 145/145 (100.00%)；B 145/145 (100.00%)。
- Acronym retention rate：A 127/145 (87.59%)；B 127/145 (87.59%)。
- Expansion attempt rate（疑似词面代理）：A 29/145 (20.00%)；B 34/145 (23.45%)。
- Acronym + full-form 共现率（疑似词面代理）：A 0/145 (0.00%)；B 0/145 (0.00%)。
- 产生疑似 expansion 的样本：A 11/29；B 12/29；A/B 合并 15/29。
- 格式/重复：严格格式 A 145/145 (100.00%)、B 145/145 (100.00%)；规范化重复输出 A 0、B 0；近重复 A 2、B 0；候选替换后重复 A 0、B 0。
