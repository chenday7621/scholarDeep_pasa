# LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004

## 审计结论

本审计对 `PAGE2_ROUTING_PREREG_VALIDATION_003B` 中 **Page1 与所有 native-query Page2 均未命中 GT 的 38 题**进行归因。保守分类结果为：

| 类别 | 题数 | 占 38 题 |
|---|---:|---:|
| `QUERY_DIRECTION_MISS` | 11 | 28.95% |
| `RANKING_DEPTH_MISS` | 0 | 0.00% |
| `SOURCE_INDEX_MISS` | 7 | 18.42% |
| `UNCERTAIN` | 20 | 52.63% |

逐类题号：

- `QUERY_DIRECTION_MISS`（11）：Q01、Q08、Q21、Q25、Q27、Q29、Q30、Q36、Q37、Q44、Q45
- `RANKING_DEPTH_MISS`（0）：无
- `SOURCE_INDEX_MISS`（7）：Q10、Q34、Q35、Q40、Q47、Q48、Q49
- `UNCERTAIN`（20）：Q03、Q05、Q06、Q09、Q11、Q12、Q14、Q15、Q16、Q18、Q20、Q23、Q26、Q31、Q32、Q39、Q41、Q42、Q43、Q46

核心判断是：**当前证据不支持“主要瓶颈就是 native query quality / query direction，而不是 Page2 本身没有价值”作为 38 题的主解释。** 在能够较明确归因的 18 题中，query-direction miss 的确多于 source-index miss（11 对 7）；但 20/38（52.63%）仍然不确定，不能把它们强行计入 query failure。此外，15 个方向较合理问题的真实 Page3–Page5 probe 没有一次命中 GT，冻结 Page2 的 arXiv source adherence 又从 Page1 的 100% 降到 17.54%，说明 provider pagination/source behavior 是实质性混杂因素。

这也不等于“Page2 没有价值”的一般性结论。本审计只分析 003B 的 38 个双页 miss，且 003B 本身的 Always-Page2 没有为这些题增加 GT；它能支持的是：**对当前 native queries 和当前 Serper/arXiv 请求行为，机械地继续翻页不是优先级最高的修复方向。**

## 数据边界与可审计性

- 输入完全来自冻结的 003B：原始 question、native queries、Page1/Page2 raw response、GT title/metadata，以及本地 GT abstract。
- 未修改 `paper_agent.py`，未修改 003B 的 snapshot、response 或 hash。
- 离线自动证据包括 token coverage、Question→GT 与 Query→GT 的 token/字符/TF-IDF 相似度，以及冻结结果 title+snippet→GT metadata 的主题相似度。
- 每题保留自动规则建议、结构化人工/规则判断、是否覆盖自动建议、置信度、failure modes、probe ranks 和证据路径，详见 `failure_cases.json`。
- `RANKING_DEPTH_MISS` 只在固定 native query 的真实 Page3–Page5 结果直接出现 GT 时成立；不能仅凭“语义方向合理”推测为深度问题。
- `UNCERTAIN` 是有意保留的审计结果，不是待补齐的标签。

## 诊断性 probes

共冻结并执行 159 个 probe，159 次 HTTP attempt，均保存原始 response bytes、结构化响应、payload 与 SHA-256：

| Probe | 问题数/请求数 | GT 命中题数 |
|---|---:|---:|
| Exact GT title，Page1 Top10 | 38 | 31 |
| GT deterministic core phrase，Page1 Top10 | 38 | 31 |
| Original question，Page1 Top10 | 38 | 2 |
| 方向较合理 native query，Page3–Page5 | 15 题 / 45 请求 | 0 |

**这 159 个请求全部是读取 GT 的 failure-attribution diagnostics。它们不是可部署策略，不是 Controller 候选，不是新的模型性能估计，也没有回写或替换 003B 的结果。** Page3–Page5 子集的 case 选择与 native-query 选择也读取了 GT metadata，因此只能用于诊断“是否观察到更深命中”，不能报告为策略 recall。

