"""Native ID metadata, frozen title evaluator, and paired component accounting."""
import argparse
from collections import Counter
import contextlib
import fcntl
import io
import json
from pathlib import Path
import re
import runpy
import statistics
import sys
import time
import types
from urllib.parse import urlparse, parse_qs
import warnings
import zipfile
from common import ROOT, WORK, OUT, DATA, now, read, save, sha, protected, native_function


def metadata():
    import arxiv
    import requests
    lock = (WORK / 'metadata.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    d = read()
    assert d['status'] in ('search_complete', 'metadata_running')
    p = d['provenance']
    assert p['protected_before'] == protected()
    ids = sorted({aid for q in d['per_query'] for s in q['searches'].values() for aid in s['returned_arxiv_ids']})
    p.setdefault('metadata_started_utc', now())
    p['metadata_runner_sha256'] = sha(__file__)
    network_path = WORK / 'metadata_network.json'
    network = read(network_path) if network_path.exists() else []
    original_request = requests.sessions.Session.request
    active = {'arxiv_id': None}

    def guard(session, method, url, *args, **kwargs):
        if urlparse(url).hostname not in ('export.arxiv.org', 'arxiv.org') or method.upper() != 'GET':
            raise RuntimeError('Only native arXiv ID metadata GET is allowed')
        params = kwargs.get('params') or parse_qs(urlparse(url).query, keep_blank_values=True)
        search_query = params.get('search_query')
        assert search_query in (None, '', ['']), 'No title searches allowed'
        raw_ids = params.get('id_list', [])
        raw_ids = raw_ids if isinstance(raw_ids, list) else [raw_ids]
        assert raw_ids and all(item in ids for value in raw_ids for item in value.split(','))
        record = {'arxiv_id': active['arxiv_id'], 'method': method, 'url': url,
                  'params': params, 'started_utc': now()}
        t = time.monotonic()
        try:
            response = original_request(session, method, url, *args, **kwargs)
            record['http_status'] = response.status_code
            return response
        except Exception as exc:
            record.update(http_status=None, error_type=type(exc).__name__, error_message=str(exc))
            raise
        finally:
            record.update(finished_utc=now(), elapsed_seconds=time.monotonic() - t)
            network.append(record)
            save(network_path, network)

    requests.sessions.Session.request = guard
    keep, _ = native_function('keep_letters')
    database = ROOT / 'data/paper_database'
    p['metadata_database_files'] = {n: {'sha256': sha(database / n), 'bytes': (database / n).stat().st_size}
                                    for n in ('id2paper.json', 'cs_paper_2nd.zip')}
    archive = zipfile.ZipFile(database / 'cs_paper_2nd.zip', 'r')
    env = {'keep_letters': keep, 'id2paper': read(database / 'id2paper.json'), 'paper_db': archive,
           '_paper_db_names': set(archive.namelist()), 'json': json, 'arxiv': arxiv,
           'arxiv_client': arxiv.Client(delay_seconds=.05), 'warnings': warnings}
    resolve, source = native_function('search_paper_by_arxiv_id', env)
    p['native_metadata_function_source'] = source
    p['metadata_policy'] = 'Unchanged native function, sequential IDs, original arxiv.Client(delay_seconds=.05) and default retry config. Local ZIP first, native arXiv ID fallback. No prior experiment metadata reuse, GT/Serper title substitution, aliases or extra candidates. Same title snapshot used for all A/B/common/q5/anchor comparisons.'
    d['status'] = 'metadata_running'
    save(OUT, d)
    resolved = unresolved = 0
    for index, aid in enumerate(ids, 1):
        path = WORK / 'metadata' / f'{aid}.json'
        if path.exists():
            record = read(path)
        else:
            active['arxiv_id'] = aid
            t = time.monotonic()
            first = len(network)
            record = {'arxiv_id': aid, 'started_utc': now()}
            try:
                result = resolve(aid)
                if result is None:
                    record.update(status='UNRESOLVED', title=None, source=None)
                else:
                    record.update(status='PASS', title=result['title'], normalized_title=keep(result['title']), source=result['source'])
            except Exception as exc:
                record.update(status='UNRESOLVED', title=None, source=None, error_type=type(exc).__name__, error_message=str(exc))
            record.update(finished_utc=now(), elapsed_seconds=time.monotonic() - t,
                          network_record_indices=list(range(first, len(network))))
            save(path, record)
        resolved += record['status'] == 'PASS'
        unresolved += record['status'] != 'PASS'
        if index % 25 == 0 or record['status'] != 'PASS' or index == len(ids):
            print(f'Metadata {index}/{len(ids)}; resolved={resolved}, unresolved={unresolved}; last={aid}', flush=True)
    archive.close()
    p.update(metadata_finished_utc=now(), protected_after_metadata=protected(),
             metadata_summary={'unique_search_ids': len(ids), 'resolved_titles': resolved, 'unresolved_titles': unresolved,
                               'http_attempts': len(network), 'http_statuses': dict(Counter(str(r.get('http_status')) for r in network))})
    assert p['protected_after_metadata'] == p['protected_before']
    d['status'] = 'metadata_complete'
    save(OUT, d)
    print('Native ID metadata complete; scoring can now decode GT.', flush=True)


def aggregate(qs):
    output = {'questions': len(qs), 'TOTAL_GT': sum(q['gt']['total'] for q in qs)}
    for group in ('A', 'B'):
        gs = [q['groups'][group] for q in qs]
        found = sum(g['gt_found'] for g in gs)
        output[group] = {'GT_FOUND': found, 'MACRO_SEARCH_RECALL': statistics.mean(g['recall'] for g in gs),
                         'MICRO_SEARCH_RECALL': found / output['TOTAL_GT'],
                         'LOGICAL_SERPER_CALLS': sum(len(g['search_keys']) for g in gs),
                         'ATTRIBUTED_SERPER_ATTEMPTS': sum(g['serper_attempts'] for g in gs),
                         'SUCCESSFUL_QUERY_RESPONSES': sum(g['successful_queries'] for g in gs)}
    output['comparison'] = {'B_gt_A_questions': sum(q['comparison']['delta_gt'] > 0 for q in qs),
                            'B_eq_A_questions': sum(q['comparison']['delta_gt'] == 0 for q in qs),
                            'B_lt_A_questions': sum(q['comparison']['delta_gt'] < 0 for q in qs),
                            'macro_recall_delta': output['B']['MACRO_SEARCH_RECALL'] - output['A']['MACRO_SEARCH_RECALL'],
                            'micro_recall_delta': output['B']['MICRO_SEARCH_RECALL'] - output['A']['MICRO_SEARCH_RECALL']}
    for key in ('common_gt', 'q5_component_gt', 'anchor_component_gt', 'q5_only_gt', 'anchor_only_gt',
                'q5_marginal_gt', 'anchor_marginal_gt', 'shared_exclusive_component_marginal_gt'):
        output[key + '_count'] = sum(len(q['comparison'][key]) for q in qs)
    attempts = [a for q in qs for s in q['searches'].values() for a in s['attempts']]
    output['actual_unique_logical_queries'] = sum(len(q['searches']) for q in qs)
    output['actual_unique_serper_attempts'] = len(attempts)
    output['actual_successful_responses'] = sum(s['status'] == 'PASS' for q in qs for s in q['searches'].values())
    output['http_statuses'] = dict(Counter(str(a.get('http_status')) for a in attempts))
    return output


def official_metrics(d, subsets, keep, cal):
    result = {}
    for subset, qs in subsets.items():
        result[subset] = {}
        for group in ('A', 'B'):
            folder = WORK / 'official_metric_inputs' / subset / group
            for q in qs:
                nodes = [{'title': d['metadata'][aid]['title'], 'child': {}, 'select_score': 0}
                         for aid in q['groups'][group]['candidate_ids'] if d['metadata'][aid]['status'] == 'PASS']
                save(folder / f"{q['query_id']}.json", {'title': q['original_question'], 'extra': {'answer': q['gt']['raw_titles']},
                     'child': {'Search-only candidates': nodes}})
            shim = types.ModuleType('utils')
            shim.keep_letters, shim.cal_micro = keep, cal
            previous_utils, previous_args = sys.modules.get('utils'), sys.argv[:]
            sys.modules['utils'] = shim
            sys.argv = [str(ROOT / 'metrics.py'), '--output_folder', str(folder)]
            stdout = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout):
                    runpy.run_path(str(ROOT / 'metrics.py'), run_name='__main__')
            finally:
                sys.argv = previous_args
                if previous_utils is None:
                    sys.modules.pop('utils', None)
                else:
                    sys.modules['utils'] = previous_utils
            value = float(stdout.getvalue().strip().splitlines()[0].split('&')[0])
            assert value == round(d['summary'][subset][group]['MACRO_SEARCH_RECALL'], 4)
            result[subset][group] = {'stdout': stdout.getvalue(), 'macro_search_recall': value, 'matches': True}
    return result


