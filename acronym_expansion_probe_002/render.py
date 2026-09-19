"""Render descriptive A/B measurements and an unfilled human review form."""
import collections
import hashlib
import json
from pathlib import Path
from metrics import metrics, summarize, norm
from probe import OUT, ROOT, save, sha

LABELS={'parse_success':'Search query 正常解析率','strict_native_envelope':'严格原生格式率',
        'acronym_retained':'Acronym Retention Rate','original_surface_retained':'原文大小写/词形严格保留率',
        'expansion_attempt_proxy':'Expansion Attempt Rate（疑似，词面代理）',
        'acronym_expansion_cooccurrence_proxy':'Acronym + full-form 共现率（疑似，词面代理）',
        'has_candidate_not_in_original':'出现原问题未包含的疑似展开词组',
        'any_normalized_duplicate':'含规范化重复 query 的输出',
        'any_near_duplicate':'含近重复 query 的输出',
        'any_candidate_collapsed_duplicate':'候选全称替换为缩写后重复的输出',
        'non_search_action_marker_present':'含非 Search 动作标记的输出',
        'query_cap_applied':'触发原生前 5 条截取的输出'}

def md(value):
    return str(value).replace('|','\\|').replace('\n','<br>')

def rate(summary,key):
    m=summary[key]
    return f"{m['run_count']}/{m['denominator']} ({m['rate']:.2%})"

def bits(runs,key):
    return ''.join('1' if r['metrics'][key] else '0' for r in runs)

