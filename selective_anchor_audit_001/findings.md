已完成 **50/50 题、177 个原文元素**的离线文本审计。结论是：**可以识别原问题被改写时丢失了什么，但目前没有发现能仅凭 original question + native queries 明显区分这 5 个正例与其余题的共同规律。** Q48 支持“补回窄任务短语可能带来收益”；另外 4 个正例的关键元素在 native union 中已经保留，Q28 则说明严重约束丢失也不保证 anchor 有新增 GT。

本报告的“无增益”仅指已有缓存中相对完整 native 的新增 GT 为零，不代表这些问题的 anchor 没有找到任何 GT，也不代表不存在其他有用论文。50 题汇总表见下方；每题每元素的原文、query 频次与全部 original-native 相似度见 [逐元素复核表](SELECTIVE_ANCHOR_AUDIT_001_ELEMENT_REVIEW.md)。

## 正例共同特征，以及无收益题中的反例

| 观察 | 正例 5 题 | 无收益 45 题 | 含义 |
|---|---:|---:|---|
| 至少一个高信息元素被全部 native 遗漏 | 1/5（20.0%） | 11/45（24.4%） | 没有呈现正例更常缺失的现象 |
| 复核 union coverage=100% | 4/5（80.0%） | 33/45（73.3%） | 正例多数并不需要补回全部缺失的元素 |
| benchmark/dataset/acronym 元素全部遗漏 | 0/5 | 2/45 | 出现在无收益的 Q17、Q28，不能直接作为收益证据 |
| 至少一个高信息元素只被一条 native 保留 | 0/5 | 14/45 | “仅一条 query 保留”也不是这些正例的共同点 |
| 无任何单条 native 同时覆盖所有高信息元素 | 1/5 | 19/45 | 碎片化覆盖不能明显区分正例 |
| native 平均 Jaccard，组内均值 | 0.3202 | 0.3183 | 两组非常接近，分布广泛重叠 |
| original-native 平均 Jaccard，组内均值 | 0.3079 | 0.2839 | 正例甚至没有更低的平均词面相似度 |

5 个正例都没有 benchmark/dataset 专名全遗漏；都有至少一条 native 明确表达主要领域。这些都是大量无收益题同样具备的特征，不具备区分力。更具体的“关键元素缺失”“方向被中性化”“native 高度相似”无法同时解释 5 个正例。

按本次逐项复核，高信息全遗漏的无收益题为 **Q0、Q3、Q5、Q7、Q14、Q17、Q18、Q20、Q28、Q39、Q40**。Q28 缺少三个参照 benchmark 与两条比较关系，Q17 缺少 RE/EE；都没有增益。这里的 5 个遗漏不等于 5 个独立事实，比较关系与其中实体有明确重叠，不能靠增加标注颗粒度制造“风险更高”的数值结论。

正例的 native 平均 Jaccard 范围为 0.2754–0.3743，无收益题为 0.1017–0.5260，前者完全落在后者内。Q1（0.5260）、Q30（0.4553）、Q31（0.4576）都比全部正例更相似且无新增收益。Q15 与 Q13 同样存在“部分 query 保留负向关系、部分转为中性”的现象，却没有增益。去除固定通用停用词后，native Jaccard 的组均值为正例 0.3229、无收益 0.3615，仍不支持“正例更冗余”的解释。**这里不挑选分界值，也不据这些结果拟合规则。**

## 五个正例的逐题解释

以下“事实”来自原始问题、已保存 queries 和既有 GT matching；机制解释属于假设。检索排名/论文标题只用于事后核对，未用于元素提取，不能成为仅依赖输入文本的 trigger 特征。原始缓存出处、命中标题和 metadata 状态另存于 [case_evidence.json](selective_anchor_audit_001/case_evidence.json)。

### Q13：否定方向部分变弱，但并非 union 全遗漏

Original：`Provide papers demonstrating that the self-correction of LLMs does not enhance their performance.`

