"""Descriptive report only: no decisions, thresholds, or deployment policy."""
from audit_common import HERE


def render(result, environment):
    fs=result['features']
    fmt=lambda v,n=3: 'NA' if v is None else f'{v:.{n}f}'
    strength=lambda name:abs(fs[name]['high_is_positive']['roc_auc']-.5)
    eligible=[n for n in fs if fs[n]['family']!='original_heuristic_diagnostic']
    leaders=sorted(eligible,key=lambda n:(-strength(n),n))
    sets=[n for n in leaders if fs[n]['family']=='set_statistics']
    lexical=[n for n in leaders if fs[n]['family'] in ['question_lexical','query_lexical']]
    s_best,l_best=sets[0],lexical[0]
    directional=lambda n:'高值偏 positive' if fs[n]['high_is_positive']['roc_auc']>.5 else '低值偏 positive' if fs[n]['high_is_positive']['roc_auc']<.5 else '无排序区分'
    ci=lambda n:fs[n]['question_cluster_bootstrap_95ci']['auc_high']
    top_description='；'.join(f"`{n}`（{directional(n)}，原向 AUC={fmt(fs[n]['high_is_positive']['roc_auc'])}，95% CI [{fmt(ci(n)['low'])}, {fmt(ci(n)['high'])}]）" for n in leaders[:5])
    lines=['# PAGE2_ROUTING_SIGNAL_AUDIT_002','',
           f"固定 248 条 native query / 50 个用户问题：**{result['positive_count']} positive、{result['negative_count']} negative**，positive prevalence={result['positive_prevalence']:.4%}。全部 248 条 isolated Page2 gain 与上一实验逐项一致；全量去重新增 GT=63。",'',
           '**本实验只做回顾性信号分析，不生成 policy。未找到本地 embedding 模型，semantic relevance 未测量；下文 relevance 数值全部是明确标注的 TF-IDF 词面代理，不能解释成语义判断。**','',
           '## 主要问题与结论','',
           '1. **哪些特征区分最明显？** 按本批 |ROC-AUC−0.5| 描述性排序（不含原组合 heuristic），前列为：'+top_description+'。该排序本身使用标签，只是离线发现，不能作为已验证的特征选择。',
           f"2. **原 heuristic 为什么可能方向错误？** 它奖励完整页、独有候选多、低 Jaccard；本批 mean Jaccard 的原向 AUC={fmt(fs['mean_jaccard']['high_is_positive']['roc_auc'])}，exclusive ratio 的原向 AUC={fmt(fs['exclusive_candidate_ratio']['high_is_positive']['roc_auc'])}，原分数的原向 AUC={fmt(fs['original_need_more_search_score']['high_is_positive']['roc_auc'])}。这检验的是相关方向；不证明重复导致收益。低 novelty 可能对应主题更集中且仍有可深挖结果，高 novelty 也可能来自主题扩散；这是待验证解释。",
           f"3. **semantic / tail 是否更强？** semantic embedding 没有可用测量，无法回答真正的语义相关性是否更优。词面 family 中最高区分度为 `{l_best}`（AUC={fmt(fs[l_best]['high_is_positive']['roc_auc'])}），低于本批 max Jaccard 的 {fmt(fs['max_jaccard']['high_is_positive']['roc_auc'])}。Question tail / Query tail AUC 分别为 {fmt(fs['question_lexical_tail3']['high_is_positive']['roc_auc'])} / {fmt(fs['query_lexical_tail3']['high_is_positive']['roc_auc'])}，同题 AUC 进一步为 {fmt(fs['question_lexical_tail3']['conditional_within_question']['pair_weighted_within_question_auc_high'])} / {fmt(fs['query_lexical_tail3']['conditional_within_question']['pair_weighted_within_question_auc_high'])}，没有显示比 overlap 更强的信号。decay/slope 接近随机且区间跨 0.5，本轮给出负结论。16 条 query 的 tail 缺失，另做相同有效样本上的配对比较，不把不同样本数的 AUC 直接当作严格优劣检验。",
           f"4. **哪些值得独立预注册验证？** 优先候选是高 max/mean Jaccard，或等价方向的高跨 query 重复/低 exclusive（这些高度相关，不能当独立证据）。其次是 Question↔results 的词面 mean（全局 AUC={fmt(fs['question_lexical_mean']['high_is_positive']['roc_auc'])}、同题 AUC={fmt(fs['question_lexical_mean']['conditional_within_question']['pair_weighted_within_question_auc_high'])}），可检验用户原问题相关度是否补充 overlap，但本轮没有证明其增量价值。tail 暂无优于 mean/overlap 的证据；decay/slope、valid count、延迟不作为本批支持的优先候选。question union 等题级变量题内 AUC=0.5，不能单独完成题内 query 选择。当前不选择阈值、不组合权重、不生成新 policy。", 
           '5. **证据边界：**本轮是已知历史数据上的探索性分析，50 个问题内存在依赖，多特征存在严格互补及共线性。分组 bootstrap 缓解独立性假设，但不提供独立题集泛化证明；不把多个相关统计当作多份独立证据，也不强行产出部署规则。','',
           '## 冻结数据与标签','',
           '- positive：该 native query 的 Page2 至少命中 1 个未被整题全部 native Page1 覆盖的 GT 组；negative：该增量为 0。不是相对该 query 自己的 Page1，也不是相对 Controller 排名前面的 Page2。',
           '- 沿用 PAGE2_SEARCH_PROBE_001 的 790 个归一化标题组和标注 arXiv ID 匹配：组中任一 ID 被原 organic URL parser 提取即算命中；不进行新标题匹配、语义匹配或 snippet 补候选。Page1=157，全量 Page1+Page2=220。',
           f"- isolated query gain 分布：`{result['gain_distribution']}`。逐 query gain 求和为 {result['sum_isolated_query_gains']}，同题多个 Page2 可以找回同一 GT，故不能把该和当作 63 个全量新增 GT。",
           '- 48 题各 5 条 native，Q18/Q28 各 4 条。Page1 与 Page2 分别为 2026-09-10 / 2026-09-11 历史缓存；索引和排序可能发生时间变化，不是同时检索的快照。',
           f"- Snapshot ID：`{result['snapshot_id']}`。所有 496 份响应文件哈希与上一实验完全一致。",'',
           '## 本地模型和语义特征可用性','',
           '- 检查了项目 checkpoints、用户 Hugging Face/Torch cache、NVMe 上两个 Hugging Face cache 和相关环境变量指定位置；详细路径、配置哈希和包版本见 environment_audit.json。',
           '- 仅发现 pasa-7b-crawler / pasa-7b-selector，架构均为 Qwen2ForCausalLM；未发现 sentence embedding checkpoint。sentence-transformers 未安装。未加载、改造或调用这两个生成模型。',
           '- 网络下载=0、模型调用=0、Crawler generation=0。semantic embedding 字段明确记为 NOT_MEASURED_NO_LOCAL_EMBEDDING_MODEL，而非赋 0 或伪造相似度。',
           '- 检查范围是当前项目及用户缓存，不能声称扫描过其他用户或系统的所有存储位置。', '',
           '## Page1 特征及冻结计算方法','',
           '- 集合统计直接复用 001 的特征提取逻辑，重新读取原 Page1 响应，并与 states.json 全部特征逐项一致性检查。包括 valid candidate count、leave-one-out exclusive/marginal unique、顺序 marginal、mean/max Jaccard、重复率、question union 等。',
           '- exclusive count 是相对同题其余 query 并集的独有 ID 数；sequential marginal 是相对之前 query 的新增 ID 数，二者分开。question union/duplicate 是整题共享特征，可能区分题目却不能独自决定同题 query 的 routing。',
           '- 词面特征：Question 或 native Query 与每条有效 Page1 organic 的 title+snippet 做 TF-IDF cosine。仅用 Page1 去重文本构造 IDF；固定英文小写分词/停用词，log TF、smoothed IDF、L2 normalization；没有同义词、语义蕴含或缩写扩展。',
           '- Question 文本来自旧约束提取记录中的 /attempts/0/prompt 的原始 USER QUESTION 段，未使用生成约束或模型输出。Feature 阶段完全不读取含 GT 的数据集，分析阶段再与原实验问题逐题核对。',
           '- 窗口按 organic 原数组位置：top1、top1–3、tail8–10；另算 mean/max、top3−tail3（正值=尾部下降）和 relevance 对 rank 的 OLS slope（正值=尾部上升）。仅保留原 parser 可识别候选，不改排序；重复 ID 保留各原位置的词面分数。',
           '- 空窗口为 null，不填 0、不用更前位置代替 tail；部分窗口取现有位置均值并记录覆盖数。每特征报告有效/缺失正负样本数。输出 word-level similarity 是词面代理，不是 semantic embedding。',
           '- 原 need_more_search_score 只作为既有失败分数的诊断列；未新增分数组合。所有特征和分析计划在读取本轮标签前冻结。','',
           '## 统计方法','',
           '- positive/negative 均值、中位数、样本标准差、min/p10/q25/q75/p90/max、逐值频数/ECDF 全部写入 feature_stats.json；下表给出主要摘要。',
           '- 效应量：Hedges g（positive−negative，pooled SD 小样本校正）与 Cliff delta（含 ties；等于 2×原向 AUC−1）。零方差时 g/相关系数为 null。',
           '- 单特征 ROC-AUC 与 PR-AUC 同时报告高值=positive 和低值=positive 两个方向，避免用 AUC<0.5 错判为无信息。主要 PR 指标为 average precision/AP（阶梯积分、ties 成组）；JSON 另存梯形 PR-AUC，后者可能因 ties 和初始 (0,1) 插值偏乐观。AP 参考水平为该特征有效样本的 positive prevalence。',
           '- Pearson/Spearman 均针对整数 isolated Page2 gain；Spearman 用 ties 平均秩。统计相互关联，不能按 query gain 的重复命中总和解释全量收益。',
           '- 1000 次用户问题 cluster bootstrap（seed=20260917），每次有放回抽 50 个问题，并保留其全部 native query；所有特征共享相同抽样。95% CI 是探索性的逐特征边际 percentile 区间，未做多重比较校正，不用于宣布选中特征。',
           '- 分层使用标签不可见的 pooled 20/40/60/80% 分位边界；重复边界合并，ties 不拆分，所以可能少于 5 层、层大小不等。这些只是分布摘要，不是调出的 routing threshold。',
           '- 额外报告同题正负 query 对的 pair-weighted AUC、题目中心化 Pearson、题内秩中心化相关。仅含正负两类的题才能贡献题内 AUC；不把题间差异当作题内路由能力。','',
           '## 全特征分布、效应量与单特征区分度','',
           f"全样本 AP 参考 prevalence={result['positive_prevalence']:.4f}；有缺失的特征使用其有效子集 prevalence（见 JSON）。按 |原向 AUC−0.5| 展示，属于事后描述性排序。",'',
           '| Feature | n / missing | positive mean / median | negative mean / median | Hedges g | Cliff δ | AUC 高 / 低 | 高向 AUC 95% CI | AP 高 / 低 |',
           '|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for name in sorted(fs,key=lambda n:(-strength(n),n)):
        s=fs[name];c=ci(name)
        lines.append(f"| {name} | {s['n_valid']} / {s['n_missing']} | {fmt(s['positive']['mean'])} / {fmt(s['positive']['median'])} | {fmt(s['negative']['mean'])} / {fmt(s['negative']['median'])} | {fmt(s['effect_size']['hedges_g_positive_minus_negative'])} | {fmt(s['effect_size']['cliffs_delta'])} | {fmt(s['high_is_positive']['roc_auc'])} / {fmt(s['low_is_positive']['roc_auc'])} | [{fmt(c['low'])}, {fmt(c['high'])}] | {fmt(s['high_is_positive']['average_precision'])} / {fmt(s['low_is_positive']['average_precision'])} |")
    lines+=['','## 与 Page2 gain 的相关性及题内区分','',
            '| Feature | Pearson gain | Spearman gain | 同题 AUC 高向 | 题目中心化 Pearson | 题内秩中心化相关 | 混合标签题数 |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for name in sorted(fs):
        s=fs[name];c=s['conditional_within_question'];r=s['correlation_with_integer_page2_gain']
        lines.append(f"| {name} | {fmt(r['pearson'])} | {fmt(r['spearman'])} | {fmt(c['pair_weighted_within_question_auc_high'])} | {fmt(c['question_centered_pearson_gain'])} | {fmt(c['within_question_rank_centered_correlation_gain'])} | {c['mixed_label_question_count']} |")
    focus=['mean_jaccard','max_jaccard','cross_query_duplicate_ratio','question_duplicate_ratio','exclusive_candidate_ratio','marginal_unique_candidate_count','question_unique_candidate_count','original_need_more_search_score']
    focus += [f'{source}_lexical_{metric}' for source in ['question','query'] for metric in ['mean','top3','tail3','top3_minus_tail3','rank_slope']]
    lines+=['','## overlap / novelty 反向趋势与词面 tail、decay 分层','',
            '括号为每层 query 数，按特征值由低到高。分位边界严格按数值合并 ties，没有按标签挑切点。完整边界、分组 gain 均值和所有其他特征见 JSON。','',
            '| Feature | 由低到高的 positive rate（n） |', '|---|---|']
    for name in focus:
        ss=fs[name]['pooled_quintile_strata']['bins']
        text=' → '.join(f"{b['positive_rate']:.1%} ({b['n']})" for b in ss)
        lines.append(f'| {name} | {text} |')
    lines+=['','mean Jaccard 从最低到最高分位的 positive rate 为 8.0%→50.0%，max Jaccard 为 7.8%→51.1%；exclusive ratio 则为 49.2%→6.7%。反向趋势并非仅由整题共同属性造成：max/mean Jaccard 的题内 AUC 仍为约 0.731/0.714。重复率和 exclusive ratio 在当前非空候选样本中互补，不能累计成两份独立证据。','','## 相同有效样本上的词面指标比较','',
            '这是发现 tail 缺失后补充的敏感性分析；未改变任何特征或标签。每行双方使用完全相同的 query，均以高值对应 positive；CI 用同一组问题 bootstrap 做配对差值。差值为左−右，没有选择 threshold 或重新组合分数。区间仍是未校正多重比较的探索性结果。','',
            '| 左特征 | 右特征 | n | AUC 左 / 右 | ΔAUC [95% cluster CI] | AP 左 / 右 | ΔAP [95% cluster CI] |',
            '|---|---|---:|---:|---|---:|---|']
    for row in result['paired_common_support_comparisons']:
        c=row['auc_difference_cluster_95ci'];a=row['ap_difference_cluster_95ci']
        lines.append(f"| {row['left']} | {row['right']} | {row['common_support_n']} | {fmt(row['left_auc'])} / {fmt(row['right_auc'])} | {fmt(row['auc_difference_left_minus_right'])} [{fmt(c[0])}, {fmt(c[1])}] | {fmt(row['left_ap'])} / {fmt(row['right_ap'])} | {fmt(row['ap_difference_left_minus_right'])} [{fmt(a[0])}, {fmt(a[1])}] |")
    lines+=['','## 验证与复现','',
            '- query 数量及逐 query key 与 001 完全一致；独立从冻结 GT 组和原始 Page1/Page2 ID 集重算标签，对 248 条 gain 和新 GT 标题集合逐项核对。',
            '- Feature 脚本使用数据读取白名单，只允许旧 states、Page1 响应、原始 question prompt 记录和环境审计；访问日志核验无 GT、Page2 outcome、旧/新评测报告读取。主动尝试读取 6 个 GT/Page2/outcome 受保护输入均在 I/O 前被拒绝。分析程序独立加入标签，无法改变已冻结特征。',
            '- 所有阶段阻止网络/模型库导入、socket/DNS 和子进程；源码及产物有哈希追踪，正式主流程、旧实验、全部历史响应均未改动。',
            '- 统计函数验证了完美/反向/常数排序、ties、单类、零方差和题间/题内差异案例；bootstrap 抽样由同 seed 重建并核对。',
            '- query_signal_table.json/csv 是逐 query 的冻结特征＋离线标签；feature_stats.json 包含完整分布、双向 AUC/AP、相关性、bootstrap CI 和固定分位层；page1_features.json 是独立、无标签的特征产物。', '',
            '```bash', '/mnt/nvme3/chenyi/conda-envs/pasa/bin/python -B page2_routing_signal_audit_002/environment_probe.py',
            'python3 -B page2_routing_signal_audit_002/extract_features.py',
            'python3 -B page2_routing_signal_audit_002/validate_features.py',
            'python3 -B page2_routing_signal_audit_002/analyze.py', '```','']
    (HERE/'PAGE2_ROUTING_SIGNAL_AUDIT_002.md').write_text('\n'.join(lines))
