# PAGE2_ROUTING_SIGNAL_AUDIT_002

固定 248 条 native query / 50 个用户问题：**69 positive、179 negative**，positive prevalence=27.8226%。全部 248 条 isolated Page2 gain 与上一实验逐项一致；全量去重新增 GT=63。

**本实验只做回顾性信号分析，不生成 policy。未找到本地 embedding 模型，semantic relevance 未测量；下文 relevance 数值全部是明确标注的 TF-IDF 词面代理，不能解释成语义判断。**

## 主要问题与结论

1. **哪些特征区分最明显？** 按本批 |ROC-AUC−0.5| 描述性排序（不含原组合 heuristic），前列为：`max_jaccard`（高值偏 positive，原向 AUC=0.730，95% CI [0.642, 0.810]）；`cross_query_duplicate_ratio`（高值偏 positive，原向 AUC=0.717，95% CI [0.641, 0.784]）；`exclusive_candidate_ratio`（低值偏 positive，原向 AUC=0.283，95% CI [0.216, 0.359]）；`mean_jaccard`（高值偏 positive，原向 AUC=0.715，95% CI [0.616, 0.803]）；`marginal_unique_candidate_count`（低值偏 positive，原向 AUC=0.300，95% CI [0.231, 0.374]）。该排序本身使用标签，只是离线发现，不能作为已验证的特征选择。
2. **原 heuristic 为什么可能方向错误？** 它奖励完整页、独有候选多、低 Jaccard；本批 mean Jaccard 的原向 AUC=0.715，exclusive ratio 的原向 AUC=0.283，原分数的原向 AUC=0.317。这检验的是相关方向；不证明重复导致收益。低 novelty 可能对应主题更集中且仍有可深挖结果，高 novelty 也可能来自主题扩散；这是待验证解释。
3. **semantic / tail 是否更强？** semantic embedding 没有可用测量，无法回答真正的语义相关性是否更优。词面 family 中最高区分度为 `question_lexical_mean`（AUC=0.670），低于本批 max Jaccard 的 0.730。Question tail / Query tail AUC 分别为 0.663 / 0.626，同题 AUC 进一步为 0.599 / 0.533，没有显示比 overlap 更强的信号。decay/slope 接近随机且区间跨 0.5，本轮给出负结论。16 条 query 的 tail 缺失，另做相同有效样本上的配对比较，不把不同样本数的 AUC 直接当作严格优劣检验。
4. **哪些值得独立预注册验证？** 优先候选是高 max/mean Jaccard，或等价方向的高跨 query 重复/低 exclusive（这些高度相关，不能当独立证据）。其次是 Question↔results 的词面 mean（全局 AUC=0.670、同题 AUC=0.701），可检验用户原问题相关度是否补充 overlap，但本轮没有证明其增量价值。tail 暂无优于 mean/overlap 的证据；decay/slope、valid count、延迟不作为本批支持的优先候选。question union 等题级变量题内 AUC=0.5，不能单独完成题内 query 选择。当前不选择阈值、不组合权重、不生成新 policy。
5. **证据边界：**本轮是已知历史数据上的探索性分析，50 个问题内存在依赖，多特征存在严格互补及共线性。分组 bootstrap 缓解独立性假设，但不提供独立题集泛化证明；不把多个相关统计当作多份独立证据，也不强行产出部署规则。

## 冻结数据与标签

- positive：该 native query 的 Page2 至少命中 1 个未被整题全部 native Page1 覆盖的 GT 组；negative：该增量为 0。不是相对该 query 自己的 Page1，也不是相对 Controller 排名前面的 Page2。
- 沿用 PAGE2_SEARCH_PROBE_001 的 790 个归一化标题组和标注 arXiv ID 匹配：组中任一 ID 被原 organic URL parser 提取即算命中；不进行新标题匹配、语义匹配或 snippet 补候选。Page1=157，全量 Page1+Page2=220。
- isolated query gain 分布：`{0: 179, 1: 49, 2: 18, 3: 2}`。逐 query gain 求和为 91，同题多个 Page2 可以找回同一 GT，故不能把该和当作 63 个全量新增 GT。
- 48 题各 5 条 native，Q18/Q28 各 4 条。Page1 与 Page2 分别为 2026-09-10 / 2026-09-11 历史缓存；索引和排序可能发生时间变化，不是同时检索的快照。
- Snapshot ID：`939fe3fed9d9d9c217ec12b23b03c844595705a73b3bafa0643792a905e96509`。所有 496 份响应文件哈希与上一实验完全一致。

