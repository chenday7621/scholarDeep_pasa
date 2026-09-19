# ADAPTIVE_PAGE2_CONTROLLER_OFFLINE_001

在固定历史 snapshot 上，budget=50 时 Adaptive 新增 **6 GT**，Random 为 **16.763 ± 3.671**，Oracle 为 **63**。Always Page2 全部 248 次新增 63 GT；Adaptive 保留 **9.5238%**。

## 结论

- **是否稳定优于 Random：**6 个非全量预算中，0 个高于 Random 均值（无）；Holm 校正后的单侧 p<0.05 有 0 个（无）。当前规则在全部非全量预算均低于 Random 均值，未获得预期优势。
- **budget=50：**248 次原始 Page1 基础上增加 50 个逻辑槽位，即 +20.16%；新增 6 GT，效率 0.1200 GT/call。随机分配同预算已新增 16.763，因此路由本身的贡献应看与随机的差值 -10.763，不能用全部新增量代表 Controller 效果。
- **与 unconditional Anchor +50→+5：**数值上高于 +5（6 vs 5；0.120 vs 0.100 GT/call）。本次仅多 1 GT，不能称为明显改善。但 Page2 是旧 baseline 的 ID 辅助覆盖，Anchor 是另一次快照上的原生 metadata 标题匹配，不能宣称同口径显著优于 Anchor，也不能把 Page2 自身的收益归功于路由。
- **是否值得进入下一阶段：**当前启发式的排序方向失败，不支持按现规则推进集成；但不能推出 retrieval feedback 完全无信号。分层呈现反向趋势，足以提出一个后续离线假设；若研究“高重叠/检索饱和更需要 Page2”，应事先固定规则并在独立数据上验证。本轮不反转排序、不调权重、不报告事后改良 policy。

## 数据与评测口径

- 50 个用户问题、248 条 native query：Q18/Q28 各 4 条，其余各 5 条。一个 query 的 Page2 占一个全局预算槽位；不是每题相同配额。
- 仅使用 PAGE2_SEARCH_PROBE_001 的配对响应。Page1 为 2026-09-10、Page2 为 2026-09-11；不是同时获取，before 日期不能冻结索引/排名。所有 policy 共享同一历史配对快照。
- 复用 utils.py 的 keep_letters 函数，通过 AST 仅加载该纯函数，避免导入 utils 触发数据加载或网络 SDK。GT 按归一化标题分成 790 组；组内任一标注 arXiv ID 出现在原 URL parser 的 organic 链接中即算命中。每题内跨 query、跨 page 去重，不跨用户问题合并。
- Q45 Panacea/Panacea+ 两个 ID 归到同一标题组，沿用原实验；不使用 snippet 提及、fuzzy matching、站外链接补充。该口径是 ID-assisted Search coverage，不能混同官方 metadata-title Recall。
- 复现原实验 Page1=157、Page1+全部 Page2=220、新增=63；逐个核验全部 790 组的原始命中状态。Macro Search Recall 对 50 个用户问题等权，Micro 分母为 790。
- 预算单位为逻辑 Page2 calls。原缓存含失败重试，本实验不把重试算作预算，也未实际请求任何网络；不评测 Selector/Expand 或最终端到端效果。

## 冻结 heuristic 与特征

```text
page_fill_ratio * (0.5 * exclusive_candidate_ratio + 0.5 * (1 - mean_jaccard))
```

- fill = min(Page1 unique valid IDs / requested num=10, 1)。exclusive ratio = 该 query 相对同题其他全部 native queries 的独有 ID 数 / 该 query unique ID 数。mean Jaccard 为与同题其他 query 的结果 ID 集合 Jaccard 均值。
- 直觉：完整的一页提示可能还有后续候选，独有候选与较低重叠提示独立的检索方向。它不判断论文相关性，属于未经收益调参的假设。
- 同时输出：valid occurrences、invalid URL 数、页内重复率、leave-one-out marginal unique、原序 marginal unique、mean/max Jaccard、跨 query 重复率、整题重复率与 union 大小、末 5 个位置的有效/独有候选数、snippet 可用率、延迟。仅公式中的 3 个特征参与打分，其余用于可审计状态。
- marginal_unique_candidate_count 定义为 leave-one-out 独有数，避免原生顺序优势；sequential_marginal_unique_candidate_count 单独保留。cross_query_duplicate_ratio = 与其他 query 并集重合比例。空集合比率按 0 处理。
- score 降序，全局排序；并列使用 query key 与原生 query 文本的 SHA256 排序。权重固定 0.5/0.5，先生成 states/decisions 再实现和运行评测，未训练、未尝试收益驱动的替代公式。
- 所有 Page1 返回后做一次预算分配；不读取已执行 Page2 的反馈。这个批量全局控制器不等同于单用户在线调度器。

## 全策略结果

Random 为 1000 次均值 ± 总体标准差（ddof=0）。Native 和 Always 在每个预算下作为固定参照；Always 仅在 all 满足预算。保留率分母为 Always 新增的 63 GT。

