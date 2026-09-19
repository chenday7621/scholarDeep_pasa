"""Offline evaluation of saved query text. No search, embeddings, GT answers or model calls."""
import argparse
from collections import Counter,defaultdict
from itertools import combinations
import json
from pathlib import Path
import re
import statistics

ROOT=Path(__file__).resolve().parents[1]
STOP=set('a an the of in on for to by with and or as at from using use used papers paper research studies study works work show give find provide related list all some about me any that which how is are be can through according'.split())
ALIASES={
    r'large\s+language\s+models?':'llm',r'\bllms\b':'llm',
    r'large\s+vision[ -]language\s+models?':'lvlm',
    r'vision[ -]language\s+models?':'vlm',
    r'mixture\s+of\s+experts':'moe',
    r'reinforcement\s+learning\s+(?:with|from)\s+human\s+feedback':'rlhf',
    r'direct\s+preference\s+optimization':'dpo',
    r'quantization[ -]aware\s+training':'qat',
    r'supervised\s+fine[ -]?tun(?:ed|ing)':'sft',
    r'pre[ -]training':'pretraining',r'fine[ -]tuning':'finetuning',
}

def tokens(text):
    text=text.lower()
    # Long names first to avoid converting a longer model name prematurely.
    for pattern,repl in ALIASES.items():text=re.sub(pattern,repl,text)
    out=[]
    for w in re.findall(r'[a-z0-9]+',text):
        if w in STOP:continue
        if len(w)>4 and w.endswith('s') and not w.endswith(('ss','ics')):w=w[:-1]
        out.append(w)
    return set(out)

def covered(span,queries):
    required=tokens(span)
    return bool(required) and any(required<=tokens(q) for q in queries)

