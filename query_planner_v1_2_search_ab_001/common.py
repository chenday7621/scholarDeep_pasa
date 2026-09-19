"""Frozen source access; never import the PaSa pipeline or a model library."""
import ast
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT / 'QUERY_PLANNER_V1_2_GENERATION_PROBE_002.json'
OUT = ROOT / 'QUERY_PLANNER_V1_2_SEARCH_AB_001.json'
REPORT = ROOT / 'QUERY_PLANNER_V1_2_SEARCH_AB_001.md'
DATA = ROOT / 'data/RealScholarQuery/test.jsonl'
ENDPOINT = 'https://google.serper.dev/search'
ID_PATTERN = r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)'


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path=OUT):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def native_function(name, namespace=None):
    source = (ROOT / 'utils.py').read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = {} if namespace is None else namespace
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(ROOT / 'utils.py'), 'exec'), env)
    return env[name], ast.get_source_segment(source, node)


def protected():
    paths = list(ROOT.glob('*.py')) + [ROOT / 'agent_prompt.json', DATA]
    paths += [p for p in ROOT.glob('*.md') if p != REPORT]
    paths += [p for p in ROOT.glob('*.json') if p != OUT]
    for directory in ('query_planner_v1_search_ab_001', 'query_planner_v1_2_generation_probe_001', 'query_planner_v1_2_generation_probe_002'):
        paths += list((ROOT / directory).glob('*.py'))
        paths += list((ROOT / directory).glob('validation.json'))
    return {str(p): sha(p) for p in sorted(set(paths))}


def project_questions():
    qs = []
    for i, line in enumerate(DATA.open()):
        fields = {}
        for key in ('question', 'qid', 'source_meta'):
            m = re.search(r'"' + key + r'"\s*:\s*', line)
            assert m
            fields[key], _ = json.JSONDecoder().raw_decode(line[m.end():])
        before = (datetime.strptime(fields['source_meta']['published_time'], '%Y%m%d') - timedelta(days=7)).strftime('%Y-%m-%d')
        qs.append({'query_id': f'Q{i}', 'query_index': i, 'dataset_qid': fields['qid'],
                   'original_question': fields['question'], 'before_date': before})
    assert len(qs) == 50
    return qs


def parse_hits(structured):
    hits = []
    for rank, hit in enumerate(structured['organic'], 1):
        m = re.search(ID_PATTERN, hit.get('link', ''))
        if m:
            hits.append({'arxiv_id': m.group(1), 'organic_index': rank - 1,
                         'position': hit.get('position', rank), 'link': hit.get('link'),
                         'title': hit.get('title'), 'snippet': hit.get('snippet')})
    return hits
