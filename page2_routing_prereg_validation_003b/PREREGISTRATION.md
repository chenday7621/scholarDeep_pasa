# PAGE2_ROUTING_PREREG_VALIDATION_003 — PREREGISTRATION

冻结时间 UTC：2026-09-17T03:07:55.907028+00:00
状态：**未激活；兼容性 gate 已要求停止，未抽取正式 50 题。**

本文件冻结用户指定的协议和当前 gate 结论。未激活时，本文件不是完成 50 题实验的声明，不授权绕过停止条件。

## 固定假设和数据

- 方向固定：同题 native Page1 结果集合的 max_jaccard 越高，该 query 越值得继续搜索 Page2。
- Princeton LitSearch；specificity=1（官方论文 Table 1：0=Broad，1=Specific）。manual_acl/manual_iclr 归 author-written；inline_acl/inline_nonacl 归 inline-citation。
- 静态兼容性：全部 gold corpusid→title→原 keep_letters→原本地 arXiv title index 唯一匹配，且本地 ZIP 标题同一归一化、ID 可被原 parser 识别；不丢弃某题部分 gold、不用模糊匹配或别名、不依据检索结果筛选。
- 任一组不足 25 题或存在未解决映射歧义：停止并报告，不改变组别配额、样本规模或映射定义。
- 通过 gate 才按 row index 排序候选池，用 Python random.Random(20260917) 先抽 author-written 25，再抽 inline-citation 25；无放回，不按质量/主题/结果挑题。
- 数据版本：`9573fb284a1026c998df47024b888a163f0f0e25`；dataset_manifest.json SHA256：`66faffbbd7524098561e975676e79a14fd82046d2403e366afe7a3561d2fb6c2`。

| 来源 | specific题数 | 全gold兼容题数 | 不兼容题数 | 要求抽样 |
|---|---:|---:|---:|---:|
| author-written | 211 | 164 | 47 | 25 |
| inline-citation | 231 | 165 | 66 | 25 |

## 原生生成与快照

- 仅使用已有 pasa-7b-crawler 和 agent_prompt.json.generate_query；每题一次原生生成，最多保留原 parser 解析的前 5 条，不补写、重排、重生成或修复。seed=42，每题生成前固定 Python/NumPy/Torch/CUDA；保留 checkpoint 的 do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05，原 max_new_tokens=512。
- 原生少于 5 条则如实保留；若 0 条或生成失败，停止为 INCOMPLETE，不替换问题或以 0 收益掩盖失败。
- 搜索请求 num=10，原 site:arxiv.org 和固定 before:2026-09-17；同一 query 的 Page1 后尽快请求 Page2，分别冻结完整原始 response、payload、UTC 时间及哈希。
- 为比较全部基线，采集所有 native query 的 Page1/Page2；Primary 的每题 1 次 Page2 是 replay 逻辑预算，实际采集成本为 Always Page2，不混淆两者。
- 不重复成功请求；瞬时连接错误/429/5xx 最多 3 次记录在案的尝试，不能成功则整个结果标为 INCOMPLETE，不改采样或悄悄删除失败 query。所有策略共享完全相同的成功响应快照。

## 唯一 Primary policy

- S_i 为同题 query i 的 Page1 organic URL 经原 PaSa 正则提取并去重的 arXiv ID 集。
- max_jaccard(i)=max_{j≠i}|S_i∩S_j|/|S_i∪S_j|；空并集为 0，只有一条 native query 时得分为 0。
- 每题只选最高分 1 条；并列按原生成序号从小到大。GT、Page2、词面 relevance、其他统计均不进入 routing。
- 不调整排序方向、阈值、权重、feature 或预算；不根据结果决定是否报告。

## 基线、endpoint 与统计

- Native Page1；Random（每题均匀随机选 1 条，1000 trials，seed=20260917）；Jaccard Router；Always Page2；Oracle top1（每题按 GT 增量最大选 1 条，并列原生成序号，仅离线上界）。
- 沿用项目的归一化 GT 标题分组，静态唯一映射到 arXiv ID；按原 parser 的 ID 覆盖判断是否命中，同题跨 query/page 去重。该指标是 ID 辅助 Search 覆盖，不是 Selector 或最终端到端 Recall。
- Primary endpoint：每题 1 次额外 Page2 下的总 ΔGT 与 incremental recall；Jaccard Router 对 Random 的 P(Random≥Router)。同时报告经验频率 count/1000 和加一 Monte Carlo p=(1+count)/1001。
- 报告 GT found、macro/micro Recall、ΔGT/额外逻辑调用、Always gain retention（Always 增量为 0 时记 NA）；Random 报告 mean/std。
- max_jaccard ROC-AUC 标签为单条 Page2 相对整题全部 Page1 是否新增至少 1 GT；报告全局及同题正负 pair 加权 AUC，单类不可定义时 NA。
- 25 author-written / 25 inline-citation 分组结果为 secondary，不用于调参；不另挑 budget。

## 当前执行边界

- Gate：STOPPED_MAPPING_AMBIGUITY；映射异常 1 个；正式抽样 0 题。
- 截至冻结，Crawler=0、Serper Search=0、Page1=0、Page2=0。元数据下载不是本实验论文检索。
- paper_agent.py 及原正式代码不变。若当前 gate 未激活，任何后续修订须由用户明确决定并另立版本，不能覆盖本文件。
