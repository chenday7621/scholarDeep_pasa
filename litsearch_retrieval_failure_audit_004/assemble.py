"""Assemble probe evidence, expert annotations, and computed summaries."""
from collections import Counter, defaultdict
import base64
import hashlib
import json
import statistics

from annotations import ANNOTATIONS
from common import ROOT, SOURCE, now, read, save, sha, verify_source

CATEGORIES = ["QUERY_DIRECTION_MISS", "RANKING_DEPTH_MISS", "SOURCE_INDEX_MISS", "UNCERTAIN"]

def verify_raw(record):
    raw = base64.b64decode(record["raw_response_base64"])
    assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"]
    assert json.loads(raw) == record["structured_response"]

def automatic_suggestion(case, probes, depth_ranks):
    exact = bool(probes["exact_gt_title"]["gold_hit_ranks"])
    core = bool(probes["gt_core_phrase"]["gold_hit_ranks"])
    if depth_ranks:
        return "RANKING_DEPTH_MISS", "GT appears on Page3-5 for the fixed direction-plausible native query."
    if not exact and not core:
        return "SOURCE_INDEX_MISS", "Neither exact title nor deterministic core phrase retrieves GT in diagnostic Top10."
    x = case["lexical"]
    if (x["native_union_question_supported_gt_element_coverage"] < 0.60 or
            x["query_reformulation_gt_similarity_delta"] < -0.02):
        return "QUERY_DIRECTION_MISS", "Low supported-element coverage or native reformulation moves materially farther from GT metadata."
    return "UNCERTAIN", "Exact/core search works but there is neither a direct deep-rank hit nor sufficiently strong automatic direction-miss evidence."

def counts(records, field="final_category"):
    counter = Counter(record[field] for record in records)
    return {category: {"count": counter[category], "fraction": counter[category] / len(records) if records else None} for category in CATEGORIES}

