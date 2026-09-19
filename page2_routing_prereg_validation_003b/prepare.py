"""Identity-only amendment, inherited protocol freeze, then fixed-seed sample."""
from collections import Counter, defaultdict
import copy
from html.parser import HTMLParser
import random
import re
import zipfile
from common import ROOT, REPO, OLD, SEED, read, save, sha, create, now, normalize_function

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = defaultdict(list)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').startswith('citation_'):
            self.meta[attrs['name']].append(attrs.get('content', ''))

def main():
    assert not (ROOT / 'PREREGISTRATION.md').exists(), 'Never overwrite frozen protocol'
    old = read(OLD / 'dataset_manifest.json')
    assert old['status'] == 'STOPPED_MAPPING_AMBIGUITY' and old['sample_size'] == 0
    # Preserve every original non-vendor/source-repo artifact, including metadata byte ranges.
    historical = {str(p.relative_to(OLD)): sha(p) for p in sorted(OLD.rglob('*')) if p.is_file()
                  and not set(p.relative_to(OLD).parts) & {'vendor', '__pycache__', 'upstream_LitSearch', 'identity_evidence'}}
    norm = normalize_function()
    idpath = REPO / 'data/paper_database/id2paper.json'
    assert sha(idpath) == old['provenance']['id2paper_sha256']
    assert sha(REPO / 'utils.py') == old['provenance']['utils_sha256']
    local = defaultdict(list)
    for aid, title in read(idpath).items():
        local[norm(title)].append(aid)
    # Empty normalized titles are ordinary compatibility misses recorded by
    # the original 003 gate, not identity conflicts.  Only non-empty gold
    # titles can form a title -> multiple local-ID ambiguity.
    conflicts = [m for m in old['gold_mappings']
                 if norm(m['title']) and len(local[norm(m['title'])]) > 1]
    assert len(conflicts) == len(old['ambiguous_cases']) == 1, 'New identity conflict: stop for evidence, never bypass'
    assert conflicts[0]['corpusid'] == 258960101
    records = []
    for aid in local[norm(conflicts[0]['title'])]:
        p = OLD / 'identity_evidence' / f'{aid}.html'
        meta = read(p.with_suffix('.json'))
        assert meta['sha256'] == sha(p) and meta['http_status'] == 200
        assert meta['source_url'] == f'https://arxiv.org/abs/{aid}'
        parser = Metadata()
        parser.feed(p.read_text())
        assert len(parser.meta['citation_title']) == 1
        assert parser.meta['citation_arxiv_id'] == [aid]
        records.append({'arxiv_id': aid, 'official_title': parser.meta['citation_title'][0],
                        'official_metadata': dict(parser.meta), 'source': meta,
                        'matches_normalized_gold_title': norm(parser.meta['citation_title'][0]) == norm(conflicts[0]['title'])})
    matches = [r for r in records if r['matches_normalized_gold_title']]
    if len(matches) != 1:
        save(ROOT / 'identity_resolution.json', {'status': 'STOPPED_MAPPING_AMBIGUITY', 'records': records})
        raise RuntimeError('Identity not unique; experiment stopped')
    aid = matches[0]['arxiv_id']
    assert aid == '2305.17359'
    # Retain original ZIP/ID support checks for the resolved identity.
    key = norm(conflicts[0]['title'])
    with zipfile.ZipFile(REPO / 'data/paper_database/cs_paper_2nd.zip') as z:
        raw = z.read(key)
    import hashlib
    import json
    assert norm(json.loads(raw)['title']) == key and re.fullmatch(r'\d{4}\.\d+', aid)
    resolution = {'status': 'UNIQUELY_RESOLVED', 'created_utc': now(), 'gold_corpusid': 258960101,
                  'gold_title': conflicts[0]['title'], 'retained_id': aid,
                  'rejected_local_index_ids': [r['arxiv_id'] for r in records if not r['matches_normalized_gold_title']],
                  'records': records, 'specific_gold_corpusids_audited': len(old['gold_mappings']),
                  'specific_questions_audited': len(old['queries']), 'identity_conflict_count': len(conflicts),
                  'additional_identity_conflicts': [], 'local_zip_record_sha256': hashlib.sha256(raw).hexdigest(),
                  'ordinary_title_miss_repaired': 0, 'local_index_modified': False, 'search_outcomes_used': False}
    save(OLD / 'identity_evidence/identity_resolution.json', resolution)
    save(ROOT / 'identity_resolution.json', resolution)
    amendment = f'''# MAPPING_AMENDMENT — identity resolution only

冻结时间 UTC：{now()}

## 唯一映射修订规则

- 同一 normalized gold title 对应多个本地 arXiv ID 时，只允许依据静态官方论文身份 metadata 核验。
- 禁止依据 Page1/Page2 Search outcome、GT gain 或后续实验结果选择 ID。
- 只有一个候选的官方 arXiv title/metadata 与 gold paper 身份一致时保留该 ID，其余视为本地 index 错误；仍无法唯一确定则立即停止。
- 只处理一对多 identity conflict；不扩大 fuzzy matching，不补普通 title miss，不改原 keep_letters，不修改正式本地 index。

## 静态核验结论与证据

审计原冻结的 442 个 specific questions、432 个不同 gold corpusid，仅发现 DNA-GPT 这一处 normalized title → multiple arXiv IDs。

- corpusid=258960101；保留 `2305.17359`，官方标题为 DNA-GPT: Divergent N-Gram Analysis for Training-Free Detection of GPT-Generated Text。
- `2303.02909` 官方标题为 Dynamic Prompting: A Unified Framework for Prompt Tuning，拒绝本地索引中的错误 DNA-GPT 关联。
- 官方来源：https://arxiv.org/abs/2305.17359 、https://arxiv.org/abs/2303.02909 。
- 原始 HTML、HTTP 来源/时间、citation metadata 和逐文件 SHA-256 存于原 003 的 identity_evidence/。
- identity_resolution.json SHA-256：`{sha(ROOT / 'identity_resolution.json')}`。
- 原 003 全部已存停止记录与原 PREREGISTRATION.md 保持不变；本修订不改变其历史停止结论。

## 003B 继承与激活

003B 的 PREREGISTRATION.md 是原 003 文件的逐字节副本，SHA-256 `{sha(OLD / 'PREREGISTRATION.md')}`。其中原 003 名称、冻结日期、旧 dataset hash、旧兼容计数及“未激活/停止”段落是历史记录；本用户授权的 003B 通过本 amendment 唯一解决 identity gate 后独立激活，并以 registration_manifest.json 和新的 dataset_manifest.json 记录状态。

除此 identity-resolution amendment 和必要的新版本执行记录外，所有实验条件保持不变：seed=20260917、先 author-written 25 再 inline-citation 25、原 Crawler 每题 seed=42、原 prompt/parser/generation 配置、before:2026-09-17、每 query 配对 Page1/Page2 Top10、每题 max_jaccard top1、并列原生成序号最小、Random 1000 trials、原统计口径及停止规则。

本文件及继承协议在抽样、任何 Crawler/Search 之前冻结；不按新数据结果调参、改变方向或重抽样。
'''
    create(OLD / 'MAPPING_AMENDMENT.md', amendment)
    create(ROOT / 'MAPPING_AMENDMENT.md', amendment)
    create(ROOT / 'PREREGISTRATION.md', (OLD / 'PREREGISTRATION.md').read_text())
    for name in ('PREREGISTRATION', 'MAPPING_AMENDMENT'):
        create(ROOT / f'{name}.sha256', f'{sha(ROOT / (name + ".md"))}  {name}.md\n')
    create(OLD / 'MAPPING_AMENDMENT.sha256', f'{sha(OLD / "MAPPING_AMENDMENT.md")}  MAPPING_AMENDMENT.md\n')
    registration = {'experiment': 'PAGE2_ROUTING_PREREG_VALIDATION_003B', 'status': 'ACTIVE', 'frozen_utc': now(),
                    'frozen_files': {p: sha(ROOT / p) for p in ['PREREGISTRATION.md', 'MAPPING_AMENDMENT.md', 'identity_resolution.json']},
                    'protected_sources': old['provenance']['protected_sources'], 'original_003_artifacts': historical,
                    'original_preregistration_byte_identical': True, 'generations_at_freeze': 0, 'searches_at_freeze': 0,
                    'seed': SEED, 'amendment_only': 'Resolve sole exact-normalized-title identity conflict using official metadata'}
    save(ROOT / 'registration_manifest.json', registration)
    # First sampling operation occurs AFTER both protocol files and their hashes exist.
    mapped = copy.deepcopy(old['gold_mappings'])
    for m in mapped:
        if m['corpusid'] == 258960101:
            m.update(status='compatible', arxiv_id=aid, identity_amendment=True,
                     local_record_sha256=resolution['local_zip_record_sha256'], local_record_title=json.loads(raw)['title'])
    bycid = {m['corpusid']: m for m in mapped}
    queries = copy.deepcopy(old['queries'])
    pools = {'author-written': [], 'inline-citation': []}
    for q in queries:
        q['gold_mappings'] = [bycid[c] for c in q['gold_corpusids']]
        q['exclusion_reasons'] = sorted({m['status'] for m in q['gold_mappings'] if m['status'] != 'compatible'})
        if not q['gold_corpusids']:
            q['exclusion_reasons'].append('empty_gold')
        q['eligible_all_gold_compatible'] = not q['exclusion_reasons']
        if q['eligible_all_gold_compatible']:
            pools[q['group']].append(q)
    assert all(len(p) >= 25 for p in pools.values()), 'Insufficient pool: stop'
    rng = random.Random(SEED)
    sample = []
    for group in ['author-written', 'inline-citation']:
        sample.extend(rng.sample(sorted(pools[group], key=lambda q: q['row_index']), 25))
    for i, q in enumerate(sample):
        q['question_id'] = f'Q{i:02d}'
    manifest = {'experiment': 'PAGE2_ROUTING_PREREG_VALIDATION_003B', 'status': 'SAMPLED', 'sampled_utc': now(),
                'dataset_revision': old['dataset_revision'], 'original_manifest_sha256': sha(OLD / 'dataset_manifest.json'),
                'sample_seed': SEED, 'sample_size': 50, 'group_counts': {g: {'specific_total': sum(q['group'] == g for q in queries),
                'eligible': len(pools[g]), 'sampled': 25} for g in pools}, 'sample': sample, 'queries': queries,
                'gold_mappings': mapped, 'gold_mapping_counts': dict(Counter(m['status'] for m in mapped)),
                'identity_resolution_sha256': sha(ROOT / 'identity_resolution.json'), 'unresolved_identity_conflicts': [],
                'registration_manifest_sha256': sha(ROOT / 'registration_manifest.json')}
    save(ROOT / 'dataset_manifest.json', manifest)
    save(ROOT / 'questions.json', {'questions': [{'question_id': q['question_id'], 'question': q['question']} for q in sample]})
    save(ROOT / 'input_manifest.json', {'created_utc': now(), 'files': {p: sha(ROOT / p) for p in ['dataset_manifest.json', 'questions.json']}})
    assert all(sha(OLD / p) == h for p, h in historical.items())
    print({'groups': manifest['group_counts'], 'sample_rows': [q['row_index'] for q in sample],
           'resolved_identity': aid, 'registration': 'ACTIVE; protocols frozen before sampling'})

if __name__ == '__main__':
    main()