def diversity(queries):
    pairs=[]
    for (i,a),(j,b) in combinations(enumerate(queries,1),2):
        x,y=tokens(a),tokens(b)
        score=len(x&y)/len(x|y) if x|y else 1.0
        pairs.append({'a':i,'b':j,'content_token_jaccard':score})
    canonical=[' '.join(q.lower().split()) for q in queries]
    return {'query_count':len(queries),'exact_duplicates':len(canonical)-len(set(canonical)),
            'mean_pair_similarity':statistics.mean(x['content_token_jaccard'] for x in pairs) if pairs else None,
            'pairs_ge_0_8':sum(x['content_token_jaccard']>=.8 for x in pairs),'pair_count':len(pairs),'pairs':pairs,
            'mean_word_count':statistics.mean(len(q.split()) for q in queries) if queries else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',default=str(ROOT/'CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json'))
    ap.add_argument('--artifacts',default='/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0/run')
    ap.add_argument('--report',default=str(ROOT/'CONSTRAINT_QUERY_PLANNER_AUDIT.md'))
    a=ap.parse_args()
    data=json.loads(Path(a.results).read_text())
    repair_dir=Path(a.artifacts).parent/'repair'
    # Preserve every valid saved facet query even if another facet failed.
    # No text is synthesized to fill an unsuccessful slot.
    for i,row in enumerate(data['rows']):
        if row['generation_status']=='PASS':continue
        partial=[]
        for j,facet in enumerate(row['planned_facets'],1):
            f=repair_dir/f'{i:02d}_query_{j}.json'
            if f.exists():
                rec=json.loads(f.read_text())
                if rec['status']=='PASS':partial.append(dict(rec['parsed'],facet=facet['facet']))
        if partial:row['constraint_queries']=partial;row['generation_status']='PARTIAL'
    reference=json.loads(Path(__file__).with_name('reference_constraints.json').read_text())
    refs={x['query_id']:x['constraints'] for x in reference['rows']}
    notes_file=Path(__file__).with_name('manual_review.json')
    notes=json.loads(notes_file.read_text()) if notes_file.exists() else {}
    totals=Counter();cats=defaultdict(Counter);facet_counts=Counter();extraction_removed=[];stages=Counter()
    comparisons=[]
    for row in data['rows']:
        qid=row['query_id'];b=row['baseline_queries'];n=[x['query'] for x in row['constraint_queries']]
        for x in row['constraint_queries']:
            x['planned_sequence']=next(j for j,f in enumerate(row['planned_facets'],1) if f['facet']==x['facet'])
        bd,nd=diversity(b),diversity(n)
        ex=row['constraint_json'];ex_text=[v for value in ex.values() for v in (value if isinstance(value,list) else [value]) if v]
        checks=[]
        for c in refs[qid]:
            assert c['source_span'].lower() in row['user_question'].lower()
            record=dict(c,baseline_retained=covered(c['source_span'],b),planner_retained=covered(c['source_span'],n),extraction_retained=covered(c['source_span'],ex_text))
            checks.append(record)
            for key in ['baseline_retained','planner_retained','extraction_retained']:
                totals[key]+=record[key];cats[c['category']][key]+=record[key]
            totals['constraints']+=1;cats[c['category']]['constraints']+=1
        claims=[]
        for j,x in enumerate(row['constraint_queries'],1):
            facet_counts[x['facet']]+=1
            for field in x['covered_constraints']:
                value=ex.get(field,'');values=value if isinstance(value,list) else [value]
                supported=bool(values) and all(v and covered(v,[x['query']]) for v in values)
                claims.append({'query_sequence':j,'field':field,'lexically_supported':supported})
        row['automatic_audit']={'baseline_diversity':bd,'planner_diversity':nd,'reference_constraint_checks':checks,'self_reported_coverage_checks':claims,'coverage_definition':'Every normalized content token of a source span must occur in a single query; OR across queries. Lexical proxy, not semantic entailment.'}
        row['manual_review']=notes.get(qid,{'status':'PENDING'})
        comparisons.append((row,bd,nd,checks))
    for f in Path(a.artifacts).glob('[0-9][0-9]_*.json'):
        r=json.loads(f.read_text());stages[r['stage']+'_records']+=1;stages[r['stage']+'_pass']+=r['status']=='PASS';stages[r['stage']+'_attempts']+=len(r['attempts'])
        for attempt in r['attempts']:
            for item in attempt.get('rejected_ungrounded_extractions',[]):extraction_removed.append(dict(item,query_id=r['query_id'],attempt=attempt['attempt']))
    recovery_records=[]
    for f in repair_dir.glob('[0-9][0-9]_*.json'):
        r=json.loads(f.read_text());recovery_records.append({'path':str(f),'query_id':r['query_id'],'stage':r['stage'],'status':r['status'],'attempts':len(r['attempts'])})
        for attempt in r['attempts']:
            for item in attempt.get('rejected_ungrounded_extractions',[]):extraction_removed.append(dict(item,query_id=r['query_id'],attempt=attempt['attempt'],source='recovery'))
    aggregate_recovery={'stage_records':len(recovery_records),'attempts':sum(x['attempts'] for x in recovery_records),'failed_records':sum(x['status']!='PASS' for x in recovery_records),'records':recovery_records}
    aggregate={}
    for name,pos in [('baseline',1),('planner',2)]:
        ds=[v[pos] for v in comparisons]
        aggregate[name]={'queries':sum(x['query_count'] for x in ds),'exact_duplicates':sum(x['exact_duplicates'] for x in ds),'mean_pair_similarity_macro':statistics.mean(x['mean_pair_similarity'] for x in ds if x['mean_pair_similarity'] is not None),'pairs_ge_0_8':sum(x['pairs_ge_0_8'] for x in ds),'pair_count':sum(x['pair_count'] for x in ds),'mean_word_count':statistics.mean(x['mean_word_count'] for x in ds if x['mean_word_count'] is not None)}
    paired=[v for v in comparisons if v[0]['generation_status']=='PASS']
    aggregate['paired_success_only']={'queries_compared':len(paired),
       'baseline_mean_pair_similarity':statistics.mean(x[1]['mean_pair_similarity'] for x in paired) if paired else None,
       'planner_mean_pair_similarity':statistics.mean(x[2]['mean_pair_similarity'] for x in paired) if paired else None}
    for i,row in enumerate(data['rows']):
        row['stage_provenance']={}
        for stage in ['extract','facets','generate']:
            f=Path(a.artifacts)/f'{i:02d}_{stage}.json'
            if f.exists():
                r=json.loads(f.read_text());row['stage_provenance'][stage]={'path':str(f),'status':r['status'],'attempts':len(r['attempts']),'last_error':r['attempts'][-1]['validation_error']}
            else:row['stage_provenance'][stage]={'status':'SKIPPED_DEPENDENCY_FAILURE'}
    data['generation_success_rate']=data['generation_success_count']/data['dataset_size']
    aggregate.update(reference_constraints=dict(totals),by_constraint_category={k:dict(v) for k,v in cats.items()},facet_distribution=dict(facet_counts),stage_outcomes=dict(stages),rejected_ungrounded_extractions=extraction_removed,manual_reviews_completed=sum(r['manual_review'].get('status')=='REVIEWED' for r in data['rows']))
    aggregate['recovery']=aggregate_recovery
    aggregate['primary_complete_queries']=stages['generate_pass']
    aggregate['empty_extractions']=[r['query_id'] for r in data['rows'] if not any(r['constraint_json'].values())]
    aggregate['control_token_queries']=[{'query_id':r['query_id'],'sequence':j,'query':x['query']} for r in data['rows'] for j,x in enumerate(r['constraint_queries'],1) if x['query'].strip().lower() in {'search','expand','stopsearch','stopexpand'}]
    for row in data['rows']:
        row['recovery_provenance']=[x for x in recovery_records if x['query_id']==row['query_id']]
    data['evaluation']=aggregate
    Path(a.results).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    def pct(n,d):return f'{100*n/d:.2f}%' if d else 'N/A'
    def escape(x):return str(x).replace('|','\\|').replace('\n',' ')
    def queries(xs):return '<br>'.join(f'{i}. {escape(x)}' for i,x in enumerate(xs,1))
    lines=['# Constraint-aware Query Planner V0：Query Generation 审计','','## Overview','',
       f"- 数据集：RealScholarQuery-50，共 {data['dataset_size']} 题；结构化三阶段生成成功 {data['generation_success_count']}/{data['dataset_size']}（{pct(data['generation_success_count'],data['dataset_size'])}）。成功只表示 schema、source grounding、五条 query 与 facet 对齐通过，不表示语义质量通过。",
       '- Baseline：直接复用冻结 smoke 中 248 条 Crawler queries，未重跑 baseline；Q18、Q28 各 4 条，其余各 5 条。',
       '- V0：同一现有 PaSa Crawler checkpoint，三阶段（约束提取 → facet planning → query generation）；保持权重，独立新 prompts。seed=42、batch=8，主流程max_new_tokens=1200，其余sampling使用checkpoint配置。批量生成失败时逐facet生成，单条max_new_tokens=350。相较baseline增加调用次数与输出预算，这是完整规划流程对照，不能归因于单独一句prompt。',
       '- 完全离线：HF local_files_only/offline，并阻断 socket 网络访问；没有导入 paper_agent/utils，没有调用 Serper、Selector、Expand，没有产生搜索结果。',
       '- 原 Crawler 在合成样例中倾向输出 Search/Expand action。独立脚本采用 JSON 起始前缀，解析完整 JSON 后忽略已记录的尾随 action 标签；不会执行标签。每阶段最多三次格式修复，原始响应和拒绝值均保存。',
       '- 提取字段必须是原问题的连续原文片段；不受支持的值被置空/删除，而非由规则猜出替代值。这样能阻止提取结果增加不存在的信息，但可能保留遗漏。后续 facet/query 仍可能引入无依据内容，需要人工审计。',
       f'- 三阶段记录：`{dict(stages)}`；所有尝试累计剔除无原文依据的提取值 {len(extraction_removed)} 项（含失败尝试，非唯一实体数）。',
       f"- 主流程完整成功 {stages['generate_pass']}/50。其余走通用补救：失败提取/规划额外最多3次；失败的五query批次改成逐facet生成，每槽最多3次，程序仅绑定facet、不改写query内容。补救共 {aggregate_recovery['stage_records']} 个记录、{aggregate_recovery['attempts']} 次样本尝试；仍失败 {aggregate_recovery['failed_records']} 个记录。未成功槽位保留失败证据，不人工补词。",
       '- 工程过程中先看到批量格式不稳定，再增加逐facet补救；只修复通用结构交付，没有按某题GT或质量分数调词。因此这是一轮V0工程可行性与文本审计，不是盲化预注册效果检验。',
       '', '## Query diversity analysis','',
       '统一采用内容 token Jaccard，移除常见检索包装词，使用脚本内公开的小型缩写/拼写规范化表；没有 embedding 模型或语义相似度调用。阈值 0.8 只是本报告词面冗余诊断；同义改写可能低估，关键约束共享可能高估。不能与此前使用不同 token 规则的审计数值直接比较。','',
       '| 指标 | Baseline | V0 |','|---|---:|---:|']
    for key,label in [('queries','总 query 数'),('exact_duplicates','同题完全重复 query 数'),('mean_pair_similarity_macro','题级平均 pair Jaccard 的均值'),('pairs_ge_0_8','Jaccard≥0.8 的 pair 数'),('pair_count','pair 总数'),('mean_word_count','题级平均 query 单词数')]:
        bv,nv=aggregate['baseline'][key],aggregate['planner'][key]
        lines.append(f'| {label} | {bv:.4f} | {nv:.4f} |' if isinstance(bv,float) else f'| {label} | {bv} | {nv} |')
    lines+=['',f"仅在双方都有完整输出的 {len(paired)} 题上配对，平均 Jaccard：`{aggregate['paired_success_only']}`。上方全量表纳入部分失败题中仍可解析的query；配对表仅含完整题。下方coverage分母始终保留全部50题的标注，有效部分输出可命中，未生成槽位没有命中，不通过丢弃困难题提高coverage。",'','## Constraint preservation rate','',
       '分母是运行 50Q 生成前，依据用户 question 单独标注的 140 个约束片段；不读取 GT title/论文答案，不使用 V0 自身提取结果作为分母。标注文件只供审计，生成脚本不加载它。每项要求其规范化内容词全部在同一条 query 中出现；同题五条取 OR。表中是**词面保留率**，不能证明比较方向、否定作用域或相关性正确；长句同义改写也可能被低估。',
       f"\nBaseline={totals['baseline_retained']}/{totals['constraints']}（{pct(totals['baseline_retained'],totals['constraints'])}）；V0={totals['planner_retained']}/{totals['constraints']}（{pct(totals['planner_retained'],totals['constraints'])}）；提取阶段={totals['extraction_retained']}/{totals['constraints']}（{pct(totals['extraction_retained'],totals['constraints'])}）。",'',
       '| 原问题约束类型 | 标注数 | Baseline 保留 | V0 保留 | Extraction 保留 |','|---|---:|---:|---:|---:|']
    for cat,v in sorted(cats.items()):lines.append(f"| {cat} | {v['constraints']} | {v['baseline_retained']} ({pct(v['baseline_retained'],v['constraints'])}) | {v['planner_retained']} ({pct(v['planner_retained'],v['constraints'])}) | {v['extraction_retained']} ({pct(v['extraction_retained'],v['constraints'])}) |")
    allclaims=[x for row in data['rows'] for x in row['automatic_audit']['self_reported_coverage_checks']]
    lines+=['',f"模型自报 covered_constraints 共 {len(allclaims)} 项；其中 {sum(x['lexically_supported'] for x in allclaims)} 项通过同 query 的独立词面检查。自报列表不能当作真实 coverage。空提取字段也不算被支持；详细逐项结果保存在 JSON。",'', '## Facet distribution','',
       '下表为模型实际生成的标签分布，不把标签不同直接等同语义互补。V0 不强制每题都有 benchmark facet：无此约束时允许调整，但调整是否合理见人工表。','', '| 实际 facet 标签 | Query 数 |','|---|---:|']
    for label,count in facet_counts.most_common():lines.append(f'| {escape(label)} | {count} |')
    lines+=['','## Manual audit table','',
       '逐题对照完整 question 与双方全部 query，由当前助手人工复核；不是独立多评审盲审。表中的改进只指可见文本行为，不表示搜索有效。完整问题、提取 JSON、facets、逐项保留检查均在 RESULTS.json。Q18/Q28 的数量不同需谨慎比较。','',
       '| ID | Baseline Query | New Query | Improvement | Problem |','|---|---|---|---|---|']
    for row,bd,nd,checks in comparisons:
        note=row['manual_review']
        new_text='<br>'.join(f"槽{x['planned_sequence']}. {escape(x['query'])}" for x in row['constraint_queries'])
        lines.append(f"| {row['query_id']} | {queries(row['baseline_queries'])} | {new_text} | {escape(note.get('improvement','待人工复核'))} | {escape(note.get('problem','待人工复核'))} |")
    lines+=['','## 结论边界','',
       '**本轮不能认定 V0 生成了整体更合理、更互补的 queries。**部分实体保留有进步，但词面冗余没有下降，人工审计发现反向约束、无依据技术扩展与缩写错误。这个结论针对本次现有Crawler作为结构化规划模型的V0实现，不能推广为所有constraint-aware方法都无效。',
       f"约束提取完全为空的题数={len(aggregate['empty_extractions'])}，ID为 `{aggregate['empty_extractions']}`。这是原文片段校验后的结果：严格过滤既阻止了幻觉，也删除了许多不逐字一致的改写。模型仍能从后续输入的原问题生成query，所以不能把最终实体命中全归功于提取步骤。",
       f"另有 {len(aggregate['control_token_queries'])} 条仅为控制词的不可用输出：`{aggregate['control_token_queries']}`。它们保留在原始候选中供审计，不能送入未来搜索；45/50只是结构完整率，不是45题全部满足英文检索质量与硬约束。",
       '代表性反例：Q28补回三个benchmark名称却未保留难度顺序；Q48补回factor mining但LLM约束分散；Q18多条直接复制原问题且完全重复；Q5错误展开RLHF；Q43错误展开DPO。Q13虽有否定方向的语义保留，严格词面匹配可能未计入，因此不能把负约束词面0%解释为所有否定语义都丢失。',
       '此实验只能判断保存的 query 是否更忠实、更互补。结构化成功率、facet 标签数、词面保留率和 pair 相似度都是不同指标，任何一项单独改善都不能证明整体 query 质量改善，更不能证明 Search Recall 提升。具体判断以逐题人工发现为依据，不提前认定方案有效。',
       f"新query未执行任何搜索；没有真实候选集、Recall、Precision或F1。未来搜索实验需要双方各自的replay、同期配对采集以及相同预算；本次{aggregate['planner']['queries']}对248条也不构成严格等量搜索A/B。",
       '', '## 运行与证据','',
       '```bash\ncd /home/chenyi/pasa\nCUDA_VISIBLE_DEVICES=1 PYTHONHASHSEED=42 /mnt/nvme3/chenyi/conda-envs/pasa/bin/python query_planner_v0/generate.py --batch-size 8\nCUDA_VISIBLE_DEVICES=1 PYTHONHASHSEED=42 /mnt/nvme3/chenyi/conda-envs/pasa/bin/python query_planner_v0/repair.py --batch-size 8\npython3 query_planner_v0/audit.py\npython3 -m unittest query_planner_v0.test_validation\n```','',
       '- 原始阶段记录：[run](/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0/run)。每题三个阶段文件保存 prompt、原始输出、格式失败/修复、剔除项、延迟。',
       '- 机器可读结果：[CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json](/home/chenyi/pasa/CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json)。',
       '- 只增加独立 planner 与审计文件，PaSa 原 search、Selector、Expand、checkpoint、原 prompt 和评测入口未更改，未提交 Git。']
    Path(a.report).write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in aggregate.items() if k!='rejected_ungrounded_extractions'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
