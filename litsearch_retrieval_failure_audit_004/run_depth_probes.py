"""Execute frozen Page3-5 diagnostics, preserving complete response bytes."""
import base64, hashlib, json, os
from pathlib import Path
import time
from common import ROOT, now, parsed_id, read, save, sha, verify_source

ENDPOINT = "https://google.serper.dev/search"

def main():
    verify_source(); plan = read(ROOT / "depth_probe_plan.json")
    assert plan["status"] == "FROZEN_BEFORE_DEPTH_REQUESTS" and plan["requests_at_freeze"] == 0
    assert (ROOT / "depth_probe_plan.sha256").read_text().split()[0] == sha(ROOT / "depth_probe_plan.json")
    key = os.environ.get("SERPER_API_KEY", "").strip() or Path("/mnt/nvme3/chenyi/pasa/secrets/serper_api_key").read_text().strip()
    import requests
    client = requests.Session(); headers = {"X-API-KEY": key, "Content-Type": "application/json"}; attempts = 0
    for index, probe in enumerate(plan["probes"], 1):
        path = ROOT / "depth_probe_responses" / f"{probe['question_id']}_q{probe['native_query_index']:02d}_page{probe['page']}.json"
        assert not path.exists(), "Depth diagnostic never resumes/repeats a completed response"
        for attempt in range(1, 4):
            attempts += 1; start = time.monotonic(); response = None; retryable = False
            record = {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "diagnostic_only": True, "gt_aware_query_selection": True, "not_a_deployable_policy": True, **probe, "attempt": attempt, "global_attempt_sequence": attempts, "started_utc": now(), "status": "FAILED"}
            try:
                response = client.post(ENDPOINT, headers=headers, data=json.dumps(probe["payload"]), timeout=(15, 60), allow_redirects=False); raw = response.content
                record.update(http_status=response.status_code, response_headers=dict(response.headers), response_bytes=len(raw), response_bytes_sha256=hashlib.sha256(raw).hexdigest(), raw_response_base64=base64.b64encode(raw).decode("ascii"))
                try: structured = response.json()
                except ValueError: structured = None
                record["structured_response"] = structured
                if response.status_code == 200 and isinstance(structured, dict) and isinstance(structured.get("organic"), list):
                    echoed = structured.get("searchParameters", {}); mismatch = {k: {"requested": v, "echoed": echoed[k]} for k, v in probe["payload"].items() if k in echoed and echoed[k] != v}; record["echoed_parameter_mismatches"] = mismatch
                    if not mismatch:
                        hits = [{"rank_on_page": rank, "nominal_rank": 10 * (probe["page"] - 1) + rank, "title": hit.get("title", ""), "snippet": hit.get("snippet", ""), "link": hit.get("link", ""), "arxiv_id": parsed_id(hit.get("link", ""))} for rank, hit in enumerate(structured["organic"], 1)]
                        record.update(status="PASS", hits=hits, gold_hit_nominal_ranks=[hit["nominal_rank"] for hit in hits if hit["arxiv_id"] == probe["gold_arxiv_id"]])
                retryable = response.status_code == 429 or 500 <= response.status_code < 600
            except Exception as exc:
                retryable = True; record.update(http_status=None, error_type=type(exc).__name__, error_message=str(exc).replace(key, "[REDACTED]"))
            record.update(retryable=retryable, finished_utc=now(), elapsed_seconds=time.monotonic() - start)
            attempt_path = ROOT / "depth_probe_attempts" / f"{probe['question_id']}_q{probe['native_query_index']:02d}_page{probe['page']}_attempt{attempt}.json"; save(attempt_path, record)
            if record["status"] == "PASS": save(path, record); break
            if not retryable: raise RuntimeError(f"Non-retryable depth probe {probe['sequence']}")
            if attempt < 3: time.sleep(float(attempt))
        else: raise RuntimeError(f"Depth probe failed {probe['sequence']}")
        if index % 10 == 0 or index == len(plan["probes"]): print(f"depth probes {index}/{len(plan['probes'])}; attempts={attempts}", flush=True)
    save(ROOT / "depth_probe_run_manifest.json", {"status": "COMPLETE", "finished_utc": now(), "depth_probe_plan_sha256": sha(ROOT / "depth_probe_plan.json"), "successful_responses": len(list((ROOT / "depth_probe_responses").glob("*.json"))), "http_attempts": attempts, "gt_aware": True, "diagnostic_only": True, "not_a_deployable_policy": True})

if __name__ == "__main__": main()
