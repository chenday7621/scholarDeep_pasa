"""Offline preregistered policy replay; this is the first stage allowed to read GT."""
from collections import Counter
import math
import random
import statistics

from common import ROOT, SEED, ids, normalize_function, now, read, save, sha, verify_freeze


TRIALS = 1000


def auc(scores, labels):
    positives = [score for score, label in zip(scores, labels) if label]
    negatives = [score for score, label in zip(scores, labels) if not label]
    if not positives or not negatives:
        return None
    wins = ties = 0
    for positive in positives:
        for negative in negatives:
            wins += positive > negative
            ties += positive == negative
    return (wins + 0.5 * ties) / (len(positives) * len(negatives))


def metric(question_ids, base, extra, denominators, calls):
    found = {qid: base[qid] | extra.get(qid, set()) for qid in question_ids}
    base_count = sum(len(base[qid]) for qid in question_ids)
    found_count = sum(len(found[qid]) for qid in question_ids)
    total = sum(denominators[qid] for qid in question_ids)
    delta = found_count - base_count
    base_macro = statistics.mean(len(base[qid]) / denominators[qid] for qid in question_ids)
    macro = statistics.mean(len(found[qid]) / denominators[qid] for qid in question_ids)
    return {
        "questions": len(question_ids),
        "total_gt": total,
        "base_gt_found": base_count,
        "gt_found": found_count,
        "macro_recall": macro,
        "micro_recall": found_count / total,
        "delta_gt": delta,
        "incremental_macro_recall": macro - base_macro,
        "incremental_micro_recall": delta / total,
        "extra_page2_calls": calls,
        "delta_gt_per_extra_call": delta / calls if calls else None,
    }


