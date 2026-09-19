"""Search-only paired run. Reuse frozen queries and each shared response once."""
import argparse
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.parse import urlparse
from common import ROOT, WORK, SOURCE, OUT, ENDPOINT, ID_PATTERN, now, read, save, sha, protected, project_questions, native_function, parse_hits


def prepare():
    assert not OUT.exists(), 'Refuse to overwrite an experiment'
    source = read(SOURCE)
    assert source['status'] == 'complete'
    validation = read(ROOT / 'query_planner_v1_2_generation_probe_002/validation.json')
    for path, expected in validation['artifact_sha256'].items():
        assert sha(path) == expected
    qs = project_questions()
    for q, old in zip(qs, source['per_query']):
        assert q['query_id'] == old['query_id'] and q['original_question'] == old['original_question']
        native, a, b = old['native_queries'], old['A_queries'], old['B_queries']
        assert native == a and b == [old['normalized_anchor']] + native[:4]
        assert not old['anchor_exact_duplicate']
        assert len(native) in (4, 5)
        assert len(set(a + b)) == len(native) + 1, 'Unexpected exact query duplicate needs explicit accounting'
        labels = [f'q{i+1}' for i in range(len(native))]
        q.update(native_queries=native, anchor=old['normalized_anchor'], source_generation_id=old['generation_id'],
                 cohort='equal_budget_48Q' if len(native) == 5 else 'anchor_addition_2Q',
                 groups={'A': {'queries': a, 'search_keys': labels}, 'B': {'queries': b, 'search_keys': ['anchor'] + labels[:4]}},
                 searches={k: {'query_key': k, 'query_text': text, 'attempts': [], 'status': 'PENDING',
                               'returned_arxiv_ids': [], 'organic_hits': []}
                           for k, text in list(zip(labels, native)) + [('anchor', old['normalized_anchor'])]})
        # Keep common queries in native order; run exclusive pair adjacently and counterbalance its order.
        tail = (['q5', 'anchor'] if q['query_index'] % 2 == 0 else ['anchor', 'q5']) if len(native) == 5 else ['anchor']
        q['execution_order'] = labels[:4] + tail
    assert [q['query_id'] for q in qs if q['cohort'] == 'anchor_addition_2Q'] == ['Q18', 'Q28']
    _, search_source = native_function('google_search_arxiv_id')
    assert ID_PATTERN in search_source
    p = {'prepared_utc': now(), 'source_queries': str(SOURCE), 'source_sha256': sha(SOURCE),
         'source_seed': 42, 'new_crawler_generations': 0, 'protected_before': protected(),
         'native_serper_function_source': search_source, 'candidate_id_pattern': ID_PATTERN,
         'request_parameters': {'endpoint': ENDPOINT, 'page': 1, 'num': 10, 'site': 'arxiv.org',
                                'before_rule': 'source_meta.published_time minus 7 days'},
         'search_policy': 'Fresh Serper response once per Q/query key; shared q1-q4 response referenced by both groups. No prior Search replay/cache reused. A/B query arrays preserve validated order; HTTP schedule runs common first, then adjacent exclusive pair with even Q q5-first and odd Q anchor-first.',
         'retry_policy': 'Same V1 Search-only cap: at most 3 HTTP attempts per logical query, connect/read timeout 15/60 s, 1/2 s backoff and Retry-After up to 30 s. Persist every attempt, never replay a successful request. Sandbox DNS/permission failures stop for escalation and remain counted.',
         'evaluation_policy': 'Frozen native search_paper_by_arxiv_id, local ZIP then native arXiv ID metadata; one metadata snapshot shared by all components. keep_letters title exact match, cal_micro and unchanged metrics.py. GT decoded only after Search/metadata stage.',
         'marginal_definitions': 'For GT title sets C=common, Q=q5, H=anchor: q5-only=Q-(C|H)=A-B; anchor-only=H-(C|Q)=B-A; q5 marginal=Q-C; anchor marginal=H-C. Also report raw component GT counts Q and H. Counts sum (QID, normalized GT title) pairs.',
         'call_accounting': 'A/B attributed calls count shared requests in each group; actual unique HTTP attempts count once. Expected logical A=248, B=250, common=200, q5=48, anchor=50, actual=298. Equal-budget subset A=B=240 logical slots; supplemental A=8/B=10.',
         'scope': 'Only Search and returned-ID metadata. No Crawler, Selector, Citation Expand, full PaSa, query edits or evaluator/source changes.'}
    d = {'experiment': 'QUERY_PLANNER_V1_2_SEARCH_AB_001', 'status': 'prepared', 'provenance': p, 'per_query': qs}
    save(OUT, d)
    print('Prepared 48 replacement pairs + Q18/Q28 additions; 298 unique logical requests.', flush=True)


