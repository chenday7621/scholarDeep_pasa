"""Offline construction revision over the 50 frozen V1.2 native generations."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT / "QUERY_PLANNER_V1_2_GENERATION_PROBE_001.json"
SOURCE_WORK = ROOT / "query_planner_v1_2_generation_probe_001"
OUT = ROOT / "QUERY_PLANNER_V1_2_GENERATION_PROBE_002.json"
REPORT = ROOT / "QUERY_PLANNER_V1_2_GENERATION_PROBE_002.md"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def normalize_anchor(text):
    # Preserve case in the actual anchor; lowercase is for exact comparison only.
    return " ".join(text.strip().split())


def construct(question, native):
    anchor = normalize_anchor(question)
    key = anchor.lower()
    kept, removed = [], []
    for index, query in enumerate(native, 1):
        if normalize_anchor(query).lower() == key:
            removed.append({"native_index_1based": index, "native_query": query,
                            "normalized_match_key": key})
        else:
            kept.append(index)
    selected = kept[:4]
    return {"normalized_anchor": anchor, "anchor_match_key": key,
            "A_queries": list(native),
            "B_queries": [anchor] + [native[i - 1] for i in selected],
            "anchor_exact_duplicate": bool(removed),
            "anchor_exact_duplicate_count": len(removed),
            "removed_native_queries": removed,
            "B_native_indices_1based": selected,
            "nonduplicate_native_indices_excluded_by_cap": kept[4:]}


def construction_sanity():
    # Synthetic boundary cases, kept separate from the 50 real questions.
    cases = [
        ("Anchor", ["q1", "q2", "q3", "q4", "q5"], ["Anchor", "q1", "q2", "q3", "q4"], []),
        ("  Anchor\tText \n", ["q1", " ANCHOR  text ", "q3", "q4", "q5"],
         ["Anchor Text", "q1", "q3", "q4", "q5"], [2]),
        ("anchor", ["ANCHOR", "anchor", "same", "same", "q5"], ["anchor", "same", "same", "q5"], [1, 2]),
        ("anchor", ["anchor", "q2"], ["anchor", "q2"], [1]),
        ("anchor", [], ["anchor"], []),
        ("anchor", ["anchor!", "q2"], ["anchor", "anchor!", "q2"], []),
    ]
    for question, native, expected, deleted in cases:
        result = construct(question, native)
        assert result["A_queries"] == native
        assert result["B_queries"] == expected
        assert [x["native_index_1based"] for x in result["removed_native_queries"]] == deleted
    return len(cases)


def main():
    assert not OUT.exists() and not REPORT.exists(), "Refuse to overwrite existing results"
    blocked = []

    def deny_network(event, args):
        if ((event == "socket.__new__" and args[1] in (socket.AF_INET, socket.AF_INET6))
                or event in ("socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr")
                or (event in ("socket.connect", "socket.sendto") and args[0].family in (socket.AF_INET, socket.AF_INET6))):
            blocked.append(event)
            raise RuntimeError("Network forbidden in V1.2 construction validation")

    sys.addaudithook(deny_network)
    started = datetime.now(timezone.utc).isoformat()
    boundary_cases = construction_sanity()
    source = read(SOURCE)
    p = source["provenance"]
    assert source["status"] == "complete"
    assert source["generation_calls_started"] == source["generation_calls_completed"] == 50
    assert len(source["per_query"]) == 50 and p["seed"] == 42
    assert p["protected_before"] == p["protected_after"]
    assert p["checkpoint_before"] == p["checkpoint_after"]
    source_validation = read(SOURCE_WORK / "validation.json")
    frozen = dict(p["protected_after"])
    frozen.update(source_validation["artifact_sha256"])
    frozen[str(SOURCE_WORK / "validation.json")] = sha(SOURCE_WORK / "validation.json")
    raw_paths = sorted((SOURCE_WORK / "raw_generations").glob("*.json"))
    assert len(raw_paths) == 50
    frozen.update({str(path): sha(path) for path in raw_paths})
    for path, expected in frozen.items():
        assert sha(path) == expected, path
    assert p["prompt_template"] == read(ROOT / "agent_prompt.json")["generate_query"]
    checkpoint = Path(p["checkpoint"])
    assert p["generation_config_file"] == read(checkpoint / "generation_config.json")
    assert p["generation_overrides"] == {"max_new_tokens": 512}
    assert p["batch_size"] == 1
    for key, value in p["generation_config_file"].items():
        if not key.startswith("_") and key != "transformers_version":
            assert p["loaded_generation_config"][key] == value
    print("Frozen source records, original prompt/config and six construction cases: PASS", flush=True)
    assert {f.name for f in checkpoint.iterdir() if f.is_file()} == set(p["checkpoint_after"])
    for name, expected in p["checkpoint_after"].items():
        path = checkpoint / name
        assert path.stat().st_size == expected["bytes"] and sha(path) == expected["sha256"], name
    print("Current Crawler checkpoint matches original generation fingerprint: PASS", flush=True)

    cls = next(n for n in ast.parse((ROOT / "paper_agent.py").read_text()).body
               if isinstance(n, ast.ClassDef) and n.name == "PaperAgent")
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    defaults = dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):], init.args.defaults))
    assert ast.literal_eval(defaults["search_queries"]) == 5
    patterns = [ast.literal_eval(v) for n in ast.walk(init) if isinstance(n, ast.Dict)
                for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant) and k.value == "search_template"]
    assert patterns == [p["native_parser_regex"]] == [r"Search\](.*?)\["]
    lines = Path(p["dataset"]).read_text().splitlines()
    assert len(lines) == 50
    records = []
    for index, (q, line) in enumerate(zip(source["per_query"], lines)):
        match = re.search(r'"question"\s*:\s*', line)
        question, _ = json.JSONDecoder().raw_decode(line[match.end():])
        assert q["query_id"] == f"Q{index}" and q["original_question"] == question
        assert q == read(SOURCE_WORK / "raw_generations" / f"Q{index}.json")
        assert q["seed"] == 42
        assert q["prompt"] == p["prompt_template"].format(user_query=question).strip()
        assert q["generation_id"] == q["A_generation_id"] == q["B_generation_id"] == f"Q{index}_native_001"
        parsed = [x.strip() for x in re.findall(patterns[0], q["raw_output"], re.DOTALL)]
        assert parsed == q["all_parsed_queries"] and parsed[:5] == q["native_queries"] == q["A_queries"]
        result = {k: q[k] for k in ("query_id", "original_question", "raw_output", "native_queries", "generation_id", "seed",
                                    "prompt", "formatted_prompt", "generated_token_ids", "generation_started_utc", "generation_finished_utc")}
        result.update(construct(question, parsed[:5]))
        result.update(A_generation_id=q["generation_id"], B_generation_id=q["generation_id"],
                      source_raw_record_sha256=frozen[str(SOURCE_WORK / "raw_generations" / f"Q{index}.json")])
        # Independent direct reconstruction: whitespace regex + lower, no sorting/set/dedup.
        anchor = re.sub(r"\s+", " ", question.strip())
        keep = [i for i, n in enumerate(parsed[:5], 1)
                if re.sub(r"\s+", " ", n.strip()).lower() != anchor.lower()]
        assert result["A_queries"] == parsed[:5]
        assert result["B_queries"] == [anchor] + [parsed[i - 1] for i in keep[:4]]
        assert result["B_native_indices_1based"] == keep[:4]
        assert [x["native_index_1based"] for x in result["removed_native_queries"]] == [i for i in range(1, len(parsed[:5]) + 1) if i not in keep]
        records.append(result)

    summary = {"completed_questions": len(records), "source_native_generation_calls": 50, "new_crawler_generation_calls": 0,
               "search_action_parse_success": sum(bool(q["native_queries"]) for q in records),
               "native_query_count_distribution": dict(sorted(Counter(str(len(q["native_queries"])) for q in records).items())),
               "A_query_count_distribution": dict(sorted(Counter(str(len(q["A_queries"])) for q in records).items())),
               "B_query_count_distribution": dict(sorted(Counter(str(len(q["B_queries"])) for q in records).items())),
               "B_starts_with_faithful_anchor": sum(q["B_queries"][0] == normalize_anchor(q["original_question"]) for q in records),
               "anchor_exact_duplicate_questions": sum(q["anchor_exact_duplicate"] for q in records),
               "anchor_exact_duplicate_occurrences": sum(q["anchor_exact_duplicate_count"] for q in records),
               "A_exact_native_order_preserved": 50, "B_relative_native_order_preserved": 50,
               "A_B_share_same_generation": 50, "serper_requests": 0, "selector_calls": 0, "citation_expand_calls": 0,
               "sanity_check": "PASS"}
    for path, expected in frozen.items():
        assert sha(path) == expected, path
    assert all(value == 0 for value in source["execution"].values())
    data = {"experiment": "QUERY_PLANNER_V1_2_GENERATION_PROBE_002", "status": "complete",
            "provenance": {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
                           "source": str(SOURCE), "source_sha256": sha(SOURCE),
                           "generation_reuse": "Reuse the 50 frozen native generations from 001; no fresh generation, resampling, V1/V1.1 prompt, or separate A/B generation.",
                           "source_generation_provenance": p,
                           "normalization": "actual anchor = ' '.join(original_question.strip().split()); exact-match key = same normalization followed by .lower(), not casefold; native text remains unchanged",
                           "construction": "A = native[:5]; filter anchor exact matches from native[:5] in original order, then B = [anchor] + remaining[:4]. No native-native dedup or rewrite.",
                           "removed_index_scope": "All anchor exact matches among at most 5 parsed native queries; indices are 1-based in the original native list, including q5 if it matches.",
                           "frozen_file_sha256": frozen, "checkpoint_hash_verified_now": True,
                           "blocked_network_events": blocked, "script_sha256": sha(__file__),
                           "synthetic_construction_sanity_cases": boundary_cases},
            "summary": summary, "per_query": records}
    save(OUT, data)
    report = ["# QUERY_PLANNER_V1_2_GENERATION_PROBE_002", "",
              "本次是 V1.2 构造规则补充验证。复用 001 已完成的 50 次原生 Crawler generation，本次新增 generation 为 0；每题 A/B 共享同一原始输出。001 及主流程保持不变。", "",
              "原始 PaSa checkpoint、generate_query prompt、generation 配置和 seed=42 均已核验；未使用 V1/V1.1 prompt。", "",
              "## 固定构造规则", "",
              "按原生正则提取并 strip，最多前 5 条。native/A 始终保留 Crawler 原始输出顺序，不排序或重排。",
              "Anchor 仅 trim 并将连续空白合为单个空格，保留原有大小写。比较键额外使用 lowercase。",
              "A 不做任何去重。B 先删除 native[:5] 中比较键与 anchor 完全相同的条目，再按原顺序取前 4 条，前置 anchor；q5 可补位，数量不足时允许少于 5 条。",
              "不做其他去重、semantic/Jaccard dedup、LLM rewrite、constraint extraction 或 acronym expansion。", "",
              "## Sanity check", "", "```json", json.dumps(summary, ensure_ascii=False, indent=2), "```", "",
              "重复出现次数指 native[:5] 中所有 Anchor exact duplicate 条目数，同时另列涉及题数。删除记录含 1-based native 序号、原 query 和比较键；本批未发生重复。",
              "六个独立合成 sanity 样例验证正常构造、q2 重复后 q5 补位、多次 anchor 重复、保留 native-native 重复、不足数量、零 native 和标点差异；不计入 50 题统计。", "",
              "## 逐题构造与顺序证据", "",
              "| Q | Native / A / B 条数 | B 保留的原 native 序号 | 删除的原 native 序号 |", "|---|---|---|---|"]
    report += [f"| {q['query_id']} | {len(q['native_queries'])} / {len(q['A_queries'])} / {len(q['B_queries'])} | {q['B_native_indices_1based']} | {[x['native_index_1based'] for x in q['removed_native_queries']]} |" for q in records]
    report += ["", "## 产物与边界", "",
               "主 JSON 保存全部原始 question、normalized anchor、raw Crawler output、native/A/B queries、重复标记、删除条目及原 native 索引，并保留源 generation ID、prompt、seed、token IDs 和哈希。",
               "本脚本只使用 Python 标准库；网络审计钩子阻止 Internet socket/DNS。本次没有模型加载、Serper、Selector、Citation Expand 或真实 Search。",
               "所有保护输入哈希前后相同，当前 Crawler checkpoint 完整哈希与源生成记录相同。构造规则验证到此结束，未进入下一阶段。", ""]
    REPORT.write_text("\n".join(report))
    save(WORK / "validation.json", {"summary": summary, "synthetic_cases_passed": boundary_cases,
         "independent_reconstruction": "PASS: source/raw equality, native regex and cap, exact A order, B anchor filtering with original indices and q5 refill",
         "artifact_sha256": {str(path): sha(path) for path in (OUT, REPORT, Path(__file__))}})
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
