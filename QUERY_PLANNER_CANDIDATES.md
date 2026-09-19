# Query Planner 候选方案：证据、取舍与后续实验

本阶段只做设计审阅，没有实现 planner、替换 prompt 或运行新 50Q A/B。下面的排序是建议测试顺序，不代表已替用户选定最终策略。方案只依据用户需求、生成行为与公开机制设计，禁止用 RealScholarQuery GT title 或漏失论文为 query 调词。

## 决策依据

PaSa 当前一次生成最多 5 条 query；自然语言要求互斥，但没有结构化约束验证或检索反馈。冻结审计可见 Q28 比较基准约束遗漏、Q48 factor/mining 概念遗漏、Q2 高冗余；Q10 又证明原模型有时能自行生成不同角度。不能把这些现象泛化为全部 276 个 miss 的已证实原因。

受控 page2 观测找回 35/276（12.6812%），241 个仍未找回；全量 790 个标题组的 ID 辅助 Search 覆盖率从 157/790 到 220/790，新增 63 组，其中只有 35 组属于本阶段目标子集。加深检索有增量，但没有证据把 Top-10 深度认定为目标 miss 的主要瓶颈，也不能据此把剩余 miss 全归因 planner。详见 [probe 报告](/home/chenyi/pasa/PAGE2_SEARCH_PROBE_001.md) 和 [PaSa 源码审计](/home/chenyi/pasa/PASA_QUERY_GENERATION_AUDIT.md)。

## 参考版本与核查范围

2026-09-11 读取以下公开仓库的源码快照，仅分析 query 的产生/演化及直接调用路径；未运行项目。引用固定 commit，避免 main 分支后续变化使结论失去依据。

| 项目 | 读取的 commit |
|---|---|
| allenai/asta-paper-finder | `0623cce6ff61b0a1a637c78d352c4f4d431d0364` |
| allenai/ai2-scholarqa-lib | `a96232870bdb0bd763f0131320e8377c6deb575e` |
| xiaofengShi/SPAR | `c276e107862ca09fdba6ffbce0e65e162a3ab701` |
| Future-House/paper-qa | `57e89f7223b0960d5ee5ea048c69e3c47e088572` |

### 1. Ai2 Asta Paper Finder