| Budget | Policy | GT found | ΔGT | Macro Search Recall | Extra calls | ΔGT/call | 保留 Always 新增GT |
|---|---|---:|---:|---:|---:|---:|---:|
| 25 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 25 | random_page2 | 165.694 ± 2.908 | 8.694 ± 2.908 | 25.3175 ± 0.6706% | 25 | 0.3478 ± 0.1163 | 13.80 ± 4.62% |
| 25 | adaptive | 157 | 0 | 23.9020% | 25 | 0.0000 | 0.0000% |
| 25 | oracle | 198 | 41 | 31.2206% | 25 | 1.6400 | 65.0794% |
| 25 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| 50 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 50 | random_page2 | 173.763 ± 3.671 | 16.763 ± 3.671 | 26.5609 ± 0.8059% | 50 | 0.3353 ± 0.0734 | 26.61 ± 5.83% |
| 50 | adaptive | 163 | 6 | 25.7297% | 50 | 0.1200 | 9.5238% |
| 50 | oracle | 220 | 63 | 32.8951% | 50 | 1.2600 | 100.0000% |
| 50 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| 75 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 75 | random_page2 | 181.275 ± 4.009 | 24.275 ± 4.009 | 27.6729 ± 0.8148% | 75 | 0.3237 ± 0.0535 | 38.53 ± 6.36% |
| 75 | adaptive | 168 | 11 | 26.4190% | 75 | 0.1467 | 17.4603% |
| 75 | oracle | 220 | 63 | 32.8951% | 75 | 0.8400 | 100.0000% |
| 75 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| 100 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 100 | random_page2 | 188.185 ± 4.183 | 31.185 ± 4.183 | 28.6827 ± 0.8425% | 100 | 0.3119 ± 0.0418 | 49.50 ± 6.64% |
| 100 | adaptive | 173 | 16 | 26.7394% | 100 | 0.1600 | 25.3968% |
| 100 | oracle | 220 | 63 | 32.8951% | 100 | 0.6300 | 100.0000% |
| 100 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| 150 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 150 | random_page2 | 200.460 ± 3.858 | 43.460 ± 3.858 | 30.3856 ± 0.7227% | 150 | 0.2897 ± 0.0257 | 68.98 ± 6.12% |
| 150 | adaptive | 189 | 32 | 28.2140% | 150 | 0.2133 | 50.7937% |
| 150 | oracle | 220 | 63 | 32.8951% | 150 | 0.4200 | 100.0000% |
| 150 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| 200 | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| 200 | random_page2 | 211.110 ± 2.912 | 54.110 ± 2.912 | 31.7701 ± 0.5410% | 200 | 0.2706 ± 0.0146 | 85.89 ± 4.62% |
| 200 | adaptive | 205 | 48 | 30.4860% | 200 | 0.2400 | 76.1905% |
| 200 | oracle | 220 | 63 | 32.8951% | 200 | 0.3150 | 100.0000% |
| 200 | always_page2（超预算参照） | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| all | native_page1 | 157 | 0 | 23.9020% | 0 | — | 0.0000% |
| all | random_page2 | 220.000 ± 0.000 | 63.000 ± 0.000 | 32.8951 ± 0.0000% | 248 | 0.2540 ± 0.0000 | 100.00 ± 0.00% |
| all | adaptive | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| all | oracle | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |
| all | always_page2 | 220 | 63 | 32.8951% | 248 | 0.2540 | 100.0000% |

## 随机比较与稳定性

固定 seed=20260916。每次均匀打乱全部 248 个 query，取预算长度前缀；1000 次 trial，每个预算都是无放回均匀采样。各预算共享随机排列的嵌套前缀。重新从 seed 生成选择并重算全部指标，逐项完全相同。随机均值另用超几何覆盖概率计算精确期望作为核查。

| Budget | Adaptive ΔGT | Random ΔGT mean ± std | Random ΔGT 95%区间 | Adaptive−Random mean | 严格胜率 | P(Random≥Adaptive) | Holm校正p | 精确随机期望ΔGT |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 25 | 0 | 8.694 ± 2.908 | [3, 15] | -8.694 | 0.0000% | 1.0000 | 1.0000 | 8.819 |
| 50 | 6 | 16.763 ± 3.671 | [10, 24] | -10.763 | 0.0000% | 1.0000 | 1.0000 | 16.937 |
| 75 | 11 | 24.275 ± 4.009 | [17, 32] | -13.275 | 0.0000% | 1.0000 | 1.0000 | 24.410 |
| 100 | 16 | 31.185 ± 4.183 | [23, 40] | -15.185 | 0.0000% | 1.0000 | 1.0000 | 31.293 |
| 150 | 32 | 43.460 ± 3.858 | [36, 51] | -11.460 | 0.1000% | 0.9990 | 1.0000 | 43.516 |
| 200 | 48 | 54.110 ± 2.912 | [48, 59] | -6.110 | 1.2000% | 0.9880 | 1.0000 | 54.054 |
| all | 63 | 63.000 ± 0.000 | [63, 63] | +0.000 | 0.0000% | 1.0000 | — | 63.000 |

