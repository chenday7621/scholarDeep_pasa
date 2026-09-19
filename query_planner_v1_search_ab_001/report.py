"""Final Search-only comparison; no prompt changes or new retrieval."""
import datetime as dt
import collections
import statistics
from common import ROOT,WORK,OUT,REPORT,now,read,save,sha

def pct(v):return 'N/A' if v is None else f'{v:.4%}'
def esc(s):return str(s).replace('|','\\|').replace('\n','<br>')
def pp(v):return f'{v*100:+.4f} pp'

def main():
    d=read();assert d['status'] in ('evaluated','complete')
    p=d['provenance'];a=d['summary']['A'];b=d['summary']['B'];c=d['summary']['comparison']
    for group in ('A','B'):
        for q in d['per_query']:
            g=q['groups'][group]
            g['format_diagnostic']={'contains_expand_markers':'[Expand]' in g['raw_output'] or '[StopExpand]' in g['raw_output'],
              'literal_search_markers':g['raw_output'].count('[Search]'),'no_parseable_search_query':len(g['queries'])==0,
              'native_search_envelope':g['raw_output'].strip().startswith('[Search]') and g['raw_output'].strip().endswith('[StopSearch]')}
        d['summary'][group]['GENERATIONS_WITH_EXPAND_MARKERS']=sum(q['groups'][group]['format_diagnostic']['contains_expand_markers'] for q in d['per_query'])
    zero_q=[q for q in d['per_query'] if q['groups']['B']['query_count']==0]
    nonzero_q=[q for q in d['per_query'] if q['groups']['B']['query_count']>0]
    d['summary']['B_query_availability_breakdown']={label:{'Q_count':len(qs),'TOTAL_GT':sum(q['gt']['normalized_title_count'] for q in qs),
      'A_found':sum(q['groups']['A']['formal_evaluation']['SEARCH_GT_FOUND'] for q in qs),
      'B_found':sum(q['groups']['B']['formal_evaluation']['SEARCH_GT_FOUND'] for q in qs)} for label,qs in [('B_zero_query',zero_q),('B_nonzero_query',nonzero_q)]}
    gaps=[]
    for q in d['per_query']:
        ga,gb=q['groups']['A'],q['groups']['B']
        qgaps=[]
        for sa,sb in zip(ga['searches'],gb['searches']):
            gap=abs((dt.datetime.fromisoformat(sa['attempts'][0]['started_utc'])-dt.datetime.fromisoformat(sb['attempts'][0]['started_utc'])).total_seconds())
            gaps.append(gap);qgaps.append(gap)
        q['comparison']['paired_first_attempt_time_gaps_seconds']=qgaps
    p['temporal_pairing']={'paired_query_index_count':len(gaps),'median_start_gap_seconds':statistics.median(gaps) if gaps else None,'max_start_gap_seconds':max(gaps) if gaps else None}
    p['report_finished_utc']=now()
    p['experiment_finished_utc']=p['evaluation_finished_utc']
    p['total_run_wall_seconds']=(dt.datetime.fromisoformat(p['experiment_finished_utc'])-dt.datetime.fromisoformat(p['started_utc'])).total_seconds()
    p['end_to_end_delivery_wall_seconds']=(dt.datetime.fromisoformat(p['report_finished_utc'])-dt.datetime.fromisoformat(p['started_utc'])).total_seconds()
    p['post_evaluation_reporting_gap_seconds']=p['end_to_end_delivery_wall_seconds']-p['total_run_wall_seconds']
    p['metadata_http_status_distribution']=dict(collections.Counter(str(r.get('http_status')) for r in p['metadata_request_log']))
    p['report_script_sha256']=sha(WORK/'report.py')
    d['status']='complete';save(OUT,d)
    headline=(f"A→B：正式 Search macro recall **{pct(a['SEARCH_RECALL'])} → {pct(b['SEARCH_RECALL'])}**（{pp(c['macro_recall_absolute_delta'])}；相对 {pct(c['macro_recall_relative_delta'])}）；"
              f"GT 命中 **{a['SEARCH_GT_FOUND']} → {b['SEARCH_GT_FOUND']} / {a['TOTAL_GT']}**；实际 Serper 调用 **{a['SERPER_CALLS']} → {b['SERPER_CALLS']}**。")
    lines=['# QUERY_PLANNER_V1_SEARCH_AB_001','',headline,'',
      f"B 新找回 {c['B_new_gt_count']} 个 GT，丢失 A 原先找到的 {c['B_lost_gt_count']} 个 GT；净变化 {b['SEARCH_GT_FOUND']-a['SEARCH_GT_FOUND']:+d}。这些数量均按 (Q, 归一化 GT 标题) 计数。",'',
      f"**生成格式需要单独看待：A 有 {a['GENERATIONS_WITH_ZERO_QUERIES']} 个 Q、B 有 {b['GENERATIONS_WITH_ZERO_QUERIES']} 个 Q 没有可解析的 Search query；A/B 含 `[Expand]` 标记的生成分别为 {a['GENERATIONS_WITH_EXPAND_MARKERS']}/{b['GENERATIONS_WITH_EXPAND_MARKERS']}。这些标记只是模型输出文本，没有执行 Expand，也没有改成 Search 后补跑。零 query 的题保留在 50 题 Recall 分母中。**",'',
      f"标题获取也有限制：共有 {len(p['metadata_summary']['unresolved_ids'])} 个直接返回 ID 未能取得原生标题，正式标题匹配不会计入它们。该结果包含本次元数据基础设施失败的影响；另附 ID-aware 诊断，A/B 为 {a['ID_AWARE_DIAGNOSTIC']['FOUND_GT_IDS']}/{b['ID_AWARE_DIAGNOSTIC']['FOUND_GT_IDS']} 个 GT ID，未用来替代正式指标。",'',
      '## 一次性固定实验','',
      '- 数据：RealScholarQuery-50 Q0–Q49。每 Q 的 A/B 都重新生成并执行真实 Serper；无旧 baseline/PAGE2 搜索结果复用，无本地 Search 响应缓存。',
      f"- Checkpoint：`{p['checkpoint']}`；同一 Crawler、同一 generation config、同一 GPU、batch_size=1。每次 A/B generate 前均重置 seed=42，PYTHONHASHSEED=42。只传原生 max_new_tokens=512，不覆盖 sampling 参数。", 
      '- 原采样参数：do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05。prompt 固定，无多次试验后挑结果或根据 GT 修改 query。',
      '- A 从仓库 `agent_prompt.json` 直接读取完整原始字符串，包括原始空白；B 使用用户指定文本。两组均用原生 chat template 和 `[Search]` parser。',
      '- 原生 parser：`Search\\](.*?)\\[` + DOTALL，strip 后最多保留前 5 条。未补 query、未因重复而删除 query、未将 `[Expand]` 文本转成 Search。',
      '- 请求：同一 Serper endpoint/凭据；page=1、num=10、site:arxiv.org。source_meta.published_time=20241001，按原脚本减 7 天，因此全部 before:2024-09-24。before 是请求中的搜索操作符，没有额外本地日期过滤。',
      '- 每 Q 先产生 A/B 输出，再按 query 序号交错请求两组。偶数 Q 先 A，奇数 Q 先 B；同文本也分别发真实请求。少 query 组结束后另一组继续，绝不补齐。',
      f"- 按相同 query 序号配对的首次请求共有 {len(gaps)} 对；开始时间差中位数 {p['temporal_pairing']['median_start_gap_seconds']:.3f}s，最大 {p['temporal_pairing']['max_start_gap_seconds']:.3f}s。紧邻执行降低时间差异，不能保证搜索索引完全不变。",'',
      '### A prompt（原生）','', '```text',p['A_template'],'```','', '### B prompt（固定 V1）','', '```text',p['B_template'],'```','',
      '## 正式评测口径','',
      '- 沿用冻结 `utils.keep_letters`：仅保留 Unicode 字母并转小写；标题完全相等才算命中，不使用 fuzzy/alias/embedding，也不按 GT ID 替代正式匹配。原始 791 条标注归一化为 790 个 (Q,title) GT；碰撞按冻结规则保留，不修 evaluator。',
      '- 只对 Serper organic URL 经原生正则解析得到的 arXiv IDs 评测。ID 正则保持原样：`arxiv.org/(abs|pdf|html)/(\\d{4}\\.\\d+)`；不从 snippet 或站外链接补候选。',
      '- 候选标题使用未改动的原生 `search_paper_by_arxiv_id`：本地 ZIP 记录优先，缺失时仅按已返回 ID 查询原生 arXiv 元数据。同一 ID 在 A/B 使用共享标题快照。没有标题搜索、引用搜索或新候选补充；未解析到标题的 ID 不用 GT/Serper 展示标题替代。',
      '- **SEARCH_RECALL 为 macro**：50 个逐 Q recall 的平均值。MICRO_SEARCH_RECALL 为总命中 GT / 790。',
      '- **SEARCH_RECALL_PER_CALL = 命中 GT 数 / 实际 Serper HTTP 尝试次数**，单位为 GT/调用，不是百分比，也不是 recall 再除调用数。失败尝试计入成本；另列 logical calls。',
      '- unique candidates 同时报告：全组跨 Q 去重 ID 数、逐 Q 去重后求和的 (Q,ID) 数。后者与逐题评测/候选处理量更接近。',
      '- 用原始 `metrics.py` 对 Search-only 候选树复算，A/B macro recall 与独立汇总均一致。验证树中的 select_score=0 仅为满足文件结构；未运行 Selector，其余 Selector/ranking 输出不作实验指标。', '',
      '## A/B 总体结果','', '| 指标 | A：Baseline | B：V1 |','|---|---:|---:|']
    rows=[('TOTAL_GT',a['TOTAL_GT'],b['TOTAL_GT']),('SEARCH_GT_FOUND',a['SEARCH_GT_FOUND'],b['SEARCH_GT_FOUND']),
      ('SEARCH_RECALL（正式 macro）',pct(a['SEARCH_RECALL']),pct(b['SEARCH_RECALL'])),('MICRO_SEARCH_RECALL',pct(a['MICRO_SEARCH_RECALL']),pct(b['MICRO_SEARCH_RECALL'])),
      ('SEARCH_RECALL_PER_CALL（GT/调用）',f"{a['SEARCH_RECALL_PER_CALL']:.6f}",f"{b['SEARCH_RECALL_PER_CALL']:.6f}"),
      ('Serper calls（HTTP attempts）',a['SERPER_CALLS'],b['SERPER_CALLS']),('Logical Search calls / queries',a['LOGICAL_SEARCH_CALLS'],b['LOGICAL_SEARCH_CALLS']),
      ('Unique candidate arXiv IDs（全组去重）',a['UNIQUE_CANDIDATE_PAPERS_GLOBAL'],b['UNIQUE_CANDIDATE_PAPERS_GLOBAL']),
      ('Unique candidates（逐 Q 去重后求和）',a['UNIQUE_CANDIDATE_PAPERS_SUM_PER_Q'],b['UNIQUE_CANDIDATE_PAPERS_SUM_PER_Q']),
      ('成功取得标题的全组 ID 数',a['RESOLVED_TITLE_CANDIDATES_GLOBAL'],b['RESOLVED_TITLE_CANDIDATES_GLOBAL']),
      ('未取得标题的全组 ID 数',len(a['MISSING_METADATA_IDS_GLOBAL']),len(b['MISSING_METADATA_IDS_GLOBAL'])),
      ('无可解析 query 的 Q 数',a['GENERATIONS_WITH_ZERO_QUERIES'],b['GENERATIONS_WITH_ZERO_QUERIES']),
      ('空 query / 未 EOS 生成数',f"{a['GENERATIONS_WITH_EMPTY_QUERY']} / {a['NON_EOS_GENERATIONS']}",f"{b['GENERATIONS_WITH_EMPTY_QUERY']} / {b['NON_EOS_GENERATIONS']}")]
    for name,x,y in rows:lines.append(f'| {name} | {x} | {y} |')
    lines += ['',f"Macro 绝对变化 **{pp(c['macro_recall_absolute_delta'])}**，相对变化 **{pct(c['macro_recall_relative_delta'])}**。Micro 绝对变化 **{pp(c['micro_recall_absolute_delta'])}**，相对变化 **{pct(c['micro_recall_relative_delta'])}**。",'',
      '| GT 分组 | 数量 |','|---|---:|',f"| B 新找回、A 未找到 | {c['B_new_gt_count']} |",f"| A 找到、B 丢失 | {c['B_lost_gt_count']} |",f"| 两组都找到 | {c['both_found_gt_count']} |",f"| 两组都没找到 | {c['both_missed_gt_count']} |",'',
      f"逐题 Recall：提升 {c['queries_improved']} 题、下降 {c['queries_declined']} 题、持平 {c['queries_tied']} 题。",'',
      f"格式可用性的描述性分解：B 无可解析 query 的 {len(zero_q)} 题，A 命中 {d['summary']['B_query_availability_breakdown']['B_zero_query']['A_found']} 个 GT，B 命中 0；其余 {len(nonzero_q)} 题，A/B 命中 {d['summary']['B_query_availability_breakdown']['B_nonzero_query']['A_found']}/{d['summary']['B_query_availability_breakdown']['B_nonzero_query']['B_found']}。这只是分解完整结果，没有从正式 50 题指标中剔除格式失败，也不能据此推断修复格式后的效果。",'',
      '## Query 数量、重复与结果 overlap','',f"A query 数量分布：`{a['QUERY_COUNT_DISTRIBUTION']}`；B：`{b['QUERY_COUNT_DISTRIBUTION']}`。",'',
      '| 指标 | A | B |','|---|---:|---:|',
      f"| 规范化后完全重复 query 对 | {a['NORMALIZED_DUPLICATE_QUERY_PAIRS']} | {b['NORMALIZED_DUPLICATE_QUERY_PAIRS']} |",
      f"| 词集合 Jaccard≥0.85 的近重复 query 对 | {a['NEAR_DUPLICATE_QUERY_PAIRS']} | {b['NEAR_DUPLICATE_QUERY_PAIRS']} |",
      f"| 同题不同 query 之间重复的 ID occurrences | {a['REPEATED_ID_OCCURRENCES_BETWEEN_QUERIES']} | {b['REPEATED_ID_OCCURRENCES_BETWEEN_QUERIES']} |",
      f"| 各题 query 对返回 ID Jaccard 的平均值 | {a['MEAN_PER_Q_PAIRWISE_ID_JACCARD']:.6f} | {b['MEAN_PER_Q_PAIRWISE_ID_JACCARD']:.6f} |",'',
      '重复 query 使用小写字母数字 token 序列精确比较；近重复只作词面诊断。ID overlap 矩阵及每对重叠 ID 保存在 JSON 的 per_query[].groups.A/B.query_overlap 中。少于 2 条 query 的题其 overlap 均值记为 0，因此该汇总也受零 query/少 query 影响，不单独视作质量改善。', '',
      '## Recall 提升与下降最大的 Q','']
    for label,condition,reverse in [('提升最大',lambda q:q['comparison']['recall_delta']>0,True),('下降最大',lambda q:q['comparison']['recall_delta']<0,False)]:
        selected=sorted([q for q in d['per_query'] if condition(q)],key=lambda q:q['comparison']['recall_delta'],reverse=reverse)[:5]
        lines += [f'### {label}','', '| Q | GT | A 命中 / Recall | B 命中 / Recall | Δ Recall | B 新增 / 丢失 |','|---|---:|---|---|---|---|']
        for q in selected:
            aa=q['groups']['A']['formal_evaluation'];bb=q['groups']['B']['formal_evaluation'];cc=q['comparison']
            lines.append(f"| {q['query_id']} | {aa['TOTAL_GT']} | {aa['SEARCH_GT_FOUND']} / {pct(aa['SEARCH_RECALL'])} | {bb['SEARCH_GT_FOUND']} / {pct(bb['SEARCH_RECALL'])} | {pp(cc['recall_delta'])} | {len(cc['B_new_gt'])} / {len(cc['B_lost_gt'])} |")
        if not selected:lines.append('| 无 | — | — | — | — | — |')
        lines.append('')
    lines += ['## Q0–Q49 逐题结果','', '| Q | GT | A queries/calls | B queries/calls | A found | B found | A Recall | B Recall | Δ | 新增/丢失 | A/B candidates |','|---|---:|---|---|---:|---:|---|---|---|---|---|']
    for q in d['per_query']:
        ga,gb=q['groups']['A'],q['groups']['B'];ea,eb=ga['formal_evaluation'],gb['formal_evaluation'];cc=q['comparison']
        lines.append(f"| {q['query_id']} | {ea['TOTAL_GT']} | {ga['query_count']}/{ga['serper_calls']} | {gb['query_count']}/{gb['serper_calls']} | {ea['SEARCH_GT_FOUND']} | {eb['SEARCH_GT_FOUND']} | {pct(ea['SEARCH_RECALL'])} | {pct(eb['SEARCH_RECALL'])} | {pp(cc['recall_delta'])} | {len(cc['B_new_gt'])}/{len(cc['B_lost_gt'])} | {len(ga['returned_unique_arxiv_ids'])}/{len(gb['returned_unique_arxiv_ids'])} |")
    lines += ['', '## Q18、Q28、Q43、Q48 详细结果','']
    for qi in (18,28,43,48):
        q=d['per_query'][qi];cc=q['comparison']
        lines += [f"### {q['query_id']}",'','Original Question: '+q['original_question'],'',f"GT={q['gt']['normalized_title_count']}；Recall delta={pp(cc['recall_delta'])}；B 新增={len(cc['B_new_gt'])}，B 丢失={len(cc['B_lost_gt'])}。",'']
        for group,g in q['groups'].items():
            e=g['formal_evaluation']
            lines += [f"**{group} 组**：queries={g['query_count']}，实际 Serper calls={g['serper_calls']}，unique candidates={len(g['returned_unique_arxiv_ids'])}，GT found={e['SEARCH_GT_FOUND']}/{e['TOTAL_GT']}，Recall={pct(e['SEARCH_RECALL'])}。",'', '| Query # | 实际生成 query | 返回 unique ID 数 | IDs |','|---|---|---:|---|']
            for search in g['searches']:lines.append(f"| {search['query_sequence']} | {esc(search['crawler_query'])} | {len(search['returned_arxiv_ids'])} | {', '.join(search['returned_arxiv_ids'])} |")
            if not g['searches']:lines.append('| — | 无可解析 Search query；未补跑 | 0 | — |')
            lines += ['', '原始模型输出：','', '```text',g['raw_output'],'```','']
        lines += ['GT 命中明细（仅冻结标题匹配）：','', '| GT 原始标题 | arXiv ID | A | B | 分组 |','|---|---|---|---|---|']
        for case in q['gt_comparison_cases']:
            lines.append(f"| {esc(' / '.join(x['title'] for x in case['annotations']))} | {', '.join(x['arxiv_id'] for x in case['annotations'])} | {'找到' if case['A_evidence'] else '未找到'} | {'找到' if case['B_evidence'] else '未找到'} | {case['category']} |")
        lines.append('')
    lines += ['## ID-aware diagnostic（不替代正式指标）','',
      '直接使用数据标注的 GT arXiv IDs 对 Search URL ID 做匹配。Q45 的归一化标题碰撞仍保持冻结处理；ID 口径有 791 个 (Q,ID)，正式标题口径为 790。诊断差异可能来自标题写法或元数据失败，不将 ID 命中自动补进正式结果。','',
      '| 指标 | A | B |','|---|---:|---:|',f"| GT IDs | {a['ID_AWARE_DIAGNOSTIC']['TOTAL_GT_IDS']} | {b['ID_AWARE_DIAGNOSTIC']['TOTAL_GT_IDS']} |",
      f"| Found GT IDs | {a['ID_AWARE_DIAGNOSTIC']['FOUND_GT_IDS']} | {b['ID_AWARE_DIAGNOSTIC']['FOUND_GT_IDS']} |",
      f"| Micro ID recall | {pct(a['ID_AWARE_DIAGNOSTIC']['MICRO_ID_RECALL'])} | {pct(b['ID_AWARE_DIAGNOSTIC']['MICRO_ID_RECALL'])} |",
      f"| Macro ID recall | {pct(a['ID_AWARE_DIAGNOSTIC']['MACRO_ID_RECALL'])} | {pct(b['ID_AWARE_DIAGNOSTIC']['MACRO_ID_RECALL'])} |",
      f"| 按 annotated ID 找到的归一化 GT 组 | {a['ID_AWARE_DIAGNOSTIC']['FOUND_TITLE_GROUPS_BY_ID']} | {b['ID_AWARE_DIAGNOSTIC']['FOUND_TITLE_GROUPS_BY_ID']} |",'',
      '## 运行时间与请求健康','',
      f"- 实验执行 UTC：{p['started_utc']} → {p['experiment_finished_utc']}；总实验 wall time **{p['total_run_wall_seconds']:.2f}s（{p['total_run_wall_seconds']/60:.2f} 分钟）**，包括加载、生成、搜索、元数据/评测及两执行阶段之间的等待。",
      f"- 生成+Search 阶段：{p['generation_search_wall_seconds']:.2f}s；元数据+评测阶段：{p['evaluation_wall_seconds']:.2f}s。",
      f"- 报告生成 UTC：{p['report_finished_utc']}；从实验启动到本次报告落盘共 {p['end_to_end_delivery_wall_seconds']/60:.2f} 分钟，其中评测结束后到报告生成的间隔为 {p['post_evaluation_reporting_gap_seconds']/60:.2f} 分钟。此间隔不计为 Search/元数据实际运行时间。",
      f"- Serper HTTP attempts：A {a['SERPER_CALLS']}，B {b['SERPER_CALLS']}，合计 {a['SERPER_CALLS']+b['SERPER_CALLS']}。失败 attempts A/B={a['FAILED_HTTP_ATTEMPTS']}/{b['FAILED_HTTP_ATTEMPTS']}；最终失败 logical calls={a['FAILED_LOGICAL_CALLS']}/{b['FAILED_LOGICAL_CALLS']}；429={a['HTTP_429_COUNT']}/{b['HTTP_429_COUNT']}。",
      f"- HTTP status：A `{a['HTTP_STATUS_DISTRIBUTION']}`；B `{b['HTTP_STATUS_DISTRIBUTION']}`。每条逻辑请求最多 3 次；固定 15/60 秒 connect/read timeout、1/2 秒 backoff，Retry-After 最长 30 秒；这些基础设施参数 A/B 一致。",
      f"- 标题元数据（A/B 共用）：{p['metadata_summary']['unique_search_ids']} 个直接 Search ID，成功解析 {p['metadata_summary']['resolved_titles']}；原生 arXiv 元数据 HTTP 请求 {p['metadata_summary']['http_requests']}，429={p['metadata_summary']['http_429_count']}。这些不是 Serper calls，也不增加候选。",
      f"- 元数据 HTTP/传输状态分布：`{p['metadata_http_status_distribution']}`；None 表示没有收到 HTTP 响应，具体异常类型保存在逐请求记录中。",
      f"- 元数据未解析 IDs：{', '.join(p['metadata_summary']['unresolved_ids']) or '无'}。未解析造成的正式标题覆盖限制与 ID diagnostic 均已保留。",'',
      '## 复核与边界','',
      '- 原始响应、payload、HTTP status、UTC/latency、返回 ID/标题、每个 GT 的 A/B 证据和增失分组都保存在 JSON。每次 HTTP attempt 另有独立文件，可检查未改写的响应。',
      '- 冻结源码/配置、baseline 文件和既有实验文件已做前后 SHA-256 校验；原始 metrics.py 验证结果在 provenance.official_evaluator_verification。',
      '- 此结果比较的是固定 prompt 的一次 seed=42 Search-only 测量，包含模型是否遵守原生 Search 格式的影响。少量 query 与低成本不自动等于更好；per-call 与总 Recall 必须一起看。',
      '- 同一 before 日期不能冻结搜索引擎索引或排序；A/B 请求紧邻且交错，但仍不是完全静态检索环境。',
      '- 没有运行 Citation Expand、Selector、完整 PaSa；没有 facet/acronym expansion 模块，没有外部 LLM，没有 page2、prompt 调优或 GT-based query 修改，没有 Git commit。实验到此结束，未继续修改 V1。', '',
      '输出：`QUERY_PLANNER_V1_SEARCH_AB_001.json`、`QUERY_PLANNER_V1_SEARCH_AB_001.md`；独立运行/评测脚本及请求证据在 `query_planner_v1_search_ab_001/`。','']
    REPORT.write_text('\n'.join(lines))
    print(headline)
    print(f"New={c['B_new_gt_count']}; lost={c['B_lost_gt_count']}; both={c['both_found_gt_count']}; neither={c['both_missed_gt_count']}")

if __name__=='__main__':main()