def live():
    import requests
    lock = (WORK / 'search.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    d = read()
    assert d['status'] in ('prepared', 'search_running'), 'Search already completed'
    p = d['provenance']
    assert p['protected_before'] == protected()
    key = os.environ.get('SERPER_API_KEY', '').strip()
    key_source = 'SERPER_API_KEY environment'
    if not key:
        key = Path('/mnt/nvme3/chenyi/pasa/secrets/serper_api_key').read_text().strip()
        key_source = 'local protected credential file'
    assert key
    p.setdefault('search_started_utc', now())
    p.update(credential_source=key_source, requests_version=requests.__version__)
    for name in ('run.py', 'common.py'):
        fingerprint = sha(WORK / name)
        if name in p.get('runner_sha256', {}):
            assert p['runner_sha256'][name] == fingerprint
        p.setdefault('runner_sha256', {})[name] = fingerprint
    original_request = requests.sessions.Session.request

    def guard(session, method, url, *args, **kwargs):
        if url != ENDPOINT or method.upper() != 'POST':
            raise RuntimeError('Only fixed Serper POST is allowed')
        return original_request(session, method, url, *args, **kwargs)

    requests.sessions.Session.request = guard
    client = requests.Session()
    headers = {'X-API-KEY': key, 'Content-Type': 'application/json'}
    d['status'] = 'search_running'
    sequence = sum(len(s['attempts']) for q in d['per_query'] for s in q['searches'].values())
    save(OUT, d)
    for q in d['per_query']:
        for query_key in q['execution_order']:
            s = q['searches'][query_key]
            if s['status'] in ('PASS', 'FAILED'):
                continue
            payload = {'q': f"{s['query_text']} before:{q['before_date']} site:arxiv.org", 'num': 10, 'page': 1}
            s['request_payload'] = payload
            # Attempt files can recover a response saved immediately before an interrupted manifest write.
            for path in sorted((WORK / 'requests').glob(f"{q['query_id']}_{query_key}_attempt*.json")):
                r = read(path)
                if r['attempt'] > len(s['attempts']):
                    assert r['attempt'] == len(s['attempts']) + 1
                    s['attempts'].append(r)
                    sequence = max(sequence, r['global_attempt_sequence'])
                    if r['status'] == 'PASS':
                        hits = parse_hits(r['structured_response'])
                        s.update(status='PASS', organic_hits=hits, returned_arxiv_ids=sorted({h['arxiv_id'] for h in hits}))
            if s['status'] == 'PASS':
                save(OUT, d)
                continue
            for attempt in range(len(s['attempts']) + 1, 4):
                sequence += 1
                artifact = WORK / 'requests' / f"{q['query_id']}_{query_key}_attempt{attempt}.json"
                assert not artifact.exists()
                record = {'global_attempt_sequence': sequence, 'query_id': q['query_id'], 'query_key': query_key,
                          'attempt': attempt, 'query_text': s['query_text'], 'request_payload': payload,
                          'artifact_path': str(artifact), 'started_utc': now()}
                t = time.monotonic()
                response, sandbox_failure = None, False
                try:
                    response = client.post(ENDPOINT, headers=headers, data=json.dumps(payload), timeout=(15, 60), allow_redirects=False)
                    record.update(http_status=response.status_code, response_text=response.text,
                                  response_bytes_base64=base64.b64encode(response.content).decode('ascii'),
                                  response_sha256=hashlib.sha256(response.content).hexdigest())
                    try:
                        structured = response.json()
                    except ValueError:
                        structured = None
                    record['structured_response'] = structured
                    if response.status_code != 200:
                        record['status'] = 'HTTP_FAILURE'
                    elif not isinstance(structured, dict) or not isinstance(structured.get('organic'), list):
                        record['status'] = 'RESPONSE_SCHEMA_FAILURE'
                    else:
                        params = structured.get('searchParameters', {})
                        mismatch = {k: {'requested': v, 'echoed': params[k]} for k, v in payload.items() if k in params and params[k] != v}
                        record['echoed_parameter_mismatches'] = mismatch
                        if mismatch:
                            record['status'] = 'PARAMETER_MISMATCH'
                        else:
                            hits = parse_hits(structured)
                            record['status'] = 'PASS'
                            s.update(status='PASS', organic_hits=hits, returned_arxiv_ids=sorted({h['arxiv_id'] for h in hits}))
                except Exception as exc:
                    message = str(exc).replace(key, '[REDACTED]')
                    record.update(status='TRANSPORT_OR_CLIENT_FAILURE', http_status=None, error_type=type(exc).__name__, error_message=message)
                    sandbox_failure = any(x in message.lower() for x in ('operation not permitted', 'permission denied', 'failed to resolve', 'name resolution', 'network is unreachable'))
                record.update(finished_utc=now(), elapsed_seconds=time.monotonic() - t)
                save(artifact, record)
                s['attempts'].append(record)
                save(OUT, d)
                if sandbox_failure:
                    raise RuntimeError('Network/DNS permission failure recorded; resume outside sandbox, without repeating completed responses.')
                if s['status'] == 'PASS':
                    break
                if attempt < 3:
                    pause = float(attempt)
                    if response is not None:
                        try:
                            pause = max(pause, min(30, float(response.headers.get('Retry-After', '0'))))
                        except ValueError:
                            pass
                    time.sleep(pause)
            if s['status'] != 'PASS':
                s['status'] = 'FAILED'
            save(OUT, d)
        save(WORK / 'completed_queries' / f"{q['query_id']}.json", q)
        print(f"{q['query_id']} Search complete; unique queries={len(q['searches'])}, failures={sum(s['status'] != 'PASS' for s in q['searches'].values())}; attempts={sequence}", flush=True)
    p.update(search_finished_utc=now(), protected_after_search=protected())
    assert p['protected_before'] == p['protected_after_search']
    d['status'] = 'search_complete'
    save(OUT, d)
    print('All paired Search requests complete. No GT evaluation, model or expansion calls in this process.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('prepare', 'live'))
    {'prepare': prepare, 'live': live}[parser.parse_args().phase]()