## 本地模型和语义特征可用性

- 检查了项目 checkpoints、用户 Hugging Face/Torch cache、NVMe 上两个 Hugging Face cache 和相关环境变量指定位置；详细路径、配置哈希和包版本见 environment_audit.json。
- 仅发现 pasa-7b-crawler / pasa-7b-selector，架构均为 Qwen2ForCausalLM；未发现 sentence embedding checkpoint。sentence-transformers 未安装。未加载、改造或调用这两个生成模型。
- 网络下载=0、模型调用=0、Crawler generation=0。semantic embedding 字段明确记为 NOT_MEASURED_NO_LOCAL_EMBEDDING_MODEL，而非赋 0 或伪造相似度。
- 检查范围是当前项目及用户缓存，不能声称扫描过其他用户或系统的所有存储位置。

## Page1 特征及冻结计算方法

- 集合统计直接复用 001 的特征提取逻辑，重新读取原 Page1 响应，并与 states.json 全部特征逐项一致性检查。包括 valid candidate count、leave-one-out exclusive/marginal unique、顺序 marginal、mean/max Jaccard、重复率、question union 等。
- exclusive count 是相对同题其余 query 并集的独有 ID 数；sequential marginal 是相对之前 query 的新增 ID 数，二者分开。question union/duplicate 是整题共享特征，可能区分题目却不能独自决定同题 query 的 routing。
- 词面特征：Question 或 native Query 与每条有效 Page1 organic 的 title+snippet 做 TF-IDF cosine。仅用 Page1 去重文本构造 IDF；固定英文小写分词/停用词，log TF、smoothed IDF、L2 normalization；没有同义词、语义蕴含或缩写扩展。
- Question 文本来自旧约束提取记录中的 /attempts/0/prompt 的原始 USER QUESTION 段，未使用生成约束或模型输出。Feature 阶段完全不读取含 GT 的数据集，分析阶段再与原实验问题逐题核对。
- 窗口按 organic 原数组位置：top1、top1–3、tail8–10；另算 mean/max、top3−tail3（正值=尾部下降）和 relevance 对 rank 的 OLS slope（正值=尾部上升）。仅保留原 parser 可识别候选，不改排序；重复 ID 保留各原位置的词面分数。
- 空窗口为 null，不填 0、不用更前位置代替 tail；部分窗口取现有位置均值并记录覆盖数。每特征报告有效/缺失正负样本数。输出 word-level similarity 是词面代理，不是 semantic embedding。
- 原 need_more_search_score 只作为既有失败分数的诊断列；未新增分数组合。所有特征和分析计划在读取本轮标签前冻结。

## 统计方法

- positive/negative 均值、中位数、样本标准差、min/p10/q25/q75/p90/max、逐值频数/ECDF 全部写入 feature_stats.json；下表给出主要摘要。
- 效应量：Hedges g（positive−negative，pooled SD 小样本校正）与 Cliff delta（含 ties；等于 2×原向 AUC−1）。零方差时 g/相关系数为 null。
- 单特征 ROC-AUC 与 PR-AUC 同时报告高值=positive 和低值=positive 两个方向，避免用 AUC<0.5 错判为无信息。主要 PR 指标为 average precision/AP（阶梯积分、ties 成组）；JSON 另存梯形 PR-AUC，后者可能因 ties 和初始 (0,1) 插值偏乐观。AP 参考水平为该特征有效样本的 positive prevalence。
- Pearson/Spearman 均针对整数 isolated Page2 gain；Spearman 用 ties 平均秩。统计相互关联，不能按 query gain 的重复命中总和解释全量收益。
- 1000 次用户问题 cluster bootstrap（seed=20260917），每次有放回抽 50 个问题，并保留其全部 native query；所有特征共享相同抽样。95% CI 是探索性的逐特征边际 percentile 区间，未做多重比较校正，不用于宣布选中特征。
- 分层使用标签不可见的 pooled 20/40/60/80% 分位边界；重复边界合并，ties 不拆分，所以可能少于 5 层、层大小不等。这些只是分布摘要，不是调出的 routing threshold。
- 额外报告同题正负 query 对的 pair-weighted AUC、题目中心化 Pearson、题内秩中心化相关。仅含正负两类的题才能贡献题内 AUC；不把题间差异当作题内路由能力。