- `self-correction` 保留于 5/5；显式 LLM 类别保留于 q3/q4/q5；“不改善性能”保留于 q3 的 `not enhancing` 和 q4 的 `ineffectiveness`。q1 的 limitations 不等于明确不改善，q2/q5 的 impact 也未保留负向结论。
- 复核 coverage=3/3，Jnn=0.3016，Jon=0.2567。Anchor 保持原始否定关系及完整句式，可能使搜索排序与中性或 survey 表达不同；**不能解释成缺失约束首次被加入**，因为 q3/q4 已经保留它。
- 原有 GT 3/12→4/12。新增 `On the Intrinsic Self-Correction Capability of LLMs: Uncertainty and Latent Concept`，在缓存 anchor 中排第 8。
- 此处只确认既有 evaluator 的 GT 标题命中，不重新判断论文是否支持原问题的否定主张；缓存 snippet 甚至提到 self-correction 可以被改善，不能把命中数直接当成论证正确性的证据。

### Q19：保护质量的任务已保留，完整表达仍有检索差异

Original：`Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.`

- `LLMs` 在 5/5；`generation quality` 在 q1/q2/q4；`vocabulary watermarking` 在 q1/q2/q4/q5；“保护生成质量”在 q1/q2。q3 转向 embeddings 和 watermarking attacks，q4 转成中性 impact，但不能据此说全部 native 遗漏原任务。
- coverage=5/5，Jnn=0.3041，Jon=0.3495。q1/q2 已同时表达保护质量和 watermark 条件，Anchor 的可能价值在于原始词汇/完整措辞对应另一份排名，而非独有一个缺失实体。
- 原有 GT 4/37→5/37，新增 `REMARK-LLM: A Robust and Efficient Watermarking Framework for Generative Large Language Models`，anchor 第 9。仅凭这些输入文本，无法预知这一边际命中。

### Q44：组合原词与同义/具体化改写产生差别

Original：`What are the researches that have explored the application of Crypto-based Private Learning in privacy-preserving machine learning?.`

- `Crypto-based Private Learning` 原词在 q1，语义复核保留于 q1/q2/q3/q5；`privacy-preserving machine learning` 保留于 q2/q3/q5。q4 将问题具体化为 homomorphic encryption，本审计不把该特定子类等同于保留整个开放方法范围。
- coverage=2/2，严格词面 union coverage 也为 100%；Jnn=0.2754，Jon=0.2548。Anchor 同时保留原始两个长短语，可能与分散在多条 query 中的原词组合产生不同排名；仍不能说 union 缺失，也不能将未明确给出的同态加密自动视为用户原始约束。
- 原有 GT 6/25→7/25，新增 `Hawk: Accurate and Fast Privacy-Preserving Machine Learning Using Secure Lookup Table Computation`，anchor 第 10。其原因不能由词面 coverage 单独确定。

### Q45：元素无丢失，是“只在缺失时加 anchor”的直接反例

Original：`All papers about controllability of video generation.`

- `controllability` 和 `video generation` 在 5/5 中均以原词或直接任务同义表达保留；q4 的 control aspects/video production 是明确记录的语境同义判断。即使不接受 q4，其他 queries 也已完整覆盖。
- coverage=2/2，严格词面 coverage=100%；Jnn=0.3743，Jon=0.3653。原始 query 较短，native 带有 survey/latest/techniques 等不同措辞，但仅凭这一点无法推导哪个会新命中目标。
- 原有 GT 12/57→13/57，新增 `Training-free Camera Control for Video Generation`，anchor 第 9。**这是补充检索表达的边际收益，不能归因为约束修复。** Q1/Q30/Q31 等更高 Jaccard 的无收益题又反驳了“相似就该加”的简单推断。

### Q48：窄任务 `mining factors` 全遗漏，是最清晰的内容修复案例

Original：`Papers that explore using large language models for mining factors in stock exchange analysis.`

- 5 条 native 全部没有 `mining factors` 或直接同义任务；它们谈股票分析、预测、趋势、通用模型应用，并引入了 GPT-3。因子挖掘与一般预测不是等价任务。
- coverage=2/3，Hmiss=1；Jnn=0.3454，Jon=0.3133。Jaccard 不低，仍可发生关键任务丢失，说明平均词面相似度不能替代窄任务核对。
- 原有 GT 1/8→2/8，Recall 12.5%→25.0%。新增 `Automate Strategy Finding with LLM in Quant investment`，anchor 第 2；既有 snippet 明确包含 `mine alpha factors`。这与 anchor 恢复因子挖掘任务的解释一致，是本批中最强的内容证据。
- 这是观察到的吻合，不是隔离单个短语的因果实验；不能据此扩展为“遗漏窄任务时 anchor 必有收益”。

### 正例中的另一项事后观察

