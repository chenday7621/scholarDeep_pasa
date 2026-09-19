"""Freeze a narrow GT-aware Page3-5 diagnostic subset for depth evidence."""
from common import END_DATE, ROOT, now, read, save, sha, verify_source

def main():
    verify_source()
    assert not (ROOT / "depth_probe_plan.json").exists()
    offline = read(ROOT / "offline_evidence.json")
    selected = []
    for case in offline["cases"]:
        exact = read(ROOT / "probe_responses" / f"{case['question_id']}_exact_gt_title.json")
        x = case["lexical"]
        eligible = bool(exact["gold_hit_ranks"]) and x["native_union_question_supported_gt_element_coverage"] >= 0.75 and (x["best_native_query_to_gt_metadata_tfidf"] >= 0.15 or x["result_to_gt_metadata_similarity_max"] >= 0.20)
        if not eligible: continue
        best = max(case["query_features"], key=lambda row: (row["query_to_gt_metadata"]["tfidf_cosine"], -row["query_index"]))
        for page in (3, 4, 5):
            selected.append({"sequence": len(selected) + 1, "question_id": case["question_id"], "group": case["group"], "native_query_index": best["query_index"], "native_query": best["native_query"], "selection_reason": "Fixed eligibility thresholds plus highest GT-metadata TF-IDF native query; GT-aware diagnostic only.", "gold_arxiv_id": case["gold"]["arxiv_id"], "page": page, "payload": {"q": f"{best['native_query']} before:{END_DATE} site:arxiv.org", "num": 10, "page": page}})
    assert len(selected) == 45 and len({row["question_id"] for row in selected}) == 15
    save(ROOT / "depth_probe_plan.json", {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "status": "FROZEN_BEFORE_DEPTH_REQUESTS", "frozen_utc": now(), "input_manifest_sha256": sha(ROOT / "input_manifest.json"), "offline_evidence_sha256": sha(ROOT / "offline_evidence.json"), "probe_plan_sha256": sha(ROOT / "probe_plan.json"), "diagnostic_probe_results_not_yet_created": True, "gt_aware": True, "diagnostic_only": True, "not_a_deployable_policy": True, "selection_rule": "Cases whose exact-title Page1 probe hits GT, native-query union covers >=0.75 of question-supported GT elements, and either best native-to-GT-metadata TF-IDF >=0.15 or frozen result-to-GT max >=0.20; choose highest GT-metadata TF-IDF native query, tie original index; request Page3-5.", "requests_at_freeze": 0, "probes": selected})
    (ROOT / "depth_probe_plan.sha256").write_text(f"{sha(ROOT / 'depth_probe_plan.json')}  depth_probe_plan.json\n")
    print("Frozen 45 Page3-5 diagnostic requests over 15 direction-plausible cases.")

if __name__ == "__main__": main()