## 全特征分布、效应量与单特征区分度

全样本 AP 参考 prevalence=0.2782；有缺失的特征使用其有效子集 prevalence（见 JSON）。按 |原向 AUC−0.5| 展示，属于事后描述性排序。

| Feature | n / missing | positive mean / median | negative mean / median | Hedges g | Cliff δ | AUC 高 / 低 | 高向 AUC 95% CI | AP 高 / 低 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| max_jaccard | 248 / 0 | 0.474 / 0.500 | 0.298 / 0.267 | 0.878 | 0.460 | 0.730 / 0.270 | [0.642, 0.810] | 0.504 / 0.196 |
| cross_query_duplicate_ratio | 248 / 0 | 0.720 / 0.778 | 0.513 / 0.556 | 0.785 | 0.434 | 0.717 / 0.283 | [0.641, 0.784] | 0.482 / 0.199 |
| exclusive_candidate_ratio | 248 / 0 | 0.280 / 0.222 | 0.487 / 0.444 | -0.785 | -0.434 | 0.283 / 0.717 | [0.216, 0.359] | 0.199 / 0.482 |
| mean_jaccard | 248 / 0 | 0.292 / 0.293 | 0.181 / 0.170 | 0.807 | 0.431 | 0.715 / 0.285 | [0.616, 0.803] | 0.487 / 0.193 |
| marginal_unique_candidate_count | 248 / 0 | 2.565 / 2.000 | 4.302 / 4.000 | -0.734 | -0.400 | 0.300 / 0.700 | [0.231, 0.374] | 0.210 / 0.456 |
| original_need_more_search_score | 248 / 0 | 0.457 / 0.443 | 0.583 / 0.555 | -0.670 | -0.365 | 0.317 / 0.683 | [0.232, 0.403] | 0.201 / 0.445 |
| question_lexical_mean | 248 / 0 | 0.167 / 0.160 | 0.130 / 0.117 | 0.546 | 0.340 | 0.670 / 0.330 | [0.573, 0.758] | 0.405 / 0.204 |
| question_duplicate_ratio | 248 / 0 | 0.429 / 0.439 | 0.351 / 0.380 | 0.605 | 0.333 | 0.667 / 0.333 | [0.560, 0.756] | 0.445 / 0.212 |
| tail5_exclusive_candidate_count | 248 / 0 | 1.725 / 1.000 | 2.553 / 2.000 | -0.595 | -0.328 | 0.336 / 0.664 | [0.273, 0.401] | 0.222 / 0.393 |
| question_lexical_tail3 | 232 / 16 | 0.146 / 0.142 | 0.110 / 0.104 | 0.589 | 0.326 | 0.663 / 0.337 | [0.564, 0.747] | 0.444 / 0.221 |
| question_unique_candidate_count | 248 / 0 | 26.319 / 26.000 | 28.927 / 30.000 | -0.454 | -0.257 | 0.371 / 0.629 | [0.273, 0.480] | 0.224 / 0.375 |
| question_lexical_max | 248 / 0 | 0.287 / 0.270 | 0.250 / 0.245 | 0.376 | 0.254 | 0.627 / 0.373 | [0.522, 0.720] | 0.358 / 0.216 |
| query_lexical_tail3 | 232 / 16 | 0.198 / 0.180 | 0.161 / 0.149 | 0.447 | 0.253 | 0.626 / 0.374 | [0.536, 0.719] | 0.393 / 0.229 |
| query_lexical_mean | 248 / 0 | 0.224 / 0.216 | 0.192 / 0.180 | 0.429 | 0.231 | 0.615 / 0.385 | [0.507, 0.723] | 0.381 / 0.222 |
| question_lexical_top3 | 248 / 0 | 0.182 / 0.165 | 0.154 / 0.137 | 0.307 | 0.228 | 0.614 / 0.386 | [0.512, 0.710] | 0.348 / 0.220 |
| sequential_marginal_unique_candidate_count | 248 / 0 | 4.826 / 4.000 | 6.022 / 6.000 | -0.403 | -0.225 | 0.387 / 0.613 | [0.325, 0.447] | 0.238 / 0.405 |
| question_lexical_top1 | 248 / 0 | 0.195 / 0.187 | 0.168 / 0.160 | 0.234 | 0.163 | 0.581 / 0.419 | [0.490, 0.670] | 0.315 / 0.229 |
| query_lexical_top3 | 248 / 0 | 0.246 / 0.236 | 0.223 / 0.202 | 0.239 | 0.146 | 0.573 / 0.427 | [0.481, 0.671] | 0.335 / 0.243 |
| query_lexical_max | 248 / 0 | 0.377 / 0.365 | 0.351 / 0.344 | 0.247 | 0.140 | 0.570 / 0.430 | [0.468, 0.676] | 0.343 / 0.241 |
| query_lexical_top1 | 248 / 0 | 0.269 / 0.267 | 0.242 / 0.218 | 0.208 | 0.133 | 0.566 / 0.434 | [0.474, 0.654] | 0.321 / 0.241 |
| question_lexical_rank_slope | 248 / 0 | -0.005 / -0.003 | -0.007 / -0.005 | 0.219 | 0.104 | 0.552 / 0.448 | [0.454, 0.650] | 0.309 / 0.251 |
| query_lexical_rank_slope | 248 / 0 | -0.007 / -0.006 | -0.009 / -0.009 | 0.181 | 0.092 | 0.546 / 0.454 | [0.475, 0.621] | 0.291 / 0.244 |
| tail5_valid_candidate_count | 248 / 0 | 4.957 / 5.000 | 4.715 / 5.000 | 0.295 | 0.080 | 0.540 / 0.460 | [0.511, 0.569] | 0.295 / 0.275 |
| valid_candidate_occurrence_count | 248 / 0 | 9.957 / 10.000 | 9.704 / 10.000 | 0.289 | 0.080 | 0.540 / 0.460 | [0.511, 0.569] | 0.295 / 0.275 |
| organic_count | 248 / 0 | 9.957 / 10.000 | 9.709 / 10.000 | 0.283 | 0.075 | 0.537 / 0.463 | [0.510, 0.565] | 0.294 / 0.275 |
| text_tail3_observed_count | 248 / 0 | 2.957 / 3.000 | 2.743 / 3.000 | 0.289 | 0.075 | 0.537 / 0.463 | [0.510, 0.565] | 0.294 / 0.275 |
| question_lexical_top3_minus_tail3 | 232 / 16 | 0.034 / 0.028 | 0.047 / 0.033 | -0.182 | -0.071 | 0.465 / 0.535 | [0.373, 0.562] | 0.270 / 0.330 |
| query_lexical_top3_minus_tail3 | 232 / 16 | 0.047 / 0.044 | 0.061 / 0.054 | -0.161 | -0.069 | 0.466 / 0.534 | [0.395, 0.538] | 0.266 / 0.324 |
| question_native_query_count | 248 / 0 | 5.000 / 5.000 | 4.955 / 5.000 | 0.253 | 0.045 | 0.522 / 0.478 | [0.500, 0.556] | 0.287 / 0.278 |
| latency_seconds | 248 / 0 | 3.034 / 2.843 | 3.464 / 2.836 | -0.261 | -0.040 | 0.480 / 0.520 | [0.405, 0.558] | 0.251 / 0.270 |
| page_fill_ratio | 248 / 0 | 0.932 / 1.000 | 0.902 / 1.000 | 0.201 | 0.021 | 0.511 / 0.489 | [0.434, 0.578] | 0.281 / 0.269 |
| valid_candidate_count | 248 / 0 | 9.319 / 10.000 | 9.022 / 10.000 | 0.201 | 0.021 | 0.511 / 0.489 | [0.434, 0.578] | 0.281 / 0.269 |
| invalid_url_count | 248 / 0 | 0.000 / 0.000 | 0.006 / 0.000 | -0.088 | -0.006 | 0.497 / 0.503 | [0.491, 0.500] | 0.278 / 0.279 |
| within_query_duplicate_ratio | 248 / 0 | 0.066 / 0.000 | 0.076 / 0.000 | -0.095 | 0.002 | 0.501 / 0.499 | [0.434, 0.576] | 0.274 / 0.277 |
| snippet_available_ratio | 248 / 0 | 1.000 / 1.000 | 1.000 / 1.000 | NA | 0.000 | 0.500 / 0.500 | [0.500, 0.500] | 0.278 / 0.278 |
| text_top3_observed_count | 248 / 0 | 3.000 / 3.000 | 3.000 / 3.000 | NA | 0.000 | 0.500 / 0.500 | [0.500, 0.500] | 0.278 / 0.278 |