**源码可验证实现。**查询分析先拆解需求、提取结构化 specifications，再决定 content/metadata 等处理路径。PaperSpec 包含年份、作者及排除条件，并验证部分冲突；查询分析与路由有实际调用，不是只声明一个 schema。[查询分析](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/query_analyzer/query_analyzer.py#L250-L283)、[PaperSpec](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/data_model/specifications.py#L140-L184)、[路由](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/paper_finder/paper_finder_agent.py#L110-L149)。

Dense formulation 在没有已知论文时采用多种改写模板分配查询数，可选择保留原 query；已有高相关论文时，筛选/采样未用过的论文作为下一批 query 改写上下文。模板强调领域术语及概念关系，避免仅换常用词的表面改写。[改写与相关论文采样](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/dense/formulation.py#L23-L104)、[改写模板](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/dense/formulation_prompts.py#L24-L108)。这些规则在 [DenseAgent](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/dense/dense_agent.py#L75-L105) 被调用，[broad search 迭代](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/agents/mabool/api/mabool/agents/complex_search/broad_search.py#L114-L125) 携带文档并重新检索、判断相关性。

**值得借鉴：**结构化意图与元数据约束分开管理、领域术语层面的多样化，以及由相关论文反馈驱动的后续改写。**边界：**dense 内容改写并不承担所有 metadata 过滤；不同字段须追踪到对应 backend 才能声称真正执行。某模板要求避免旧 query，但该 formulation 调用没有显式传入完整旧 query 列表，不能据模板声称实现了历史语义去重。公开 repo 自述是产品快照，并不覆盖线上服务全部能力；多源、多轮预算也不能直接等同于 PaSa 的 5×10。[快照范围说明](https://github.com/allenai/asta-paper-finder/blob/0623cce6ff61b0a1a637c78d352c4f4d431d0364/README.md#L5-L20)。

### 2. Ai2 ScholarQA

**源码可验证实现。**`decompose_query` 结构化提取年份、venue、authors、领域，并生成自然语言 rewritten query 与 keyword query 两种表示。构造的 search_filters 实际传递 year、venue、fieldsOfStudy；源码声明 authors 字段，却没有把 authors 加入这里的 filters，因此不能称该路径已经落实作者过滤。[结构化解析与 filter 构造](https://github.com/allenai/ai2-scholarqa-lib/blob/a96232870bdb0bd763f0131320e8377c6deb575e/api/scholarqa/preprocess/query_preprocessor.py#L21-L81)。

主流程将自然语言改写用于 passage retrieval，将 keyword query 用于 additional paper retrieval，再按 corpus ID 去重；这是互补检索表示，有实际调用。[两种表示的检索路径](https://github.com/allenai/ai2-scholarqa-lib/blob/a96232870bdb0bd763f0131320e8377c6deb575e/api/scholarqa/scholar_qa.py#L100-L145)。普通流程先 preprocess/retrieve/rerank，再做后续摘要；后面的 iterative summarization 不能被解释为基于检索反馈不断生成新 search query。[主流程入口](https://github.com/allenai/ai2-scholarqa-lib/blob/a96232870bdb0bd763f0131320e8377c6deb575e/api/scholarqa/scholar_qa.py#L682-L700)。

**值得借鉴：**保留主题语义的自然语言表示与面向 keyword backend 的紧凑表示并用，metadata 作为独立条件。**边界：**不是现成的五 facet planner，也没有在上述普通调用链验证到搜索 query evolution。模板的相对时间说明含固定年份，移植必须以实验日期显式参数化，而不能照搬。[预处理指令](https://github.com/allenai/ai2-scholarqa-lib/blob/a96232870bdb0bd763f0131320e8377c6deb575e/api/scholarqa/llms/prompts.py#L299-L313)。这里只认定公开库的可调用实现，不把相关论文/产品的全部能力归给这份代码。

### 3. SPAR

**论文描述。**论文介绍先判断 intent/domain/time/source、按需要扩展 query，再用相关论文和历史查询做 query evolution，并配合引用扩展。描述还包括抑制重叠和基于文档数量/深度停止。参见 [SPAR 论文 §3.1–3.2](https://arxiv.org/html/2507.15245v1#S3.SS1)。

**源码可验证实现。**`expand_query` 确实执行意图/领域分析与是否需要扩展的判断，选择对应模板生成初始列表；`query_fusion` 还会在缺失时补入原用户 query。[初始 query expansion](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/search_engine.py#L714-L792)、[初始列表与原 query](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/pipeline_spar.py#L172-L204)。反馈阶段挑选相关且未使用的文档，把 original query、searched queries、论文 title/abstract/field 传入 `_generate_query_from_reference`，生成方法、应用、局限三个方向的候选；排除完全相同的历史字符串，合并后再采样限制数量。[实际反馈生成函数](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/search_engine.py#L531-L567)、[实际被调用的上下文模板](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/instruction.py#L290-L318)、[反馈文档选择与 query 剪枝](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/pipeline_spar.py#L585-L672)。搜索循环实际调用此演化函数。[搜索迭代](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/pipeline_spar.py#L694-L760)。

**论文与源码的差异。**引用搜索有实现但当前 `DO_REFERENCE_SEARCH=False`；停止函数虽然计算足够相关论文数量，最终仅返回 depth 条件。这里能验证 exact-string 历史去重，不能把它说成完整语义重叠抑制。仓库还存在其他 evolution 模板，不能仅搜索到模板名就认定它在上述链路生效。[引用搜索开关](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/global_config.py#L95-L110)、[实际停止条件](https://github.com/xiaofengShi/SPAR/blob/c276e107862ca09fdba6ffbce0e65e162a3ab701/pipeline_spar.py#L91-L134)。

**值得借鉴：**将原问题、历史 query 和真实相关论文共同用于剩余搜索预算的分配，而非简单多做同义改写。**边界：**原实现多轮、多源，初始列表可能因补入原 query 超过 5，不能原样作为公平 5×10 对照；也不能将论文中的完整 RefChain 当作当前默认开启的流程。

### 4. PaperQA2 / paper-qa

**源码可验证实现。**ToolSelector agent 保留消息 ledger，把工具 observation 追加后再选择下一动作；因此后续 PaperSearch query 可以利用前次检索反馈。[工具反馈循环](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/agents/main.py#L276-L320)。PaperSearch 在当前索引中按 query 搜索；相同 query/year key 再次调用时提高 offset，即翻页。工具反馈可按设置包含论文标题/年份，否则主要是状态；不能假设所有配置都向模型暴露相同 metadata。[PaperSearch 及重复查询翻页](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/agents/tools.py#L109-L210)。

另有 `litellm_get_search_query` helper 要求多个不同 keyword query，组合宽、窄表达；在读取的 `run_fake_agent` 固定流程中，该 helper 被调用来生成 3 条。这属于可定位的另一入口，不能声称默认 ToolSelector 必然采用这套批量 broad/narrow 规划。[query helper](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/agents/helpers.py#L27-L75)、[helper 的实际调用入口](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/agents/main.py#L182-L244)。

**值得借鉴：**让 query 选择成为可观察的工具决策，保留历史与反馈，并明确控制继续搜索还是改写。宽窄组合也有独立实现参考。**边界：**这里 PaperSearch 面向本地目录索引，不能等同 Serper 全网搜索。可见实现清理 year 参数、用于 previous_searches key，但 `index.query` 没有传递 year filter；不能因接口存在年份参数就断言过滤有效。重复查询次数约束有 docstring 指导，不能据此当作预算硬上限。当前仓库快照也不自动等同 PaperQA2 论文发表时的所有默认配置。

## 四个候选设计

下面是机制定义，不是新 prompt 文本，也不是已经实现的行为。潜在收益目前只能按所针对的可观察问题排序，不能把某类 miss 数量当作方案保证找回数。

| 候选 | 机制与修改范围 | 针对问题 | ≤5 query、每条 Top10 | 复杂度 / 主要风险 |
|---|---|---|---|---|
| A：结构化意图与约束校验 | query 生成前整理用户给出的实体、任务、比较关系、否定、硬/软约束；生成后核对保留情况，必要时在发请求前修正 | constraint loss、coverage 不足、无依据收窄 | 可保持；校验/修正不发搜索请求 | 低至中；误提取或把软条件当硬条件导致过窄 |
| B：Facet 分配与领域术语多样化 | 为至多五个 query 分配不同检索职责，生成候选后按需求覆盖和语义冗余选出最多五条 | query redundancy、coverage 不足 | 可保持；候选池未被选中项不请求 Serper | 中；虚构 facet、错误术语扩展、为求差异丢失核心需求 |
| C：互补检索表达与宽窄组合 | 同一用户意图采用自然语言/关键词两种序列化，并控制可选背景条件的粒度，构成五槽静态组合 | too broad、too narrow、表达方式造成的 coverage 不足 | 可保持；所有槽位合计最多五条 | 低至中；宽 query 噪声、窄 query 零结果、不同 backend 对表达响应不同 |
| D：有预算的检索反馈演化 | 例如先 3 条再按反馈生成至多 2 条，依据已返回 metadata、历史 query 和未覆盖需求决定下一步 | redundancy、coverage 不足、宽窄失衡 | 可保持 3+2；翻页/替换也必须占槽位 | 高；额外模型调用、反馈偏移、延迟和非确定性 |

### A：结构化意图与约束校验

核心是让每项约束能追溯到用户文本：实体/任务、关系与比较、否定、时间和来源分别存储，区分检索必须包含的核心语义与供后续判断的资格条件。集合层面检查每个硬条件是否有承载它的 query，同时阻止任何 query 与用户要求冲突；并非机械把所有词塞进每条 query。外部固定 before/site 仍由请求层追加。

相较原 PaSa，新增生成前意图表示与生成后验证；原 query model 权重、Selector、Expand 可保持。参考 Asta/ScholarQA 的结构化提取，但作者/时间等字段必须验证实际落到支持它的检索或评估步骤，不能“提取即完成”。预期首先减少 Q28/Q48 这类可直接核验的约束损失，不预测具体 GT 增益。

预算最多 5×10，可在请求前完成修正；额外规划 token/调用数必须单独报告。主要副作用是错误约束抽取、比较关系在 keyword 搜索中难以表达、过度保留使召回下降。A/B 应另报基于用户文本的人工盲审约束保留率，并做“只有结构化提取”与“再加校验”的消融；是否提升 Recall 仍以盲化冻结后的检索实验判断。

### B：Facet 分配与领域术语多样化

将最多五条视为一个查询组合：从用户问题识别互补 facet，保留忠实核心表达，其余槽位服务不同研究对象/任务角度或领域等价术语。没有可分解 facet 时不凭空创造，只尝试真正等价的专业表述。请求前按核心约束、组合覆盖、query 语义重复选择候选；不同的 papers/studies/research 包装不算新角度。

相较原 PaSa，新增显式槽位职责、候选选择和可审查的术语来源；仍是一次计划后静态搜索，可借鉴 Asta 的专业术语改写和 SPAR 的方向区分，但不引入其多轮/多源检索。主要针对 Q2 式表面改写，也保留 Q10 已体现的分角度优点。

候选生成数可以多于五，但发给 Serper 最多五；所有规划计算纳入成本。风险是术语不等价、过度多样化降低精确性、通用“方法/应用/局限”强套到不适合的问题。A/B 应分开比较 facet 分配与冗余筛选，固定 A 的约束机制后可做 A vs A+B；同时保留原 PaSa 对照，避免把 A 的收益误归 B。结果指标包括 unique ID yield 和返回集合重合，但这些代理指标本身不等于 GT Recall。

### C：互补表达与受控宽窄组合

保持相同意图，改变适配检索器的表达方式：例如一个忠实自然语言槽、两个专业关键词/术语槽、一个减少可选背景限制的较宽槽、一个突出用户指定子任务的较窄槽。槽位是可在独立开发集确定的通用策略示意，不是针对 RealScholarQuery 的新 query。必须区分硬约束与可选背景；宽化不能改写用户任务，窄化不能无依据锁定某个模型或 benchmark。

相比 B 的“不同语义角度”，C 主要研究**同一意图的表达与粒度**，避免把两个实验混在一起。参考 ScholarQA 的自然语言/关键词双表示及 PaperQA helper 的宽窄组合；Serper 不等同 S2/dense index，不能照搬后端专属运算符。

修改范围是静态 query 组织与请求前序列化，预算仍最多 5×10，复杂度低至中。风险包括泛化 query 把小众论文挤出 Top10、窄 query 无结果、五槽划分不适用于简单问题。A/B 先固定语义意图与 A 的约束检查，比较单一表达 vs 双表示，之后才引入宽窄分配；分别报告两个增量，不能仅凭更低字符串相似度宣称有效。

### D：有预算的检索反馈演化

第一阶段最多 3 条，第二阶段最多 2 条。后续输入只来自用户问题、已执行 query 和本题实际 Serper 返回的 title/snippet/ID 等 metadata；以新 ID 收益、结果重合、需求覆盖缺口判断剩余槽位投向。没有相关结果时回到用户需求扩大可选背景范围；相关结果丰富时补充尚未覆盖的用户 facet。论文措辞可作为检索反馈，但不能读取 GT 或已知漏失论文标题。

参考 Asta 的相关论文改写、SPAR 的历史与文档驱动演化、PaperQA 的工具反馈循环。相比原 PaSa，这是从静态改为分阶段生成：未来需要更改 query 生成及 Search 调度、状态记录；权重、Selector 和 Expand 可保持。本阶段仅提出，不执行这些更改。

搜索总预算必须由程序计数器硬限制为 5×10，反馈阶段不能隐含增加第六条、page2 或额外 metadata 网络查询；重试相同失败请求单独报告。额外模型推理使计算/延迟不再天然公平，需要同时报告质量与总成本。风险是首批结果诱导主题漂移、snippet 信息不完整、结果相关性判断错误、串行延迟。严格比较静态 5 条 vs 3+2，同时做“带历史但不带结果”的消融，区分多次模型调用和真实反馈的作用。

## 建议实验顺序与潜在收益/成本/风险

建议 **A → B → C → D**，各步均保留原 PaSa 对照，是否采用由审核和后续实验决定。

1. A 的目标缺陷最容易依据用户文本直接判定，修改面较小、归因清楚，先验证是否减少 constraint loss；没有承诺能找回多少 GT。
2. B 针对已经观察到的重复预算消耗，仍可保持静态流程，优先检验多样性要求能否转化为更多相关候选。
3. C 成本接近静态方案，但需要区分表达形式与语义粒度，且检索器敏感性更强，适合作为独立增量或替代路径。
4. D 可能适应更多未知问题，但实施与评估成本最高，搜索反馈也可能放大早期偏差；在静态对照明确后再测。

此顺序按证据直接性、潜在覆盖收益与实现/评估风险综合安排，不是对真实 Recall 增益的排序。A、B、C 可独立比较或做预先指定组合；不应默认必须全部叠加。

## 公平、可归因的后续 A/B 规范（本阶段未执行）

1. **先冻结设计，再看结果。**在独立开发问题上确定提取规则、facet、候选选择与反馈阈值，禁止读取 GT 作为 planner 输入。RealScholarQuery 的缺陷已经被审计揭示，后续 50Q 结果应视为探索性；最终泛化结论需独立保留集，不能反复对这 50 题调参。
2. **预算口径明确。**每题最多 5 条逻辑搜索、每条 num=10/page=1，同一 Serper、before/site；相同失败请求的传输重试另计 attempts，不能借重试换 query。原 baseline Q18/Q28 各 4 条，所以同时报告实际请求数，并提供这两题也限 4 条的 matched-budget 敏感性对照，避免仅靠补满 250 对 248 获益。每个 planner 的模型调用、token、GPU 时间、总 latency 另报；搜索预算相同不代表计算成本相同。
3. **新 query 需要自己的响应。**原 248 条 replay 只能重放相同 payload，不能为改写后的 query 提供反事实结果。获准实验后，原 PaSa 与候选 query 应在接近时间窗口配对采集、随机请求顺序，保存双方 replay；可做多时间窗口复验。固定 before 不冻结搜索索引。不得把本次额外 page2 结果混入 5×10 对照。
4. **其他模块冻结。**固定 Crawler/Selector checkpoint、实际生成配置、seed、日期、来源、论文库与标题 resolver、Selector 阈值、Expand 层数及其余参数；内容缓存/网络材料两臂一致。对多轮方案按同题控制历史和预算，避免不同模型或新增工具成为隐藏变量。
5. **分层评估。**首先比较 Search 候选 GT 覆盖，再比较完整 Crawler Recall 与最终 Precision/Recall/F1；后两项需要日后授权运行原 Selector/Expand。额外报用户约束保留率、unique IDs、返回重合、query 数量、失败率和成本。代理指标提高不自动证明 Recall 提高。
6. **配对统计与归因。**按题报告差值，预先指定主指标，并做题级配对 bootstrap 置信区间；生成随机性用预先固定的多个 seed 检查。对 A/B/C/D 的关键新增机制分别消融，避免堆叠后无法归因。50 题样本有限，不能仅用总数改善宣称普遍优越。
7. **评测身份口径双报。**保留冻结 baseline 的 keep_letters title 集合口径；同时报 GT ID 辅助诊断，明确 Q45 Panacea 与 Panacea+ 的标题归一化碰撞（790 组、791 个不同 query/ID）。不修改历史 baseline，也不把 ID 诊断指标冒充原官方评测。

## 本阶段状态

完成公开源码/论文机制核查与四个候选的可审阅设计。没有复制参考项目代码，没有写入新 prompt，没有实现或执行候选 planner；冻结 baseline、冻结 miss audit 与 Git commit 均保留。等待用户审阅方案后再确定下一阶段修改策略。
