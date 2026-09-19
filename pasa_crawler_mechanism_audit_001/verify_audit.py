"""Document/source integrity checks only. No PaSa imports, network, models or experiments."""
import hashlib,json,re
from datetime import datetime, timezone
from pathlib import Path
R=Path(__file__).resolve().parent
REPO=R.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks={}
    def check(k,v):
        checks[k]=bool(v)
        assert v,k
    protected=json.loads((R/'initial_source_hashes.json').read_text())
    for f,h in protected.items():check('unchanged:'+f,sha(REPO/f)==h)
    matrix=json.loads((R/'paper_vs_code_matrix.json').read_text());catalog=matrix['evidence_catalog']
    required={'state','actions','search_decision','query_generation','feedback','alternation','subsection','queue','stop','finish','budget','cost','feedback_loop','trajectory','autonomy'}
    check('all_15_requested_comparisons',required<={x['id'] for x in matrix['items']})
    check('distinct_matrix_rows',len(matrix['items'])==len({x['id'] for x in matrix['items']}))
    for x in matrix['items']:
        check('status:'+x['id'],x['status'] in {'MATCH','PARTIAL','MISSING','UNCLEAR'})
        check('three_layers_and_evidence:'+x['id'],all(x[k] for k in ['paper_definition','checkpoint_training_evidence','current_inference','discrepancy','evidence_ids']) and all(k in catalog for k in x['evidence_ids']))
    for k,e in catalog.items():
        if 'file' in e:
            p=R/e['file'];check('code_line_range:'+k,p.is_file() and 1<=e['line_start']<=e['line_end']<=len(p.read_text().splitlines()))
        else:check('paper_evidence:'+k,(R/e['local_text']).is_file())
    report=R/'PASA_CRAWLER_MECHANISM_AUDIT_001.md';graph=R/'inference_call_graph.md'
    for p in [report,graph]:
        check('artifact_nonempty:'+p.name,p.is_file() and len(p.read_text())>1000)
        for i,link in enumerate(re.findall(r'\]\(([^)]+)\)',p.read_text())):
            if link.startswith('http'):continue
            path=re.sub(r':\d+$','',link);f=Path(path) if path.startswith('/') else p.parent/path
            check(f'local_link:{p.name}:{i}',f.exists())
            if re.search(r':\d+$',link) and f.is_file():check(f'local_line:{p.name}:{i}',1<=int(link.rsplit(':',1)[1])<=len(f.read_text().splitlines()))
    check('matrix_markdown_sync',(R/'matrix_table.md').read_text() in report.read_text())
    check('call_graph_present','```mermaid' in graph.read_text())
    for function in ['run','search','search_paper','expand','infer','infer_score','get_paper_content','search_ref','do_expand']:
        check('call_graph_function:'+function,function in graph.read_text())
    requirement_map={
      '1_paper_state_actions_stop_alternation_observations_queue':'报告 §2.1–2.4；matrix state/actions/stop/alternation/feedback/queue。已逐项阅读论文正文、附录与源码，未明确处标为未证实。',
      '2_imitation_trajectories_ppo_reward_cost_global_budget':'报告 §3.1–3.5，引用正式版 D.1/D.2、Eq.(1)–(8)、G.2，及公开训练 handler/rollout；区分预算约束与 budget observation。',
      '3_actual_function_call_chain_and_observations':'报告 §4、inference_call_graph.md：函数行号、Mermaid、observation 表、frontier 与 Stop/EOS 边界。',
      '4_at_least_15_rows_with_required_statuses':'报告 §5 与 paper_vs_code_matrix.json 共18条，包括全部15项；每项三层说明和证据。',
      '5_separate_paper_checkpoint_orchestration':'报告 §1、§3.5、§7；JSON 每条有三层独立字段，声明训练语料/精确训练 run 的证据缺口。',
      '6_constraints_recovery_extension_and_novelty':'报告 §8.1–8.3：条件化地回答限制、两者皆有及合理/不合理创新表述；未设计 Planner。',
      'discrepancies_not_reconciled':'报告 §6 D01–D10；明确 Stop shaping、采样、去重、Selector stub、队列/数据路径差异，层数计数不确定未擅断。',
      'three_named_deliverables':'PASA_CRAWLER_MECHANISM_AUDIT_001.md、paper_vs_code_matrix.json、inference_call_graph.md 均存在并互相链接。',
      'no_formal_source_changes':'本次开头冻结的9份正式代码/文档 SHA-256 与当前全部一致。',
      'no_new_experiments_or_model_training':'本次操作限于下载/阅读公开论文源码、读取已有产物、生成审计文档与静态一致性检查；未导入 PaSa 管线或执行模型/检索脚本。'
    }
    sources={}
    for p in (R/'sources').rglob('*'):
        if p.is_file() and '.git' not in p.parts:sources[str(p.relative_to(R))]=sha(p)
    artifacts={f:sha(R/f) for f in ['PASA_CRAWLER_MECHANISM_AUDIT_001.md','paper_vs_code_matrix.json','inference_call_graph.md','source_provenance.json','build_matrix.py','verify_audit.py']}
    out={'audit':'PASA_CRAWLER_MECHANISM_AUDIT_001','status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),'validation_scope':'Static document/source integrity and requirement-to-evidence coverage. This does not verify checkpoint capabilities or reproduce training/benchmark results.','check_count':len(checks),'checks':checks,'reviewed_requirement_evidence':requirement_map,'protected_sources':protected,'artifact_sha256':artifacts,'source_sha256':sources}
    (R/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':len(checks),'matrix_rows':len(matrix['items']),'formal_sources_unchanged':len(protected),'sources_hashed':len(sources)},indent=2))

if __name__=='__main__':main()