## 与 Page2 gain 的相关性及题内区分

| Feature | Pearson gain | Spearman gain | 同题 AUC 高向 | 题目中心化 Pearson | 题内秩中心化相关 | 混合标签题数 |
|---|---:|---:|---:|---:|---:|---:|
| cross_query_duplicate_ratio | 0.308 | 0.338 | 0.711 | 0.262 | 0.278 | 29 |
| exclusive_candidate_ratio | -0.308 | -0.338 | 0.289 | -0.262 | -0.278 | 29 |
| invalid_url_count | -0.036 | -0.039 | 0.494 | -0.085 | -0.076 | 29 |
| latency_seconds | -0.121 | -0.043 | 0.578 | -0.011 | 0.098 | 29 |
| marginal_unique_candidate_count | -0.301 | -0.317 | 0.299 | -0.259 | -0.272 | 29 |
| max_jaccard | 0.343 | 0.358 | 0.731 | 0.289 | 0.319 | 29 |
| mean_jaccard | 0.337 | 0.338 | 0.714 | 0.252 | 0.267 | 29 |
| organic_count | 0.100 | 0.125 | 0.529 | 0.082 | 0.087 | 29 |
| original_need_more_search_score | -0.288 | -0.292 | 0.315 | -0.232 | -0.243 | 29 |
| page_fill_ratio | 0.065 | 0.018 | 0.435 | 0.001 | -0.122 | 29 |
| query_lexical_max | 0.094 | 0.107 | 0.519 | 0.034 | 0.026 | 29 |
| query_lexical_mean | 0.165 | 0.176 | 0.558 | 0.105 | 0.092 | 29 |
| query_lexical_rank_slope | 0.069 | 0.068 | 0.571 | 0.036 | 0.061 | 29 |
| query_lexical_tail3 | 0.166 | 0.196 | 0.533 | 0.035 | 0.053 | 28 |
| query_lexical_top1 | 0.083 | 0.101 | 0.506 | 0.031 | -0.002 | 29 |
| query_lexical_top3 | 0.098 | 0.118 | 0.519 | 0.067 | 0.046 | 29 |
| query_lexical_top3_minus_tail3 | -0.056 | -0.050 | 0.504 | -0.000 | 0.030 | 28 |
| question_duplicate_ratio | 0.270 | 0.268 | 0.500 | NA | NA | 29 |
| question_lexical_max | 0.129 | 0.187 | 0.594 | 0.163 | 0.119 | 29 |
| question_lexical_mean | 0.193 | 0.254 | 0.701 | 0.260 | 0.247 | 29 |
| question_lexical_rank_slope | 0.101 | 0.084 | 0.558 | 0.066 | 0.055 | 29 |
| question_lexical_tail3 | 0.199 | 0.241 | 0.599 | 0.121 | 0.092 | 28 |
| question_lexical_top1 | 0.074 | 0.121 | 0.558 | 0.072 | 0.080 | 29 |
| question_lexical_top3 | 0.096 | 0.168 | 0.617 | 0.149 | 0.144 | 29 |
| question_lexical_top3_minus_tail3 | -0.090 | -0.061 | 0.504 | 0.014 | 0.028 | 28 |
| question_native_query_count | 0.103 | 0.112 | 0.500 | NA | NA | 29 |
| question_unique_candidate_count | -0.220 | -0.214 | 0.500 | NA | NA | 29 |
| sequential_marginal_unique_candidate_count | -0.156 | -0.177 | 0.386 | -0.088 | -0.121 | 29 |
| snippet_available_ratio | NA | NA | 0.500 | NA | NA | 29 |
| tail5_exclusive_candidate_count | -0.248 | -0.261 | 0.344 | -0.176 | -0.208 | 29 |
| tail5_valid_candidate_count | 0.104 | 0.131 | 0.536 | 0.095 | 0.104 | 29 |
| text_tail3_observed_count | 0.100 | 0.125 | 0.529 | 0.082 | 0.087 | 29 |
| text_top3_observed_count | NA | NA | 0.500 | NA | NA | 29 |
| valid_candidate_count | 0.065 | 0.018 | 0.435 | 0.001 | -0.122 | 29 |
| valid_candidate_occurrence_count | 0.103 | 0.131 | 0.536 | 0.089 | 0.104 | 29 |
| within_query_duplicate_ratio | -0.023 | 0.002 | 0.584 | 0.067 | 0.154 | 29 |