Exact title 和 core phrase 都能命中的 31 题，说明至少在诊断时点搜索源能够识别多数 GT；两者都不命中的 7 题支持 `SOURCE_INDEX_MISS`。Original question 只命中 2/38，说明直接照抄问题也不是充分修复。15 个方向较合理 case 的 Page3–Page5 为 0/15，只能说明本次有限深度 panel 没找到正面的 ranking-depth 证据，不能证明 GT 永远不在更深位置。

## Query-direction failure 的常见形式

以下计数只在 11 个 `QUERY_DIRECTION_MISS` 中统计；同一题可有多个 failure mode：

| Query failure mode | 题数 |
|---|---:|
| 过度泛化 | 10 |
| 关键方法/实体遗漏 | 9 |
| 任务框架漂移 | 4 |
| 关系/限定条件丢失 | 3 |
| 约束被拆散 | 2 |

最常见的是**过度泛化**和**关键方法/实体遗漏**。典型模式是把一个可识别的方法、工具、数据集或机制改写成宽泛 survey/主题检索；其次是把“方法用于什么任务”“在什么限制下成立”等关系丢掉，或把一个多条件问题拆进不同 query，导致没有任何一条 query 保留完整合取条件。

表面模式也与此一致：38 题共有 172 条 native query，其中 37 条包含 `survey`，覆盖 36/38 题。这个数字只说明生成配置存在明显的泛化倾向，**不能单独作为因果分类规则**。

## Author-written 与 inline-citation

分类顺序为 Query / Depth / Source / Uncertain：

| 分组 | 题数 | Query / Depth / Source / Uncertain |
|---|---:|---:|
| author-written | 16 | 3 / 0 / 1 / 12 |
| inline-citation | 22 | 8 / 0 / 6 / 8 |

- Author-written：query miss 3/16（18.75%），source miss 1/16（6.25%），uncertain 12/16（75.00%）。主要表现为方向语义合理，但 GT 使用问题中未显式出现的标题术语，因此难以区分 query wording、排序波动和 source behavior。
- Inline-citation：query miss 8/22（36.36%），source miss 6/22（27.27%），uncertain 8/22（36.36%）。它比 author-written 更容易得到明确的方向遗漏或 source-index 归因。

两组 pattern 有描述性差异，但样本只有 16/22，且这是 003B miss 条件下的选择后子集；这里不做显著性推断，也不把差异外推到完整 LitSearch。

## Page2 source-adherence 限制

在这 38 题的冻结响应中：

| 冻结页 | Organic results | 可解析 arXiv URL | 比例 |
|---|---:|---:|---:|
| Page1 | 1706 | 1706 | 100.00% |
| Page2 | 1579 | 277 | 17.54% |

请求 payload 虽包含 `site:arxiv.org`，但 Page2 大量返回非 arXiv 结果。这使“Page2 没找到 GT”同时混合了 query direction、Google/Serper pagination、site restriction adherence 与索引/排序因素。因而不能把 Page2 miss 全部解释为 native query 错误，也不能用这些诊断 probes 声称某个 Controller 会提升性能。

## 下一步实验优先级

| 优先级 | 实验 | 原因与建议范围 |
|---:|---|---|
| 1 | `FEEDBACK_REQUERY` | Preregister on QUERY_DIRECTION_MISS cases; use question plus frozen Page1 evidence without GT; target missing bridge terms and constraint preservation. |
| 2 | Citation Expansion | Preregister on UNCERTAIN cases with topical Page1 neighbors and hidden title terminology; evaluate whether citations bridge to GT. |
| 3 | 替换/增加 retrieval source | Target seven SOURCE_INDEX_MISS cases and compare arXiv-native/Semantic Scholar retrieval against frozen Serper behavior. |
| 4 | 更深 PageN | Low priority: fixed Page3-5 diagnostics found 0/15 GT for direction-plausible native queries, and frozen Page2 source adherence degraded sharply. |

