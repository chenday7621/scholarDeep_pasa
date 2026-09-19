"""Independent integrity and protocol validation for the completed 003B run."""
import base64
import hashlib
import json
import random
import re

from common import ROOT, REPO, OLD, SEED, ids, native_spec, read, save, sha, verify_freeze


REQUIRED = [
    "MAPPING_AMENDMENT.md",
    "PREREGISTRATION.md",
    "MAPPING_AMENDMENT.sha256",
    "PREREGISTRATION.sha256",
    "dataset_manifest.json",
    "snapshot_manifest.json",
    "states.json",
    "decisions.json",
    "results.json",
    "PAGE2_ROUTING_PREREG_VALIDATION_003B.md",
]


def jaccard(left, right):
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def auc(scores, labels):
    positives = [score for score, label in zip(scores, labels) if label]
    negatives = [score for score, label in zip(scores, labels) if not label]
    if not positives or not negatives:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives) / (len(positives) * len(negatives))


def close(left, right, tolerance=1e-12):
    if left is None or right is None:
        assert left is right
    else:
        assert abs(left - right) <= tolerance, (left, right)


def main():
    registration = verify_freeze()
    for name in REQUIRED:
        assert (ROOT / name).is_file(), name
    assert (ROOT / "PREREGISTRATION.sha256").read_text().split()[0] == sha(ROOT / "PREREGISTRATION.md")
    assert (ROOT / "MAPPING_AMENDMENT.sha256").read_text().split()[0] == sha(ROOT / "MAPPING_AMENDMENT.md")
    assert sha(ROOT / "PREREGISTRATION.md") == "d084f7a5fe253e7f00e06b7d3222f51f96c503df886303c579c542787264d2f8"
    assert sha(ROOT / "MAPPING_AMENDMENT.md") == "65e0c52874e1822c869b9d9e8170b9aff22777ede644639129e906665d5b53f9"

    old_dataset = read(OLD / "dataset_manifest.json")
    old_results = read(OLD / "results.json")
    old_snapshots = read(OLD / "snapshot_manifest.json")
    assert old_dataset["status"] == "STOPPED_MAPPING_AMBIGUITY" and old_dataset["sample_size"] == 0
    assert old_results["status"] == "STOPPED_MAPPING_AMBIGUITY"
    assert old_snapshots["snapshots"] == []
    for relative, expected in registration["original_003_artifacts"].items():
        assert sha(OLD / relative) == expected, relative

    identity = read(ROOT / "identity_resolution.json")
    assert identity["status"] == "UNIQUELY_RESOLVED"
    assert identity["gold_corpusid"] == 258960101
    assert identity["retained_id"] == "2305.17359"
    assert identity["rejected_local_index_ids"] == ["2303.02909"]
    assert identity["identity_conflict_count"] == 1 and identity["additional_identity_conflicts"] == []
    titles = {row["arxiv_id"]: row["official_title"] for row in identity["records"]}
    assert titles["2305.17359"].startswith("DNA-GPT:")
    assert titles["2303.02909"].startswith("Dynamic Prompting:")
    assert identity["search_outcomes_used"] is False and identity["ordinary_title_miss_repaired"] == 0

    dataset = read(ROOT / "dataset_manifest.json")
    assert dataset["status"] == "SAMPLED" and dataset["sample_seed"] == SEED
    assert dataset["sample_size"] == 50 and dataset["unresolved_identity_conflicts"] == []
    assert {group: data["sampled"] for group, data in dataset["group_counts"].items()} == {
        "author-written": 25, "inline-citation": 25
    }
    assert all(data["eligible"] == 165 for data in dataset["group_counts"].values())
    pools = {group: [] for group in ("author-written", "inline-citation")}
    for query in dataset["queries"]:
        if query["eligible_all_gold_compatible"]:
            pools[query["group"]].append(query)
    rng = random.Random(SEED)
    reproduced = []
    for group in ("author-written", "inline-citation"):
        reproduced.extend(rng.sample(sorted(pools[group], key=lambda row: row["row_index"]), 25))
    assert [row["row_index"] for row in reproduced] == [row["row_index"] for row in dataset["sample"]]
    assert [row["question_id"] for row in dataset["sample"]] == [f"Q{i:02d}" for i in range(50)]

    run = read(ROOT / "run_manifest.json")
    assert run["status"] == "SNAPSHOT_COMPLETE"
    assert run["runner_sha256"] == sha(ROOT / "collect.py")
    assert run["common_sha256"] == sha(ROOT / "common.py")
    assert run["model_seed_per_question"] == 42 and run["end_date"] == "2026-09-17"
    assert run["prior_environment_preflight"]["generated_tokens"] == 0
    assert run["prior_environment_preflight"]["search_requests"] == 0
    questions = read(ROOT / "questions.json")["questions"]
    pattern, cap = native_spec()
    query_count = 0
    response_paths = set()
    for question in questions:
        qid = question["question_id"]
        generation = read(ROOT / "generations" / f"{qid}.json")
        assert generation["status"] == "PASS" and generation["seed"] == 42
        assert generation["question"] == question["question"]
        assert hashlib.sha256(generation["raw_output"].encode()).hexdigest() == generation["raw_output_sha256"]
        parsed = [item.strip() for item in re.findall(pattern, generation["raw_output"], flags=re.DOTALL)]
        assert generation["all_parsed_queries"] == parsed
        assert generation["queries"] == parsed[:cap] and generation["queries"]
        query_count += len(generation["queries"])
        for index, query in enumerate(generation["queries"]):
            previous_finished = None
            for page in (1, 2):
                path = ROOT / "responses" / f"{qid}_q{index:02d}_page{page}.json"
                response_paths.add(path.resolve())
                record = read(path)
                payload = {"q": f"{query} before:2026-09-17 site:arxiv.org", "num": 10, "page": page}
                assert record["status"] == "PASS" and record["request_payload"] == payload
                raw = base64.b64decode(record["raw_response_base64"])
                assert hashlib.sha256(raw).hexdigest() == record["response_bytes_sha256"]
                assert json.loads(raw) == record["structured_response"]
                assert 1 <= record["attempt"] <= 3
                assert len(record["attempts"]) == record["attempt"]
                if previous_finished is not None:
                    assert record["started_utc"] >= previous_finished
                previous_finished = record["finished_utc"]
    actual_responses = {path.resolve() for path in (ROOT / "responses").glob("*.json")}
    assert actual_responses == response_paths
    assert len(actual_responses) == 2 * query_count
    assert run["successful_generations"] == 50
    assert run["successful_page1"] == run["successful_page2"] == query_count

    snapshots = read(ROOT / "snapshot_manifest.json")
    states = read(ROOT / "states.json")
    decisions = read(ROOT / "decisions.json")
    assert snapshots["status"] == "COMPLETE" and snapshots["query_count"] == query_count
    assert snapshots["page1_successful"] == snapshots["page2_successful"] == query_count
    assert snapshots["snapshot_id"] == states["snapshot_id"] == decisions["snapshot_id"]
    assert decisions["states_sha256"] == sha(ROOT / "states.json")
    assert decisions["gt_reads"] == decisions["page2_outcome_reads_for_routing"] == 0
    decision_by_q = {row["question_id"]: row for row in decisions["decisions"]}
    for question in states["questions"]:
        sets = [set(row["page1_ids"]) for row in question["queries"]]
        for index, row in enumerate(question["queries"]):
            expected = max((jaccard(sets[index], sets[other]) for other in range(len(sets)) if other != index), default=0.0)
            close(row["max_jaccard"], expected)
        selected = min(question["queries"], key=lambda row: (-row["max_jaccard"], row["query_index"]))
        assert decision_by_q[question["question_id"]]["selected_query_index"] == selected["query_index"]

    result = read(ROOT / "results.json")
    outcomes = read(ROOT / "evaluation_question_outcomes.json")
    trials = read(ROOT / "random_trials.json")
    assert result["status"] == "EVALUATED" and result["rules_changed_after_outcome"] is False
    assert result["native_query_count"] == query_count
    assert result["actual_page1_calls"] == result["actual_page2_calls"] == query_count
    assert result["snapshot_id"] == snapshots["snapshot_id"]
    assert result["random_trials_sha256"] == sha(ROOT / "random_trials.json")
    assert result["evaluation_question_outcomes_sha256"] == sha(ROOT / "evaluation_question_outcomes.json")
    assert trials["seed"] == SEED and trials["trials"] == 1000
    rerun_rng = random.Random(SEED)
    query_counts = {row["question_id"]: len(row["queries"]) for row in outcomes["questions"]}
    random_deltas = []
    gain_by_q = {
        row["question_id"]: {query["query_index"]: query["page2_delta_gt"] for query in row["queries"]}
        for row in outcomes["questions"]
    }
    for trial_index, trial in enumerate(trials["records"]):
        expected = {qid: rerun_rng.randrange(query_counts[qid]) for qid in trials["question_order"]}
        assert trial["trial"] == trial_index and trial["selected_query_indices"] == expected
        delta = sum(gain_by_q[qid][index] for qid, index in expected.items())
        assert trial["overall"]["delta_gt"] == delta
        random_deltas.append(delta)
    router_delta = sum(row["router_gain"] for row in outcomes["questions"])
    always_delta = sum(row["always_gain"] for row in outcomes["questions"])
    oracle_delta = sum(row["oracle_gain"] for row in outcomes["questions"])
    assert result["policies"]["jaccard_router"]["delta_gt"] == router_delta
    assert result["policies"]["always_page2"]["delta_gt"] == always_delta
    assert result["policies"]["oracle_top1"]["delta_gt"] == oracle_delta
    exceed = sum(delta >= router_delta for delta in random_deltas)
    assert result["policies"]["random_top1_1000_trials"]["random_greater_or_equal_router_count"] == exceed
    close(result["primary_endpoint"]["p_random_greater_or_equal_router_empirical"], exceed / 1000)
    close(result["primary_endpoint"]["p_random_greater_or_equal_router_plus_one"], (exceed + 1) / 1001)
    query_rows = outcomes["query_rows"]
    close(result["auc"]["global_roc_auc"], auc(
        [row["max_jaccard"] for row in query_rows], [row["page2_adds_gt"] for row in query_rows]
    ))

    artifacts = {name: sha(ROOT / name) for name in REQUIRED}
    artifacts.update({
        "run_manifest.json": sha(ROOT / "run_manifest.json"),
        "random_trials.json": sha(ROOT / "random_trials.json"),
        "evaluation_question_outcomes.json": sha(ROOT / "evaluation_question_outcomes.json"),
        "identity_resolution.json": sha(ROOT / "identity_resolution.json"),
        "registration_manifest.json": sha(ROOT / "registration_manifest.json"),
    })
    validation = {
        "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "status": "PASS",
        "checks": {
            "original_003_stop_record_preserved": True,
            "frozen_protocol_hashes_match": True,
            "protected_formal_sources_unchanged": True,
            "identity_uniquely_resolved_from_static_official_metadata": True,
            "no_additional_identity_conflicts": True,
            "fixed_seed_sample_reproduced": True,
            "sample_is_25_plus_25": True,
            "all_50_native_generations_present_and_parser_reproduced": True,
            "all_page1_page2_raw_bytes_and_payloads_verified": True,
            "page1_then_page2_pair_order_verified": True,
            "all_page1_only_states_and_tie_breaks_recomputed": True,
            "routing_decisions_frozen_before_gt_evaluation": True,
            "all_1000_random_trials_reproduced": True,
            "primary_endpoint_recomputed": True,
            "global_roc_auc_recomputed": True,
            "no_result_based_rule_or_sample_change": True,
        },
        "counts": {
            "questions": 50,
            "author_written": 25,
            "inline_citation": 25,
            "native_queries": query_count,
            "successful_page1": query_count,
            "successful_page2": query_count,
            "random_trials": 1000,
        },
        "artifact_hashes": artifacts,
        "source_hashes": {name: sha(ROOT / name) for name in ["common.py", "collect.py", "route.py", "evaluate.py", "report.py", "validate.py"]},
    }
    save(ROOT / "validation.json", validation)
    print(f"PASS: 50 questions, {query_count} paired snapshots, 1000 Random trials, all primary metrics reproduced.")


if __name__ == "__main__":
    main()
