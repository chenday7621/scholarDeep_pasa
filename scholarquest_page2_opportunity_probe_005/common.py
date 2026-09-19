"""Small local helpers; no pipeline/model/network imports."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SEED = 20260919
PATTERN = r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)'

def now():
    return datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(Path(p).read_text())

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def digest(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def save(p, d):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(p)

def create(p, text):
    with Path(p).open('x') as f:
        f.write(text)

def normalize_function():
    source = (REPO / 'utils.py').read_text()
    n = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'keep_letters')
    scope = {}
    exec(compile(ast.Module(body=[n], type_ignores=[]), 'native keep_letters', 'exec'), scope)
    return scope['keep_letters']

def native_spec():
    source = (REPO / 'paper_agent.py').read_text()
    cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == 'PaperAgent')
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    defaults = dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):], init.args.defaults))
    cap = ast.literal_eval(defaults['search_queries'])
    patterns = [ast.literal_eval(v) for node in ast.walk(init) if isinstance(node, ast.Dict)
                for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant) and k.value == 'search_template']
    assert cap == 5 and patterns == [r'Search\](.*?)\[']
    assert PATTERN in (REPO / 'utils.py').read_text()
    return patterns[0], cap

def ids(response):
    return sorted({m.group(1) for hit in response['organic']
                   if (m := re.search(PATTERN, hit.get('link', '')))})

def verify_freeze():
    r = read(ROOT / 'registration_manifest.json')
    assert r['status'] == 'ACTIVE'
    for name, h in r['frozen_files'].items():
        assert sha(ROOT / name) == h, name
    for name, h in r['protected_sources'].items():
        assert sha(REPO / name) == h, name
    return r
