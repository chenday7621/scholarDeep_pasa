"""Reparse saved V1.2 Crawler output without any query-count cap; offline."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
RAW = ROOT / 'query_planner_v1_2_generation_probe_001/raw_generations'
OUT = ROOT / 'RAW_GENERATION_AUDIT_001.json'
REPORT = ROOT / 'RAW_GENERATION_AUDIT_001.md'
BLOCKED = []


def guard(event, args):
    network = (event == 'socket.__new__' and args[1] in (socket.AF_INET, socket.AF_INET6)) or event in ('socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr')
    forbidden_import = event == 'import' and args[0].split('.')[0] in ('requests','arxiv','torch','transformers','models','paper_agent','httpx','aiohttp')
    if network or forbidden_import or event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','os.fork'):
        BLOCKED.append(event)
        raise RuntimeError('Offline raw generation audit: prohibited action')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


sys.addaudithook(guard)
assert not OUT.exists(), 'Do not overwrite an existing audit'
paths = [RAW / f'Q{i}.json' for i in range(50)]
assert len(list(RAW.glob('*.json'))) == 50
protected = paths + [ROOT / name for name in ('models.py','paper_agent.py','utils.py','agent_prompt.json','metrics.py','QUERY_PLANNER_V1_2_GENERATION_PROBE_001.json','QUERY_PLANNER_V1_2_GENERATION_PROBE_002.json')]
before = {str(path): sha(path) for path in protected}
source = read(ROOT / 'QUERY_PLANNER_V1_2_GENERATION_PROBE_001.json')
constructed = read(ROOT / 'QUERY_PLANNER_V1_2_GENERATION_PROBE_002.json')
rows = []
for i, path in enumerate(paths):
    q = read(path)
    assert q == source['per_query'][i]
    assert q['query_id'] == f'Q{i}'
    raw = q['raw_output']
    assert raw == constructed['per_query'][i]['raw_output']
    # Original PaSa regex + strip, deliberately NO [:5] or other parsing cap.
    queries = [v.strip() for v in re.findall(r'Search\](.*?)\[', raw, flags=re.DOTALL)]
    # Independently count literal action markers and parse complete action blocks.
    markers = raw.count('[Search]')
    independent = [v.strip() for v in re.findall(r'\[Search\](.*?)(?=\[Search\]|\[StopSearch\]|$)', raw, flags=re.DOTALL)]
    assert queries == independent == q['all_parsed_queries']
    assert markers == len(queries)
    assert re.fullmatch(r'\s*(?:\[Search\][^\[\]]+)+\[StopSearch\]\s*', raw, flags=re.DOTALL)
    discarded = [{'native_index': j, 'query': text} for j, text in enumerate(queries, 1) if j > 5]
    assert [v['query'] for v in discarded] == q['discarded_queries']
    assert [text for j, text in enumerate(queries, 1) if j <= 5] == q['native_queries']
    rows.append({'query_id': q['query_id'], 'original_question': q['original_question'],
                 'raw_output': raw, 'all_queries': queries,
                 'numbered_queries': {f'q{j}': text for j, text in enumerate(queries, 1)},
                 'search_marker_count': markers, 'unlimited_parsed_count': len(queries),
                 'would_be_truncated': discarded, 'source_raw_record': str(path),
                 'source_raw_sha256': before[str(path)]})
counts = Counter(q['unlimited_parsed_count'] for q in rows)
truncated = [q for q in rows if q['would_be_truncated']]
summary = {'completed_questions': len(rows), 'exact_count_distribution': dict(sorted(counts.items())),
           'bins': {'0-4': sum(n for k,n in counts.items() if k<5), '5': counts[5], '6': counts[6], '7+': sum(n for k,n in counts.items() if k>=7)},
           'questions_over_five': len(truncated), 'total_search_queries': sum(k*n for k,n in counts.items()),
           'total_truncated_queries': sum(len(q['would_be_truncated']) for q in rows),
           'questions_with_q6': sum(q['unlimited_parsed_count']>=6 for q in rows),
           'questions_with_q7': sum(q['unlimited_parsed_count']>=7 for q in rows)}
assert not truncated, 'If any extras exist, inspect duplicate/similarity/new direction evidence before completing.'
execution = {'new_crawler_generations': 0, 'new_network_requests': 0, 'new_serper_requests': 0,
             'new_selector_calls': 0, 'new_citation_expand_calls': 0, 'search_queries_modified': False, 'blocked_events': BLOCKED}
save(OUT, {'experiment': 'RAW_GENERATION_AUDIT_001', 'status': 'complete', 'summary': summary,
           'extra_query_comparison': {'status': 'not_applicable', 'reason': 'No q6/q7 or other truncated queries in any of the 50 raw outputs; no duplicate/similarity/novelty population to assess.'},
           'execution': execution, 'source_sha256': before, 'per_query': rows, 'over_five_cases': truncated})
lines = ['# RAW_GENERATION_AUDIT_001', '', '50/50题已离线复核。原生正则不加数量截断，并独立核对字面[Search]标记与完整action块；50题均以[StopSearch]完整结束，标记数与解析数一致。', '',
         '| 原始Search数量 | 题数 |', '|---|---:|', '| 0–4 | 2（Q18、Q28各4条） |', '| 5 | 48 |', '| 6 | 0 |', '| 7及以上 | 0 |', '',
         '- 实际生成超过5条：0题。', '- 总计248条Search；被[:5]截断：0条。', '- q6/q7：本批均不存在。', '- 被截断query的exact duplicate、词面相似度、新方向比较：不适用，没有样本；不能据此推断额外query质量。',
         '- 本结论仅针对这50份已保存的V1.2原始输出，不代表Crawler在其他输入/随机种子下不可能生成超过5条。',
         '- JSON保留全部50题原问题、完整raw、q1…qN、会被截断的列表（均为空）及源哈希。',
         '- new Crawler generations = 0；new network requests = 0；new Serper requests = 0。',
         '- 未运行Selector/Citation Expand，未修改search_queries或主流程，未进入新Search。', '', '| Q | 原始Search数 | 截断数 |', '|---|---:|---:|']
lines += [f"| {q['query_id']} | {q['unlimited_parsed_count']} | {len(q['would_be_truncated'])} |" for q in rows]
REPORT.write_text('\n'.join(lines)+'\n')
assert all(sha(path)==value for path,value in before.items()) and not BLOCKED
save(WORK/'validation.json', {'status': 'PASS', 'validated_utc': datetime.now(timezone.utc).isoformat(),
     'checks': '50 raw files equal original generation artifact and follow-up construction raw; uncapped native parser equals independent action parser and marker count; all outputs complete StopSearch format; previous parsed/discarded records identical; source and protected files unchanged.',
     'execution': execution, 'artifact_sha256': {str(p):sha(p) for p in (OUT,REPORT,Path(__file__))}})
print(json.dumps(summary, ensure_ascii=False))
