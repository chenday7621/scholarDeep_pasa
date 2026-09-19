"""Independent integrity and statistics validator for audit 004."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SOURCE = REPO / "page2_routing_prereg_validation_003b"
REPORT = ROOT / "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004.md"
PAPER_AGENT_SHA256_AT_AUDIT = "54a9e5829726ed0275cf7ed1f82f0ab83f0371687a97d1c75b6d5e2be3837993"
CATEGORIES = (
    "QUERY_DIRECTION_MISS",
    "RANKING_DEPTH_MISS",
    "SOURCE_INDEX_MISS",
    "UNCERTAIN",
)
ARXIV_PATTERN = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)")


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def raw_json(record):
    raw = base64.b64decode(record["raw_response_base64"], validate=True)
    assert len(raw) == record["response_bytes"]
    assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"]
    structured = json.loads(raw)
    assert structured == record["structured_response"]
    return structured


def parsed_id(link):
    match = ARXIV_PATTERN.search(link or "")
    return match.group(1) if match else None


def frozen_hits(record):
    structured = raw_json(record)
    return [
        {
            "rank": rank,
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
            "arxiv_id": parsed_id(item.get("link", "")),
        }
        for rank, item in enumerate(structured.get("organic", []), 1)
    ]


def load_annotations():
    spec = importlib.util.spec_from_file_location("audit004_annotations", ROOT / "annotations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ANNOTATIONS


def fraction_counts(cases):
    counter = Counter(case["final_category"] for case in cases)
    return {
        category: {
            "count": counter[category],
            "fraction": counter[category] / len(cases) if cases else None,
        }
        for category in CATEGORIES
    }


def main():
    checks = {}

    source_validation = read(SOURCE / "validation.json")
    assert source_validation["status"] == "PASS"
    for name, expected in source_validation["artifact_hashes"].items():
        path = SOURCE / name
        assert path.exists(), name
        assert sha(path) == expected, name
    for name, expected in source_validation["source_hashes"].items():
        assert sha(SOURCE / name) == expected, name
    assert (SOURCE / "PREREGISTRATION.sha256").read_text().split()[0] == sha(
        SOURCE / "PREREGISTRATION.md"
    )
    assert (SOURCE / "MAPPING_AMENDMENT.sha256").read_text().split()[0] == sha(
        SOURCE / "MAPPING_AMENDMENT.md"
    )
    checks["source_003b_artifact_and_protocol_hashes"] = True

    snapshot = read(SOURCE / "snapshot_manifest.json")
    assert snapshot["status"] == "COMPLETE"
    assert snapshot["query_count"] == len(snapshot["snapshots"]) == 222
    frozen_response_count = 0
    for query_key, item in snapshot["snapshots"].items():
        assert query_key == f"{item['question_id']}/q{item['query_index']:02d}"
        generation_path = SOURCE / item["generation_path"]
        assert sha(generation_path) == item["generation_file_sha256"]
        generation = read(generation_path)
        assert generation["queries"][item["query_index"]] == item["native_query"]
        for page in ("page1", "page2"):
            manifest_record = item[page]
            path = SOURCE / manifest_record["path"]
            assert sha(path) == manifest_record["file_sha256"]
            response = read(path)
            assert response["status"] == "PASS"
            assert response["request_payload"] == manifest_record["request_payload"]
            assert response["response_bytes_sha256"] == manifest_record["response_bytes_sha256"]
            assert raw_json(response) == response["structured_response"]
            frozen_response_count += 1
    assert frozen_response_count == 444
    checks["source_003b_222_paired_snapshots_and_444_raw_responses"] = True

    manifest = read(ROOT / "input_manifest.json")
    for name, expected in manifest["source_files"].items():
        assert sha(SOURCE / name) == expected, name
    for name, expected in manifest["response_files"].items():
        assert sha(SOURCE / name) == expected, name
    outcomes = read(SOURCE / "evaluation_question_outcomes.json")["questions"]
    misses = [
        row for row in outcomes
        if row["base_gt_found"] == 0 and row["always_gain"] == 0
    ]
    miss_ids = [row["question_id"] for row in misses]
    assert len(misses) == 38
    assert Counter(row["group"] for row in misses) == {
        "author-written": 16,
        "inline-citation": 22,
    }
    assert miss_ids == manifest["miss_question_ids"]
    assert manifest["miss_definition"] == "base_gt_found == 0 and always_gain == 0"
    checks["miss_panel_rederived_38_with_16_22_groups"] = True

    offline = read(ROOT / "offline_evidence.json")
    assert offline["input_manifest_sha256"] == sha(ROOT / "input_manifest.json")
    assert [case["question_id"] for case in offline["cases"]] == miss_ids
    native_query_count = sum(len(case["queries"]) for case in offline["cases"])
    assert native_query_count == 172
    checks["offline_evidence_panel_and_172_native_queries"] = True

    probe_plan = read(ROOT / "probe_plan.json")
    depth_plan = read(ROOT / "depth_probe_plan.json")
    assert probe_plan["status"] == "FROZEN_BEFORE_REQUESTS"
    assert probe_plan["requests_at_freeze"] == 0
    assert probe_plan["gt_aware"] and probe_plan["not_a_deployable_policy"]
    assert len(probe_plan["probes"]) == 114
    assert (ROOT / "probe_plan.sha256").read_text().split()[0] == sha(
        ROOT / "probe_plan.json"
    )
    assert depth_plan["status"] == "FROZEN_BEFORE_DEPTH_REQUESTS"
    assert depth_plan["requests_at_freeze"] == 0
    assert depth_plan["gt_aware"] and depth_plan["diagnostic_only"]
    assert depth_plan["not_a_deployable_policy"]
    assert len(depth_plan["probes"]) == 45
    assert len({probe["question_id"] for probe in depth_plan["probes"]}) == 15
    assert (ROOT / "depth_probe_plan.sha256").read_text().split()[0] == sha(
        ROOT / "depth_probe_plan.json"
    )
    checks["diagnostic_plans_frozen_before_114_plus_45_requests"] = True

    plan_by_key = {
        (probe["question_id"], probe["kind"]): probe
        for probe in probe_plan["probes"]
    }
    assert len(plan_by_key) == 114
    page1_counts = Counter()
    diagnostic_hashes = {}
    for key, probe in plan_by_key.items():
        qid, kind = key
        path = ROOT / "probe_responses" / f"{qid}_{kind}.json"
        record = read(path)
        assert record["status"] == "PASS" and record["http_status"] == 200
        assert record["question_id"] == qid and record["probe_kind"] == kind
        assert record["request_payload"] == probe["payload"]
        hits = frozen_hits(record)
        assert hits == record["hits"]
        ranks = [hit["rank"] for hit in hits if hit["arxiv_id"] == probe["gold_arxiv_id"]]
        assert ranks == record["gold_hit_ranks"]
        page1_counts[kind] += bool(ranks)
        diagnostic_hashes[str(path.relative_to(ROOT))] = sha(path)
    assert page1_counts == {
        "exact_gt_title": 31,
        "gt_core_phrase": 31,
        "original_question": 2,
    }

    depth_by_key = {
        (probe["question_id"], probe["native_query_index"], probe["page"]): probe
        for probe in depth_plan["probes"]
    }
    assert len(depth_by_key) == 45
    depth_hit_questions = set()
    for key, probe in depth_by_key.items():
        qid, query_index, page = key
        path = ROOT / "depth_probe_responses" / f"{qid}_q{query_index:02d}_page{page}.json"
        record = read(path)
        assert record["status"] == "PASS" and record["http_status"] == 200
        assert record["payload"] == probe["payload"]
        structured = raw_json(record)
        hits = [
            {
                "rank_on_page": rank,
                "nominal_rank": 10 * (page - 1) + rank,
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
                "arxiv_id": parsed_id(item.get("link", "")),
            }
            for rank, item in enumerate(structured.get("organic", []), 1)
        ]
        assert hits == record["hits"]
        ranks = [
            hit["nominal_rank"]
            for hit in hits
            if hit["arxiv_id"] == probe["gold_arxiv_id"]
        ]
        assert ranks == record["gold_hit_nominal_ranks"]
        if ranks:
            depth_hit_questions.add(qid)
        diagnostic_hashes[str(path.relative_to(ROOT))] = sha(path)
    assert not depth_hit_questions
    checks["all_159_probe_payloads_raw_bytes_hashes_and_hits"] = True
    checks["probe_hits_recomputed_exact31_core31_question2_depth0of15"] = True

    probe_run = read(ROOT / "probe_run_manifest.json")
    depth_run = read(ROOT / "depth_probe_run_manifest.json")
    assert probe_run["status"] == depth_run["status"] == "COMPLETE"
    assert probe_run["successful_responses"] == probe_run["http_attempts"] == 114
    assert depth_run["successful_responses"] == depth_run["http_attempts"] == 45
    assert len(list((ROOT / "probe_responses").glob("*.json"))) == 114
    assert len(list((ROOT / "depth_probe_responses").glob("*.json"))) == 45
    checks["probe_run_manifests_complete_without_retries"] = True

    diagnostic = read(ROOT / "diagnostic_probe_results.json")
    assert diagnostic["gt_aware"] and diagnostic["diagnostic_only"]
    assert diagnostic["not_a_deployable_policy"]
    assert diagnostic["not_a_performance_estimate"]
    assert diagnostic["response_hashes"] == diagnostic_hashes
    expected_panel = {
        "page1_requests": 114,
        "depth_requests": 45,
        "total_requests": 159,
        "http_attempts": 159,
        "exact_title_hit_questions": 31,
        "core_phrase_hit_questions": 31,
        "original_question_hit_questions": 2,
        "depth_eligible_questions": 15,
        "depth_hit_questions": 0,
    }
    assert diagnostic["panel"] == expected_panel
    checks["diagnostic_result_index_recomputed"] = True

    failure_file = read(ROOT / "failure_cases.json")
    cases = failure_file["cases"]
    assert [case["question_id"] for case in cases] == miss_ids
    assert len(cases) == 38
    annotations = load_annotations()
    assert set(annotations) == set(miss_ids)
    for case in cases:
        annotated = annotations[case["question_id"]]
        assert (
            case["final_category"],
            case["confidence"],
            case["failure_modes"],
            case["expert_rationale"],
        ) == annotated
        assert case["final_category"] in CATEGORIES
        if case["final_category"] == "RANKING_DEPTH_MISS":
            assert case["diagnostic_evidence"]["depth_gold_nominal_ranks"]
    recomputed_categories = fraction_counts(cases)
    assert recomputed_categories == {
        "QUERY_DIRECTION_MISS": {"count": 11, "fraction": 11 / 38},
        "RANKING_DEPTH_MISS": {"count": 0, "fraction": 0 / 38},
        "SOURCE_INDEX_MISS": {"count": 7, "fraction": 7 / 38},
        "UNCERTAIN": {"count": 20, "fraction": 20 / 38},
    }
    recomputed_groups = {}
    for group in ("author-written", "inline-citation"):
        subset = [case for case in cases if case["group"] == group]
        recomputed_groups[group] = fraction_counts(subset)
    assert {category: row["count"] for category, row in recomputed_groups["author-written"].items()} == {
        "QUERY_DIRECTION_MISS": 3,
        "RANKING_DEPTH_MISS": 0,
        "SOURCE_INDEX_MISS": 1,
        "UNCERTAIN": 12,
    }
    assert {category: row["count"] for category, row in recomputed_groups["inline-citation"].items()} == {
        "QUERY_DIRECTION_MISS": 8,
        "RANKING_DEPTH_MISS": 0,
        "SOURCE_INDEX_MISS": 6,
        "UNCERTAIN": 8,
    }
    checks["classifications_and_group_counts_recomputed"] = True
    checks["ranking_depth_requires_positive_evidence_and_is_zero"] = True

    source_counts = {
        1: {"organic": 0, "arxiv_parseable": 0},
        2: {"organic": 0, "arxiv_parseable": 0},
    }
    offline_by_id = {case["question_id"]: case for case in offline["cases"]}
    for qid in miss_ids:
        for query in offline_by_id[qid]["queries"]:
            for page_record in query["pages"]:
                page = page_record["page"]
                source_counts[page]["organic"] += len(page_record["hits"])
                source_counts[page]["arxiv_parseable"] += sum(
                    hit["arxiv_id"] is not None for hit in page_record["hits"]
                )
    assert source_counts == {
        1: {"organic": 1706, "arxiv_parseable": 1706},
        2: {"organic": 1579, "arxiv_parseable": 277},
    }
    checks["frozen_page_source_adherence_recomputed"] = True

    summary = read(ROOT / "failure_summary.json")
    assert summary["categories"] == recomputed_categories
    for group in recomputed_groups:
        assert summary["groups"][group]["categories"] == recomputed_groups[group]
    assert summary["diagnostic_probes"] == expected_panel
    assert summary["frozen_source_adherence"]["page1"] == {
        **source_counts[1],
        "arxiv_ratio": 1.0,
    }
    assert summary["frozen_source_adherence"]["page2"] == {
        **source_counts[2],
        "arxiv_ratio": 277 / 1579,
    }
    assert summary["hypothesis_assessment"]["verdict"] == "NOT_SUPPORTED_AS_PRIMARY_EXPLANATION"
    checks["failure_summary_recomputed_and_consistent"] = True

    assert REPORT.exists() and REPORT.stat().st_size > 0
    report_text = REPORT.read_text()
    for required in (
        "QUERY_DIRECTION_MISS",
        "RANKING_DEPTH_MISS",
        "SOURCE_INDEX_MISS",
        "UNCERTAIN",
        "FEEDBACK_REQUERY",
        "Citation Expansion",
        "retrieval source",
        "Page2 source-adherence",
        "不是可部署策略",
    ):
        assert required in report_text, required
    checks["report_exists_and_answers_required_sections"] = True

    paper_agent = REPO / "paper_agent.py"
    assert sha(paper_agent) == PAPER_AGENT_SHA256_AT_AUDIT
    git_check = subprocess.run(
        ["git", "diff", "--quiet", "--", "paper_agent.py"],
        cwd=REPO,
        check=False,
    )
    assert git_check.returncode == 0
    checks["paper_agent_unchanged"] = True

    artifacts = {}
    for name in (
        "input_manifest.json",
        "offline_evidence.json",
        "probe_plan.json",
        "depth_probe_plan.json",
        "probe_run_manifest.json",
        "depth_probe_run_manifest.json",
        "diagnostic_probe_results.json",
        "failure_cases.json",
        "failure_summary.json",
        "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004.md",
    ):
        artifacts[name] = sha(ROOT / name)
    result = {
        "experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004",
        "status": "PASS",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "counts": {
            "miss_questions": 38,
            "author_written": 16,
            "inline_citation": 22,
            "native_queries": 172,
            "source_snapshot_queries": 222,
            "source_raw_responses": 444,
            "diagnostic_page1_responses": 114,
            "diagnostic_depth_responses": 45,
            "diagnostic_total_responses": 159,
            "exact_title_hit_questions": 31,
            "core_phrase_hit_questions": 31,
            "original_question_hit_questions": 2,
            "depth_hit_questions": 0,
            "categories": {key: value["count"] for key, value in recomputed_categories.items()},
            "groups": {
                group: {key: value["count"] for key, value in values.items()}
                for group, values in recomputed_groups.items()
            },
        },
        "protected_hashes": {
            "paper_agent.py": sha(paper_agent),
            "003b_snapshot_manifest.json": sha(SOURCE / "snapshot_manifest.json"),
            "003b_PREREGISTRATION.md": sha(SOURCE / "PREREGISTRATION.md"),
            "003b_MAPPING_AMENDMENT.md": sha(SOURCE / "MAPPING_AMENDMENT.md"),
        },
        "artifact_hashes": artifacts,
    }
    temporary = ROOT / "validation.json.tmp"
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(ROOT / "validation.json")
    print(json.dumps({"status": "PASS", "checks": len(checks), "counts": result["counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