def main():
    d=json.loads(OUT.read_text())
    assert d['status'] in ('generations_complete','complete')
    p=d['provenance']
    assert sha(Path(__file__).with_name('metrics.py'))==p['metrics_script_sha256_at_inference'], 'Detection algorithm changed after inference began'
    for s in d['samples']:
        for group,g in s['groups'].items():
            assert len(g['runs'])==5
            for r in g['runs']: r['metrics']=metrics(r,s)
            g['summary']={key:sum(r['metrics'][key] for r in g['runs']) for key in LABELS}
        s['human_review']={'gold_expansion':None,'A_judgment':None,'B_judgment':None,'B_vs_A':None,'notes':None}
    summary={g:summarize(d['samples'],g) for g in ('A','B')}
    summary['combined']={'acronym_sample_count':len(d['samples']),'unique_acronym_count':len({s['acronym'] for s in d['samples']}),
      'unique_question_count':len({s['query_id'] for s in d['samples']}),'generation_count':sum(summary[g]['generation_count'] for g in ('A','B')),
      'samples_with_any_expansion_candidate':sum(any(r['metrics']['expansion_attempt_proxy'] for g in s['groups'].values() for r in g['runs']) for s in d['samples']),
      'human_labeled_count':0,'expansion_accuracy':None}
    summary['paired_run_outcomes']={}
    for key in ('parse_success','acronym_retained','expansion_attempt_proxy','acronym_expansion_cooccurrence_proxy'):
        counts=collections.Counter()
        for s in d['samples']:
            for a,b in zip(s['groups']['A']['runs'],s['groups']['B']['runs']):
                va,vb=a['metrics'][key],b['metrics'][key]
                counts['both' if va and vb else 'A_only' if va else 'B_only' if vb else 'neither']+=1
        summary['paired_run_outcomes'][key]=dict(counts)
    d['summary']=summary
    p['analysis_definitions']={
      'main_denominator':'145 independent sample/run outputs per group, including parse failures as absence; rates among parsed outputs also recorded.',
      'parse_success':'Native regex Search\\](.*?)\\[ with DOTALL; strip; first 5. Success iff at least one final query and every final query nonempty. No fallback parser or repair.',
      'strict_native_envelope':'Supplement: entire output must be one or more [Search]nonempty-text segments followed by [StopSearch], with no other bracketed content.',
      'retention':'Target acronym with alphanumeric/underscore boundaries, case-insensitive and optional plural s. Not substring matching (RE does not match research). Exact original-case/form metric also retained.',
      'expansion_attempt_proxy':'Any literal contiguous phrase whose word initials align with target acronym; optional connector words; nested all-capital token may supply its letters. At least 2 non-connector words. Do not cross comma/semicolon/parenthesis clauses or include target acronym in the candidate. Prefer minimal nested spans. No acronym/full-form dictionary or model judge.',
      'cooccurrence_proxy':'At least one final query contains both retained target acronym and a detected literal candidate expansion.',
      'candidate_limitations':'Lexical proxy can miss noninitial or unusual full forms and can flag coincidental initials. Presence does not establish model intent or correctness. Candidates already in original question are separately marked; copying also counts in the broad occurrence-based attempt proxy.',
      'duplicate':'Within the same final query list only: lowercase alphanumeric token sequence after punctuation/whitespace normalization. Do not deduplicate before metrics.',
      'near_duplicate':'Different normalized query strings with token-set Jaccard >=0.85; word-order changes may qualify. Descriptive, no semantic judge.',
      'candidate_collapsed_duplicate':'Replace detected candidate phrase with target acronym, normalize target plural/case, collapse consecutive identical acronym tokens. Different original queries equal after this rewrite are flagged only; queries are never actually rewritten. Cannot establish causality or semantic equivalence without human gold.',
      'wrong_suspicious':'Only actual generated candidate spans and context listed; correctness remains null. No automatic WRONG labels.',
      'human_judgment':'All gold/judgment/comparison/notes fields left empty.'}
    p['render_script_sha256']=sha(Path(__file__))
    d['status']='complete'; save(d)
    a,b=summary['A'],summary['B']; c=summary['combined']
    lines=['# ACRONYM_EXPANSION_PROBE_002','',
      '**独立离线 A/B 实验。所有 expansion 均仅作为模型实际产生的待审核词组；人工审核前不计算、不宣称 expansion accuracy。**','',
      '## 数据与隔离','',
      f"直接复用 `{p['source_path']}` 的 {c['acronym_sample_count']} 个样本、{c['unique_acronym_count']} 种缩写，涉及 {c['unique_question_count']} 个原始问题。每样本 A/B 各 5 次，共 {c['generation_count']} 次真实独立生成。",
      '', '只投影 query_id、original_question、acronym、原始 mention 和已有中文翻译；001 的模型输出、候选答案和人工标签不进入本次 prompt 或检测规则。未重新筛选样本，未读取 GT title/paper、miss audit 或搜索结果。同一问题中的多个 acronym 仍单独计样本，以不同 seed 独立生成，未复用其他样本输出。',
      '', '仅加载指定本地 Crawler；禁止 Internet socket/DNS，开启 HF offline 和 local_files_only。没有执行 Serper、Selector、Expand、真实搜索或 PaSa 主流程；原生文件只读解析。未修改 baseline、Query Planner、checkpoint 或主流程，未写 SFT 数据，未提交 Git。',
      '', '## 原生 A/B 设置','', 'A 组原始 prompt：','', '```text',p['native_prompt_template'],'```','',
      'B 组 = A 组的完整 prompt + 一个换行 + 以下指令；没有添加目标 acronym 参数、JSON 要求、planner、facet 或 constraint 机制：','', '```text',p['B_instruction'],'```','',
      f"原生解析逻辑从 `paper_agent.py` 的 AST 读取并按原方式使用：`re.findall({p['native_search_regex']!r}, raw_output, flags=re.DOTALL)`，逐条 strip 后取前 {p['native_search_query_limit']} 条。保留全部匹配、原始文本和被截去部分，不补全缺失标记、不修复格式、不去重、不执行任何 query。",'',
      f"Checkpoint：`{p['checkpoint']}`。文件 SHA-256、prompt、chat template 后的输入、每次 seed、token IDs、软件版本和原生代码指纹保存在 JSON provenance。",'',
      '沿用 checkpoint generation config：do_sample=true，temperature=0.7，top_p=0.8，top_k=20，repetition_penalty=1.05；max_new_tokens=512。use_cache=true 仅启用 KV 缓存。batch_size=1，与原生单问题生成方式一致；原始问题不截断。', '',
      'seed = 2026091300 + sample_index × 10 + run_number − 1。每个样本的 5 个 seed 不同；145 个样本/轮次 seed 互不相同；同一轮 A/B 配对使用相同 seed。两个条件都重新调用 generate，无聊天历史，也不将 A 输出提供给 B。', '',
      f"运行于 {p['gpu']}（物理 GPU 1），torch {p['torch']}，transformers {p['transformers']}；UTC {p['started_utc']} 至 {p['finished_utc']}。保护文件前后指纹一致：{p['protected_files_before']==p['protected_files_after']}。", '',
      '## 指标定义与限制','',
      '- 主统计单位是 sample × run，每组分母固定 145；正常解析指原生解析得到至少 1 条 query 且最终列表无空 query。格式失败不会从分母消失。另报告整个输出严格匹配 `[Search]…[StopSearch]` 的比例。',
      '- Retention：最终前 5 条 query 至少一条包含目标缩写，忽略大小写并允许复数 s，采用完整词边界。另给出原文大小写/词形的严格匹配。',
      '- Expansion Attempt：**疑似展开的词面代理率**，检测模型实际输出中首字母与缩写匹配的连续词组；允许跳过连接词、混合连字符及内嵌大写缩写。没有预置任何标准全称。只保留原文真实出现的候选子串与位置，不补写全称。',
      '- 这只是可复现的候选检测：会漏掉不按首字母构成的全称，也可能把恰好首字母匹配的普通词组列为候选。不能把候选率当作确认的展开意图或正确率。来自原始 question 的已有全称也计入宽口径，并单独标记来源；不是新增知识的证明。',
      '- 本次实际存在这种歧义：`learning in language models`、`limitations in language models` 在跳过连接词 in 后也会匹配 LLM。它们是原始输出中的真实词组，但模型没有明确声称这是 LLM 的全称。保留这些命中供审核，不把它们自动判为“错误展开”，也不删除后重新选择统计规则。下文所有 attempt / 共现数字必须按此代理口径解读。',
      '- 共现：同一条最终 query 同时含目标缩写和疑似展开。不同 query 分别出现不算共现。',
      '- 重复：同一 run 的最终列表内，先比较规范化 token 序列完全相同，再列出 token-set Jaccard ≥0.85 的近重复；候选全称替换回缩写后相同的 query 对另列为复核线索，不能据此断言 B 指令导致重复或两种表达语义等价。',
      '- 多 acronym 的同一个 original question 会被重复计入样本，LLM 样本较多；结果是本次固定语料、prompt 和 5 次采样的描述性比较，不提供总体可靠性或准确率推断。', '',
      '## A/B 自动统计','', '| 指标 | A | B |','|---|---:|---:|']
    for key in LABELS: lines.append(f"| {LABELS[key]} | {rate(a,key)} | {rate(b,key)} |")
    lines += [f"| 最终 query 总数 | {a['final_query_count']} | {b['final_query_count']} |",f"| 出现疑似展开的样本数 | {a['expansion_attempt_proxy']['sample_count']}/29 | {b['expansion_attempt_proxy']['sample_count']}/29 |",f"| 达上限且未 EOS 的输出 | {a['truncated_generations']} | {b['truncated_generations']} |",f"| 空 query 数 | {a['empty_queries']} | {b['empty_queries']} |",f"| 未被原生正则提取的 [Search] 标记数 | {a['unparsed_literal_search_markers']} | {b['unparsed_literal_search_markers']} |",'',
      f"合并 A/B 后共有 {c['samples_with_any_expansion_candidate']}/29 个样本至少产生一次疑似展开。仅以成功解析输出为分母的补充指标保存在 JSON 的 summary.A/B.rates_among_parsed_runs。",'',
      '### 配对运行的指标变化','', '| 指标 | A/B 均出现 | 仅 A | 仅 B | 均未出现 |','|---|---:|---:|---:|---:|']
    for key,counts in summary['paired_run_outcomes'].items():
        lines.append(f"| {LABELS[key]} | {counts.get('both',0)} | {counts.get('A_only',0)} | {counts.get('B_only',0)} | {counts.get('neither',0)} |")
    lines += ['', '这些差异只表示指标是否出现，不是人工表中“更好/相同/更差”的自动标签。', '',
      '### 每样本 5 次结果','', '五位字符串从左到右对应 Run 1–5：1=该指标出现，0=未出现；“展开”和“共现”均是疑似词面指标。', '',
      '| Sample | A 解析 | B 解析 | A 保留 | B 保留 | A 展开 | B 展开 | A 共现 | B 共现 |','|---|---|---|---|---|---|---|---|---|']
    for s in d['samples']:
        values=[bits(s['groups'][g]['runs'],k) for k in ('parse_success','acronym_retained','expansion_attempt_proxy','acronym_expansion_cooccurrence_proxy') for g in ('A','B')]
        lines.append('| '+s['sample_id']+' | '+' | '.join(values)+' |')
    lines += ['', '## 模型实际产生的疑似展开：待人工审核','', '只列出生成 query 中实际出现的候选词组；此表不预填 Gold，也不自动判正确、错误或可疑程度。疑似表示词面检测命中。问题本身已有的词组用“原问题已有”标记。', '',
      '| Sample | 组 | 实际候选词组 | 原问题已有 | 位置（Run / Query，1 起） |','|---|---|---|---|---|']
    candidate_rows=[]
    for s in d['samples']:
        for group,g in s['groups'].items():
            seen={}
            for r in g['runs']:
                for q in r['metrics']['per_query']:
                    for candidate in q['expansion_candidates']:
                        key=candidate['text']
                        seen.setdefault(key,{'in_original':candidate['also_in_original_question'],'positions':[]})['positions'].append(f"R{r['run']}/Q{q['query_index']+1}")
            for text,info in seen.items():
                candidate_rows.append(f"| {s['sample_id']} | {group} | {md(text)} | {'是' if info['in_original'] else '否'} | {', '.join(info['positions'])} |")
    lines.extend(candidate_rows or ['| — | — | 未检出 | — | — |'])
    lines += ['', '## 格式与重复明细','']
    issues=0
    for s in d['samples']:
        for group,g in s['groups'].items():
            for r in g['runs']:
                m=r['metrics'];labels=[]
                if not m['parse_success']: labels.append('原生解析失败或空 query')
                if not m['strict_native_envelope']: labels.append('整个输出不满足严格原生格式')
                if m['non_search_action_marker_present']: labels.append('含非 Search 动作标记（未执行）')
                if m['query_cap_applied']: labels.append(f"生成 {m['all_generated_query_count']} 条，按原生上限保留前 5 条")
                if not r['ended_with_eos']: labels.append('生成未以 EOS 结束')
                for k,label in [('normalized_duplicate_pairs','规范化重复'),('near_duplicate_pairs','近重复'),('candidate_collapsed_duplicate_pairs','候选替换后的重复')]:
                    if m[k]: labels.append(f"{label} query 索引（0 起）={json.dumps(m[k])}")
                if labels:
                    issues+=1
                    lines += [f"- {s['sample_id']} / {group} / Run {r['run']}：{'；'.join(labels)}。"]
    if not issues: lines.append('未检测到上述格式或重复问题。')
    lines += ['', '## 文件与人工审核','',
      '- `ACRONYM_EXPANSION_PROBE_002.json`：全部 prompt、seed、原始输出、所有/最终 queries、候选证据、解析及重复指标、provenance。',
      '- `ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW.md`：29 个样本及中文翻译，A/B 各 5 次全部 queries；人工 gold、组内判断、组间比较和 Notes 留空。',
      '- 独立脚本位于 `acronym_expansion_probe_002/`；检测规则在推理前固定，哈希已核对。没有进行重试挑选或修改 prompt 后重新采样。', '',
      '## 最后总结','',
      f"- A/B Search query 解析率：A {rate(a,'parse_success')}；B {rate(b,'parse_success')}。",
      f"- Acronym retention rate：A {rate(a,'acronym_retained')}；B {rate(b,'acronym_retained')}。",
      f"- Expansion attempt rate（疑似词面代理）：A {rate(a,'expansion_attempt_proxy')}；B {rate(b,'expansion_attempt_proxy')}。",
      f"- Acronym + full-form 共现率（疑似词面代理）：A {rate(a,'acronym_expansion_cooccurrence_proxy')}；B {rate(b,'acronym_expansion_cooccurrence_proxy')}。",
      f"- 产生疑似 expansion 的样本：A {a['expansion_attempt_proxy']['sample_count']}/29；B {b['expansion_attempt_proxy']['sample_count']}/29；A/B 合并 {c['samples_with_any_expansion_candidate']}/29。",
      f"- 格式/重复：严格格式 A {rate(a,'strict_native_envelope')}、B {rate(b,'strict_native_envelope')}；规范化重复输出 A {a['any_normalized_duplicate']['run_count']}、B {b['any_normalized_duplicate']['run_count']}；近重复 A {a['any_near_duplicate']['run_count']}、B {b['any_near_duplicate']['run_count']}；候选替换后重复 A {a['any_candidate_collapsed_duplicate']['run_count']}、B {b['any_candidate_collapsed_duplicate']['run_count']}。",'']
    (ROOT/'ACRONYM_EXPANSION_PROBE_002.md').write_text('\n'.join(lines))
    manual=['# ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW','',
      '人工审核前不宣称 expansion accuracy。中文翻译沿用 001，不输入 Crawler。每条 query 原样展示、不去重；主指标只使用原生前 5 条，超出部分另列。疑似展开检测结果仅供定位原文，不是标准答案。', '']
    for s in d['samples']:
        manual += ['---','',f"## {s['sample_id']}",'',f"Query ID: {s['query_id']}",'','Original Question:',s['original_question'],'','中文翻译:',s['question_zh'],'',f"Acronym: {s['acronym']}",f"原始写法: {', '.join(dict.fromkeys(m['text'] for m in s['mentions']))}",'']
        for group,g in s['groups'].items():
            manual += [f'### {group}组','']
            for r in g['runs']:
                manual += [f"#### Run {r['run']}",'',f"Seed: {r['seed']}",'','Search Queries（原生前 5 条）:','']
                if r['search_queries']:
                    manual += [f'{i}. {query}' for i,query in enumerate(r['search_queries'],1)]
                else: manual += ['[未解析到 Search query]']
                if r['discarded_queries_by_native_cap']:
                    manual += ['','超出原生 5 条上限的已解析 Search Queries（不进入主指标）:','']
                    manual += [f'{i}. {query}' for i,query in enumerate(r['discarded_queries_by_native_cap'],6)]
                cs=[f"Query {q['query_index']+1}: {c['text']}" for q in r['metrics']['per_query'] for c in q['expansion_candidates']]
                manual += ['','疑似展开词面命中（未判正确/错误）: '+('；'.join(cs) if cs else '未检出；不代表确认未展开'),'','<details>','<summary>原始输出与解析状态</summary>','','```text',r['raw_output'],'```','',
                  f"Native parse success: {r['metrics']['parse_success']}; strict format: {r['metrics']['strict_native_envelope']}; EOS: {r['ended_with_eos']}",'','</details>','']
        manual += ['Gold Expansion:','[人工填写]','','A组判断：','','- [ ] 正确展开','- [ ] 错误展开','- [ ] 未展开','- [ ] 不确定','','B组判断：','','- [ ] 正确展开','- [ ] 错误展开','- [ ] 未展开','- [ ] 不确定','','B相比A：','','- [ ] 更好','- [ ] 相同','- [ ] 更差','','Notes:','[人工填写]','']
    (ROOT/'ACRONYM_EXPANSION_PROBE_002_MANUAL_REVIEW.md').write_text('\n'.join(manual))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