## overlap / novelty 反向趋势与词面 tail、decay 分层

括号为每层 query 数，按特征值由低到高。分位边界严格按数值合并 ties，没有按标签挑切点。完整边界、分组 gain 均值和所有其他特征见 JSON。

| Feature | 由低到高的 positive rate（n） |
|---|---|
| mean_jaccard | 8.0% (50) → 18.4% (49) → 28.0% (50) → 34.7% (49) → 50.0% (50) |
| max_jaccard | 7.8% (51) → 13.0% (54) → 35.0% (60) → 36.8% (38) → 51.1% (45) |
| cross_query_duplicate_ratio | 11.3% (53) → 13.0% (46) → 29.7% (64) → 40.0% (40) → 48.9% (45) |
| question_duplicate_ratio | 18.5% (54) → 18.4% (49) → 21.8% (55) → 30.0% (40) → 52.0% (50) |
| exclusive_candidate_ratio | 49.2% (63) → 30.2% (43) → 30.2% (43) → 16.7% (54) → 6.7% (45) |
| marginal_unique_candidate_count | 43.7% (87) → 23.8% (42) → 36.4% (33) → 10.9% (46) → 10.0% (40) |
| question_unique_candidate_count | 36.4% (55) → 44.4% (45) → 18.6% (59) → 22.4% (49) → 17.5% (40) |
| original_need_more_search_score | 48.0% (50) → 32.7% (49) → 28.0% (50) → 20.4% (49) → 10.0% (50) |
| question_lexical_mean | 10.0% (50) → 24.5% (49) → 28.0% (50) → 32.7% (49) → 44.0% (50) |
| question_lexical_top3 | 12.0% (50) → 24.5% (49) → 36.0% (50) → 28.6% (49) → 38.0% (50) |
| question_lexical_tail3 | 12.8% (47) → 26.1% (46) → 28.3% (46) → 30.4% (46) → 48.9% (47) |
| question_lexical_top3_minus_tail3 | 34.0% (47) → 32.6% (46) → 21.7% (46) → 32.6% (46) → 25.5% (47) |
| question_lexical_rank_slope | 22.0% (50) → 28.6% (49) → 22.0% (50) → 34.7% (49) → 32.0% (50) |
| query_lexical_mean | 20.0% (50) → 18.4% (49) → 30.0% (50) → 30.6% (49) → 40.0% (50) |
| query_lexical_top3 | 20.0% (50) → 22.4% (49) → 32.0% (50) → 32.7% (49) → 32.0% (50) |
| query_lexical_tail3 | 14.9% (47) → 28.3% (46) → 34.8% (46) → 26.1% (46) → 42.6% (47) |
| query_lexical_top3_minus_tail3 | 27.7% (47) → 30.4% (46) → 39.1% (46) → 28.3% (46) → 21.3% (47) |
| query_lexical_rank_slope | 18.0% (50) → 28.6% (49) → 34.0% (50) → 30.6% (49) → 28.0% (50) |

