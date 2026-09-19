"""Execute the frozen diagnostic panel and preserve raw responses."""
import base64
import hashlib
import json
import os
from pathlib import Path
import time

from common import ROOT, now, parsed_id, read, save, sha, verify_source

ENDPOINT = "https://google.serper.dev/search"

def load_success(path, payload):
    if not path.exists(): return None
    record = read(path); assert record["status"] == "PASS" and record["request_payload"] == payload
    raw = base64.b64decode(record["raw_response_base64"])
    assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"] and json.loads(raw) == record["structured_response"]
    return record

def main():
    verify_source(); plan = read(ROOT / "probe_plan.json")
    assert plan["status"] == "FROZEN_BEFORE_REQUESTS" and plan["requests_at_freeze"] == 0
    assert (ROOT / "probe_plan.sha256").read_text().split()[0] == sha(ROOT / "probe_plan.json")
    key = os.environ.get("SERPER_API_KEY", "").strip()
    if not key: key = Path("/mnt/nvme3/chenyi/pasa/secrets/serper_api_key").read_text().strip()
    assert key
    import requests
    client = requests.Session(); headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    sequence = max([0] + [read(path)["global_attempt_sequence"] for path in (ROOT / "probe_attempts").glob("*.json")])
    for index, probe in enumerate(plan["probes"], 1):
        stem = f"{probe['question_id']}_{probe['kind']}"; final = ROOT / "probe_responses" / f"{stem}.json"
        if load_success(final, probe["payload"]): continue
        attempt_summaries = []
        for attempt in range(1, 4):
            attempt_path = ROOT / "probe_attempts" / f"{stem}_attempt{attempt}.json"
            if attempt_path.exists():
                record = read(attempt_path); attempt_summaries.append({"path": str(attempt_path.relative_to(ROOT)), "sha256": sha(attempt_path), "status": record["status"]}); sequence = max(sequence, record["global_attempt_sequence"])
                if record["status"] == "PASS":
                    record["attempts"] = attempt_summaries; save(final, record); break
                if not record.get("retryable", False): raise RuntimeError(f"Prior non-retryable failure: {stem}")
                continue
            sequence += 1; started = now(); start = time.monotonic(); response = None; retryable = False
            record = {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "diagnostic_only": True, "not_a_deployable_policy": True, "question_id": probe["question_id"], "group": probe["group"], "probe_kind": probe["kind"], "gold_arxiv_id": probe["gold_arxiv_id"], "request_payload": probe["payload"], "attempt": attempt, "global_attempt_sequence": sequence, "started_utc": started, "status": "FAILED"}
            try:
                response = client.post(ENDPOINT, headers=headers, data=json.dumps(probe["payload"]), timeout=(15, 60), allow_redirects=False)
                raw = response.content; record.update(http_status=response.status_code, response_headers=dict(response.headers), response_bytes=len(raw), response_bytes_sha256=hashlib.sha256(raw).hexdigest(), raw_response_base64=base64.b64encode(raw).decode("ascii"))
                try: structured = response.json()
                except ValueError: structured = None
                record["structured_response"] = structured
                if response.status_code == 200 and isinstance(structured, dict) and isinstance(structured.get("organic"), list):
                    echoed = structured.get("searchParameters", {}); mismatch = {k: {"requested": v, "echoed": echoed[k]} for k, v in probe["payload"].items() if k in echoed and echoed[k] != v}; record["echoed_parameter_mismatches"] = mismatch
                    if not mismatch:
                        hits = [{"rank": rank, "title": hit.get("title", ""), "snippet": hit.get("snippet", ""), "link": hit.get("link", ""), "arxiv_id": parsed_id(hit.get("link", ""))} for rank, hit in enumerate(structured["organic"], 1)]
                        record.update(status="PASS", hits=hits, gold_hit_ranks=[hit["rank"] for hit in hits if hit["arxiv_id"] == probe["gold_arxiv_id"]])
                retryable = response.status_code == 429 or 500 <= response.status_code < 600
            except Exception as exc:
                retryable = True; record.update(http_status=None, error_type=type(exc).__name__, error_message=str(exc).replace(key, "[REDACTED]"))
            record.update(retryable=retryable, finished_utc=now(), elapsed_seconds=time.monotonic() - start); save(attempt_path, record); attempt_summaries.append({"path": str(attempt_path.relative_to(ROOT)), "sha256": sha(attempt_path), "status": record["status"]})
            if record["status"] == "PASS": record["attempts"] = attempt_summaries; save(final, record); break
            if not retryable: raise RuntimeError(f"Non-retryable response: {stem}")
            if attempt < 3: time.sleep(float(attempt))
        else: raise RuntimeError(f"Probe failed: {stem}")
        if index % 10 == 0 or index == len(plan["probes"]): print(f"diagnostic probes {index}/{len(plan['probes'])}; attempts={sequence}", flush=True)
    save(ROOT / "probe_run_manifest.json", {"status": "COMPLETE", "finished_utc": now(), "probe_plan_sha256": sha(ROOT / "probe_plan.json"), "successful_responses": len(list((ROOT / "probe_responses").glob("*.json"))), "http_attempts": sequence, "gt_aware": True, "diagnostic_only": True, "not_a_deployable_policy": True})
    print("Diagnostic panel complete.")

if __name__ == "__main__": main()
