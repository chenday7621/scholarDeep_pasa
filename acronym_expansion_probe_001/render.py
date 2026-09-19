"""Descriptive consistency statistics only; no automated gold judge."""
import collections
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from probe import OUT, ROOT, save

ZH = {
 'Q5':'应用 RLHF 来解决图像和视频描述中幻觉问题的论文。',
 'Q9':'展示利用 LLM 对搜索结果进行排序的研究。',
 'Q11':'给出所有采用 MoE 架构的视觉 LLM 模型。',
 'Q13':'提供表明 LLMs 的自我纠正不会提升其性能的论文。',
 'Q14':'寻找使用 LLMs 或基于 LLM 的智能体，为多篇学术文献自动撰写综述或摘要的论文。',
 'Q15':'提供声称强化学习可能对经过监督微调的 LLMs 的性能产生负面影响的论文。',
 'Q17':'提供解释为什么 LLMs 的上下文学习性能无法在 NER、RE 和 EE 等信息抽取任务上超越经过监督微调的小语言模型的论文。',
 'Q18':'LLMs 能否以零样本方式检测由 LLM 生成的文本？它们是否比经过监督微调的小型分类模型表现更好？请提供相关论文。',
 'Q19':'提供关于在词表水印设置下保护 LLMs 生成质量的方法的论文。',
 'Q20':'寻找支持以下观点的论文：知识丰富的 LLMs 具有足够的归纳能力，可以分析多篇论文之间的关系，并系统地撰写关于这些论文的综述。',
 'Q21':'搜索与大语言模型有关的论文，展示同一提示搭配不同回答如何提升 SFT 模型的性能。',
 'Q28':'展示中等难度的代码评测数据集，应比 HumanEval 和 MBPP 更难，但比 code_contests 更容易。',
 'Q29':'关于教 llms 进行数学证明并解决 IMO 级别数学问题的研究。',
 'Q30':'我想寻找 LLM 研究领域中关于测试时训练的论文。',
 'Q31':'面向大规模视觉语言模型的 DPO 训练。',
 'Q34':'展示利用 3D AIGC 基础模型进展开展 3d 场景理解的研究。',
 'Q35':'给出关于 LLM 量化预训练的论文。',
 'Q37':'给出一些表明 LLM 智能体能够进行日程规划的论文。',
 'Q40':'能否列出展示量化感知训练（QAT）优势的研究？这种训练可以使模型为低比特权重学习到更好的表示。',
 'Q41':'使用合成数据来扩大 sft 数据的规模。',
 'Q43':'AI 用于科学的论文，尤其是蛋白质设计和抗体设计中的 DPO。',
 'Q47':'如何对金融任务中的 LLM 智能体进行评估和基准测试？请注意，我指的是智能体。',
 'Q49':'能否帮我寻找使用大型视觉语言模型作为智能体自动玩 PC 游戏的研究论文？',
}