mean Jaccard 从最低到最高分位的 positive rate 为 8.0%→50.0%，max Jaccard 为 7.8%→51.1%；exclusive ratio 则为 49.2%→6.7%。反向趋势并非仅由整题共同属性造成：max/mean Jaccard 的题内 AUC 仍为约 0.731/0.714。重复率和 exclusive ratio 在当前非空候选样本中互补，不能累计成两份独立证据。

## 相同有效样本上的词面指标比较

这是发现 tail 缺失后补充的敏感性分析；未改变任何特征或标签。每行双方使用完全相同的 query，均以高值对应 positive；CI 用同一组问题 bootstrap 做配对差值。差值为左−右，没有选择 threshold 或重新组合分数。区间仍是未校正多重比较的探索性结果。

| 左特征 | 右特征 | n | AUC 左 / 右 | ΔAUC [95% cluster CI] | AP 左 / 右 | ΔAP [95% cluster CI] |
|---|---|---:|---:|---|---:|---|
| question_lexical_mean | mean_jaccard | 248 | 0.670 / 0.715 | -0.045 [-0.165, 0.079] | 0.405 / 0.487 | -0.081 [-0.228, 0.082] |
| question_lexical_mean | max_jaccard | 248 | 0.670 / 0.730 | -0.060 [-0.174, 0.060] | 0.405 / 0.504 | -0.099 [-0.226, 0.080] |
| question_lexical_tail3 | mean_jaccard | 232 | 0.663 / 0.702 | -0.040 [-0.168, 0.087] | 0.444 / 0.491 | -0.046 [-0.219, 0.106] |
| question_lexical_tail3 | max_jaccard | 232 | 0.663 / 0.718 | -0.055 [-0.175, 0.066] | 0.444 / 0.508 | -0.064 [-0.202, 0.099] |
| query_lexical_mean | mean_jaccard | 248 | 0.615 / 0.715 | -0.100 [-0.242, 0.054] | 0.381 / 0.487 | -0.106 [-0.303, 0.071] |
| query_lexical_mean | max_jaccard | 248 | 0.615 / 0.730 | -0.115 [-0.243, 0.032] | 0.381 / 0.504 | -0.124 [-0.282, 0.047] |
| query_lexical_tail3 | mean_jaccard | 232 | 0.626 / 0.702 | -0.076 [-0.211, 0.068] | 0.393 / 0.491 | -0.097 [-0.303, 0.075] |
| query_lexical_tail3 | max_jaccard | 232 | 0.626 / 0.718 | -0.092 [-0.217, 0.047] | 0.393 / 0.508 | -0.115 [-0.265, 0.047] |
| question_lexical_tail3 | question_lexical_mean | 232 | 0.663 / 0.656 | 0.006 [-0.066, 0.068] | 0.444 / 0.414 | 0.031 [-0.060, 0.078] |
| query_lexical_tail3 | query_lexical_mean | 232 | 0.626 / 0.618 | 0.009 [-0.053, 0.072] | 0.393 / 0.406 | -0.013 [-0.078, 0.045] |

