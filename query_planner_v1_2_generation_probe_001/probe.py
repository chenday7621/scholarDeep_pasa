"""One native Crawler generation per question; construct A/B without retrieval."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
OUT = ROOT / "QUERY_PLANNER_V1_2_GENERATION_PROBE_001.json"
REPORT = ROOT / "QUERY_PLANNER_V1_2_GENERATION_PROBE_001.md"
DATA = ROOT / "data/RealScholarQuery/test.jsonl"
CHECKPOINT = ROOT / "checkpoints/pasa-7b-crawler"
SEED = 42


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def protected():
    # Prior experiments are fingerprinted only, never used as generation inputs.
    paths = list(ROOT.glob("*.py")) + [ROOT / "agent_prompt.json", DATA]
    paths += [p for p in ROOT.glob("*.md") if p != REPORT]
    paths += [p for p in ROOT.glob("*.json") if p != OUT]
    return {str(p): sha(p) for p in sorted(set(paths))}


def checkpoint_hashes():
    return {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(CHECKPOINT.iterdir()) if p.is_file()}


def questions():
    result = []
    for index, line in enumerate(DATA.open()):
        # Decode only question, not answers or GT IDs.
        match = re.search(r'"question"\s*:\s*', line)
        assert match
        question, _ = json.JSONDecoder().raw_decode(line[match.end():])
        assert isinstance(question, str) and question.strip()
        result.append({"query_id": f"Q{index}", "original_question": question})
    assert len(result) == 50
    return result


def native_spec():
    source = (ROOT / "paper_agent.py").read_text()
    cls = next(n for n in ast.parse(source).body
               if isinstance(n, ast.ClassDef) and n.name == "PaperAgent")
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    defaults = dict(zip([a.arg for a in init.args.args][-len(init.args.defaults):], init.args.defaults))
    cap = ast.literal_eval(defaults["search_queries"])
    patterns = []
    for node in ast.walk(init):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "search_template":
                    patterns.append(ast.literal_eval(value))
    assert cap == 5 and patterns == [r"Search\](.*?)\["]
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "search")
    return patterns[0], cap, ast.get_source_segment(source, method)


def run():
    assert not OUT.exists(), "Existing run is never overwritten or regenerated."
    assert not list((WORK / "raw_generations").glob("*.json"))
    if os.environ.get("PYTHONHASHSEED") != str(SEED):
        os.environ["PYTHONHASHSEED"] = str(SEED)
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()), "run"])
    os.environ.update(CUDA_VISIBLE_DEVICES="1", HF_HUB_OFFLINE="1",
                      TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1",
                      HF_HUB_DISABLE_TELEMETRY="1", TOKENIZERS_PARALLELISM="false",
                      WANDB_DISABLED="true")
    blocked = []

    def deny_network(event, args):
        internet_creation = event == "socket.__new__" and args[1] in (socket.AF_INET, socket.AF_INET6)
        network_operation = event in ("socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr")
        internet_io = event in ("socket.connect", "socket.sendto") and args[0].family in (socket.AF_INET, socket.AF_INET6)
        if internet_creation or network_operation or internet_io:
            blocked.append({"event": event, "utc": now()})
            raise RuntimeError("Internet disabled: V1.2 generation and construction only")

    sys.addaudithook(deny_network)
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    assert torch.cuda.is_available(), "GPU unavailable; no generation or artifact run started."
    pattern, cap, native_source = native_spec()
    template = read(ROOT / "agent_prompt.json")["generate_query"]
    originals = questions()
    started = time.monotonic()
    p = {"started_utc": now(), "seed": SEED, "seed_policy": "Reset Python, NumPy, torch and CUDA via set_seed(42) immediately before each of the 50 generate calls; PYTHONHASHSEED=42.",
         "checkpoint": str(CHECKPOINT.resolve()), "dataset": str(DATA.resolve()),
         "prompt_template": template, "native_parser_regex": pattern,
         "native_query_cap": cap, "native_search_method_source": native_source,
         "generation_overrides": {"max_new_tokens": 512}, "batch_size": 1,
         "physical_gpu_index": 1, "gpu": torch.cuda.get_device_name(0),
         "python": sys.version, "torch": torch.__version__, "transformers": transformers.__version__,
         "anchor_policy": "original_question.strip(); no other normalization or semantic edits",
         "construction": "A = native_queries[:5]; B = [faithful_anchor] + native_queries[:4], even if native is empty. No padding, deduplication, repair or resampling.",
         "sharing": "Exactly one native generation per Q. Both A and B reference that same generation_id; no separate group generation.",
         "network_policy": "HF offline/local_files_only; Python audit hook blocks Internet socket creation, DNS, connects and sendto. No retrieval/pipeline imports or calls.",
         "protected_before": protected(), "script_sha256": sha(__file__)}
    d = {"experiment": "QUERY_PLANNER_V1_2_GENERATION_PROBE_001", "status": "starting",
         "provenance": p, "generation_calls_started": 0, "generation_calls_completed": 0,
         "execution": {"serper_requests": 0, "search_calls": 0, "selector_calls": 0, "citation_expand_calls": 0},
         "per_query": []}
    save(OUT, d)
    p["checkpoint_before"] = checkpoint_hashes()
    print("Frozen inputs and checkpoint hashed. Loading native Crawler only.", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT, local_files_only=True, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(CHECKPOINT, local_files_only=True,
                                               torch_dtype="auto", device_map={"": "cuda:0"}).eval()
    p["generation_config_file"] = read(CHECKPOINT / "generation_config.json")
    p["loaded_generation_config"] = model.generation_config.to_dict()
    for key, value in p["generation_config_file"].items():
        if not key.startswith("_") and key != "transformers_version":
            assert p["loaded_generation_config"][key] == value, key
    eos = model.generation_config.eos_token_id
    eos_ids = eos if isinstance(eos, list) else [eos]
    d["status"] = "running"
    save(OUT, d)
    for original in originals:
        q = dict(original)
        prompt = template.format(user_query=q["original_question"]).strip()
        formatted = tokenizer.apply_chat_template([{"role": "user", "content": prompt.strip()}],
                                                  tokenize=False, max_length=992, add_generation_prompt=True)
        inputs = tokenizer([formatted], return_tensors="pt").to(model.device)
        d["generation_calls_started"] += 1
        d["active_query"] = q["query_id"]
        save(OUT, d)
        set_seed(SEED)
        t = time.monotonic()
        generation_started = now()
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=512)
        d["generation_calls_completed"] += 1
        ids = output[0, inputs.input_ids.shape[1]:].tolist()
        raw = tokenizer.decode(ids, skip_special_tokens=True)
        parsed = [x.strip() for x in re.findall(pattern, raw, flags=re.DOTALL)]
        native = parsed[:cap]
        anchor = q["original_question"].strip()
        generation_id = f"{q['query_id']}_native_001"
        q.update(generation_id=generation_id, seed=SEED, prompt=prompt, formatted_prompt=formatted,
                 generation_started_utc=generation_started, generation_finished_utc=now(),
                 generation_seconds=time.monotonic() - t,
                 input_token_count=inputs.input_ids.shape[1], generated_token_ids=ids,
                 generated_token_count=len(ids), ended_with_eos=bool(ids and ids[-1] in eos_ids),
                 raw_output=raw, all_parsed_queries=parsed, discarded_queries=parsed[cap:],
                 native_queries=native, faithful_anchor=anchor,
                 A_queries=list(native), B_queries=[anchor] + native[:4],
                 A_generation_id=generation_id, B_generation_id=generation_id)
        save(WORK / "raw_generations" / f"{q['query_id']}.json", q)
        d["per_query"].append(q)
        save(OUT, d)
        print(f"{q['query_id']}: one generation; native={len(native)}, A={len(q['A_queries'])}, B={len(q['B_queries'])}", flush=True)
    d.pop("active_query", None)
    p.update(finished_utc=now(), wall_seconds=time.monotonic() - started,
             blocked_network_events=blocked, protected_after=protected(),
             checkpoint_after=checkpoint_hashes())
    assert p["protected_before"] == p["protected_after"]
    assert p["checkpoint_before"] == p["checkpoint_after"]
    assert p["script_sha256"] == sha(__file__)
    d["status"] = "generations_complete"
    save(OUT, d)
    print("50 native generations completed. Retrieval calls: zero. Ready for sanity check only.", flush=True)


def validate():
    d = read(OUT)
    p = d["provenance"]
    assert d["status"] in ("generations_complete", "complete")
    assert p["protected_before"] == p["protected_after"] == protected()
    assert p["checkpoint_before"] == p["checkpoint_after"]
    assert p["script_sha256"] == sha(__file__)
    assert p["prompt_template"] == read(ROOT / "agent_prompt.json")["generate_query"]
    assert p["generation_overrides"] == {"max_new_tokens": 512}
    assert d["generation_calls_started"] == d["generation_calls_completed"] == 50
    assert len(d["per_query"]) == len(list((WORK / "raw_generations").glob("*.json"))) == 50
    previous = ""
    for q, original in zip(d["per_query"], questions()):
        assert all(q[k] == v for k, v in original.items())
        assert q == read(WORK / "raw_generations" / f"{q['query_id']}.json")
        parsed = [x.strip() for x in re.findall(r"Search\](.*?)\[", q["raw_output"], re.DOTALL)]
        assert q["all_parsed_queries"] == parsed and q["discarded_queries"] == parsed[5:]
        assert q["native_queries"] == parsed[:5] == q["A_queries"]
        assert q["faithful_anchor"] == q["original_question"].strip()
        assert q["B_queries"] == [q["original_question"].strip()] + parsed[:4]
        assert q["B_queries"][1:] == q["A_queries"][:4]
        assert q["A_generation_id"] == q["B_generation_id"] == q["generation_id"] == f"{q['query_id']}_native_001"
        assert q["seed"] == SEED and 0 < len(q["generated_token_ids"]) == q["generated_token_count"] <= 512
        assert q["prompt"] == p["prompt_template"].format(user_query=q["original_question"]).strip()
        assert q["generation_started_utc"] >= previous
        previous = q["generation_finished_utc"]
    assert all(value == 0 for value in d["execution"].values())
    qs = d["per_query"]
    summary = {"completed_questions": len(qs), "crawler_generation_calls": d["generation_calls_completed"],
               "search_action_parse_success": sum(bool(q["native_queries"]) for q in qs),
               "strict_search_format_questions": sum(bool(re.fullmatch(r"\s*(?:\[Search\][^\[\]]+)+\[StopSearch\]\s*", q["raw_output"], re.DOTALL)) for q in qs),
               "native_query_count_distribution": dict(sorted(Counter(str(len(q["native_queries"])) for q in qs).items())),
               "A_query_count_distribution": dict(sorted(Counter(str(len(q["A_queries"])) for q in qs).items())),
               "B_query_count_distribution": dict(sorted(Counter(str(len(q["B_queries"])) for q in qs).items())),
               "native_total": sum(len(q["native_queries"]) for q in qs),
               "A_total": sum(len(q["A_queries"]) for q in qs), "B_total": sum(len(q["B_queries"]) for q in qs),
               "faithful_anchor_present_first": sum(q["B_queries"][0] == q["original_question"].strip() for q in qs),
               "shared_native_prefix_exact": sum(q["B_queries"][1:] == q["A_queries"][:4] for q in qs),
               "same_generation_for_A_B": sum(q["A_generation_id"] == q["B_generation_id"] for q in qs),
               "empty_native_queries": sum(not x for q in qs for x in q["native_queries"]),
               "non_eos_generations": sum(not q["ended_with_eos"] for q in qs),
               "serper_requests": 0, "sanity_check": "PASS"}
    d.update(status="complete", summary=summary)
    save(OUT, d)
    report = ["# QUERY_PLANNER_V1_2_GENERATION_PROBE_001", "",
              "Generation-only + A/B query 构造验证；不评估语义质量或检索 Recall。", "",
              "每题仅一次原始 PaSa Crawler generation，A/B 共享同一输出。原 prompt 从 agent_prompt.json 读取；未使用 V1/V1.1 prompt。",
              "A = native[:5]；B = [original_question.strip()] + native[:4]。native 少于 5 条仍使用同一公式；不补齐、不去重、不修复或重采样。",
              "", f"seed={SEED}，每次生成前重置；GPU 1，batch_size=1，max_new_tokens=512，其余 generation 配置全部沿用 checkpoint。",
              "", "## Sanity check", "", "```json", json.dumps(summary, ensure_ascii=False, indent=2), "```", "",
              "共享位置严格检查 B[1:] == A[:4]。native 为 5 条时 B 移除 q5 并前置 anchor；native 为 4 条或更少时保留全部 native 并前置 anchor，因此两组数量可以不同。",
              "", "## 执行边界", "",
              "只加载本地 Crawler。HF 离线模式、local_files_only 和 Python 网络审计钩子阻止 Internet socket/DNS；没有 Search、Serper、Selector、Citation Expand 或外部 LLM 调用。",
              f"网络钩子阻止事件：{json.dumps(p['blocked_network_events'], ensure_ascii=False)}。被阻止的 socket 创建或 DNS 事件不是成功网络请求。",
              "主流程、原 prompt、既有报告/实验 JSON 与 checkpoint 前后 SHA-256 一致。没有修改 generation config、models.py、Selector 或 Expand。",
              "", "## 原始生成 Prompt", "", "```text", p["prompt_template"], "```", "",
              "## 产物", "", "- 主 JSON 保存每题原始 question、native queries、A queries、B queries，以及 prompt、seed、原始输出、token IDs 和 generation ID。",
              "- raw_generations/Q0.json 至 Q49.json：每题唯一 generation 与 A/B 构造的完整记录。",
              "- validation.json：sanity check 与产物哈希。", "",
              "实验到此结束，未进入真实 Search 或下一阶段。", ""]
    REPORT.write_text("\n".join(report))
    save(WORK / "validation.json", {"validated_utc": now(), "summary": summary,
         "checks": "PASS: 50 original questions, 50 single generations, raw record equality, original prompt, native regex/cap, trim-only anchor, exact A/B native sharing, preserved inputs/checkpoint, no retrieval calls",
         "artifact_sha256": {str(path): sha(path) for path in (OUT, REPORT, Path(__file__))}})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("run", "validate"))
    {"run": run, "validate": validate}[parser.parse_args().phase]()