def score():
    d = read()
    assert d['status'] == 'metadata_complete'
    p = d['provenance']
    assert p['protected_before'] == protected()
    p['scoring_started_utc'] = now()
    keep, keep_source = native_function('keep_letters')
    cal, cal_source = native_function('cal_micro')
    p['frozen_evaluator_functions'] = {'keep_letters': keep_source, 'cal_micro': cal_source}
    ids = {aid for q in d['per_query'] for s in q['searches'].values() for aid in s['returned_arxiv_ids']}
    meta = {aid: read(WORK / 'metadata' / f'{aid}.json') for aid in ids}
    d['metadata'] = meta
    # Decode GT only after the live query set and ID metadata are frozen.
    rows = [json.loads(line) for line in DATA.open()]
    for q, row in zip(d['per_query'], rows):
        assert q['original_question'] == row['question']
        gt = {}
        for title, aid in zip(row['answer'], row['answer_arxiv_id']):
            gt.setdefault(keep(title), []).append({'title': title, 'arxiv_id': aid})
        labels = set(gt)
        q['gt'] = {'total': len(labels), 'raw_titles': row['answer'], 'normalized_groups': gt}
        for key, s in q['searches'].items():
            pred = {meta[aid]['normalized_title'] for aid in s['returned_arxiv_ids'] if meta[aid]['status'] == 'PASS'}
            s['matched_gt'] = sorted(pred & labels)
            s['missing_metadata_ids'] = [aid for aid in s['returned_arxiv_ids'] if meta[aid]['status'] != 'PASS']
            s['matched_gt_evidence'] = [dict(hit, normalized_gt_title=meta[hit['arxiv_id']]['normalized_title'],
                                                metadata_title=meta[hit['arxiv_id']]['title'],
                                                response_artifact=s['attempts'][-1]['artifact_path'])
                                       for hit in s['organic_hits'] if meta[hit['arxiv_id']]['status'] == 'PASS'
                                       and meta[hit['arxiv_id']]['normalized_title'] in labels]
        for group, g in q['groups'].items():
            candidates = set().union(*(set(q['searches'][key]['returned_arxiv_ids']) for key in g['search_keys']))
            pred = {meta[aid]['normalized_title'] for aid in candidates if meta[aid]['status'] == 'PASS'}
            tp, fp, fn = cal(pred, labels)
            g.update(candidate_ids=sorted(candidates), matched_gt=sorted(pred & labels), gt_found=tp,
                     recall=tp / len(labels), fp_titles=fp, fn_gt=fn,
                     missing_metadata_ids=sorted(aid for aid in candidates if meta[aid]['status'] != 'PASS'),
                     serper_attempts=sum(len(q['searches'][key]['attempts']) for key in g['search_keys']),
                     successful_queries=sum(q['searches'][key]['status'] == 'PASS' for key in g['search_keys']))
        common = set().union(*(set(q['searches'][f'q{i}']['matched_gt']) for i in range(1, 5)))
        fifth = set(q['searches']['q5']['matched_gt']) if 'q5' in q['searches'] else set()
        anchor = set(q['searches']['anchor']['matched_gt'])
        a, b = set(q['groups']['A']['matched_gt']), set(q['groups']['B']['matched_gt'])
        assert a == common | fifth and b == common | anchor
        q['comparison'] = {'delta_gt': len(b) - len(a), 'delta_recall': (len(b) - len(a)) / len(labels),
                           'common_gt': sorted(common), 'q5_component_gt': sorted(fifth), 'anchor_component_gt': sorted(anchor),
                           'q5_only_gt': sorted(a - b), 'anchor_only_gt': sorted(b - a),
                           'q5_marginal_gt': sorted(fifth - common), 'anchor_marginal_gt': sorted(anchor - common),
                           'shared_exclusive_component_marginal_gt': sorted((fifth & anchor) - common)}
        assert len(b) - len(a) == len(anchor - common) - len(fifth - common)
    subsets = {'equal_budget_48Q': [q for q in d['per_query'] if q['cohort'] == 'equal_budget_48Q'],
               'full_50Q': d['per_query']}
    assert len(subsets['equal_budget_48Q']) == 48
    d['summary'] = {name: aggregate(qs) for name, qs in subsets.items()}
    d['supplemental'] = {q['query_id']: {'A_gt_found': q['groups']['A']['gt_found'], 'B_gt_found': q['groups']['B']['gt_found'],
                                       'TOTAL_GT': q['gt']['total'], 'added_gt': q['comparison']['anchor_only_gt']}
                         for q in d['per_query'] if q['cohort'] == 'anchor_addition_2Q'}
    p['official_evaluator_verification'] = official_metrics(d, subsets, keep, cal)
    p['official_evaluator_note'] = 'Execute unchanged metrics.py with original keep_letters/cal_micro in a minimal utils shim to avoid pipeline imports. select_score=0 is a schema sentinel only; no Selector/ranking outputs are experiment results.'
    p.update(scoring_finished_utc=now(), protected_after_scoring=protected(), evaluator_script_sha256=sha(__file__),
             metrics_py_sha256=sha(ROOT / 'metrics.py'))
    assert p['protected_before'] == p['protected_after_scoring']
    d['status'] = 'evaluated'
    save(OUT, d)
    print(json.dumps(d['summary'], ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('metadata', 'score'))
    {'metadata': metadata, 'score': score}[parser.parse_args().phase]()