def summarize(values):
    return {
        "mean": statistics.mean(values),
        "population_std": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def main():
    verify_freeze()
    snapshots = read(ROOT / "snapshot_manifest.json")
    states = read(ROOT / "states.json")
    decisions = read(ROOT / "decisions.json")
    assert snapshots["status"] == "COMPLETE"
    assert snapshots["snapshot_id"] == states["snapshot_id"] == decisions["snapshot_id"]
    assert decisions["states_sha256"] == sha(ROOT / "states.json")

    # Routing is already frozen. Gold is decoded only below this point.
    dataset = read(ROOT / "dataset_manifest.json")
    assert dataset["status"] == "SAMPLED" and len(dataset["sample"]) == 50
    normalizer = normalize_function()
    sample = {q["question_id"]: q for q in dataset["sample"]}
    question_ids = [f"Q{i:02d}" for i in range(50)]
    groups = {group: [qid for qid in question_ids if sample[qid]["group"] == group]
              for group in ("author-written", "inline-citation")}
    assert all(len(qids) == 25 for qids in groups.values())

    gt_groups = {}
    id_to_gt = {}
    denominators = {}
    for qid in question_ids:
        grouped = {}
        for mapping in sample[qid]["gold_mappings"]:
            assert mapping["status"] == "compatible"
            normalized = mapping["normalized_title"]
            assert normalized == normalizer(mapping["title"])
            grouped.setdefault(normalized, set()).add(mapping["arxiv_id"])
        assert grouped
        gt_groups[qid] = grouped
        denominators[qid] = len(grouped)
        reverse = {}
        for normalized, arxiv_ids in grouped.items():
            for arxiv_id in arxiv_ids:
                reverse.setdefault(arxiv_id, set()).add(normalized)
        id_to_gt[qid] = reverse

    state_by_q = {q["question_id"]: q for q in states["questions"]}
    decision_by_q = {q["question_id"]: q for q in decisions["decisions"]}
    base = {}
    query_gains = {}
    query_rows = []
    question_outcomes = []
    for qid in question_ids:
        state = state_by_q[qid]
        page1_union = set()
        page2_by_index = {}
        for row in state["queries"]:
            key = row["query_key"]
            snap = snapshots["snapshots"][key]
            p1_record = read(ROOT / snap["page1"]["path"])
            p2_record = read(ROOT / snap["page2"]["path"])
            p1 = set(ids(p1_record["structured_response"]))
            p2 = set(ids(p2_record["structured_response"]))
            assert sorted(p1) == row["page1_ids"] == snap["page1"]["arxiv_ids"]
            assert sorted(p2) == snap["page2"]["arxiv_ids"]
            page1_union |= p1
            page2_by_index[row["query_index"]] = p2
        base[qid] = set().union(*(id_to_gt[qid].get(aid, set()) for aid in page1_union))
        query_gains[qid] = {}
        for row in state["queries"]:
            index = row["query_index"]
            hits = set().union(*(id_to_gt[qid].get(aid, set()) for aid in page2_by_index[index]))
            gains = hits - base[qid]
            query_gains[qid][index] = gains
            query_rows.append({
                "question_id": qid,
                "group": sample[qid]["group"],
                "query_key": row["query_key"],
                "query_index": index,
                "native_query": row["native_query"],
                "max_jaccard": row["max_jaccard"],
                "page2_adds_gt": bool(gains),
                "page2_delta_gt": len(gains),
                "new_normalized_gt_titles": sorted(gains),
            })
        router_index = decision_by_q[qid]["selected_query_index"]
        recomputed = min(state["queries"], key=lambda row: (-row["max_jaccard"], row["query_index"]))
        assert router_index == recomputed["query_index"]
        oracle_index = min(query_gains[qid], key=lambda index: (-len(query_gains[qid][index]), index))
        question_outcomes.append({
            "question_id": qid,
            "group": sample[qid]["group"],
            "row_index": sample[qid]["row_index"],
            "question": sample[qid]["question"],
            "gt": [{"normalized_title": title, "arxiv_ids": sorted(arxiv_ids)} for title, arxiv_ids in sorted(gt_groups[qid].items())],
            "base_found": sorted(base[qid]),
            "base_gt_found": len(base[qid]),
            "router_query_index": router_index,
            "router_gain": len(query_gains[qid][router_index]),
            "oracle_query_index": oracle_index,
            "oracle_gain": len(query_gains[qid][oracle_index]),
            "always_gain": len(set().union(*query_gains[qid].values())),
            "queries": [row for row in query_rows if row["question_id"] == qid],
        })

    router_selection = {qid: decision_by_q[qid]["selected_query_index"] for qid in question_ids}
    oracle_selection = {
        qid: min(query_gains[qid], key=lambda index: (-len(query_gains[qid][index]), index))
        for qid in question_ids
    }
    router_extra = {qid: query_gains[qid][router_selection[qid]] for qid in question_ids}
    oracle_extra = {qid: query_gains[qid][oracle_selection[qid]] for qid in question_ids}
    always_extra = {qid: set().union(*query_gains[qid].values()) for qid in question_ids}
    query_counts = {qid: len(query_gains[qid]) for qid in question_ids}

    base_metrics = metric(question_ids, base, {}, denominators, 0)
    router_metrics = metric(question_ids, base, router_extra, denominators, 50)
    oracle_metrics = metric(question_ids, base, oracle_extra, denominators, 50)
    always_metrics = metric(question_ids, base, always_extra, denominators, sum(query_counts.values()))
    for policy in (base_metrics, router_metrics, oracle_metrics, always_metrics):
        policy["always_page2_gain_retention"] = (
            policy["delta_gt"] / always_metrics["delta_gt"] if always_metrics["delta_gt"] else None
        )

    rng = random.Random(SEED)
    random_trials = []
    for trial in range(TRIALS):
        selected = {qid: rng.randrange(query_counts[qid]) for qid in question_ids}
        extra = {qid: query_gains[qid][selected[qid]] for qid in question_ids}
        overall = metric(question_ids, base, extra, denominators, 50)
        group_metrics = {
            group: metric(qids, base, extra, denominators, len(qids)) for group, qids in groups.items()
        }
        random_trials.append({
            "trial": trial,
            "selected_query_indices": selected,
            "overall": overall,
            "groups": group_metrics,
        })
    random_delta = [trial["overall"]["delta_gt"] for trial in random_trials]
    exceed = sum(value >= router_metrics["delta_gt"] for value in random_delta)
    random_summary = {
        "trials": TRIALS,
        "seed": SEED,
        "delta_gt": summarize(random_delta),
        "gt_found": summarize([trial["overall"]["gt_found"] for trial in random_trials]),
        "macro_recall": summarize([trial["overall"]["macro_recall"] for trial in random_trials]),
        "micro_recall": summarize([trial["overall"]["micro_recall"] for trial in random_trials]),
        "delta_gt_per_extra_call": summarize([trial["overall"]["delta_gt_per_extra_call"] for trial in random_trials]),
        "p_random_greater_or_equal_router_empirical": exceed / TRIALS,
        "p_random_greater_or_equal_router_plus_one": (exceed + 1) / (TRIALS + 1),
        "random_greater_or_equal_router_count": exceed,
        "delta_gt_distribution": dict(sorted(Counter(random_delta).items())),
    }

    global_auc = auc(
        [row["max_jaccard"] for row in query_rows],
        [row["page2_adds_gt"] for row in query_rows],
    )
    within_wins = within_ties = within_pairs = 0
    within_questions = 0
    for qid in question_ids:
        rows = [row for row in query_rows if row["question_id"] == qid]
        positives = [row["max_jaccard"] for row in rows if row["page2_adds_gt"]]
        negatives = [row["max_jaccard"] for row in rows if not row["page2_adds_gt"]]
        if positives and negatives:
            within_questions += 1
            for positive in positives:
                for negative in negatives:
                    within_pairs += 1
                    within_wins += positive > negative
                    within_ties += positive == negative
    within_auc = (within_wins + 0.5 * within_ties) / within_pairs if within_pairs else None

    group_results = {}
    for group, qids in groups.items():
        group_always = metric(qids, base, always_extra, denominators, sum(query_counts[qid] for qid in qids))
        group_router = metric(qids, base, router_extra, denominators, len(qids))
        group_oracle = metric(qids, base, oracle_extra, denominators, len(qids))
        group_base = metric(qids, base, {}, denominators, 0)
        for policy in (group_base, group_router, group_oracle, group_always):
            policy["always_page2_gain_retention"] = (
                policy["delta_gt"] / group_always["delta_gt"] if group_always["delta_gt"] else None
            )
        group_results[group] = {
            "native_page1": group_base,
            "jaccard_router": group_router,
            "always_page2": group_always,
            "oracle_top1": group_oracle,
            "random": {
                "delta_gt": summarize([trial["groups"][group]["delta_gt"] for trial in random_trials]),
                "macro_recall": summarize([trial["groups"][group]["macro_recall"] for trial in random_trials]),
                "micro_recall": summarize([trial["groups"][group]["micro_recall"] for trial in random_trials]),
            },
        }

    results = {
        "experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "status": "EVALUATED",
        "evaluated_utc": now(),
        "primary_endpoint": {
            "one_page2_call_per_question_delta_gt": router_metrics["delta_gt"],
            "one_page2_call_per_question_incremental_micro_recall": router_metrics["incremental_micro_recall"],
            "one_page2_call_per_question_incremental_macro_recall": router_metrics["incremental_macro_recall"],
            "p_random_greater_or_equal_router_empirical": exceed / TRIALS,
            "p_random_greater_or_equal_router_plus_one": (exceed + 1) / (TRIALS + 1),
        },
        "policies": {
            "native_page1": base_metrics,
            "random_top1_1000_trials": random_summary,
            "jaccard_router": router_metrics,
            "always_page2": always_metrics,
            "oracle_top1": oracle_metrics,
        },
        "auc": {
            "label": "This query's Page2 adds at least one GT relative to the question-wide union of all native Page1 results.",
            "orientation": "Higher max_jaccard predicts positive.",
            "global_roc_auc": global_auc,
            "within_question_pair_weighted_auc": within_auc,
            "within_question_comparable_questions": within_questions,
            "within_question_positive_negative_pairs": within_pairs,
            "positive_queries": sum(row["page2_adds_gt"] for row in query_rows),
            "negative_queries": sum(not row["page2_adds_gt"] for row in query_rows),
        },
        "groups": group_results,
        "router_selection": router_selection,
        "oracle_selection": oracle_selection,
        "question_count": len(question_ids),
        "native_query_count": sum(query_counts.values()),
        "actual_page1_calls": snapshots["page1_successful"],
        "actual_page2_calls": snapshots["page2_successful"],
        "total_normalized_gt": sum(denominators.values()),
        "snapshot_id": snapshots["snapshot_id"],
        "snapshot_manifest_sha256": sha(ROOT / "snapshot_manifest.json"),
        "states_sha256": sha(ROOT / "states.json"),
        "decisions_sha256": sha(ROOT / "decisions.json"),
        "dataset_manifest_sha256": sha(ROOT / "dataset_manifest.json"),
        "random_trials_sha256": None,
        "rules_changed_after_outcome": False,
    }
    save(ROOT / "random_trials.json", {
        "seed": SEED,
        "trials": TRIALS,
        "question_order": question_ids,
        "records": random_trials,
    })
    results["random_trials_sha256"] = sha(ROOT / "random_trials.json")
    save(ROOT / "evaluation_question_outcomes.json", {
        "questions": question_outcomes,
        "query_rows": query_rows,
    })
    results["evaluation_question_outcomes_sha256"] = sha(ROOT / "evaluation_question_outcomes.json")
    save(ROOT / "results.json", results)
    print(
        f"Router delta={router_metrics['delta_gt']}; Random>=Router={exceed}/{TRIALS}; "
        f"global AUC={global_auc}; within-question AUC={within_auc}"
    )


if __name__ == "__main__":
    main()
