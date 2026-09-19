"""Freeze the pre-Search protocol and report a required compatibility stop."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
    d=json.loads((ROOT/'dataset_manifest.json').read_text())
    stopped=d['status'].startswith('STOPPED_')
    assert stopped or d['status']=='COMPATIBILITY_PASSED'
    assert d['crawler_generations']==d['serper_search_requests']==0
    assert not (ROOT/'PREREGISTRATION.md').exists(),'Registration already frozen; never overwrite.'
    stamp=datetime.now(timezone.utc).isoformat()
    rows=[]
    for group in ['author-written','inline-citation']:
        c=d['group_counts'][group]
        rows.append(f"| {group} | {c['specific_total']} | {c.get('eligible',0)} | {c.get('ineligible',0)} | 25 |")
    lines=['# PAGE2_ROUTING_PREREG_VALIDATION_003 — PREREGISTRATION','',
           f"冻结时间 UTC：{stamp}",
           '状态：**未激活；兼容性 gate 已要求停止，未抽取正式 50 题。**' if stopped else '状态：**已激活；静态兼容性通过，固定 50 题，尚无 Crawler/Search。**',
           '', '本文件冻结用户指定的协议和当前 gate 结论。未激活时，本文件不是完成 50 题实验的声明，不授权绕过停止条件。', '',
           '## 固定假设和数据','',
           '- 方向固定：同题 native Page1 结果集合的 max_jaccard 越高，该 query 越值得继续搜索 Page2。',
           '- Princeton LitSearch；specificity=1（官方论文 Table 1：0=Broad，1=Specific）。manual_acl/manual_iclr 归 author-written；inline_acl/inline_nonacl 归 inline-citation。',
           '- 静态兼容性：全部 gold corpusid→title→原 keep_letters→原本地 arXiv title index 唯一匹配，且本地 ZIP 标题同一归一化、ID 可被原 parser 识别；不丢弃某题部分 gold、不用模糊匹配或别名、不依据检索结果筛选。',
           '- 任一组不足 25 题或存在未解决映射歧义：停止并报告，不改变组别配额、样本规模或映射定义。',
           '- 通过 gate 才按 row index 排序候选池，用 Python random.Random(20260917) 先抽 author-written 25，再抽 inline-citation 25；无放回，不按质量/主题/结果挑题。',
           f"- 数据版本：`{d['dataset_revision']}`；dataset_manifest.json SHA256：`{sha(ROOT/'dataset_manifest.json')}`。",'',
           '| 来源 | specific题数 | 全gold兼容题数 | 不兼容题数 | 要求抽样 |','|---|---:|---:|---:|---:|',*rows,'',
           '## 原生生成与快照','',
           '- 仅使用已有 pasa-7b-crawler 和 agent_prompt.json.generate_query；每题一次原生生成，最多保留原 parser 解析的前 5 条，不补写、重排、重生成或修复。seed=42，每题生成前固定 Python/NumPy/Torch/CUDA；保留 checkpoint 的 do_sample=true、temperature=0.7、top_p=0.8、top_k=20、repetition_penalty=1.05，原 max_new_tokens=512。',
           '- 原生少于 5 条则如实保留；若 0 条或生成失败，停止为 INCOMPLETE，不替换问题或以 0 收益掩盖失败。',
           '- 搜索请求 num=10，原 site:arxiv.org 和固定 before:2026-09-17；同一 query 的 Page1 后尽快请求 Page2，分别冻结完整原始 response、payload、UTC 时间及哈希。',
           '- 为比较全部基线，采集所有 native query 的 Page1/Page2；Primary 的每题 1 次 Page2 是 replay 逻辑预算，实际采集成本为 Always Page2，不混淆两者。',
           '- 不重复成功请求；瞬时连接错误/429/5xx 最多 3 次记录在案的尝试，不能成功则整个结果标为 INCOMPLETE，不改采样或悄悄删除失败 query。所有策略共享完全相同的成功响应快照。', '',
           '## 唯一 Primary policy','',
           '- S_i 为同题 query i 的 Page1 organic URL 经原 PaSa 正则提取并去重的 arXiv ID 集。',
           '- max_jaccard(i)=max_{j≠i}|S_i∩S_j|/|S_i∪S_j|；空并集为 0，只有一条 native query 时得分为 0。',
           '- 每题只选最高分 1 条；并列按原生成序号从小到大。GT、Page2、词面 relevance、其他统计均不进入 routing。',
           '- 不调整排序方向、阈值、权重、feature 或预算；不根据结果决定是否报告。', '',
           '## 基线、endpoint 与统计','',
           '- Native Page1；Random（每题均匀随机选 1 条，1000 trials，seed=20260917）；Jaccard Router；Always Page2；Oracle top1（每题按 GT 增量最大选 1 条，并列原生成序号，仅离线上界）。',
           '- 沿用项目的归一化 GT 标题分组，静态唯一映射到 arXiv ID；按原 parser 的 ID 覆盖判断是否命中，同题跨 query/page 去重。该指标是 ID 辅助 Search 覆盖，不是 Selector 或最终端到端 Recall。',
           '- Primary endpoint：每题 1 次额外 Page2 下的总 ΔGT 与 incremental recall；Jaccard Router 对 Random 的 P(Random≥Router)。同时报告经验频率 count/1000 和加一 Monte Carlo p=(1+count)/1001。',
           '- 报告 GT found、macro/micro Recall、ΔGT/额外逻辑调用、Always gain retention（Always 增量为 0 时记 NA）；Random 报告 mean/std。',
           '- max_jaccard ROC-AUC 标签为单条 Page2 相对整题全部 Page1 是否新增至少 1 GT；报告全局及同题正负 pair 加权 AUC，单类不可定义时 NA。',
           '- 25 author-written / 25 inline-citation 分组结果为 secondary，不用于调参；不另挑 budget。', '',
           '## 当前执行边界','',
           f"- Gate：{d['status']}；映射异常 {len(d['ambiguous_cases'])} 个；正式抽样 {d['sample_size']} 题。",
           '- 截至冻结，Crawler=0、Serper Search=0、Page1=0、Page2=0。元数据下载不是本实验论文检索。',
           '- paper_agent.py 及原正式代码不变。若当前 gate 未激活，任何后续修订须由用户明确决定并另立版本，不能覆盖本文件。','']
    prereg=ROOT/'PREREGISTRATION.md';prereg.write_text('\n'.join(lines))
    h=sha(prereg)
    (ROOT/'PREREGISTRATION.sha256').write_text(h+'  PREREGISTRATION.md\n')
    save(ROOT/'registration_manifest.json',{'status':'NOT_ACTIVATED_GATE_STOP' if stopped else 'REGISTERED_BEFORE_GENERATION_AND_SEARCH',
                                          'frozen_utc':stamp,'preregistration_sha256':h,'dataset_manifest_sha256':sha(ROOT/'dataset_manifest.json'),
                                          'crawler_generations':0,'serper_search_requests':0})
    if not stopped:
        save(ROOT/'questions_only.json',{'questions':[{'question_id':f"LS{r['row_index']:03d}",'group':r['group'],'question':r['question']} for r in d['sample']]})
        print('REGISTERED: compatibility passed; frozen protocol ready.');return
    status=d['status']
    save(ROOT/'snapshot_manifest.json',{'status':'NOT_COLLECTED_GATE_STOP','stop_reason':status,'snapshots':[],
                                      'page1_requests':0,'page2_requests':0,'preregistration_sha256':h})
    save(ROOT/'states.json',{'status':'NOT_COMPUTED_GATE_STOP','states':[],'reason':status})
    save(ROOT/'decisions.json',{'status':'NOT_COMPUTED_GATE_STOP','decisions':[],'reason':status})
    save(ROOT/'results.json',{'experiment':d['experiment'],'status':status,'compatibility':d['group_counts'],
                             'sample_size':0,'metrics':None,'p_random_ge_router':None,'auc':None,
                             'ambiguous_cases':d['ambiguous_cases'],'crawler_generations':0,'search_requests':0,
                             'protocol_sha256':h,'note':'Not an effectiveness failure or a zero-gain result; no retrieval experiment executed.'})
    gold=json.loads((ROOT/'gold_titles.json').read_text())
    report=['# PAGE2_ROUTING_PREREG_VALIDATION_003','',
            '**已按用户协议停在静态兼容性 gate；未抽样、未生成、未 Search。**','',
            f"原因：`{status}`。这不是 Router 成功或失败的效果结果。",'',
            '| 来源 | specific题数 | 全gold兼容题数 | 不兼容题数 | 要求抽样 |','|---|---:|---:|---:|---:|',*rows,'',
            '## 数据来源与口径','',
            '- [官方 LitSearch 数据集](https://huggingface.co/datasets/princeton-nlp/LitSearch)，固定 revision `'+d['dataset_revision']+'`。6 份 query API response 的 X-Revision 均与该版本一致。',
            '- [官方论文 Table 1/2](https://aclanthology.org/2024.emnlp-main.840.pdf)确认 specificity=1，specific 共 211 author-written / 231 inline-citation；合计 442 题、432 个 unique gold corpusid。',
            '- 数据查看器 filter 接口对批量和单 ID 请求均返回 HTTP 500，改用固定 revision 的 Parquet HTTP Range，只读取 corpusid/title 列及 footer；不读取 corpus 的 abstract/full_paper 列。',
            f"- 读取列及 footer 共 {gold.get('column_bytes_downloaded',0):,} bytes，提取 {len(gold['rows'])} 个所需 corpusid/title；未下载完整 2.85GB corpus。独立 vendor 中 PyArrow 安装包约 50.1 MB，不属于 corpus 下载，未改 PaSa 环境依赖。",'',
            '## 静态兼容性','',
            '- AST 复用原 utils.keep_letters 和 _build_local_title_index，未导入模型或执行项目在线工具。要求每题全部 gold 均可唯一映射，并核对 ZIP 中原始标题归一化一致和 native parser 的 ID 格式。',
            '- 不依据 Search/Page2 outcome 过滤，不使用质量、主题、词面分数，不丢弃某题的未映射 gold 后缩小分母。',
            f"- gold 映射统计：`{d['gold_mapping_counts']}`。",'',
            '## 必须停止的映射异常','']
    for i,a in enumerate(d['ambiguous_cases'],1):report.append(f'{i}. `{json.dumps(a,ensure_ascii=False)}`')
    if not d['ambiguous_cases']:report.append('无身份歧义；停止原因是兼容样本不足：`'+json.dumps(d['insufficient_groups'])+'`。')
    report+=['','用户要求“若数据映射存在歧义，先停止并报告，不自行修改实验定义”。即使某组兼容数量已够，也未自行忽略、修复或选择一个候选 ID；正式抽样保持 0。','',
             '## 预注册与执行状态','',
             '- PREREGISTRATION.md 已冻结用户指定方向、每题 top1、tie-break、1000 次 Random、评测和失败处理，但明确标记 **NOT_ACTIVATED_GATE_STOP**。不存在完成抽样后的有效 50 题 preregistration。',
             f'- PREREGISTRATION.md SHA256：`{h}`。',
             '- dataset_manifest.json 保存全部 442 题兼容性、432 个 gold 映射和源哈希；snapshot_manifest/states/decisions 均显式未执行，results 指标为 null，不伪造 0 收益。',
             '- Crawler generation=0；Serper Search=0；Page1=0；Page2=0；正式 paper_agent.py 等源码哈希未变。没有比较 policy、调方向或挑预算。','',
             '## 验证','',
             '- query 数据版本、specific 来源计数、全部本地索引函数和源码哈希已核对；金标题来自固定版本列数据。',
             '- 停止时没有生成 50 题样本，沒有新实验响应；所有效果指标未定义。',
             '- 兼容性结果可用 `python3 -B page2_routing_prereg_validation_003/compatibility.py` 在冻结前复算；冻结后不覆盖原 manifest，后续修订须独立版本。','']
    (ROOT/'PAGE2_ROUTING_PREREG_VALIDATION_003.md').write_text('\n'.join(report))
    print('STOP recorded, registration not activated:',status)

if __name__=='__main__':main()