## 验证与复现

- query 数量及逐 query key 与 001 完全一致；独立从冻结 GT 组和原始 Page1/Page2 ID 集重算标签，对 248 条 gain 和新 GT 标题集合逐项核对。
- Feature 脚本使用数据读取白名单，只允许旧 states、Page1 响应、原始 question prompt 记录和环境审计；访问日志核验无 GT、Page2 outcome、旧/新评测报告读取。主动尝试读取 6 个 GT/Page2/outcome 受保护输入均在 I/O 前被拒绝。分析程序独立加入标签，无法改变已冻结特征。
- 所有阶段阻止网络/模型库导入、socket/DNS 和子进程；源码及产物有哈希追踪，正式主流程、旧实验、全部历史响应均未改动。
- 统计函数验证了完美/反向/常数排序、ties、单类、零方差和题间/题内差异案例；bootstrap 抽样由同 seed 重建并核对。
- query_signal_table.json/csv 是逐 query 的冻结特征＋离线标签；feature_stats.json 包含完整分布、双向 AUC/AP、相关性、bootstrap CI 和固定分位层；page1_features.json 是独立、无标签的特征产物。

```bash
/mnt/nvme3/chenyi/conda-envs/pasa/bin/python -B page2_routing_signal_audit_002/environment_probe.py
python3 -B page2_routing_signal_audit_002/extract_features.py
python3 -B page2_routing_signal_audit_002/validate_features.py
python3 -B page2_routing_signal_audit_002/analyze.py
```
