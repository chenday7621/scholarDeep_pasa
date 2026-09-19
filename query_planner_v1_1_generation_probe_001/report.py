"""Render fixed mechanical analysis and human review; no model or network imports."""
import collections
import datetime as dt
import json
from pathlib import Path
from analysis import measure, summarize, THRESHOLD
from probe import OUT, REPORT, MANUAL, WORK, read, save, sha, protected

FOCUS={18:'检查是否正常输出 [Search]，而非 [Expand]。',28:'检查 HumanEval、MBPP、code_contests，以及更难／更容易的比较关系是否保留。',43:'检查是否同时覆盖 protein design 和 antibody design / DPO。',48:'检查是否保留 factor mining，而非退化为普通 stock prediction。'}
OBSERVATIONS={18:'文本核查：本次 B 正常生成 4 条 [Search] 并以 [StopSearch] 结束，未出现 Expand 标记。',28:'文本核查：本次 A/B 均未出现 HumanEval、MBPP、code_contests 这三个名称。B 实际生成 5 条，但数量不代表保留了难度比较关系。',43:'文本核查：B 出现 protein design、antibody design 和 DPO，也产生了 “Decoding Protein Optimization”。这里只记录模型实际文本，该展开的正确性留给人工审核。',48:'文本核查：B 出现 factor identification / factor mining，同时出现原问题未提及的 GPT-2、BERT-based。factor mining 所在 query 使用 machine learning；是否保留了原问题要求的大语言模型与因子挖掘之间的关系，留给人工审核。'}
def numbered(queries):
    return '\n'.join(f'{i+1}. {q}' for i,q in enumerate(queries)) if queries else '（无可解析 Search query；未补齐。）'
def raw_block(g):return '```text\n'+g['raw_output']+'\n```\n\n解析结果：\n\n'+numbered(g['queries'])
def table_summary(s):
    fields=[('Search parse success（题数 / 50）','search_parse_success'),('无 Search query 题数','no_search_query_questions'),('严格 Search 格式题数','strict_search_format_questions'),('非 Search action 题数','non_search_action_questions'),('非 Search action 标记出现次数','non_search_action_marker_occurrences'),('含 Expand / StopExpand 题数','expand_questions'),('总 query 数','total_query_count'),('每题 query 数分布','query_count_distribution'),('空 query 数','empty_query_count'),('exact duplicate query 数（重复条目）','exact_duplicate_query_count'),('exact duplicate pair 数','exact_duplicate_pair_count'),('高相似 pair 数（Jaccard ≥ 0.85，含 exact）','high_similarity_pair_count'),('near-duplicate pair 数（排除 exact）','near_duplicate_pair_count'),('全部题内 pair 数','pair_count'),('平均 pairwise token Jaccard（所有 pair）','mean_pairwise_token_jaccard_pooled'),('平均 pairwise token Jaccard（有 pair 的题等权）','mean_pairwise_token_jaccard_macro_eligible'),('未以 EOS 结束的生成数','non_eos_generations'),('超过原生 5 条上限的生成数','generations_exceeding_native_query_cap')]
    def fmt(v):return f'{v:.6f}' if isinstance(v,float) else json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else str(v)
    return '\n'.join(['| 指标 | A：Baseline | B：V1.1 |','|---|---:|---:|']+[f'| {label} | {fmt(s["A"][key])} | {fmt(s["B"][key])} |' for label,key in fields])

