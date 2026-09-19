# PASA_CRAWLER_MECHANISM_AUDIT_001

本审计的核心结论：**当前 inference 是“一次生成查询列表 → 批量 Search → 固定层数的论文/章节扩展”，不是统一的逐工具执行、接收 observation、再决定下个工具动作的解释器。与此同时，论文公开的 SFT 模板和 PPO 源码本身也以 Search/Expand session 分阶段运行，不能据此宣称 checkpoint 已经学会任意 Search↔Expand 交替或基于 SERP 的即时重查询，只是被开源 inference 隐藏了。**

论文确有 session、局部 Stop、论文队列、跨 session 状态变化，以及考虑后续引用价值的 RL；这些不是后续 Adaptive Crawler 可以重新声称的创新。新增显式检索反馈、预算状态和可学习全局结束，应分别说明是实现层恢复、机制扩展，还是尚无证据的能力假设。

## 1. 范围、版本和证据等级

- **当前 inference**：`/home/chenyi/pasa`，commit `fe89b48`。冻结正式文件的 SHA-256，见 [initial_source_hashes.json](initial_source_hashes.json)。当前不是未经修改的上游仓库：已有本地标题解析、Selector 串行化、线程异常传播和参数传递修补。
- **论文主证据**：[ACL 2025 正式版，He et al., pp.11663–11679](https://aclanthology.org/2025.acl-long.572/)，本地 [PDF](sources/pasa_acl2025.pdf)。Crawler 训练细节在 **附录 D.1/D.2**，action-cost 消融在 **G.2**。
- **版本对照**：[arXiv v1](https://arxiv.org/html/2501.10120v1)，本地 HTML 保留。v1 的对应训练附录是 **A.1/A.2**；不能把正式版的 D.2 误标为 A.2。正式版 Eq.(3) 的求和/KL 排版也与 v1 不同，下文使用正式版。
- **公开训练代码**：项目 [README:132](/home/chenyi/pasa/README.md:132)、[README:205](/home/chenyi/pasa/README.md:205) 指向 `hyc2026/trl`。本次只下载阅读，固定 commit `7a266d8b4be2cbce2ae54082ac99ba97037bfd6b`（2025-01-20）；文件在 [sources/trl](sources/trl)。它是公开训练实现证据，**不是该 checkpoint 完整生产训练 run 的日志**。
- **模型证据**：官方 [Crawler model card](https://huggingface.co/bytedance-research/pasa-7b-crawler/tree/f287c2cc6a8c53774d833730dcc6b21de12503a6) 标示 base model 为 Qwen2.5-7B-Instruct，并链接 PaSa 数据集和论文；本地读取了 tokenizer/generation 配置，没有加载权重或运行推理。
- **明确缺口**：本地没有 `data/sft_crawler/train.jsonl`；官方固定 revision 的该文件下载两次返回 HTTP 401。因此没有声称逐条核验 SFT 语料。论文的构造说明、公开训练源码与 checkpoint 实际掌握能力严格分开。
- **仅作佐证的已有产物**：[PASA_QUERY_GENERATION_AUDIT.md](/home/chenyi/pasa/PASA_QUERY_GENERATION_AUDIT.md:26)、[复现基线修补说明](/home/chenyi/pasa/BASELINE_REALScholarQuery50.md:50)。已有 005 的 Q00 输出末尾包含 `[StopSearch]`，本次只读取既有文本，不进行新生成。

证据标记：**直接定义**=论文明确描述；**代码事实**=可见函数/分支/数据流；**推断**=由上述事实推出但不是论文声明；**未证实**=不能从公开证据确认 checkpoint 能力。没有启动 Search、模型 inference、训练或新 benchmark；下载论文/源码只用于文献审计。

## 2. 论文中的 Crawler

### 2.1 state、token action 与工具 action

正式版 §4.2（pp.11666–11668）将 Crawler 表述为 token-level MDP：底层 action space 是 LLM 的词表；工具层通过 Search、Expand、Stop 三个注册函数改变状态。可把它整理为 `s_t=(当前 LLM context, Q_t)`，其中 `Q_t` 是 paper queue。这个二元写法是本审计对正文的概括，不是论文额外给出的公式。[§4.2 / Table 3](https://aclanthology.org/2025.acl-long.572.pdf#page=5)

必须区分 **MDP/environment state 包括 queue** 与 **模型 prompt 包含整个 queue**。论文只明确了 session 的两种起点：`S_q` 的 context 只有 query；`S_{q+p}` 的 context 是 query 加当前论文 title、abstract、章节/子章节 outline。没有给出“把所有候选、分数、已发现量、总预算序列化给模型”的实现规定。[§4.2 session 定义](https://aclanthology.org/2025.acl-long.572.pdf#page=6)

在本地 tokenizer 中，`[` 和 `]` 的词表 ID 是58、60，`[Search]` 等完整字符串不是独立词表项，亦不在已检查的 special-token 列表内。故论文的工具标记是动作协议的抽象，不应误写成“每个工具调用必然对应一个新增 special token”。静态检查记录见 [source_provenance.json](source_provenance.json)。

### 2.2 三种工具动作和 Stop 的精确定义

| 动作 | 论文的含义 | 不应误解为 |
|---|---|---|
| Search | 从 context 生成检索 query，调用检索工具，返回论文加入队列 | 天然包含 Page2、自动翻页、读回全部 SERP 或预算控制 |
| Expand | 生成当前论文的 subsection name，工具抽取该小节引用论文并加入队列 | 模型逐篇挑引用、自由读全文、调用 forward citation search |
| Stop | 结束当前 session，context 重置为用户 query 加队列的下一篇 paper | 整个任务的 Finish、关闭全局队列、停止全部后续检索 |

证据：[Table 3、Fig.2 和 §4.2](https://aclanthology.org/2025.acl-long.572.pdf#page=5)。query-only session 中 Stop 意味着离开搜索 session；paper session 中意味着停止处理当前 paper。若无下一 paper，如何实现所有终止边界，论文没有给出完整运行时状态机；不能自行补出一个模型学习的全局 Finish。

### 2.3 Search 和 Expand 能否交替？必须按粒度回答

- **同一完整任务 trajectory 中同时含 Search 和 Expand：是。** Fig.2 和 session 分解都明确包含两者。
- **Search 后根据得到的论文继续决定 Expand：是。** 新论文的 title/abstract/outline 决定下一 paper session 的上下文。
- **同一 session 中任意混合两类动作，或 Expand 之后自主回到 Search：未证实。** Table 3 的广义函数注册没有逐状态列出禁止条件，但附录 Table 11 将两种 session 分开；Fig.2 也不能作为已经训练过任意交替的证据。
- **同一个 Search session 内，执行第一条 query 后把外部结果作为 observation 再生成第二条 query：没有明确描述或公开训练证据。** 自回归后续 token 依赖此前生成 token，不等于依赖已执行工具的 observation。

因此不能把“概念 action registry 允许表达”直接推成“公开训练和 checkpoint 已掌握并验证”。[Table 11 / D.1](https://aclanthology.org/2025.acl-long.572.pdf#page=13)、[D.2](https://aclanthology.org/2025.acl-long.572.pdf#page=14)、[公开 PPO 调度:373–415](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L373-L415)。

### 2.4 paper queue、context reset 和 subsection references

队列保留跨 paper 的发现过程；context reset 用来避免将数百篇论文的完整轨迹持续塞进上下文。跨 session 保留的是环境中的队列，不意味着上一 paper 的完整对话历史持续可见。Expand 以章节名为入口，引用抽取由工具完成。论文 §5.1 还描述了本地论文数据库和缺失时的 ar5iv 获取/解析/存储。[§4.2](https://aclanthology.org/2025.acl-long.572.pdf#page=6)、[§5.1](https://aclanthology.org/2025.acl-long.572.pdf#page=7)

论文的具体 session template 只显示 title、abstract、sections；所以“能通过工具获取完整论文”与“Crawler token context 里有完整正文和引用清单”不是同一事实。此处不将广告式 read papers 表述扩张为未证实的 full-text reasoning 接口。

## 3. Crawler 的训练机制及公开实现边界

### 3.1 Imitation learning：两类 session，不是带逐工具 observation 的完整对话

AutoScholarQuery 来自论文 Related Work 中的问题与被引论文；它主要提供 query/答案集合而非人类检索轨迹。Crawler 的 imitation 数据另行构造：

1. **Search session（3,011 条）**：从训练 query 出发，让 GPT-4o 生成互补检索词；把每条前面加 Search 标记、串接，最后加 Stop。
2. **Expand session（9,978 条）**：用上述 query 搜索并抽取结果论文，构成 `query+paper` 输入；逐 subsection 检查是否引用该 query 的已知 GT，命中则选，否则以10%概率选以增加多样性；把选中章节串成 Expand 列表，最后 Stop。
3. 合计 **12,989 条 session**，先 SFT，再 PPO。§5.1 另报告 imitation 阶段接触5,000个 query、RL 阶段16,000个 query；不能把 session 条数和独立 query 数当成同一计量单位。

[正式版 D.1 / Tables 10–11](https://aclanthology.org/2025.acl-long.572.pdf#page=13)、[§5.1](https://aclanthology.org/2025.acl-long.572.pdf#page=7)。模板中没有“搜索响应消息夹在两条 Search 中间”，也没有混合 Search/Expand 的监督示例规格。SFT 章节选择来自引用标签规则，不应误写为 GPT-4o 任意规划完整工具链。

### 3.2 相关论文 reward + action cost

论文 Eq.(1)–(2) 可写为：

\[
r(s_t,a_t)=\alpha\sum_{i=1}^{n_t}\mathbf{1}\{(p_i\in\mathcal P\;\lor\;\mathrm{Selector}(q,p_i)=1)\;\land\;p_i\notin Q_t\}-c(a_t).
\]

只有新发现且相关的论文贡献奖励；GT 与 Selector 是“或”，旨在缓解不完整 GT 导致的稀疏奖励，不是要求二者同时认定。重复发现不应继续获得相同新论文奖励。Stop 不添加论文。正式版 Table 12：`α=1.5`，`c(Search)=c(Expand)=0.1`，`c(Stop)=0`，故按论文立即奖励定义 Stop 为0。[Eq.(1)](https://aclanthology.org/2025.acl-long.572.pdf#page=5)、[Eq.(2)](https://aclanthology.org/2025.acl-long.572.pdf#page=6)、[Table 12](https://aclanthology.org/2025.acl-long.572.pdf#page=14)

**action cost 确实用于抑制无效或过多的 Search/Expand。** G.2/Table 15 中，cost 为0、0.1、0.2时，报告的 Crawler Actions 分别为1296.3、382.4、230.1。这是论文已有的效率机制，不能把“通过动作代价减少搜索/展开”本身作为新增创新。[G.2 / Table 15](https://aclanthology.org/2025.acl-long.572.pdf#page=15)

推断：当后续动作预期净收益较低时，cost 会支持少生成动作、较早结束局部 session；但不存在“cost 自动等于硬预算约束”或“因 cost 已学会何时结束全任务”的推论。长期价值可能仍使低立即回报动作值得执行。

### 3.3 Session-level PPO：长期价值不等于在线 SERP 反馈

正式版 Eq.(3) 的结构是：session 内折扣累计立即 reward，并对动作带来的新论文加入 `γ1·Σ V(S_{q+p})`，再施加相对 SFT policy 的 per-token KL 项；Eq.(4) 是 return 减 value 的 advantage，Eq.(5)–(8) 给出 PPO policy/value 目标。正式版参数包括 `γ0=1`、`γ1=0.1`、`β=0.1`、value-loss 系数10。[§4.2 Eq.(3)–(8)](https://aclanthology.org/2025.acl-long.572.pdf#page=6)、[Table 12](https://aclanthology.org/2025.acl-long.572.pdf#page=14)

这使“当前论文不直接相关，但引用网络后续有价值”成为原 PaSa 已有目标。不得把跨 session 长期回报/不相关桥梁论文探索写成后续项目首次提出。

D.2 描述每设备每步4个 Search sessions，从结果随机取6篇作 Expand，再从扩展结果产生6个 Expand sessions，共16条 session；并先训练 value，再联合训练。它是截取的 session rollout，不是每次在一条完整队列上无上限地跑到底。

### 3.4 公开训练源码真正做了什么

以固定 commit `7a266d8` 为准，以下是**代码事实**，不是猜测模型内部行为：

- [AgentDataset:5–42](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/agent_dataset.py#L5-L42) 分别构造 query-only 或 query+paper prompt；GT answers 作为独立训练数据传给 reward 端，不在这两个 prompt 模板内。
- [PPOTrainer.train:373–407](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L373-L407) 先 `batch_generation(...)` 得到整段 response，再 `rollout(...)`；不是生成 Search 一条便暂停、执行并追加结果再继续生成。
- [response_handler:138–183](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L183) 由外部 `typ` 选择 Search regex 或 Expand regex。正常成功路径的外部调度从 Search 变为 Expand，不是模型自主选择下一 session 类型；无论文的异常 fallback 是代码复用输入，不是基于反馈的自主 requery。
- [rollout:304–328](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L304-L328) 将结果论文构造成下一批 prompt。故训练确有 **跨 session 的检索结果条件化**，但未看到同 session 内逐次 SERP observation 反馈。
- [response_handler:185–249](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) 计算去重后的相关奖励、新论文 value、cost 和 stop shaping，并把分数定位到 response token；[trainer:517–542](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L517-L542) 加 KL 并以 GAE 算 advantage。不能把训练 reward 的反馈与推理 prompt 里的 observation 混称为同一种反馈。

训练阶段有外部资源/长度约束：README recipe 的 `rounds=3`、`response_length=1024`，handler 的 `max_action=5`，固定下一轮6条、有限 paper 样本等；默认 PPOConfig 的 rounds=2、reward/cost 默认值与 recipe 也不相同。它们不是模型可观察的“剩余总调用预算”，也不是显式 global Finish。[README:235–248](/home/chenyi/pasa/README.md:235)、[PPOConfig:61–76](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_config.py#L61-L76)

### 3.5 checkpoint 学过什么、不能确认什么

| 可支持的表述 | 证据强度 | 不应升级为 |
|---|---|---|
| 发布训练方案包括多 query Search session 和元信息驱动的章节 Expand session | 论文、公开模板/rollout 一致支持 | 每个权重训练 run 的全部样本、顺序和配置已核验 |
| 方案包含相关性奖励、动作代价、跨 session value 与停止标记 | 论文有定义，公开代码有实现但细节不同 | checkpoint 已稳定掌握任意全局规划 |
| 历史原生输出会生成 StopSearch | 已有输出文件直接证据 | StopSearch 会触发当前 Python orchestration 停止整个任务 |
| 泛化到混合动作、SERP 即时重查询、预算条件化 | **未证实** | “模型早已学会，只须解锁”或“模型一定做不到” |

缺少精确训练日志、完整 SFT 语料访问与该类行为验证，所以对“学过/掌握”仅作训练证据支持范围内的判断。本阶段不以新推理实验填补这些未知。

## 4. 当前 inference 的真实运行机制

结论是用户提出的流水线形式成立，但要补充两个限定：**多个查询是一次生成的列表，而非固定必须5条；每层只对当前选定 frontier 的每篇论文各生成一份章节列表。**

```text
run()
  search()
    Crawler.infer(query-only prompt) 一次完整生成
    regex 取前 search_queries 条
    批量 Search → metadata → Selector → papers_queue
  for depth in range(expand_layers):
    新 frontier 按 Selector score 排序
    depth=0 全取；depth>0 最多 expand_papers
    取论文 section keys；各自构造 query+paper prompt
    Crawler.batch_infer() 完整生成各篇章节列表
    do_expand() 解析所有 Expand → 引用标题 → resolver → Selector → 新论文入队
  return
```

证据：[run/search](/home/chenyi/pasa/paper_agent.py:132)、[expand/run](/home/chenyi/pasa/paper_agent.py:223)。完整函数、数据流和 Mermaid 图见 [inference_call_graph.md](inference_call_graph.md)。

关键边界如下：

- `Agent.infer()` / `batch_infer()` 都是独立 user-message prompt，生成最多512个新 token，返回后才解析；没有维持跨次调用的聊天历史，也没有工具回调。[models.py:47–102](/home/chenyi/pasa/models.py:47)
- `sample=False` 仅表示不覆盖为自定义高温采样，不代表强制 greedy。当前 checkpoint 的 generation_config 仍设 `do_sample=true, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.05`。[generation_config.json:1](/home/chenyi/pasa/checkpoints/pasa-7b-crawler/generation_config.json:1)
- Search utility 只返回去重 ID；完整响应、排名和 snippet 不构成 Crawler observation。模型在初始 query 列表生成之后，不会再次查看搜索反馈来补 query。[utils.py:44–81](/home/chenyi/pasa/utils.py:44)
- Expand 的 prompt 是 `question+title+abstract+sections.keys()`；正文、具体被引论文、Selector score、已命中量、失败率和剩余预算均未传入。[get_paper_content:153](/home/chenyi/pasa/paper_agent.py:153)
- Selector 只算一个 token 的 True 概率；>0.5 才进入 selected 集，但低分候选仍入 queue。score 用于之后排序，不是 Crawler 的显式 observation。[models.py:28](/home/chenyi/pasa/models.py:28)、[search_paper:111–130](/home/chenyi/pasa/paper_agent.py:111)
- `expand_layers=2` 是 Python 固定循环；`expand_papers=20` 只限制 `depth>0`，并且被截断的旧 frontier 项被指针越过，不会在下一层自动补处理。最后一轮产生的节点可以评分/入结果，但不再扩展。[expand:223–232](/home/chenyi/pasa/paper_agent.py:223)
- `[Stop]`、`[StopSearch]`、`[StopExpand]` 均无显式分支。它们可以作为 regex 的下一个 `[` 分隔符，或与自然 EOS 一同结束文本，但不是运行时状态迁移指令。生成了 Stop 后如果仍有后续可匹配 action，当前 regex 不会因 Stop 而截断。此项是静态逻辑推断，没有构造新模型实验。[templates:67–70](/home/chenyi/pasa/paper_agent.py:67)、[do_expand:189](/home/chenyi/pasa/paper_agent.py:189)
- `metrics.py` 的 `−0.1` 是读取结果树后统计 score 的代码，没有被 `run()` 作为在线 reward、预算或停止条件调用。不能将它误当实时 action cost 控制。[metrics.py:29–49](/home/chenyi/pasa/metrics.py:29)

**它不是完全无反馈。** 下一层论文的元信息来自前一层执行结果；缺失的是对累计检索反馈进行新的 Search 决策、统一选择动作类型、调整总体预算/停止的接口。

## 5. 论文与代码对照矩阵

判定只针对当前条目限定的机制：`MATCH`=在该范围一致；`PARTIAL`=保留部分机制但 observation/调度/范围不同；`MISSING`=明确定义的运行时机制未实现；`UNCLEAR`=论文/训练证据不能证明该能力。`global Finish` 的 MATCH 表示两侧均未定义这个显式动作，绝不是“已有 Finish”。

以下与 [paper_vs_code_matrix.json](paper_vs_code_matrix.json) 同源；JSON 含逐条 discrepancy、uncertainty 和完整证据索引。

| 项目 | 标记 | 论文定义 / 边界 | 训练证据 | 当前 inference | 证据 |
|---|---|---|---|---|---|
| state representation | PARTIAL | 形式状态=当前 LLM context + paper queue；Sq 为 query-only，Sq+p 为 query+当前论文元信息。并未明确整个 queue 被序列化成 token。 | 公开训练 prompt 为 query-only 或 query+title+abstract+section names；结果论文用于下一 session。 | Python 保存 queue/touch_ids/score/树；Crawler 输入只有 query 或 query+单篇论文元信息，无队列全集、分数、剩余预算。 | [P_STATE](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [T_DATA](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/agent_dataset.py#L5-L42) [T_NEXT](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L255-L330) [C_INIT](/home/chenyi/pasa/paper_agent.py:30) [C_CONTEXT](/home/chenyi/pasa/paper_agent.py:138) [C_PROMPT](/home/chenyi/pasa/agent_prompt.json:1) |
| action space | PARTIAL | token-level action 是词表；工具层函数为 Search、Expand、Stop。 | 按外部 typ 只解析 Search 或 Expand；StopSearch/StopExpand 被 reward handler 识别。 | Search 阶段只提取 Search 文本；Expand 阶段只提取 Expand 文本；没有统一三动作 dispatcher。 | [P_STATE](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [T_ACTION](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L183) [T_REWARD](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) [C_INIT](/home/chenyi/pasa/paper_agent.py:30) [C_SEARCH](/home/chenyi/pasa/paper_agent.py:132) [C_DOEXP](/home/chenyi/pasa/paper_agent.py:181) |
| Search 决策 | PARTIAL | 根据当前 context 生成 query 调用 Search；训练协议从 Sq 开始。 | 先产生整个 Search session，再 rollout；正常路径随后只构造 Expand session。 | run 固定先且仅调用一次 search；模型决定 query 文本及可解析数量，不能在 Expand 后重启 Search。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) [C_SEARCH](/home/chenyi/pasa/paper_agent.py:132) |
| query generation | MATCH | Search session 是多条互补 query 的序列；偏好 survey 是公开 prompt 的一部分。 | GPT-4o 合成 query 列表再串接 Search 标记；公开训练 prompt 与当前 prompt 同型。 | 一次 infer 自回归生成多个 query，regex 后取至多 search_queries=5；尚无外部检索反馈。 | [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_DATA](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/agent_dataset.py#L5-L42) [C_SEARCH](/home/chenyi/pasa/paper_agent.py:132) [C_INFER](/home/chenyi/pasa/models.py:47) [C_PROMPT](/home/chenyi/pasa/agent_prompt.json:1) |
| retrieval feedback | PARTIAL | 结果入 queue，下一 paper session 的输入依赖检索结果；同一 Search session 是否注入逐次结果未明确。 | batch_generation 先完成，rollout 后执行 Search；下一轮看到新论文元信息而非上一页完整 SERP。 | Search 结果转成论文对象；后续 Expand 看单篇 title/abstract/section keys，初始 query 生成不会被结果修订。 | [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [T_NEXT](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L255-L330) [C_SEARCH](/home/chenyi/pasa/paper_agent.py:132) [C_CONTEXT](/home/chenyi/pasa/paper_agent.py:138) [C_GOOGLE](/home/chenyi/pasa/utils.py:44) |
| Search/Expand 是否可交替 | UNCLEAR | 一条任务轨迹包含 Search 和 Expand 已明确；是否支持同 session 混合或 Expand→Search→Expand 自由交替未明确。 | 模板分 Search/Expand 两种；正常 PPO 调度 Search→Expand→Expand。没有受反馈驱动的混合动作训练证据。 | 严格 Search phase→若干 Expand layers，没有回 Search 的边。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [P_PPO](https://aclanthology.org/2025.acl-long.572.pdf#page=14) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [T_ACTION](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L183) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) |
| subsection selection | PARTIAL | 模型选 subsection name；工具把该 subsection 引用论文入队。 | SFT 按引用命中 GT/10% 多样性选择；公开训练按规范化章节名匹配。 | 模型选 keys；仅 exact section name 生效，程序展开该节引用标题，再解析、去重、评分。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_ACTION](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L183) [C_CONTEXT](/home/chenyi/pasa/paper_agent.py:138) [C_DOEXP](/home/chenyi/pasa/paper_agent.py:181) [C_REF](/home/chenyi/pasa/paper_agent.py:158) [C_TITLE](/home/chenyi/pasa/utils.py:658) |
| paper queue | PARTIAL | Search/Expand 追加结果；Stop 换下一 paper；Eq.(2) 依全局 Qt 去重。 | 公开 reward 的 searched_paper_set 在每次 response_handler 内新建；下一批论文由 reward/prob 排序取六条。 | queue 为分层列表；以 Selector 分数排序新 frontier；第一层全取，之后最多20，指针越过未取项。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [T_REWARD](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) [T_NEXT](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L255-L330) [C_EXPAND](/home/chenyi/pasa/paper_agent.py:223) [C_NODE](/home/chenyi/pasa/paper_node.py:14) |
| Stop 语义 | MISSING | 结束当前 session：query-only 时结束搜索 session，paper session 时结束当前 paper；context reset 到 query+下一 paper。 | 训练识别 StopSearch/StopExpand 并给 stop 位置奖励；不是 global Finish。 | 没有 Stop parser 或分支；生成由 EOS/token cap 结束，Python 固定执行后续调度；空 Expand 列表仅间接跳过该 paper。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [T_REWARD](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) [C_INFER](/home/chenyi/pasa/models.py:47) [C_BATCH](/home/chenyi/pasa/models.py:74) [C_DOEXP](/home/chenyi/pasa/paper_agent.py:181) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) |
| global Finish | MATCH | 未定义明确的可学习 global Finish；Stop 不等于任务完成，实践另有深度限制。 | 未见 global Finish 动作或模型输入的总预算；训练以 rounds/长度等外部界限截止。 | run 在固定 layers 迭代后返回；模型无整体结束任务动作。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SETUP](https://aclanthology.org/2025.acl-long.572.pdf#page=7) [P_PPO](https://aclanthology.org/2025.acl-long.572.pdf#page=14) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [T_CONFIG](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_config.py#L53-L76) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) |
| budget awareness | PARTIAL | cost 是优化目标中的软惩罚；§5.2 有外部探索深度上限，不等于显式剩余预算状态。 | rounds、max_action、response_length 等外部限制；未见面向模型的 global budget 字段。 | search_queries/search_papers/expand_layers/expand_papers/max_new_tokens 是外部上限，没有预算 observation。 | [P_REWARD](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SETUP](https://aclanthology.org/2025.acl-long.572.pdf#page=7) [P_PPO](https://aclanthology.org/2025.acl-long.572.pdf#page=14) [T_ACTION](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L183) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [T_CONFIG](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_config.py#L53-L76) [C_INIT](/home/chenyi/pasa/paper_agent.py:30) [C_INFER](/home/chenyi/pasa/models.py:47) |
| action cost | PARTIAL | r=α·新增相关论文数−c；Search/Expand=0.1，Stop=0；附录 G.2 验证降低无效动作。 | README 覆盖参数匹配论文；公开 handler 又含截断、+cost stop shaping、局部去重和 Selector stub。 | 不在线计算 cost 或 reward；训练影响可能保留在输出中；metrics.py 的−0.1是离线统计。 | [P_REWARD](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_PPO](https://aclanthology.org/2025.acl-long.572.pdf#page=14) [P_COST](https://aclanthology.org/2025.acl-long.572.pdf#page=15) [T_REWARD](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) [T_STUB](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L116-L118) [C_RECIPE](/home/chenyi/pasa/README.md:205) [C_METRICS](/home/chenyi/pasa/metrics.py:29) |
| multi-step feedback loop | PARTIAL | 通过新论文 session 连续探索引用网络；跨 session value 为长期信用分配。 | 有下一轮 paper-context 条件化；无 session 内执行一步再生成一步的外部反馈。 | 后层 prompt 依赖前层找到的论文，所以不是完全无反馈；反馈仅在固定分层的论文元信息上。 | [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [T_NEXT](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L255-L330) [C_CONTEXT](/home/chenyi/pasa/paper_agent.py:138) [C_EXPAND](/home/chenyi/pasa/paper_agent.py:223) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) |
| trajectory execution | PARTIAL | 概念上 token MDP + session 分割；展示模板为同类动作串。 | 先 generate 整串再解析执行，与推理批量阶段具有结构相似性。 | 两处 generate 都先返回整串，后执行匹配动作；不按文本中的 Search/Expand/Stop 全局顺序解释。 | [P_STATE](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [C_SEARCH](/home/chenyi/pasa/paper_agent.py:132) [C_DOEXP](/home/chenyi/pasa/paper_agent.py:181) [C_INFER](/home/chenyi/pasa/models.py:47) |
| inference-time policy autonomy | PARTIAL | 模型决定查询与章节，并通过 RL 优化发现相关论文；论文的广义自主描述不能代替具体控制协议。 | 支持两类 session 技能和跨 session value 学习；精确 checkpoint 的任意混合/预算/重查询能力未经证明。 | 自主部分=生成 query/选章节/输出数量；调度类型、队列排序、深度、截止、TopK、工具与 Page1 由代码决定。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [T_LOOP](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L366-L423) [C_RUN](/home/chenyi/pasa/paper_agent.py:234) [C_EXPAND](/home/chenyi/pasa/paper_agent.py:223) [C_GOOGLE](/home/chenyi/pasa/utils.py:44) |
| cross-session long-term value | PARTIAL | Eq.(3) 已把新论文的下一 session 估值加入 return，允许经不直接相关论文寻找后续相关文献。 | call_vm 估计论文 prompt 的值，handler 加 gamma1·value；训练代码的采样/截断另有限制。 | 只加载 Crawler/Selector；queue 按 Selector 当前相关性排序，不在推理时调用 value head。 | [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [T_VM](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L47-L87) [T_REWARD](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L185-L249) [C_ENTRY](/home/chenyi/pasa/run_paper_agent.py:29) [C_EXPAND](/home/chenyi/pasa/paper_agent.py:223) [C_NODE](/home/chenyi/pasa/paper_node.py:14) |
| paper body / sections / references observation | PARTIAL | 可读论文的具体 session 输入列为 title+abstract+outline；不应把抽象 read papers 解释为完整正文进 LLM。 | 模板与公开 gen_value_model_prompt 仅含元信息和 section names。 | 正文由工具解析成 section→reference titles；Crawler 只收到 keys，不收到正文或引用列表。 | [P_FUN](https://aclanthology.org/2025.acl-long.572.pdf#page=5) [P_SFT](https://aclanthology.org/2025.acl-long.572.pdf#page=13) [T_DATA](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/agent_dataset.py#L5-L42) [T_VM](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L47-L87) [C_CONTEXT](/home/chenyi/pasa/paper_agent.py:138) [C_SECTIONS](/home/chenyi/pasa/utils.py:255) [C_NODE](/home/chenyi/pasa/paper_node.py:14) |
| Selector / reward versus inference scoring | PARTIAL | 训练时辅助相关性 reward；推理时判断相关，§4.3 允许单 token 概率用于排序。 | 公开 call_selector 为待部署占位；仅从 release 不能重建生产训练的服务结果。 | 计算 True token 全词表 softmax 概率，以>0.5筛选；结果入队不要求通过阈值；score只影响排序，不作为 Crawler prompt。 | [P_RETURN](https://aclanthology.org/2025.acl-long.572.pdf#page=6) [P_SETUP](https://aclanthology.org/2025.acl-long.572.pdf#page=7) [T_STUB](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L116-L118) [C_SELECTOR](/home/chenyi/pasa/models.py:28) [C_SEARCH_PAPER](/home/chenyi/pasa/paper_agent.py:94) [C_DOEXP](/home/chenyi/pasa/paper_agent.py:181) [C_EXPAND](/home/chenyi/pasa/paper_agent.py:223) |


## 6. Discrepancy 清单：不自行调和

### D01：广义函数调用叙述 vs generate-then-execute

论文 §4.2 将函数调用描述为 action 触发后改变 state；当前 inference 在模型返回完整文本后才执行所有 Search 或 Expand。**不能将二者描述为逐工具 observation 闭环等价。** 但 D.1 模板与公开 PPO 源码本身也是 session 列表式；所以不能把这全部归因于本地 inference 后来删除了一个原已实现的通用 ReAct loop。[论文](https://aclanthology.org/2025.acl-long.572.pdf#page=5)、[公开训练:383–407](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/trl/trainer/ppo_trainer.py#L383-L407)、[当前 search:132](/home/chenyi/pasa/paper_agent.py:132)

### D02：论文 Stop/reset vs 当前无 Stop handler

论文明确定义 Stop 为 session 切换；代码仅在每次调用时重新构造 prompt、由固定循环选择下一 paper。**上下文结果相似不等于 Stop 的控制语义得到实现。** 模型仍可以通过少输出章节或生成空列表间接少展开，但无显式整体控制权。

### D03：Stop 标记和奖励数值不同

论文使用 `[Stop]`，Table 12 指其 cost=0且不增 paper，立即 reward=0。公开 `response_handler` 检查的是 `[StopSearch]` / `[StopExpand]`，并在最后相应 `]` token 处写入 **`+cost`**。这是额外 shaping 的可见代码事实，不能未经作者/日志证据就声称它在所有情况下与论文定义完全抵消等价。[Table 12](https://aclanthology.org/2025.acl-long.572.pdf#page=14)、[utils:145–154、238–249](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L138-L249)

### D04：附录随机抽论文 vs 公开 rollout 排序取六条

D.2 写从结果随机采样6篇。公开 `rollout()` 却按相关性 prob 降序排序，取前6，数量不足时重复列表补齐；未见该位置的随机抽样。明确记为训练描述/代码差异，不假定发布 checkpoint 究竟采用哪一个分支。[D.2](https://aclanthology.org/2025.acl-long.572.pdf#page=14)、[utils:304–328](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L304-L328)

### D05：全局新论文奖励 vs 每个 response 的局部去重

Eq.(2) 以全局 `Q_t` 判定新发现。公开训练在每次 `response_handler` 内新建 `searched_paper_set`；它能防同一 response 内重复，但没有据此证明全任务跨 session 去重。另有分数裁剪 `[-search_cost,5]`、前5个 action 的工具执行限制、新论文 value 采样上限。因此只能说实现了类似结构的 reward，不能说精确逐项复现公式。[Eq.(2)](https://aclanthology.org/2025.acl-long.572.pdf#page=6)、[utils:163–236](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L163-L236)

### D06：论文 Selector 辅助奖励 vs release 占位服务

公开 `call_selector()` 默认返回全0，并警告用户部署服务；README 也要求补该函数。不能凭这份可下载代码推断作者训练没有 Selector；也不能声称不补服务就能重现论文 reward。训练服务配置与实际返回值是 provenance 缺口。[call_selector:116–118](https://github.com/hyc2026/trl/blob/7a266d8b4be2cbce2ae54082ac99ba97037bfd6b/custom_agent/utils.py#L116-L118)、[README:210](/home/chenyi/pasa/README.md:210)

### D07：原理中的队列消费 vs 固定 frontier 裁剪

论文概述依次处理 paper queue；当前代码按层排序、截断并移动 frontier 指针，存在未处理但被跳过的论文。论文已有 §5.2 深度上限，故不能说论文完全无限预算；但具体每层 Top20、首层不截断、队列切片行为不是 Table 3 Stop/reset 所规定的同一调度器。[paper_agent.py:223–237](/home/chenyi/pasa/paper_agent.py:223)

**不强行认定层数不一致**：论文说探索深度3，当前默认2次引用 Expand，加上初始 Search 的 paper layer，可能对应3个 paper 层；root depth=-1、Search depth=0的计数方式也影响叫法。论文未明确到足以据数字 alone 断定 bug。此项保留计数约定不确定，而非擅自宣布完全匹配。

### D08：本地复现 resolver 与论文 paper management

论文 §5.1 描述缺失时 ar5iv 获取并写数据库；当前 title resolver 只做本地唯一匹配，miss/ambiguous 即跳过。ID metadata 路径仍可访问 arXiv，sections 缺失时仍可拉 ar5iv，所以不能把当前实现说成“全程离线”。当前所读代码也没有相应持久化新文献回 ZIP 的写入路径。[utils.py:305](/home/chenyi/pasa/utils.py:305)、[utils.py:658](/home/chenyi/pasa/utils.py:658)、[复现说明:52–58](/home/chenyi/pasa/BASELINE_REALScholarQuery50.md:52)

### D09：长期 value 已在训练出现，但推理调度只用 Selector

Eq.(3) 训练新论文 future value；当前仅加载 Crawler/Selector，队列按 select_score 排序，没有 value-model 推理。不能把“没有显式 value 调度”说成“policy 绝不受长期价值训练影响”；二者是不同层面。[Eq.(3)](https://aclanthology.org/2025.acl-long.572.pdf#page=6)、[入口:41–42](/home/chenyi/pasa/run_paper_agent.py:41)、[PaperNode.sort_paper:41](/home/chenyi/pasa/paper_node.py:41)

### D10：主流程阶段化并非此次复现修补造成

对照本地历史上游基线 `2aaa6a9`，同样具有 `search()` 一次、固定 `expand_layers` 和整批章节生成。当前相对该版本的 `paper_agent.py` 变化主要是 Selector 串行化和异常传播；`run_paper_agent.py` 修正 search_queries 参数误传。完整静态 diff 存在 [sources/local_vs_upstream.diff](sources/local_vs_upstream.diff)，上游代码快照在 [sources/upstream_paper_agent_2aaa6a9.py](sources/upstream_paper_agent_2aaa6a9.py)。不能把这些本地基础设施补丁当作丢失通用 action loop 的原因。

## 7. 三层能力边界

| 能力 | 论文方法 | checkpoint 训练证据 | 当前执行许可 |
|---|---|---|---|
| 生成多条互补查询 | 明确 | SFT/RL Search session 支持 | 允许，一次生成、至多 K 条 |
| 按当前 paper 选择 subsection | 明确 | SFT/RL Expand session 支持 | 允许，按实际 section keys 解析 |
| 局部 session 停止 | 明确 | 有 Stop 类文本与 shaping 证据；实际行为质量未知 | 标记无 handler；数量/空列表可间接影响执行 |
| 通过新论文 context 连续探索 | 明确 | 跨 session rollout 支持 | 允许，但只在固定 frontier/layers 中 |
| 奖励长期引用价值 | 明确 | value bootstrap 代码支持 | 可有训练遗留偏好；无在线 value head 调度 |
| 同一 Search session 读 SERP 后改下一 query | 没有具体 observation 协议证明 | 公开模板/rollout 不提供该训练路径 | 不允许 |
| Expand→Search 的自主重规划 | 广义 action 描述未禁止，具体协议未证实 | 未见正常混合/回搜 session 训练 | 不允许 |
| 明确剩余全局预算条件化 | 未见定义 | 未见输入字段或训练机制 | 不允许 |
| 模型 global Finish | 未定义 | 未见动作或监督 | 不允许；固定循环结束 |

“未见训练路径”不等于一般 LLM 不可能泛化；“理论可表达”也不等于发布 checkpoint 已掌握。这两种跨层推断都不在本审计结论内。

## 8. 当前真正可优化的位置与创新归属

### 8.1 当前代码是否限制论文 Crawler 可能具有的 sequential decision capability？

**是，就运行时接口而言。** 外部工具返回不会影响同一 Search session 的下一条查询；没有显式 Stop/reset dispatcher，没有 Search/Expand 回转边，预算与全局结束由 Python 固定。即使模型产生跨阶段动作，当前 parser 也不会执行不属于当前阶段的类型。

**但不能进一步断言它阉割了一个已被原 checkpoint 验证掌握的通用反馈策略。** 原论文模板和公开 PPO 也明显阶段化；当前保留了论文最清楚记录的 query generation、paper-conditioned subsection selection 和有限多层引用探索。因此限制是可观察的 orchestration 边界，潜在被限制能力的实际质量仍未知。

### 8.2 Retrieval-feedback-driven Adaptive Crawler 属于恢复、扩展还是两者？

**应判为“两者都有”，并逐部件归属；其中明确的 SERP 反馈重查询更应归为扩展，而非已证实能力的简单恢复。**

| 部件/说法 | 合理归属 | 边界 |
|---|---|---|
| 忠实执行论文局部 Stop/context reset、区分 session 生命周期 | 恢复/补齐论文明确接口 | 不据此宣称性能提升；当前独立 prompt 已实现部分 reset 结果 |
| 把已有 Search/Expand 操作接入统一 action executor | 实现层整合，部分恢复方法抽象 | 不能宣称原模型已学会任意混合选择；这是行为证据缺口 |
| 将实际检索质量、重复、失败等反馈变成模型可见状态，并据此再 Search | 相对所审计训练/inference 的机制扩展 | 原论文一般 MDP 表述不足以证明具体接口已存在 |
| 预算条件化、跨 session 资源分配、任务级 Finish | 相对已查证 PaSa 的扩展 | 不把 action cost 或深度上限混称为同一机制 |
| 更多层引用探索、互补 query、选择 subsection、RL 长期 value、动作 cost | 原 PaSa 已有，或简单实现参数变化 | 本身不能作为新方法贡献 |

这里仅界定能力和贡献归属，没有设计 Planner、新 prompt、训练方案、routing 规则或实验配置。

### 8.3 哪些创新表述合理，哪些不合理？

可合理保留为**未来待验证的贡献方向**：明确且可审计的 retrieval-observation state；利用实际反馈作下一步 query/工具选择；有显式预算状态的跨 session 控制；与局部 Stop 区分的全局停止；使候选重复/源失败/执行成本进入控制决策的机制。当前源码中能定位的作用点是 observation 构造、action dispatch、frontier 调度和任务终止，而不只是改 `generate_query` 文案。

这些只是相对本次审计的 PaSa 证据范围的潜在差异，不构成跨全部文献的 novelty 证明，更不构成有效性结果。本阶段没有实现或验证它们。

不应使用的创新表述包括：“首次让 PaSa 多步搜索”“首次 Search+Expand”“首次考虑长期相关论文收益”“首次用 action cost 减少动作”“首次从不相关中间论文发现相关引用”“首次做局部 Stop”。这些均与原论文已有设计冲突，或过度否认当前实现的跨 paper 信息依赖。

**最终机制判断：当前开源 inference 的自主性集中于生成检索词与选择章节，整体动作调度由程序限定。后续 Adaptive Crawler 若以真实检索反馈和预算来决定下一步，既可能补齐论文显式 session 接口，也引入公开训练/推理未证实的新控制能力；必须分别陈述，不能整体包装成“恢复 checkpoint 原本已有的完整能力”。**
