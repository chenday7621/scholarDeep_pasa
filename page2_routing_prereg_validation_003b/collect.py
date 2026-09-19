"""Frozen native-query generation and paired live Serper Page1/Page2 capture.

This process intentionally reads questions.json, not dataset_manifest.json, so
gold labels cannot enter generation, routing, or Search collection.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys
import time

from common import ROOT, REPO, now, read, save, sha, native_spec, verify_freeze


ENDPOINT = "https://google.serper.dev/search"
CHECKPOINT = REPO / "checkpoints/pasa-7b-crawler"
END_DATE = "2026-09-17"
MODEL_SEED = 42


def seed_all(torch, numpy):
    random.seed(MODEL_SEED)
    numpy.random.seed(MODEL_SEED)
    torch.manual_seed(MODEL_SEED)
    torch.cuda.manual_seed(MODEL_SEED)
    torch.cuda.manual_seed_all(MODEL_SEED)


def redact(value, secret):
    return str(value).replace(secret, "[REDACTED]")


def successful(path, payload):
    if not path.exists():
        return None
    record = read(path)
    assert record["status"] == "PASS", path
    assert record["request_payload"] == payload, path
    raw = base64.b64decode(record["raw_response_base64"])
    assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"], path
    assert json.loads(raw) == record["structured_response"], path
    return record


def request_page(client, headers, secret, qid, query_index, query, page, global_sequence):
    payload = {"q": f"{query} before:{END_DATE} site:arxiv.org", "num": 10, "page": page}
    final_path = ROOT / "responses" / f"{qid}_q{query_index:02d}_page{page}.json"
    cached = successful(final_path, payload)
    if cached is not None:
        return cached, global_sequence

    attempts = []
    for attempt in range(1, 4):
        attempt_path = ROOT / "attempts" / f"{qid}_q{query_index:02d}_page{page}_attempt{attempt}.json"
        if not attempt_path.exists():
            break
        record = read(attempt_path)
        assert record["request_payload"] == payload
        attempts.append({"path": str(attempt_path.relative_to(ROOT)), "sha256": sha(attempt_path), "status": record["status"]})
        global_sequence = max(global_sequence, record["global_http_attempt_sequence"])
        if record["status"] == "PASS":
            raw = base64.b64decode(record["raw_response_base64"])
            assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"]
            assert json.loads(raw) == record["structured_response"]
            record["attempts"] = attempts
            record["artifact_path"] = str(final_path.relative_to(ROOT))
            save(final_path, record)
            return record, global_sequence
        if not record.get("retryable", False):
            raise RuntimeError(f"Non-retryable prior Search failure: {qid} query {query_index} page {page}")
    first_new_attempt = len(attempts) + 1
    if first_new_attempt > 3:
        raise RuntimeError(f"Search failed after 3 prior attempts: {qid} query {query_index} page {page}")

    for attempt in range(first_new_attempt, 4):
        global_sequence += 1
        started = now()
        start = time.monotonic()
        response = None
        record = {
            "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
            "question_id": qid,
            "query_index": query_index,
            "page": page,
            "attempt": attempt,
            "global_http_attempt_sequence": global_sequence,
            "request_payload": payload,
            "started_utc": started,
            "status": "FAILED",
        }
        retryable = False
        try:
            response = client.post(
                ENDPOINT,
                headers=headers,
                data=json.dumps(payload),
                timeout=(15, 60),
                allow_redirects=False,
            )
            raw = response.content
            record.update(
                http_status=response.status_code,
                response_headers=dict(response.headers),
                response_bytes=len(raw),
                response_bytes_sha256=hashlib.sha256(raw).hexdigest(),
                raw_response_base64=base64.b64encode(raw).decode("ascii"),
            )
            try:
                structured = response.json()
            except ValueError:
                structured = None
            record["structured_response"] = structured
            if response.status_code == 200 and isinstance(structured, dict) and isinstance(structured.get("organic"), list):
                echoed = structured.get("searchParameters", {})
                mismatch = {
                    key: {"requested": value, "echoed": echoed[key]}
                    for key, value in payload.items()
                    if key in echoed and echoed[key] != value
                }
                record["echoed_parameter_mismatches"] = mismatch
                if not mismatch:
                    record["status"] = "PASS"
            retryable = response.status_code == 429 or 500 <= response.status_code < 600
        except Exception as exc:
            retryable = True
            record.update(
                http_status=None,
                error_type=type(exc).__name__,
                error_message=redact(exc, secret),
            )
        record.update(retryable=retryable, finished_utc=now(), elapsed_seconds=time.monotonic() - start)
        attempt_path = ROOT / "attempts" / f"{qid}_q{query_index:02d}_page{page}_attempt{attempt}.json"
        save(attempt_path, record)
        attempts.append({"path": str(attempt_path.relative_to(ROOT)), "sha256": sha(attempt_path), "status": record["status"]})
        if record["status"] == "PASS":
            record["attempts"] = attempts
            record["artifact_path"] = str(final_path.relative_to(ROOT))
            save(final_path, record)
            return record, global_sequence
        if attempt == 3 or not retryable:
            break
        pause = float(attempt)
        if response is not None:
            try:
                pause = max(pause, min(30.0, float(response.headers.get("Retry-After", 0))))
            except ValueError:
                pass
        time.sleep(pause)
    raise RuntimeError(f"Search failed after {len(attempts)} attempt(s): {qid} query {query_index} page {page}")


def main():
    if os.environ.get("PYTHONHASHSEED") != str(MODEL_SEED):
        os.environ["PYTHONHASHSEED"] = str(MODEL_SEED)
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())])

    registration = verify_freeze()
    inputs = read(ROOT / "input_manifest.json")
    for name, expected in inputs["files"].items():
        assert sha(ROOT / name) == expected, name
    questions_path = ROOT / "questions.json"
    assert inputs["files"]["questions.json"] == sha(questions_path)
    questions = read(questions_path)["questions"]
    assert len(questions) == 50
    assert [q["question_id"] for q in questions] == [f"Q{i:02d}" for i in range(50)]
    pattern, cap = native_spec()
    prompt_template = read(REPO / "agent_prompt.json")["generate_query"]

    key = os.environ.get("SERPER_API_KEY", "").strip()
    key_source = "SERPER_API_KEY environment"
    if not key:
        secret_path = Path("/mnt/nvme3/chenyi/pasa/secrets/serper_api_key")
        key = secret_path.read_text().strip()
        key_source = "local protected serper_api_key file"
    assert key, "Serper credential unavailable"

    import numpy
    import requests
    import torch
    import transformers
    # Running this isolated script by path places only its experiment directory
    # on sys.path.  Add the repository solely to import the frozen native Agent.
    sys.path.insert(0, str(REPO))
    from models import Agent

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable: native checkpoint uses the CUDA/FlashAttention execution path")
    manifest_path = ROOT / "run_manifest.json"
    if manifest_path.exists():
        manifest = read(manifest_path)
        assert manifest["input_manifest_sha256"] == sha(ROOT / "input_manifest.json")
        assert manifest["status"] in {"RUNNING", "INCOMPLETE"}
        manifest["status"] = "RUNNING"
        manifest["resumed_utc"].append(now())
    else:
        checkpoint_files = {}
        for path in sorted(CHECKPOINT.iterdir()):
            if path.is_file():
                checkpoint_files[path.name] = {"bytes": path.stat().st_size, "sha256": sha(path)}
        manifest = {
            "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
            "status": "RUNNING",
            "started_utc": now(),
            "resumed_utc": [],
            "registration_manifest_sha256": sha(ROOT / "registration_manifest.json"),
            "input_manifest_sha256": sha(ROOT / "input_manifest.json"),
            "questions_sha256": sha(questions_path),
            "runner_sha256": sha(__file__),
            "common_sha256": sha(ROOT / "common.py"),
            "python": sys.version,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "requests": requests.__version__,
            "numpy": numpy.__version__,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "visible_gpu": torch.cuda.get_device_name(0),
            "checkpoint": str(CHECKPOINT),
            "checkpoint_files": checkpoint_files,
            "credential_source": key_source,
            "model_seed_per_question": MODEL_SEED,
            "native_query_regex": pattern,
            "native_query_cap": cap,
            "end_date": END_DATE,
            "search_parameters": {"num": 10, "pages": [1, 2]},
            "gt_isolation": "Collector reads questions.json only; dataset_manifest.json is not read or imported.",
            "prior_environment_preflight": {
                "formal_experiment_attempt": False,
                "search_requests": 0,
                "generated_tokens": 0,
                "outcome": "CPU checkpoint load succeeded, then first forward failed before token generation because the fixed FlashAttention path requires CUDA.",
            },
            "startup_attempts_before_run_manifest": [
                {
                    "generated_tokens": 0,
                    "search_requests": 0,
                    "outcome": "Initial CUDA launch exited before model load because isolated runner lacked repository import path; harness import path corrected without changing protocol or formal sources."
                }
            ],
            "successful_generations": 0,
            "successful_page1": 0,
            "successful_page2": 0,
            "http_attempts": 0,
        }
    save(manifest_path, manifest)

    client = requests.Session()
    headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    crawler = None
    existing_attempts = list((ROOT / "attempts").glob("*.json"))
    global_sequence = max(
        [manifest.get("http_attempts", 0)]
        + [read(path)["global_http_attempt_sequence"] for path in existing_attempts]
    )
    try:
        for q in questions:
            qid = q["question_id"]
            generation_path = ROOT / "generations" / f"{qid}.json"
            if generation_path.exists():
                generation = read(generation_path)
                assert generation["question"] == q["question"]
                assert generation["status"] == "PASS"
                queries = generation["queries"]
            else:
                if crawler is None:
                    crawler = Agent(str(CHECKPOINT))
                    assert crawler.model.generation_config.do_sample is True
                    manifest["effective_generation_config"] = crawler.model.generation_config.to_dict()
                    manifest["generation_call_override"] = {"max_new_tokens": 512}
                    save(manifest_path, manifest)
                seed_all(torch, numpy)
                prompt = prompt_template.format(user_query=q["question"]).strip()
                started = now()
                start = time.monotonic()
                raw = crawler.infer(prompt)
                parsed = [item.strip() for item in re.findall(pattern, raw, flags=re.DOTALL)]
                queries = parsed[:cap]
                generation = {
                    "status": "PASS" if queries else "ZERO_QUERIES",
                    "question_id": qid,
                    "question": q["question"],
                    "seed": MODEL_SEED,
                    "prompt": prompt,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "raw_output": raw,
                    "raw_output_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                    "all_parsed_queries": parsed,
                    "queries": queries,
                    "discarded_queries": parsed[cap:],
                    "started_utc": started,
                    "finished_utc": now(),
                    "elapsed_seconds": time.monotonic() - start,
                }
                save(generation_path, generation)
                if not queries:
                    raise RuntimeError(f"Native generation produced zero queries for {qid}")
                manifest["successful_generations"] += 1
                save(manifest_path, manifest)

            for query_index, query in enumerate(queries):
                for page in (1, 2):
                    record, global_sequence = request_page(
                        client, headers, key, qid, query_index, query, page, global_sequence
                    )
                    manifest[f"successful_page{page}"] = len(list((ROOT / "responses").glob(f"*_page{page}.json")))
                    manifest["http_attempts"] = global_sequence
                    save(manifest_path, manifest)
            print(
                f"{qid} complete: {len(queries)} native queries; "
                f"paired snapshots={manifest['successful_page1']}/{manifest['successful_page2']}; "
                f"HTTP attempts={global_sequence}",
                flush=True,
            )
        manifest.update(
            status="SNAPSHOT_COMPLETE",
            finished_utc=now(),
            successful_generations=len(list((ROOT / "generations").glob("Q*.json"))),
            successful_page1=len(list((ROOT / "responses").glob("*_page1.json"))),
            successful_page2=len(list((ROOT / "responses").glob("*_page2.json"))),
            http_attempts=global_sequence,
        )
        save(manifest_path, manifest)
        print("All frozen questions and paired Page1/Page2 snapshots collected.", flush=True)
    except BaseException as exc:
        manifest.update(
            status="INCOMPLETE",
            stopped_utc=now(),
            failure_type=type(exc).__name__,
            failure_message=redact(exc, key),
            http_attempts=global_sequence,
        )
        save(manifest_path, manifest)
        raise


if __name__ == "__main__":
    main()