具体建议：

1. **优先 `FEEDBACK_REQUERY`**：只在预注册的新评测上，用原 question 加冻结 Page1 证据生成一次不读取 GT 的 requery；重点测试是否能保留完整限定条件并补回桥接术语。11 个明确 query miss 提供了直接动机。
2. **其次 Citation Expansion**：20 个 uncertain 中大量 case 的检索结果仍在正确主题附近，而 GT 名称包含 hidden terminology；从高相关邻居的引用网络扩展，比盲目继续翻页更有针对性。
3. **并行小规模比较 retrieval source**：7 个 exact/core identity search 都失败的 case 应用于检验 arXiv-native API、Semantic Scholar 或其他学术索引是否解决 source-index miss；同时可隔离当前 Page2 source-adherence 问题。
4. **更深 PageN 暂列低优先级**：本次固定的 Page3–Page5 panel 为 0/15，且越深页 source adherence 恶化。若再测，必须先冻结稳定的学术源和深度预算，不能挑最好看的 PageN。

## 逐题审计索引

| QID | Group | Final category | Confidence | Failure modes | Probe GT ranks | 审计理由 |
|---|---|---|---|---|---|---|
| Q01 | author-written | `QUERY_DIRECTION_MISS` | high | OVERGENERALIZATION, KEY_METHOD_ENTITY_OMISSION | exact=[1]; core=[1]; question=-; depth=- | Native queries paraphrase generic output encoding/comparison but omit lattices, reranking and hypotheses; results drift to causal/large-language-model surveys. Exact title/core retrieves GT at rank 1. |
| Q03 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Native query explicitly preserves DRO, adversarial training and no adversarial samples, and frozen results remain topical. Exact title finds GT, but selected native query Page3-5 does not; no positive depth evidence. |
| Q05 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | All native queries preserve shared adapters across layers; GT title instead uses masks/parameter-efficient transfer. Exact title finds GT, but selected native query Page3-5 does not. |
| Q06 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries preserve dense retrieval, mixture of experts and specialization. GT is titled Chain-of-Skills/open-domain QA, a bridge not explicit in the question; evidence cannot separate hidden terminology from ranking/source behavior. |
| Q08 | author-written | `QUERY_DIRECTION_MISS` | high | TASK_FRAMING_DRIFT, KEY_METHOD_ENTITY_OMISSION, OVERGENERALIZATION | exact=[1]; core=[1]; question=-; depth=- | Queries turn instructed deception into generic hidden/censored information and omit lie detection, black-box testing and unrelated questions. Exact title/core retrieves GT at rank 1. |
| Q09 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries faithfully retain distribution shift and RLHF but GT is framed as policy alignment/PARL. Exact title finds GT; native Page3-5 diagnostic does not. |
| Q10 | author-written | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Neither exact GT title nor deterministic core phrase nor original question retrieves known arXiv ID 2208.10734 in Top10; native results are also weakly related. |
| Q11 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1, 2, 4]; core=[1, 2, 4]; question=-; depth=- | Queries preserve financial time series plus text and results stay on time-series foundation models. Exact title retrieves TEMPO, but selected native Page3-5 does not. |
| Q12 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries preserve multilingual MLM, vocabulary limitation and contrastive loss; Headless/contrastive weight tying are hidden title terms. Exact title works, without depth hit. |
| Q14 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries retain MAUVE and positioned-error test. GT title uses blind spots/model-based metrics. Exact title works; selected native Page3-5 does not. |
| Q15 | author-written | `UNCERTAIN` | medium | RANKING_VOLATILITY, SEMANTIC_DIRECTION_PLAUSIBLE | exact=[1]; core=[1]; question=[3]; depth=- | Native queries retain ControlNet, training-free and continuous video. A later original-question diagnostic retrieves GT at rank 3, but this is not a historical deeper-rank observation and may reflect query wording or index volatility. |
| Q16 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries preserve temporal instruction decomposition and video diffusion; GT title Seer/language-instructed prediction hides that detail. No Page3-5 hit. |
| Q18 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1, 2]; question=-; depth=- | Queries explicitly preserve joint chain-of-thought/program-of-thought math fine-tuning. Exact title retrieves MAMMOTH, but selected native Page3-5 does not. |
| Q20 | author-written | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, OVERGENERALIZATION | exact=[1]; core=[1]; question=-; depth=- | Queries preserve data efficiency, contrastive learning and text embeddings but not composition-contrastive/sentence embeddings. This omission is plausible yet insufficient alone for confident query attribution. |
| Q21 | author-written | `QUERY_DIRECTION_MISS` | high | KEY_METHOD_ENTITY_OMISSION, OVERGENERALIZATION | exact=[1, 2, 3]; core=[1, 2]; question=-; depth=- | Queries merely repeat Gaussian-process vulnerability analysis and omit query-efficient black-box red teaming and Bayesian optimization, the searchable framing of GT. Exact title/core finds GT. |
| Q23 | author-written | `UNCERTAIN` | medium | CONSTRAINT_FRAGMENTATION, RANKING_VOLATILITY | exact=[1]; core=[1]; question=[8]; depth=- | Native queries split persona, dialogue, image-text and episodic-memory constraints across variants. A later original-question probe retrieves GT at rank 8, but temporal/query-formulation confounding prevents a clean historical depth claim. |
| Q25 | inline-citation | `QUERY_DIRECTION_MISS` | high | TASK_FRAMING_DRIFT, KEY_METHOD_ENTITY_OMISSION, OVERGENERALIZATION | exact=[1]; core=[1]; question=-; depth=- | All queries search generic calibration and omit surface-form competition/answer aliases, the GT mechanism. Exact title/core retrieves GT at rank 1. |
| Q26 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries precisely retain per-hop independent evaluation in multi-hop QA; GT title emphasizes lexical+dense efficient retrieval. Exact title works but Page3-5 does not. |
| Q27 | inline-citation | `QUERY_DIRECTION_MISS` | high | OVERGENERALIZATION, KEY_METHOD_ENTITY_OMISSION | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries broaden to generic robustness benchmark platforms and omit dynamic/adversarial NLP benchmarking or human-in-the-loop evaluation. Exact title/core retrieves Dynabench. |
| Q29 | inline-citation | `QUERY_DIRECTION_MISS` | high | OVERGENERALIZATION, RELATION_CONDITION_LOSS, CONSTRAINT_FRAGMENTATION | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries reduce the target to vague ethical/controversial datasets, dropping sensitive questions, acceptable responses and human-machine collaboration. Exact/core title retrieves SQUARE. |
| Q30 | inline-citation | `QUERY_DIRECTION_MISS` | medium | OVERGENERALIZATION, KEY_METHOD_ENTITY_OMISSION, RELATION_CONDITION_LOSS | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries broaden to prompt-token fine-tuning and do not preserve every-layer/prefix/continuous-prompt mechanism. Exact title/core retrieves Prefix-Tuning. |
| Q31 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries retain triplet-structured and table-to-text dataset requirements; DART/open-domain record-to-text terms are hidden. No Page3-5 hit. |
| Q32 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE | exact=[1]; core=[1]; question=-; depth=- | Queries accurately retain relaxed L0, structured pruning and transformers, with topical frozen results. Exact title works but no Page3-5 hit. |
| Q34 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact IGA title/core phrase and original question all fail to retrieve known arXiv ID 2104.07000 in Top10, despite broadly topical results. |
| Q35 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact title/core phrase and original question all fail to retrieve known arXiv ID 2011.08067; results remain on task-oriented dialogue, indicating source/ranking index difficulty even under identity query. |
| Q36 | inline-citation | `QUERY_DIRECTION_MISS` | medium | TASK_FRAMING_DRIFT, OVERGENERALIZATION | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries frame the task as detecting AI text/fact checking, while GT studies reliability of human evaluation of generated text. Exact title/core retrieves GT. |
| Q37 | inline-citation | `QUERY_DIRECTION_MISS` | high | TASK_FRAMING_DRIFT, KEY_METHOD_ENTITY_OMISSION, OVERGENERALIZATION | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries seek a prompt database/list and general prompt engineering, omitting an open-source prompt-learning framework/toolkit. Exact title/core retrieves OpenPrompt. |
| Q39 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1, 2]; core=[1, 2]; question=-; depth=- | Queries retain initialization from non-diffusion pretrained weights and convergence behavior; SSD-LM/simplex terms are hidden. Exact title works, without direct depth evidence. |
| Q40 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact title/core phrase and original question fail to retrieve known arXiv ID 2104.00783. Results are topically related but identity search still misses. |
| Q41 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries faithfully retain IDF, token alignment and speech; GT SPLAT title omits IDF. Exact title works but Page3-5 does not. |
| Q42 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries accurately describe multilingual pretrained text-to-text summarization and results are topical. Exact title finds mT5 but selected native Page3-5 does not. |
| Q43 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, OVERGENERALIZATION | exact=[2]; core=[2]; question=-; depth=- | Queries cover generative information extraction and entity fields; exact title finds GenIE at rank 2, but no direct deeper-rank evidence distinguishes broad wording from ranking. |
| Q44 | inline-citation | `QUERY_DIRECTION_MISS` | high | KEY_METHOD_ENTITY_OMISSION, OVERGENERALIZATION | exact=[1]; core=[1]; question=-; depth=- | Queries focus generic teacher-student prediction-distribution distillation and omit ColBERT, lightweight late interaction and denoised supervision. Exact title/core retrieves GT. |
| Q45 | inline-citation | `QUERY_DIRECTION_MISS` | high | CONSTRAINT_FRAGMENTATION, RELATION_CONDITION_LOSS, KEY_METHOD_ENTITY_OMISSION | exact=[1]; core=[1]; question=-; depth=- | Native variants split multi-step reasoning, attribute comparison, set operations, knowledge base and no-entity-linking constraints; none preserves the full conjunction or explicit compositional programs. Exact title retrieves KQA Pro. |
| Q46 | inline-citation | `UNCERTAIN` | medium | SEMANTIC_DIRECTION_PLAUSIBLE, HIDDEN_TITLE_TERMINOLOGY | exact=[1]; core=[1]; question=-; depth=- | Queries retain multilingual NER, ambiguous annotations and knowledge retrieval; GT title instead says imperfect annotations/CrossWeigh. Exact title works but Page3-5 does not. |
| Q47 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact title/core phrase and original question all fail to retrieve known arXiv ID 2105.11098; results are broadly about overconfidence/hallucination but miss the identity. |
| Q48 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact title/core phrase and original question all fail to retrieve known arXiv ID 1704.07398, despite highly explicit native queries. |
| Q49 | inline-citation | `SOURCE_INDEX_MISS` | high | EXACT_TITLE_SOURCE_FAILURE | exact=-; core=-; question=-; depth=- | Exact title/core phrase and original question all fail to retrieve known arXiv ID 2005.02680. Frozen results include closely related RST parsing papers, so identity-level source/ranking failure dominates attribution. |

## 产物

- `failure_cases.json`：38 题逐题证据、特征、分类、置信度和判断理由。
- `failure_summary.json`：总体/分组自动统计、probe panel、source adherence 与下一步优先级。
- `diagnostic_probe_results.json`：159 个诊断结果索引、命中位置和 response hashes。
- `validation.json`：独立重算与 hash/原始字节验证结果。

报告由 `report.py` 直接从机器可读结果生成；独立一致性检查由 `validate.py` 执行。