除 Q48 外，4 个正例新增论文分别在 anchor 排第 **8、9、10、9**；Q48 排第 **2**。在已有 Top-K=10 条件下，这与“词汇表达或排序变化带来少量边界命中”的解释相容。但未观察 native 的 Top10 之外排名，也没有重复检索或消融，不能证明某篇论文真的从第 11 名升到前 10，更不能把这些排名当成搜索前 trigger。

## Q28：为什么约束明显丢失却没有收益

Original：`Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.`

4 条 native 保留了 `code evaluation datasets`，其中 q2/q3 保留中等难度；却都遗漏 **HumanEval、MBPP、code_contests，以及“比前两者更难 / 比后者更容易”两条完整关系**。coverage=2/7（28.6%），Hmiss=5，Jnn=0.3265，Jon=0.1933。Anchor 在文本上确实补回完整难度区间。

但已有缓存显示：anchor 请求 HTTP 200，返回 **8 个 organic hits、8 个可解析 arXiv ID，8 个 metadata 均 PASS，0 个 GT 命中**。原始 native 与加入 anchor 后都为 **0/4，Recall 0%→0%**。因此，对这条 anchor 而言，不是请求失败、candidate parsing 失败或 metadata 缺失遮蔽了增益。

已有 GT 是 PythonSaga、SWE-bench、CRUXEval、NaturalCodeBench。Anchor 实际候选则包括 CodeScore、HumanEval on LLMs、CodeT、CodeGeeX、Evaluating Large Language Models Trained on Code、AICoderEval、编程任务难度评估以及语言模型代码系统评估；完整标题和顺序见案例 JSON。候选与代码评测和参照 benchmark 相关，却没有返回这四个目标。

一种合理解释是：**HumanEval/MBPP/code_contests 在问题里充当难度参照，搜索匹配这些名称并不等于执行“找出位于两个难度边界之间的数据集”。** 缓存中多条 snippet 直接讨论 HumanEval/MBPP，支持“结果围绕参照对象或一般评测”的观察；但不能证明搜索引擎怎样解析比较关系、目标是否在更低排名、或改写哪一处才会有效。本阶段没有新增 Search，因此止于这一解释边界。

Q28 与 Q48 的区别不是前者没有忠实性问题，而是恢复的信息作用不同：Q48 补回一个与新增论文任务直接对应的短语；Q28 补回的是检索系统未必能转化成目标集合的比较约束。这个区别有解释力，**但只有一个明确支持的正例，尚不足以成为可预测的收益规则**。

## 候选 trigger：只保留两项文字假设

1. **原问题的窄任务/明确方法或实体，在全部 native 中都没有直接或明确同义保留时，考虑 anchor。** 依据是内容忠实性，Q48 的因子挖掘是例子；不是任意稀有词缺失都触发，也不能根据未来 GT 标题反过来选“高信息词”。Q17/Q28 等无收益反例说明这只能作为覆盖修复候选，会错过 coverage 完整的四个现有正例。本阶段不设分数、不输出触发名单、不实现语义判定器。
2. **原问题明确要求的否定、方向比较或条件关系，未被任何单条 native 完整保留时，考虑 anchor。** 必须核对关系，不能只数各实体是否出现。Q28/Q0/Q18 是需要关注的忠实性案例，却没有新增收益；Q13 的否定已经被两条 query 保留，也不满足“全遗漏”的描述。因此它可以是约束保护候选，当前不能称为正例预测器。

上述是可解释的输入侧检查方向，而非已验证的 Selective Anchor 策略。它们有重叠，未经独立标注、留出数据或后续验证；**没有依据当前 GT 设置 coverage/Jaccard 阈值，没有实现 trigger，也没有新的 Search。**

不宜直接采用的规则包括：native Jaccard 高、original-native 相似度低、问题长、包含 benchmark/acronym、某个元素出现少、或者看到 survey/泛化改写就加 anchor。它们有明确反例，部分指标的组均值甚至不沿预想方向变化。新增 GT 位于靠后排名是搜索后的现象，不能用于搜索前决策。任何专为覆盖 Q13/Q19/Q44/Q45/Q48 而拼接的关键词规则，也只是对这批标签的记忆。

**对目标问题的回答：目前存在局部的内容解释，尤其 Q48；不存在覆盖全部正例且能排除大量无收益题的明显输入文本规律。应区分“原意保留检查”与“Anchor 边际 GT 收益预测”，不能把前者的成功直接当成后者已经成立。**