def main():
    _, snapshots = verify_source()
    inputs = read(ROOT / "input_manifest.json")
    for name, expected in inputs["source_files"].items(): assert sha(SOURCE / name) == expected, name
    for name, expected in inputs["response_files"].items(): assert sha(SOURCE / name) == expected, name
    offline = read(ROOT / "offline_evidence.json")
    assert offline["input_manifest_sha256"] == sha(ROOT / "input_manifest.json")
    probe_plan = read(ROOT / "probe_plan.json"); depth_plan = read(ROOT / "depth_probe_plan.json")
    assert (ROOT / "probe_plan.sha256").read_text().split()[0] == sha(ROOT / "probe_plan.json")
    assert (ROOT / "depth_probe_plan.sha256").read_text().split()[0] == sha(ROOT / "depth_probe_plan.json")
    assert read(ROOT / "probe_run_manifest.json")["status"] == "COMPLETE"
    assert read(ROOT / "depth_probe_run_manifest.json")["status"] == "COMPLETE"
    probe_results, response_hashes = {}, {}
    for case in offline["cases"]:
        qid = case["question_id"]; probe_results[qid] = {}
        for kind in ("exact_gt_title", "gt_core_phrase", "original_question"):
            path = ROOT / "probe_responses" / f"{qid}_{kind}.json"; record = read(path); verify_raw(record)
            assert record["question_id"] == qid and record["probe_kind"] == kind
            response_hashes[str(path.relative_to(ROOT))] = sha(path)
            probe_results[qid][kind] = {"request_payload": record["request_payload"], "response_path": str(path.relative_to(ROOT)), "response_sha256": sha(path), "response_bytes_sha256": record["response_bytes_sha256"], "http_status": record["http_status"], "organic_count": len(record["hits"]), "gold_hit_ranks": record["gold_hit_ranks"], "top_hits": record["hits"][:5]}
    depth_by_q = defaultdict(list)
    for probe in depth_plan["probes"]:
        path = ROOT / "depth_probe_responses" / f"{probe['question_id']}_q{probe['native_query_index']:02d}_page{probe['page']}.json"; record = read(path); verify_raw(record)
        response_hashes[str(path.relative_to(ROOT))] = sha(path)
        depth_by_q[probe["question_id"]].append({"page": probe["page"], "native_query_index": probe["native_query_index"], "native_query": probe["native_query"], "response_path": str(path.relative_to(ROOT)), "response_sha256": sha(path), "response_bytes_sha256": record["response_bytes_sha256"], "gold_hit_nominal_ranks": record["gold_hit_nominal_ranks"], "top_hits": record["hits"][:5]})
    save(ROOT / "diagnostic_probe_results.json", {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "status": "COMPLETE", "created_utc": now(), "gt_aware": True, "diagnostic_only": True, "not_a_deployable_policy": True, "not_a_performance_estimate": True, "source_snapshot_id": snapshots["snapshot_id"], "probe_plan_sha256": sha(ROOT / "probe_plan.json"), "depth_probe_plan_sha256": sha(ROOT / "depth_probe_plan.json"), "panel": {"page1_requests": 114, "depth_requests": 45, "total_requests": 159, "http_attempts": read(ROOT / "probe_run_manifest.json")["http_attempts"] + read(ROOT / "depth_probe_run_manifest.json")["http_attempts"], "exact_title_hit_questions": sum(bool(value["exact_gt_title"]["gold_hit_ranks"]) for value in probe_results.values()), "core_phrase_hit_questions": sum(bool(value["gt_core_phrase"]["gold_hit_ranks"]) for value in probe_results.values()), "original_question_hit_questions": sum(bool(value["original_question"]["gold_hit_ranks"]) for value in probe_results.values()), "depth_eligible_questions": len(depth_by_q), "depth_hit_questions": sum(any(item["gold_hit_nominal_ranks"] for item in items) for items in depth_by_q.values())}, "cases": {qid: {"page1_diagnostics": probes, "depth_diagnostics": depth_by_q.get(qid, [])} for qid, probes in probe_results.items()}, "response_hashes": response_hashes})
    diagnostic_hash = sha(ROOT / "diagnostic_probe_results.json")
    cases = []
    for case in offline["cases"]:
        qid = case["question_id"]; probes = probe_results[qid]; depth = depth_by_q.get(qid, []); depth_ranks = sorted(rank for item in depth for rank in item["gold_hit_nominal_ranks"])
        suggested, reason = automatic_suggestion(case, probes, depth_ranks)
        final_category, confidence, modes, rationale = ANNOTATIONS[qid]
        assert final_category in CATEGORIES and confidence in {"high", "medium", "low"}
        page_counts = {}
        for page in (1, 2):
            hits = [hit for query in case["queries"] for page_record in query["pages"] if page_record["page"] == page for hit in page_record["hits"]]
            page_counts[f"page{page}"] = {"organic": len(hits), "arxiv_parseable": sum(hit["arxiv_id"] is not None for hit in hits), "arxiv_ratio": sum(hit["arxiv_id"] is not None for hit in hits) / len(hits) if hits else None}
        evidence = {"exact_title_gold_ranks": probes["exact_gt_title"]["gold_hit_ranks"], "core_phrase_gold_ranks": probes["gt_core_phrase"]["gold_hit_ranks"], "original_question_gold_ranks": probes["original_question"]["gold_hit_ranks"], "depth_gold_nominal_ranks": depth_ranks, "depth_probe_performed": bool(depth), "native_union_question_supported_gt_element_coverage": case["lexical"]["native_union_question_supported_gt_element_coverage"], "native_union_question_content_coverage": case["lexical"]["native_union_question_content_coverage"], "native_union_gt_title_coverage": case["lexical"]["native_union_gt_title_coverage"], "question_to_gt_metadata_tfidf": case["lexical"]["question_to_gt_metadata"]["tfidf_cosine"], "best_native_query_to_gt_metadata_tfidf": case["lexical"]["best_native_query_to_gt_metadata_tfidf"], "query_reformulation_gt_similarity_delta": case["lexical"]["query_reformulation_gt_similarity_delta"], "frozen_result_to_gt_metadata_similarity_max": case["lexical"]["result_to_gt_metadata_similarity_max"], "page_source_adherence": page_counts}
        cases.append({"question_id": qid, "group": case["group"], "row_index": case["row_index"], "question": case["question"], "gold": case["gold"], "native_queries": [{"query_index": row["query_index"], "native_query": row["native_query"], "query_to_gt_title": row["query_to_gt_title"], "query_to_gt_metadata": row["query_to_gt_metadata"], "question_supported_gt_element_coverage": row["question_supported_gt_element_coverage"], "result_gt_similarity_max": row["result_gt_similarity_max"]} for row in case["query_features"]], "question_supported_gt_elements": case["lexical"]["question_supported_gt_elements"], "native_query_union_tokens": case["lexical"]["native_query_union_tokens"], "top_frozen_result_evidence": case["result_evidence"], "diagnostic_evidence": evidence, "automatic_rule_suggestion": suggested, "automatic_rule_reason": reason, "final_category": final_category, "confidence": confidence, "failure_modes": modes, "expert_rationale": rationale, "manual_override_of_automatic_suggestion": final_category != suggested, "evidence_paths": {"offline_evidence": "offline_evidence.json", "diagnostic_probe_results": "diagnostic_probe_results.json", "generation": case["generation_path"]}})
    assert [case["question_id"] for case in cases] == inputs["miss_question_ids"]
    save(ROOT / "failure_cases.json", {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "status": "COMPLETE", "created_utc": now(), "source_snapshot_id": snapshots["snapshot_id"], "input_manifest_sha256": sha(ROOT / "input_manifest.json"), "offline_evidence_sha256": sha(ROOT / "offline_evidence.json"), "diagnostic_probe_results_sha256": diagnostic_hash, "annotation_source_sha256": sha(ROOT / "annotations.py"), "classification_policy": {"categories": CATEGORIES, "ranking_depth_requires_positive_evidence": "RANKING_DEPTH_MISS is assigned only if GT is directly observed beyond Page2 for a direction-plausible native query.", "source_index_rule": "Exact GT title and deterministic core phrase both miss Top10 supports SOURCE_INDEX_MISS.", "query_direction_rule": "Requires exact/core source availability plus concrete missing/fragmented key concepts or task drift; broad similarity alone is insufficient.", "uncertain_rule": "Use when evidence cannot distinguish query wording, volatile ranking, or source behavior.", "automatic_then_expert": "Automatic suggestion retained; structured expert review may override with rationale."}, "cases": cases})
    category_counts = counts(cases); group_summaries = {}
    for group in ("author-written", "inline-citation"):
        subset = [case for case in cases if case["group"] == group]
        group_summaries[group] = {"questions": len(subset), "categories": counts(subset), "failure_modes": dict(Counter(mode for case in subset for mode in case["failure_modes"])), "high_confidence": sum(case["confidence"] == "high" for case in subset)}
    modes = Counter(mode for case in cases for mode in case["failure_modes"])
    direction_cases = [case for case in cases if case["final_category"] == "QUERY_DIRECTION_MISS"]
    direction_modes = Counter(mode for case in direction_cases for mode in case["failure_modes"])
    native_queries = [query["native_query"] for case in cases for query in case["native_queries"]]
    survey_queries = [query for query in native_queries if "survey" in query.casefold()]
    source_stats = {}
    for page in ("page1", "page2"):
        totals = [case["diagnostic_evidence"]["page_source_adherence"][page] for case in cases]
        source_stats[page] = {"organic": sum(row["organic"] for row in totals), "arxiv_parseable": sum(row["arxiv_parseable"] for row in totals), "arxiv_ratio": sum(row["arxiv_parseable"] for row in totals) / sum(row["organic"] for row in totals)}
    attributable = [case for case in cases if case["final_category"] != "UNCERTAIN"]
    summary = {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "status": "COMPLETE", "created_utc": now(), "miss_questions": len(cases), "categories": category_counts, "groups": group_summaries, "failure_modes": dict(modes.most_common()), "query_direction_failure_modes": dict(direction_modes.most_common()), "native_query_surface_patterns": {"native_queries": len(native_queries), "survey_queries": len(survey_queries), "survey_query_fraction": len(survey_queries) / len(native_queries), "questions_with_survey_query": sum(any("survey" in query["native_query"].casefold() for query in case["native_queries"]) for case in cases)}, "confidence": dict(Counter(case["confidence"] for case in cases)), "automatic_manual_agreement": {"same": sum(not case["manual_override_of_automatic_suggestion"] for case in cases), "overridden": sum(case["manual_override_of_automatic_suggestion"] for case in cases)}, "diagnostic_probes": read(ROOT / "diagnostic_probe_results.json")["panel"], "frozen_source_adherence": source_stats, "hypothesis_assessment": {"hypothesis": "The main bottleneck is native query quality/direction rather than Page2 having no value.", "verdict": "NOT_SUPPORTED_AS_PRIMARY_EXPLANATION", "reason": "Only 11/38 are confidently query-direction misses; 20/38 remain uncertain, 7/38 fail even exact/core identity search, and no GT appeared in Page3-5 for 15 direction-plausible native-query diagnostics. Among the 18 attributable cases, query-direction misses outnumber source-index misses 11 to 7, but this is insufficient to call query quality the dominant explanation for all 38. Frozen Page2 also has only 17.5% parseable arXiv URLs versus 100% on Page1, so current provider pagination behavior is itself a material confound."}, "next_experiment_priority": [{"rank": 1, "experiment": "FEEDBACK_REQUERY", "scope": "Preregister on QUERY_DIRECTION_MISS cases; use question plus frozen Page1 evidence without GT; target missing bridge terms and constraint preservation."}, {"rank": 2, "experiment": "CITATION_EXPANSION", "scope": "Preregister on UNCERTAIN cases with topical Page1 neighbors and hidden title terminology; evaluate whether citations bridge to GT."}, {"rank": 3, "experiment": "ALTERNATIVE_RETRIEVAL_SOURCE", "scope": "Target seven SOURCE_INDEX_MISS cases and compare arXiv-native/Semantic Scholar retrieval against frozen Serper behavior."}, {"rank": 4, "experiment": "DEEPER_PAGEN", "scope": "Low priority: fixed Page3-5 diagnostics found 0/15 GT for direction-plausible native queries, and frozen Page2 source adherence degraded sharply."}], "artifacts": {"input_manifest.json": sha(ROOT / "input_manifest.json"), "offline_evidence.json": sha(ROOT / "offline_evidence.json"), "probe_plan.json": sha(ROOT / "probe_plan.json"), "depth_probe_plan.json": sha(ROOT / "depth_probe_plan.json"), "diagnostic_probe_results.json": diagnostic_hash, "failure_cases.json": sha(ROOT / "failure_cases.json")}}
    save(ROOT / "failure_summary.json", summary)
    print(json.dumps({"categories": category_counts, "groups": {key: value["categories"] for key, value in group_summaries.items()}, "probes": summary["diagnostic_probes"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
