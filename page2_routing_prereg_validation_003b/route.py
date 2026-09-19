"""Build immutable snapshot/state manifests and freeze Page1-only decisions."""
import base64
import hashlib
import json
from pathlib import Path

from common import ROOT, digest, ids, now, read, save, sha, verify_freeze


def response(path, expected_payload):
    record = read(path)
    assert record["status"] == "PASS", path
    assert record["request_payload"] == expected_payload, path
    raw = base64.b64decode(record["raw_response_base64"])
    assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"], path
    assert json.loads(raw) == record["structured_response"], path
    echoed = record["structured_response"].get("searchParameters", {})
    for key, value in expected_payload.items():
        if key in echoed:
            assert echoed[key] == value, (path, key)
    return record


def jaccard(left, right):
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def main():
    verify_freeze()
    run = read(ROOT / "run_manifest.json")
    assert run["status"] == "SNAPSHOT_COMPLETE"
    questions = read(ROOT / "questions.json")["questions"]
    snapshots = {}
    states = []
    decisions = []
    for q in questions:
        qid = q["question_id"]
        generation_path = ROOT / "generations" / f"{qid}.json"
        generation = read(generation_path)
        assert generation["status"] == "PASS" and generation["question"] == q["question"]
        query_rows = []
        page1_sets = []
        for index, query in enumerate(generation["queries"]):
            key = f"{qid}/q{index:02d}"
            pair = {}
            for page in (1, 2):
                payload = {"q": f"{query} before:2026-09-17 site:arxiv.org", "num": 10, "page": page}
                path = ROOT / "responses" / f"{qid}_q{index:02d}_page{page}.json"
                record = response(path, payload)
                pair[f"page{page}"] = {
                    "path": str(path.relative_to(ROOT)),
                    "file_sha256": sha(path),
                    "response_bytes_sha256": record["response_bytes_sha256"],
                    "request_payload": payload,
                    "started_utc": record["started_utc"],
                    "finished_utc": record["finished_utc"],
                    "arxiv_ids": ids(record["structured_response"]),
                    "organic_count": len(record["structured_response"]["organic"]),
                    "successful_attempt": record["attempt"],
                }
            snapshots[key] = {
                "question_id": qid,
                "query_index": index,
                "native_query": query,
                "generation_path": str(generation_path.relative_to(ROOT)),
                "generation_file_sha256": sha(generation_path),
                **pair,
            }
            page1_sets.append(set(pair["page1"]["arxiv_ids"]))
            query_rows.append({
                "query_key": key,
                "query_index": index,
                "native_query": query,
                "page1_ids": pair["page1"]["arxiv_ids"],
                "page1_count": len(pair["page1"]["arxiv_ids"]),
            })
        assert query_rows, qid
        for index, row in enumerate(query_rows):
            row["pairwise_page1_jaccard"] = [
                {"other_query_index": other, "jaccard": jaccard(page1_sets[index], page1_sets[other])}
                for other in range(len(query_rows)) if other != index
            ]
            row["max_jaccard"] = max(
                (item["jaccard"] for item in row["pairwise_page1_jaccard"]), default=0.0
            )
        selected = min(query_rows, key=lambda row: (-row["max_jaccard"], row["query_index"]))
        states.append({
            "question_id": qid,
            "question": q["question"],
            "generation_path": str(generation_path.relative_to(ROOT)),
            "queries": query_rows,
        })
        decisions.append({
            "question_id": qid,
            "selected_query_key": selected["query_key"],
            "selected_query_index": selected["query_index"],
            "selected_native_query": selected["native_query"],
            "selected_max_jaccard": selected["max_jaccard"],
            "ranking": [
                {"query_key": row["query_key"], "query_index": row["query_index"], "max_jaccard": row["max_jaccard"]}
                for row in sorted(query_rows, key=lambda row: (-row["max_jaccard"], row["query_index"]))
            ],
            "tie_break": "Smallest original native generation index among equal max_jaccard scores.",
        })
    snapshot_id = digest(snapshots)
    snapshot_manifest = {
        "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "status": "COMPLETE",
        "created_utc": now(),
        "snapshot_id": snapshot_id,
        "query_count": len(snapshots),
        "page1_successful": len(snapshots),
        "page2_successful": len(snapshots),
        "logical_search_calls": 2 * len(snapshots),
        "actual_page2_collection_policy": "Always Page2 for offline replay of all preregistered policies.",
        "pairing": "For each native query, Page1 then Page2 were requested consecutively except recorded retries/resume boundaries.",
        "snapshots": snapshots,
        "run_manifest_sha256": sha(ROOT / "run_manifest.json"),
    }
    save(ROOT / "snapshot_manifest.json", snapshot_manifest)
    save(ROOT / "states.json", {
        "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "created_utc": now(),
        "snapshot_id": snapshot_id,
        "feature_scope": "Only Page1 arXiv ID sets; no GT, Page2 outcome, lexical relevance, or other feature.",
        "score": "max_jaccard(i)=max over other queries j of |S_i intersect S_j|/|S_i union S_j|; 0 for one query or empty union.",
        "questions": states,
    })
    save(ROOT / "decisions.json", {
        "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "created_utc": now(),
        "snapshot_id": snapshot_id,
        "states_sha256": sha(ROOT / "states.json"),
        "policy": "Highest Page1 max_jaccard per question; deterministic original-index tie-break.",
        "gt_reads": 0,
        "page2_outcome_reads_for_routing": 0,
        "decisions": decisions,
    })
    print(f"Frozen {len(snapshots)} paired query snapshots and {len(decisions)} Page1-only decisions.")


if __name__ == "__main__":
    main()
