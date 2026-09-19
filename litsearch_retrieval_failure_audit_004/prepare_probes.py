"""Freeze the fixed GT-aware diagnostic panel before making any requests."""
from common import END_DATE, ROOT, core_phrase, now, read, save, sha, verify_source

def main():
    verify_source()
    assert not (ROOT / "probe_plan.json").exists(), "Never overwrite frozen diagnostic plan"
    offline = read(ROOT / "offline_evidence.json")
    probes = []
    sequence = 0
    for case in offline["cases"]:
        definitions = [
            ("exact_gt_title", case["gold"]["title"]),
            ("gt_core_phrase", core_phrase(case["gold"]["title"])),
            ("original_question", case["question"]),
        ]
        assert definitions[1][1] == case["diagnostic_core_phrase"]
        for kind, query in definitions:
            sequence += 1
            probes.append({"sequence": sequence, "question_id": case["question_id"], "group": case["group"], "kind": kind, "query": query, "gold_arxiv_id": case["gold"]["arxiv_id"], "payload": {"q": f"{query} before:{END_DATE} site:arxiv.org", "num": 10, "page": 1}})
    assert len(probes) == 114
    plan = {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "status": "FROZEN_BEFORE_REQUESTS", "frozen_utc": now(), "offline_evidence_sha256": sha(ROOT / "offline_evidence.json"), "input_manifest_sha256": sha(ROOT / "input_manifest.json"), "gt_aware": True, "not_a_deployable_policy": True, "purpose": "Failure attribution only; never a controller, performance estimate, or candidate replacement.", "probe_panel": ["exact_gt_title", "gt_core_phrase", "original_question"], "request_parameters": {"provider": "Serper", "num": 10, "page": 1, "before": END_DATE, "site": "arxiv.org"}, "retry_policy": "At most 3 attempts for transport, HTTP 429, or HTTP 5xx; never repeat a successful response.", "probes": probes, "requests_at_freeze": 0}
    save(ROOT / "probe_plan.json", plan)
    (ROOT / "probe_plan.sha256").write_text(f"{sha(ROOT / 'probe_plan.json')}  probe_plan.json\n")
    print("Frozen 114 GT-aware diagnostic Page1 probes; zero requests at freeze.")

if __name__ == "__main__": main()
