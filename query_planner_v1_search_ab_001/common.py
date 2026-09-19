"""Read-only access to frozen native logic and isolated experiment paths."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(__file__).resolve().parent
OUT=ROOT/'QUERY_PLANNER_V1_SEARCH_AB_001.json'
REPORT=ROOT/'QUERY_PLANNER_V1_SEARCH_AB_001.md'
DATA=Path('/mnt/nvme3/chenyi/pasa/data/RealScholarQuery/test.jsonl')
CHECKPOINT=Path('/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler')
B_TEMPLATE='''Please generate up to 5 mutually complementary search queries to find relevant papers according to the User Query.

Requirements:

- Preserve important entities, benchmarks, methods, tasks, comparison relations, exclusions, and negations from the user query across the query set.
- If the user query contains an acronym, preserve the original acronym in at least one search query.
- Do not invent datasets, models, methods, benchmarks, or technical mechanisms not supported by the user query.
- Avoid superficial paraphrases or highly redundant queries.
- Generate fewer than 5 queries if additional queries would only be redundant.

User Query: {user_query}'''

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)

def read(path=OUT):return json.loads(Path(path).read_text())

def native_function(name,namespace=None):
    text=(ROOT/'utils.py').read_text();tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    env={} if namespace is None else namespace
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/'utils.py'),'exec'),env)
    return env[name],ast.get_source_segment(text,node)

def native_search_spec():
    text=(ROOT/'paper_agent.py').read_text();tree=ast.parse(text)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PaperAgent')
    init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    defaults=dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):],init.args.defaults))
    limit=ast.literal_eval(defaults['search_queries'])
    pattern=None
    for n in ast.walk(init):
        if isinstance(n,ast.Dict):
            for k,v in zip(n.keys,n.values):
                if isinstance(k,ast.Constant) and k.value=='search_template':pattern=ast.literal_eval(v)
    assert pattern and limit==5
    search=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='search')
    return pattern,limit,ast.get_source_segment(text,search)

def protected():
    paths=list(ROOT.glob('*.py'))+[ROOT/'agent_prompt.json',ROOT/'BASELINE_REALScholarQuery50.md']
    paths+=list((ROOT/'query_planner_v0').rglob('*.py'))+list((ROOT/'query_planner_v0').glob('*.json'))
    paths+=list(ROOT.glob('ACRONYM_EXPANSION*'))
    paths+=[ROOT/'REPRO_LOCAL_ONLY_50Q_BASELINE_REPORT.md',DATA]
    return {str(p):sha(p) for p in sorted(set(paths)) if p.is_file()}

def project_questions():
    result=[]
    for index,line in enumerate(DATA.open()):
        fields={}
        for key in ('question','source_meta','qid'):
            m=re.search(r'"'+key+r'"\s*:\s*',line);assert m
            fields[key],_=json.JSONDecoder().raw_decode(line[m.end():])
        published=fields['source_meta']['published_time']
        before=(dt.datetime.strptime(published,'%Y%m%d')-dt.timedelta(days=7)).strftime('%Y-%m-%d')
        result.append({'query_id':f'Q{index}','query_index':index,'dataset_qid':fields['qid'],'original_question':fields['question'],'published_time':published,'before_date':before})
    assert len(result)==50
    return result