单侧 Monte Carlo p=(1+随机ΔGT≥Adaptive的次数)/1001；六个非全量预算做 Holm 校正。95%区间是随机分配结果的经验区间，不是均值置信区间。胜率/显著性仅描述此 snapshot 的预算随机性，不代表跨题集、跨随机生成种子或跨时间稳定性。已知历史基准存在结果报告，代码阶段隔离不能替代前瞻盲测。

## Oracle 上界

对每个用户问题枚举至多 2^5=32 个 native query 子集，计算其 Page2 相对整题全部 Page1 的去重 GT 增量；每个精确成本保留最优局部子集，再用跨 50 题动态规划求每个总预算的精确最优。因 GT 按用户问题区分，各题收益可相加。这避免将每条 query 的独立收益排序误称全局 Oracle。Oracle 在同 GT 数时以 Macro Recall 作第二目标，其 Macro 值不是独立最大化 Macro 的理论上界。Oracle 读取 GT 仅位于 evaluate.py，不能部署。

## 事后分数分层诊断

下面仅用于评测解释，没有反馈给 Controller。每层 unique gain 在层内去重，但不同层可重复，不能求和。

| 排名区间 | query数 | Page2有新增GT的query数 | 层内去重新增GT |
|---|---:|---:|---:|
| [1, 25] | 25 | 0 | 0 |
| [26, 50] | 25 | 5 | 6 |
| [51, 75] | 25 | 5 | 5 |
| [76, 100] | 25 | 5 | 6 |
| [101, 125] | 25 | 8 | 10 |
| [126, 150] | 25 | 6 | 7 |
| [151, 175] | 25 | 10 | 13 |
| [176, 200] | 25 | 7 | 10 |
| [201, 225] | 25 | 8 | 10 |
| [226, 248] | 23 | 15 | 14 |

最高分 25 条没有新增 GT，最低分 23 条中 15 条有新增 GT，呈现与原假设相反的方向。低重叠和高 novelty 只能说明候选集合不同，也可能来自主题扩散；它们并不自动意味着深一页更容易命中目标。这一机制解释是事后推测，未做内容相关性验证。相反方向是否能泛化，需要新验证；不能仅据本批把负相关翻转成已证实的可部署 signal。Oracle 在预算 50 下可覆盖全部 63 个新增 GT，说明收益有集中空间，但不证明 Page1 可观测特征足以识别那些 query。

## 数据隔离与离线验证

- features.py：只允许原请求计划、Page1 原始响应和自身源码。请求计划是执行前创建，不含 GT/Page2 outcomes；不读取混合了评测信息的 PAGE2_SEARCH_PROBE_001.json。
- controller.py：数据输入只有 states.json；SHA256 绑定特征和源码，排序/预算选择保存在 decisions.json。
- validate.py：无标签重算全部特征和排序，检查访问记录。主动读取 GT、Page2 响应、原结果报告、本实验 results.json 均在 I/O 前被拒绝。
- evaluate.py：唯一允许读取 GT/标签的阶段；读取冻结 decisions，不更改权重或排序。全部 policy 使用同一内存中的配对 ID 集，结果记录相同 snapshot ID。
- 所有脚本启用审计钩子，拒绝 socket/DNS、子进程、模型和网络库导入；只允许指定输出文件写入。实际网络请求、Crawler generation、模型调用均为 0。
- query 数量与原实验一致；496 份响应原始文本/字节及文件哈希核验；原始 790 组结果逐组复现；随机排列与全部 trial metrics 重算一致；Oracle 通过带重复覆盖的合成穷举核验；all 时所有策略收敛到同一结果。
- 主流程和全部输入文件哈希前后一致；Controller 的源码和产物在评测前后不变。没有修改 paper_agent.py 或其他正式代码。

## 产物与复现

- states.json：248 个 Page1 状态及特征；decisions.json：冻结分数、排序和预算选择；results.json：全部策略指标与随机比较。
- random_trials.json：7000 组 trial 指标、固定种子、采样顺序及排列哈希；evaluation_query_outcomes.json：仅评测阶段生成的逐 query GT 证据。
- snapshot_manifest.json：配对快照及输入哈希；features_access.json/controller_access.json/evaluation_access.json：读文件审计；validation_controller.json/validation_evaluation.json：验证结果。

在项目根目录执行（只读取已有本地缓存，不需要 GPU、网络或额外依赖）：

```bash
python3 -B adaptive_page2_controller_offline_001/features.py
python3 -B adaptive_page2_controller_offline_001/controller.py
python3 -B adaptive_page2_controller_offline_001/validate.py
python3 -B adaptive_page2_controller_offline_001/evaluate.py
```

Snapshot ID: `939fe3fed9d9d9c217ec12b23b03c844595705a73b3bafa0643792a905e96509`