def main():
    d=read();assert d['status'] in ('generations_complete','complete')
    p=d['provenance'];assert sha(WORK/'analysis.py')==p['analysis_sha256_before_inference']
    assert protected()==p['protected_before']==p['protected_after']
    ts=read(WORK/'translations.json');assert len(ts)==50
    for q,t in zip(d['per_query'],ts):
        q['question_zh']=t
        for g in q['groups'].values():g['metrics']=measure(g)
    s={key:summarize(d['per_query'],key) for key in ('A','B')};d['summary']=s
    d['analysis_definitions']={'scope':'Final first-five native parsed queries; only within each Q, never cross-question duplicates.', 'exact_duplicate':'Identical parsed string, case-sensitive; redundant query entries sum(count-1). Pair count reported separately.', 'tokens':'set(re.findall(r"[a-z0-9]+", text.casefold())); no stemming/stopword removal; underscore and punctuation split tokens.', 'jaccard':'intersection / union; empty union = 0', 'high_similarity_threshold':THRESHOLD,'near_duplicate':'Jaccard >= threshold and not exact string duplicate', 'averages':'Pooled over all within-Q pairs, plus equal weight per eligible Q with >=2 queries. Ineligible Qs excluded from macro pair mean, never fabricated as zero.', 'non_search_actions':'All [A-Za-z][A-Za-z0-9_]* bracket markers except Search and StopSearch. Unknown markers require human review; both Q count and marker occurrences retained.', 'strict_format':'Entire raw output must be nonempty [Search] entries followed by [StopSearch], with whitespace allowed.', 'semantic_quality':'No automatic correctness, entity-retention, unsupported-specificity, or GT judge. Human review required.'}
    p.update(report_generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),report_script_sha256=sha(Path(__file__)),translations_sha256=sha(WORK/'translations.json'),translation_provenance='Assistant-authored Chinese translations from original questions only; review-only, never model inputs; not a semantic judge.')
    a,b=s['A'],s['B']
    report=['# QUERY_PLANNER_V1_1_GENERATION_PROBE_001',f"A/B Search parse success：**{a['search_parse_success']}/50 → {b['search_parse_success']}/50**；非 Search action 题数：**{a['non_search_action_questions']} → {b['non_search_action_questions']}**；总 query 数：**{a['total_query_count']} → {b['total_query_count']}**。",'本轮只检验单次固定 seed 的输出格式与词面重复情况。是否更好地保留实体、benchmark、比较及否定条件，是否引入无依据的具体名称，均等待人工审核；不使用 GT，不宣称语义质量提升或检索 Recall。',
    '## 固定实验与边界',
    '- Q0–Q49，只解码 RealScholarQuery-50 原始 question 字段。每题 A 后紧邻生成 B，各一次，共 100 次；没有重采样或筛选结果。',
    f"- checkpoint：`{p['checkpoint']}`；物理 GPU {p['physical_gpu_index']}（{p['gpu']}），batch_size=1。A/B 每次 generate 前重置 seed=42，进程 PYTHONHASHSEED=42，max_new_tokens=512。",
    '- 两组使用同一原生 chat template、tokenizer 和 checkpoint generation config；仅传原生 max_new_tokens，不改 sampling。do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05。',
    '- A 直接读取原生 agent_prompt.json；两组均沿用原生推理的外层 strip。B 固定为用户指定 V1.1 文本。原生 parser `Search\\](.*?)\\[` + DOTALL，strip 后最多前 5 条。没有补齐、去重、修复格式或将 Expand 改写为 Search。',
    '- 仅以本地文件加载 Crawler；HF 离线模式及 Python 网络审计钩子禁止 Internet socket / DNS。未调用 Search、Serper、Expand、Selector、外部 LLM/API 或元数据查询。',
    '- baseline、源码、先前 V1 Search 实验及配置前后哈希一致。独立脚本不导入 PaSa 主流程。未更改 checkpoint、baseline、evaluator；未提交 Git。',
    '- 未加入 facet planner、acronym expansion、constraint extraction JSON 或 repair model。',
    '### A prompt（原始模板）','```text\n'+p['A_template']+'\n```','### B prompt（固定 V1.1 模板）','```text\n'+p['B_template']+'\n```',
    '## 统计口径',
    '- Parse success 指原生 parser 在该题解析出至少一条 query；零 query 题保留在 50 题分母。另列严格格式指标，以区分“可解析”与“仅含 Search 条目且以 StopSearch 结束”。',
    '- 非 Search action 统计原始输出中除 Search / StopSearch 外的 action 形括号标记，同时报告涉及题数和标记次数；未知标记并不自动证明真正执行了动作。本实验不会执行任何生成动作。',
    '- exact duplicate query 数按同题完全相同字符串的多余条目 sum(count−1) 计算；另列配对数。大小写或标点不同不算 exact。',
    '- Token 使用小写 ASCII 字母数字集合，标点与下划线分词，不移除停用词、不词干化。Jaccard ≥ 0.85 计为高相似；near-duplicate 排除 exact。只比较同题的最终 queries，不跨题计重复。',
    '- 同时报告所有 query pair 的汇总平均 Jaccard，以及有至少两条 query 的题等权平均；没有 pair 的题不人为记零。阈值和分析代码在生成前固定。词面相似只能作为重复诊断，不能判断语义冗余或信息覆盖。',
    '## Q0–Q49 逐题机械统计',
    '| Q | A/B queries | A/B 非 Search action 标记次数 | A/B exact 重复条目 | A/B 高相似 pairs | A/B 平均 Jaccard |','|---|---:|---:|---:|---:|---:|']
    table_start=len(report)-2
    for q in d['per_query']:
        ma,mb=[q['groups'][k]['metrics'] for k in ('A','B')]
        def avg(m):return '—' if m['mean_pairwise_token_jaccard'] is None else f"{m['mean_pairwise_token_jaccard']:.4f}"
        report.append(f"| {q['query_id']} | {ma['query_count']}/{mb['query_count']} | {len(ma['non_search_markers'])}/{len(mb['non_search_markers'])} | {ma['exact_duplicate_query_count']}/{mb['exact_duplicate_query_count']} | {ma['high_similarity_pair_count']}/{mb['high_similarity_pair_count']} | {avg(ma)}/{avg(mb)} |")
    report[table_start:]=['\n'.join(report[table_start:])]
    report+=['## 非 Search action 与高相似证据']
    for k in ('A','B'):
        report.append(f"{k}：非 Search 标记分布 `{s[k]['non_search_action_marker_distribution']}`；无 query 题："+(', '.join(q['query_id'] for q in d['per_query'] if not q['groups'][k]['queries']) or '无')+'。')
        for q in d['per_query']:
            g=q['groups'][k]
            if g['metrics']['non_search_markers']:report.append(f"- {q['query_id']} {k} 非 Search 标记：`{g['metrics']['non_search_markers']}`。完整原始输出见 JSON。")
            for pair in g['metrics']['pairs']:
                if pair['high_similarity']:
                    i,j=pair['query_indices'];report.append(f"- {q['query_id']} {k} query {i+1}/{j+1}：Jaccard={pair['token_jaccard']:.6f}；exact={pair['exact_duplicate']}。\n  - {g['queries'][i]}\n  - {g['queries'][j]}")
        if not s[k]['high_similarity_pair_count']:report.append(f'{k} 无达到阈值的 query pair。')
    report+=['## 运行与复核',f"- 生成阶段 UTC：{p['started_utc']} → {p['finished_utc']}；wall time {p['inference_wall_seconds']:.2f}s（{p['inference_wall_seconds']/60:.2f} 分钟，包括 checkpoint 哈希、加载与落盘）。",f"- 网络钩子阻止了 {len(p['blocked_network_events'])} 次事件：`{p['blocked_network_events']}`。这是 socket 创建阶段的拒绝，不是成功的网络请求；未记录调用栈，无法归因到具体库。生成次数 100；原始记录位于 `query_planner_v1_1_generation_probe_001/raw_generations/`。",'- JSON 保存完整 prompt、token IDs、原始输出、解析结果、seed、时间、运行配置、checkpoint 与源码哈希，以及每个 pair 的统计。人工审核表覆盖全部 50 题，中文翻译仅用于审核。独立复核证据保存在 `query_planner_v1_1_generation_probe_001/validation.json`。',
    '## 最终统计与重点原始输出',table_summary(s),
    'B 有 8 题生成超过 5 条 Search query（Q0、Q4、Q7、Q20、Q38、Q42、Q44、Q45），原生截取前共 257 条，最终保留 247 条。A 截取前后均为 248 条。超出上限的 10 条仍完整保存于 JSON 的原始输出、all_parsed_queries 和 discarded_queries；上表及人工表的 query 指标均按最终前 5 条计算。',
    '以下保留本次实际生成文本及原生解析结果，供人工检查。单个 seed 的格式成功率并不能证明跨 seed 稳定；词面重复指标也不能单独证明 query 质量提高。']
    for i,note in FOCUS.items():
        q=d['per_query'][i];report+=['### '+q['query_id'],q['original_question'],note,OBSERVATIONS[i]]
        for k,name in [('A','Baseline'),('B','V1.1')]:report+=['**'+k+'：'+name+'**',raw_block(q['groups'][k])]
    report+=['实验到此停止。等待人工审核后，再决定是否进入 Serper Search A/B；本轮没有运行 Search。']
    manual=['# QUERY_PLANNER_V1_1_GENERATION_MANUAL_REVIEW','本表只展示原始问题、人工审核用中文翻译和实际解析 queries；不足 5 条不补齐。未使用 GT 或自动语义 judge。中文翻译保留原缩写，不为模型提供标准展开。',
    '重点：[Q18](#q18) · [Q28](#q28) · [Q43](#q43) · [Q48](#q48)。原始模型输出见实验 JSON；这四题的原始输出也在实验报告末尾完整列出。']
    for q in d['per_query']:
        i=q['query_index'];manual+=['## '+q['query_id'],'Query ID: '+q['query_id'],'Original Question:\n\n'+q['original_question'],'中文翻译：\n\n'+q['question_zh']]
        if i in FOCUS:manual+=['**重点核查：'+FOCUS[i]+'**']
        manual+=['Baseline Queries:\n\n'+numbered(q['groups']['A']['queries']),'V1.1 Queries:\n\n'+numbered(q['groups']['B']['queries']),
        '关键实体 / benchmark / 方法的保留情况：\n\n[人工填写]','比较关系 / 排除 / 否定条件的保留情况：\n\n[人工填写]',
        '是否引入不受原问题支持的具体模型、数据集、方法或 benchmark：\n\n[人工填写]',
        '语义重复情况：\n\n[人工填写]','V1.1 相比 Baseline：\n\n- [ ] 更好\n- [ ] 相同\n- [ ] 更差\n- [ ] 不确定','Notes:\n\n[人工填写]']
    REPORT.write_text('\n\n'.join(report)+'\n');MANUAL.write_text('\n\n'.join(manual)+'\n')
    d['status']='complete';save(OUT,d)
    print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