def norm(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.sub(r'\s+', ' ', re.sub(r'[-‐‑‒–—−]', ' ', text)).strip().rstrip('.').strip()

def md(text):
    return str(text).replace('|','\\|').replace('\n','<br>')

def show(text):
    return '(abstain: expansion="")' if text == '' else '(unparseable)' if text is None else text

def main():
    d = json.loads(OUT.read_text())
    assert d['status'] in ('generations_complete', 'complete')
    for s in d['samples']:
        assert len(s['runs']) == 5 and [r['run'] for r in s['runs']] == [1,2,3,4,5]
        for r in s['runs']:
            objects = []
            for m in re.finditer(r'\{', r['raw_output']):
                try:
                    obj, _ = json.JSONDecoder().raw_decode(r['raw_output'][m.start():])
                    if isinstance(obj, dict) and 'expansion' in obj: objects.append(obj)
                except json.JSONDecodeError:
                    pass
            r['embedded_json_objects'] = objects
            r['target_json_objects'] = [o for o in objects if o.get('acronym') == s['acronym']]
            r['multiple_json_objects'] = len(objects)>1
            r['crawler_action_markers_present'] = bool(re.search(r'\[(?:Expand|StopExpand|Search)\]', r['raw_output']))
            r['any_target_object_ambiguous_true'] = any(o.get('ambiguous') is True for o in r['target_json_objects'])
            r['any_target_object_empty_expansion'] = any(o.get('expansion') == '' for o in r['target_json_objects'])
        s['question_zh'] = ZH[s['query_id']]
        expansions = [r['parsed_expansion'] for r in s['runs']]
        votes = collections.Counter(norm(x) for x in expansions if x is not None)
        exact = collections.Counter(x for x in expansions if x is not None)
        top = max(votes.values(), default=0)
        winners = sorted(k for k,v in votes.items() if v == top)
        representatives = {k:next(x for x in expansions if x is not None and norm(x)==k) for k in votes}
        s.update(majority_expansion=representatives[winners[0]] if top>=3 else None,
                 modal_expansions=[representatives[k] for k in winners], majority_exists=top>=3,
                 agreement_count=top, agreement_rate=top/5, agreement_fraction=f'{top}/5',
                 exact_agreement_count=max(exact.values(), default=0),
                 expansion_variants=[{'normalized_expansion':k,'representative':representatives[k], 'count':v, 'raw_forms':list(dict.fromkeys(x for x in expansions if x is not None and norm(x)==k))} for k,v in votes.most_common()],
                 different_expansions=len(votes)>1,
                 confidence_distribution=dict(collections.Counter(r['confidence'] or 'missing_or_invalid' for r in s['runs'])),
                 confidence_stable=len({r['confidence'] for r in s['runs']})==1 and s['runs'][0]['confidence'] is not None,
                 ambiguous_true_runs=sum(r['ambiguous'] is True for r in s['runs']),
                 abstain_runs=sum(x is not None and not x.strip() for x in expansions),
                 unparseable_runs=sum(x is None for x in expansions),
                 human_gold_expansion=None, human_judgment=None)
        keys = [k for k in votes if k]
        s['lexically_divergent_pairs'] = [{'a':representatives[a], 'b':representatives[b]} for i,a in enumerate(keys) for b in keys[i+1:] if difflib.SequenceMatcher(None,a,b).ratio()<.5]
        s['observed_target_expansions_including_rejected_multiobject_runs'] = list(dict.fromkeys(o['expansion'] for r in s['runs'] for o in r['target_json_objects'] if isinstance(o.get('expansion'),str)))
        s['raw_output_agreement_count'] = max(collections.Counter(r['raw_output'] for r in s['runs']).values())
        flags = []
        if s['different_expansions']: flags.append('multiple_normalized_expansions_review_required')
        if s['lexically_divergent_pairs']: flags.append('low_lexical_similarity_not_a_semantic_judgment')
        if any(r['schema_errors'] for r in s['runs']): flags.append('json_or_schema_noncompliance')
        if any(r['multiple_json_objects'] for r in s['runs']): flags.append('multiple_json_objects_no_unique_answer')
        if any(r['crawler_action_markers_present'] for r in s['runs']): flags.append('crawler_action_syntax_generated_not_executed')
        if any(x is not None and norm(x)==norm(s['acronym']) for x in expansions): flags.append('expansion_repeats_acronym')
        if any(x and (len(x)>250 or re.search(r'<tool|search\(|https?://',x)) for x in expansions): flags.append('possible_task_leakage_or_overlong_expansion')
        s['review_flags'] = flags
    samples=d['samples']; runs=[r for s in samples for r in s['runs']]
    summary = {
        'question_count':len(d['questions_scanned']), 'questions_with_samples':len({s['query_id'] for s in samples}),
        'acronym_sample_count':len(samples), 'unique_acronym_count':len({s['acronym'] for s in samples}),
        'generation_count':len(runs), 'agreement_5_of_5':sum(s['agreement_count']==5 for s in samples),
        'agreement_4_of_5':sum(s['agreement_count']==4 for s in samples),
        'agreement_le_3_of_5':sum(s['agreement_count']<=3 for s in samples),
        'exact_agreement_5_of_5':sum(s['exact_agreement_count']==5 for s in samples),
        'ambiguous_true_run_count':sum(r['ambiguous'] is True for r in runs),
        'samples_with_any_ambiguous_true':sum(s['ambiguous_true_runs']>0 for s in samples),
        'empty_expansion_run_count':sum(s['abstain_runs'] for s in samples),
        'samples_with_any_empty_expansion':sum(s['abstain_runs']>0 for s in samples),
        'unparseable_run_count':sum(s['unparseable_runs'] for s in samples),
        'schema_compliant_run_count':sum(not r['schema_errors'] for r in runs),
        'confidence_distribution':{k:sum(r['confidence']==k for r in runs) for k in ('high','medium','low',None)},
        'confidence_stable_sample_count':sum(s['confidence_stable'] for s in samples),
        'samples_with_multiple_expansions':sum(s['different_expansions'] for s in samples),
        'samples_with_lexically_divergent_expansions':sum(bool(s['lexically_divergent_pairs']) for s in samples),
        'strict_json_only_run_count':sum(r['parse_mode']=='strict_json' for r in runs),
        'recovered_single_object_run_count':sum(r['parse_mode']=='extracted_json_with_extra_text' for r in runs),
        'multiple_json_object_run_count':sum(r['multiple_json_objects'] for r in runs),
        'crawler_action_marker_run_count':sum(r['crawler_action_markers_present'] for r in runs),
        'runs_with_any_target_object_ambiguous_true_including_rejected_multiobject':sum(r['any_target_object_ambiguous_true'] for r in runs),
        'samples_with_any_target_object_ambiguous_true_including_rejected_multiobject':sum(any(r['any_target_object_ambiguous_true'] for r in s['runs']) for s in samples),
        'runs_with_any_target_object_empty_expansion_including_rejected_multiobject':sum(r['any_target_object_empty_expansion'] for r in runs),
        'samples_with_any_target_object_empty_expansion_including_rejected_multiobject':sum(any(r['any_target_object_empty_expansion'] for r in s['runs']) for s in samples),
        'samples_with_all_five_parseable_expansions':sum(s['unparseable_runs']==0 for s in samples),
        'agreement_support_histogram':dict(collections.Counter(s['agreement_fraction'] for s in samples)),
        'samples_with_zero_parseable_expansions':sum(s['unparseable_runs']==5 for s in samples),
        'accuracy':None, 'human_labeled_sample_count':0,
    }
    summary['confidence_distribution']['missing_or_invalid'] = summary['confidence_distribution'].pop(None)
    d['summary']=summary; d['status']='complete'
    d['provenance']['render_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    d['provenance']['divergence_rule']='SequenceMatcher ratio <0.5 between normalized nonempty expansions flags lexical divergence only; semantic difference requires human review.'
    save(d)
    lines=['# ACRONYM_EXPANSION_PROBE_001', '', '**仅评估 CONSISTENCY（模型输出稳定性）；ACCURACY 未评估。5 次一致不等于正确。人工 gold 与判断全部留空。**', '',
      f"**主要发现：145/145 次输出都包含 Crawler 的 `[Expand]` 动作语法，严格 JSON 合规为 {summary['schema_compliant_run_count']}/145。脚本仅记录字符串，没有执行 Expand。仅 {summary['recovered_single_object_run_count']} 次可从额外文本中恢复单个 JSON 对象，另 {summary['multiple_json_object_run_count']} 次输出多个对象，不能选取某个答案冒充唯一结果。当前实验首先揭示了该 prompt 下的任务/格式遵从问题，不能充分量化全称的语义稳定性。**", '',
      '## 数据与隔离', '',
      f"- 来源：`{d['provenance']['source_path']}`。仅解码每行原始 question 字符串，Q0–Q49 按原始行序编号；未解码 GT 字段，未读取标题、论文、miss audit、搜索结果或既有人工判断。",
      f"- 扫描 50 个问题；{summary['questions_with_samples']} 个问题中得到 **{len(samples)} 个问题 × 缩写样本、{summary['unique_acronym_count']} 种缩写**。同一问题的复数/大小写形式合并，原文、mention 和位置保留。不同问题独立计样本。",
      '- 通用提取：至少两个全大写字母（支持复数 s）；或长度 2–5、至少两个大写字母且大写比例 ≥50% 的混合大小写词。再用本语料已发现形式识别小写/复数别名（llms、sft）。没有缩写白名单，也没有从全称反向制造样本。',
      '- 单个大写字母、普通句首/标题词、数字、字母数字标识与维度记号，以及长驼峰/下划线名称单独过滤。完整排除记录在 JSON 的 excluded_candidates 中。没有发现年份；数据中的数字记号是 3d/3D。',
      '- MBPP、IMO 满足全大写 initialism 规则，因此保留；名称所属类型不是排除全部缩写的依据。HotPotQA 不拆出 QA，HumanEval 和 code_contests 不作为整体缩写。此规则针对明显缩写，不能保证发现所有隐含或仅以小写出现的缩写。',
      '- Q40 原文已经给出 QAT 的全称，仍原样保留。它考察读取现有上下文，与没有直接给出全称的样本难度不同。',
      '- 未联网、未调用外部 LLM/API，未运行 Serper / Selector / Expand 或完整 PaSa。未修改 baseline、Query Planner、主流程，未写 SFT 数据，未提交 Git。', '',
      '### 非普通大小写词的过滤明细', '', '| Query | Token | 过滤原因 |','|---|---|---|']
    for e in d['excluded_candidates']:
        if not e['reason'].startswith('single_'): lines.append(f"| {e['query_id']} | {md(e['token'])} | {md(e['reason'])} |")
    lines += ['', '## 推理条件', '', f"- 固定 checkpoint：`{d['provenance']['checkpoint']}`；各模型/分词器文件 SHA-256 保存在 JSON provenance。",
      '- 使用 checkpoint 原采样配置：do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05。每次最多 512 个新 token；use_cache=true 仅启用 KV 缓存。',
      '- 5 次分属 5 轮调用；批大小 8，问题间无会话历史。同一样本的完整 prompt 与原始 question 不变；每批使用不同且已记录的随机 seed。每条序列单独采样，未通过 beam search、复制答案或多数表决反馈生成。',
      '- 通过原生 chat template 格式化；不截断 question，不使用结构约束解码或答案修复。原始输出、含特殊 token 的输出、token IDs、解析状态和全部采样配置均保留。',
      f"- 运行：{d['provenance']['gpu']}（物理 GPU 1），torch {d['provenance']['torch']}，transformers {d['provenance']['transformers']}。开始 {d['provenance']['started_utc']}；结束 {d['provenance']['finished_utc']}。",
      '- HF offline / local_files_only，并使用 Python audit hook 禁止 Internet socket 和 DNS。人工表中的中文翻译仅翻译 question，保留缩写原写法，不输入 Crawler、不生成 gold。', '', '### 固定 Prompt', '', '```text',d['provenance']['prompt_template'],'```', '',
      '## CONSISTENCY 统计', '',
      '- 一致率 = 同一规范化 expansion 的最大票数 / 5；仅规范化大小写、空白、连字符和末尾句点，不合并语义近似答案。另保留严格字符串一致性。3 票以上才称 majority；否则 majority=null 并列出众数。',
      '- 空 expansion 是有效 abstain 投票；无法解析不视为 abstain、不投票，分母仍为 5。ambiguous 与 unknown 可以重叠；unknown 在这里仅指模型 expansion=""，不是人工 UNKNOWN 标签。', '',
      f"- 以下 expansion 统计采用宽松恢复的单对象字段；严格 JSON-only 口径下没有有效 expansion。{summary['samples_with_zero_parseable_expansions']} 个样本的 5 次输出均无可接受的唯一 expansion，记为 0/5 可用同答案支持；这不表示已证实它们产生 5 个不同全称。≤3/5 桶包含此类不可测样本。", '',
      '| 指标 | 数量 | 比例 / 分母 |','|---|---:|---|']
    for label,key,den in [('5/5 一致','agreement_5_of_5',len(samples)),('4/5 一致','agreement_4_of_5',len(samples)),('≤3/5 一致','agreement_le_3_of_5',len(samples)),('严格字符串 5/5','exact_agreement_5_of_5',len(samples)),('ambiguous=true 输出','ambiguous_true_run_count',len(runs)),('出现 ambiguous 的样本','samples_with_any_ambiguous_true',len(samples)),('空 expansion 输出','empty_expansion_run_count',len(runs)),('出现空 expansion 的样本','samples_with_any_empty_expansion',len(samples)),('无法解析输出','unparseable_run_count',len(runs)),('JSON 与 schema 合规输出','schema_compliant_run_count',len(runs)),('confidence 稳定样本','confidence_stable_sample_count',len(samples))]:
        lines.append(f'| {label} | {summary[key]} | {summary[key]/den:.1%} ({den}) |')
    lines += ['', f"Confidence 分布（145 次输出）：{json.dumps(summary['confidence_distribution'],ensure_ascii=False)}。", '', f"可用同答案支持票数细分：{json.dumps(summary['agreement_support_histogram'],ensure_ascii=False)}。没有任何样本的 5 次输出均可解析；因此 5 次语义一致性均不能完整评估。", '', '### 每种缩写的稳定性', '', '| Acronym | 样本数 | 5/5 | 4/5 | ≤3/5 | 跨上下文出现的展开（非 gold） |','|---|---:|---:|---:|---:|---|']
    for a in sorted({s['acronym'] for s in samples}):
        group=[s for s in samples if s['acronym']==a]
        variants=list(dict.fromkeys(v for s in group for v in s['observed_target_expansions_including_rejected_multiobject_runs']))
        lines.append(f"| {a} | {len(group)} | {sum(s['agreement_count']==5 for s in group)} | {sum(s['agreement_count']==4 for s in group)} | {sum(s['agreement_count']<=3 for s in group)} | {md('; '.join(map(show,variants)) or '无可恢复的 JSON expansion')} |")
    stable=[s['sample_id'] for s in samples if s['agreement_count']==5]
    lines += ['', '本轮最稳定（5/5）的样本：'+(', '.join(stable) or '无')+'。此排名不代表正确率。', '', '### 多种展开、abstain 与可疑输出', '']
    variable=[s for s in samples if s['different_expansions']]
    if not variable: lines.append('未出现同一样本内的多种规范化 expansion。')
    lines.extend(['上句仅限可恢复单对象的计票口径，不能理解为原始输出没有冲突；上表的展开列也包含下述被拒收多对象输出中的观察值。', ''])
    for s in samples:
        for r in s['runs']:
            if r['multiple_json_objects']:
                lines.append(f"- 多对象原始输出 {s['sample_id']} Run {r['run']}："+'；'.join(f"{o.get('acronym')}: {show(o.get('expansion'))}, confidence={o.get('confidence')}, ambiguous={o.get('ambiguous')}" for o in r['embedded_json_objects'])+'。全部保存，不进入单答案一致率投票。')
    for s in variable:
        lines.append(f"- {s['sample_id']}："+'；'.join(f"{show(v['representative'])} ×{v['count']}" for v in s['expansion_variants'])+'。')
    abst=[f"{s['sample_id']} ({s['abstain_runs']}/5)" for s in samples if s['abstain_runs']]
    amb=[f"{s['sample_id']} ({s['ambiguous_true_runs']}/5)" for s in samples if s['ambiguous_true_runs']]
    lines += ['', 'Abstain 样本：'+(', '.join(abst) or '无')+'。', '', 'ambiguous=true 样本：'+(', '.join(amb) or '无')+'。', '',
      f"补充的原始观察口径（包括被拒收多对象输出，只要任一目标缩写对象命中即计该 run 一次）：ambiguous=true 出现于 {summary['runs_with_any_target_object_ambiguous_true_including_rejected_multiobject']} 次输出 / {summary['samples_with_any_target_object_ambiguous_true_including_rejected_multiobject']} 个样本；expansion=空 出现于 {summary['runs_with_any_target_object_empty_expansion_including_rejected_multiobject']} 次输出 / {summary['samples_with_any_target_object_empty_expansion_including_rejected_multiobject']} 个样本。这些计数不能替代唯一答案口径。", '',
      '明显需要人工复核的现象：Q9 Run 5、Q30 Run 2 对同一 LLM 同时给出 Large Language Model 和 Latent Logic Model；Q49 Run 5 的 reason 提及 personal computers，却输出空全称并标歧义。Q40 原文已提供全称，模型仍仅产生动作语法。这里指出输出冲突/任务偏离，不将任何候选全称自动判作 gold 或 WRONG。', '',
      '可疑性只作为人工复核线索：多种展开、展开仅重复缩写、JSON/schema 不合规、异常长度/工具泄漏；不自动判 WRONG。词面相似度 <0.5 的展开对另行记录，该指标不能证明语义完全不同。']
    flagged=[s for s in samples if s['review_flags']]
    lines.append('')
    for s in flagged: lines.append(f"- {s['sample_id']}：{', '.join(s['review_flags'])}。")
    if not flagged: lines.append('上述机械检查未发现明显格式或自相矛盾信号；这不能排除稳定地产生错误全称。')
    lines += ['', '### 全部样本', '', '| Sample | Majority Expansion | Agreement | Confidence（5 次） | Ambiguous /5 | Abstain /5 |','|---|---|---|---|---:|---:|']
    for s in samples: lines.append(f"| {s['sample_id']} | {md(show(s['majority_expansion']) if s['majority_exists'] else '无 ≥3 票多数答案')} | {s['agreement_fraction']} | {md(', '.join(str(r['confidence']) for r in s['runs']))} | {s['ambiguous_true_runs']} | {s['abstain_runs']} |")
    lines += ['', '## ACCURACY 与边界', '', 'ACCURACY = 未评估；人工 gold 数量为 0。没有让其他模型充当 gold judge，也没有用常识答案自动判分。请先填写人工审核表，再分别统计正确、错误、语境歧义和未知。', '', '仅 5 次采样估计本 prompt 和 checkpoint 下的局部稳定性；样本量小、LLM 重复出现，不应外推为通用缩写准确率。大小写/复数合并、词面过滤和不同上下文也会影响计数。高 confidence、5/5 一致或未标 ambiguous 都不证明正确。', '', '## 复现与文件', '', '- 独立脚本：`acronym_expansion_probe_001/probe.py`（prepare/run），`acronym_expansion_probe_001/render.py`（纯描述统计与审核表）。run 拒绝覆盖已存在的生成记录。', '- `ACRONYM_EXPANSION_PROBE_001.json`', '- `ACRONYM_EXPANSION_PROBE_001.md`', '- `ACRONYM_EXPANSION_MANUAL_REVIEW.md`', '']
    (ROOT/'ACRONYM_EXPANSION_PROBE_001.md').write_text('\n'.join(lines))
    manual=['# ACRONYM_EXPANSION_MANUAL_REVIEW', '', '仅用于人工审核。中文翻译不输入 Crawler，缩写保留原样。所有 Human Gold Expansion、Human Judgment 和 Notes 均留空。稳定性不等于正确性；建议按原始问题独立核对全称。', '']
    for s in samples:
        manual += ['---','',f"## {s['sample_id']}",'',f"Query ID: {s['query_id']}",'','Original Question:',s['original_question'],'','Question 中文翻译:',s['question_zh'],'',f"Acronym: {s['acronym']}",f"Original forms: {', '.join(dict.fromkeys(m['text'] for m in s['mentions']))}",'']
        for r in s['runs']:
            manual += [f"Run {r['run']}:",'','```text',r['raw_output'],'```',f"Parsed expansion: {show(r['parsed_expansion'])}",f"Parse: {r['parse_mode']}; schema errors: {json.dumps(r['schema_errors'])}",'']
            if r['multiple_json_objects']:
                manual += ['Multiple JSON objects (rejected as a unique answer):', '```json',json.dumps(r['embedded_json_objects'],ensure_ascii=False,indent=2),'```','']
        manual += [f"Majority Expansion: {show(s['majority_expansion']) if s['majority_exists'] else '无 ≥3 票多数答案'}", f"Modal candidate(s): {', '.join(map(show, s['modal_expansions'])) or '无可解析候选'}",f"Agreement Rate: {s['agreement_fraction']} ({s['agreement_rate']:.0%})",f"Crawler Confidence: {', '.join(str(r['confidence']) for r in s['runs'])}; stable={str(s['confidence_stable']).lower()}",'','Human Gold Expansion:','[人工填写]','','Human Judgment:','- [ ] CORRECT','- [ ] WRONG','- [ ] AMBIGUOUS','- [ ] UNKNOWN','','Notes:','[人工填写]','']
    (ROOT/'ACRONYM_EXPANSION_MANUAL_REVIEW.md').write_text('\n'.join(manual))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
