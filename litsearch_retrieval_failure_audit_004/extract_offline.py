"""Extract frozen misses and deterministic lexical/theme evidence."""
from collections import Counter
import json
import statistics
import zipfile

from common import ROOT, REPO, SOURCE, core_phrase, idf, lexical_metrics, now, object_digest, parsed_id, read, recall, save, sha, token_set, verify_source

def main():
    _, snapshots = verify_source()
    outcomes = read(SOURCE / "evaluation_question_outcomes.json")["questions"]
    misses = [row for row in outcomes if row["base_gt_found"] == 0 and row["always_gain"] == 0]
    assert len(misses) == 38
    assert Counter(row["group"] for row in misses) == {"author-written": 16, "inline-citation": 22}
    dataset = read(SOURCE / "dataset_manifest.json")
    samples = {row["question_id"]: row for row in dataset["sample"]}
    index = read(REPO / "data/paper_database/id2paper.json")
    archive = zipfile.ZipFile(REPO / "data/paper_database/cs_paper_2nd.zip")
    raw_cases, documents, response_hashes = [], [], {}
    for outcome in misses:
        qid = outcome["question_id"]; sample = samples[qid]; gold = sample["gold_mappings"][0]
        assert gold["status"] == "compatible" and len(sample["gold_mappings"]) == 1
        record = json.loads(archive.read(gold["normalized_title"]))
        generation_path = SOURCE / "generations" / f"{qid}.json"; generation = read(generation_path)
        query_records = []
        for query_index, query in enumerate(generation["queries"]):
            pages = []
            for page in (1, 2):
                path = SOURCE / "responses" / f"{qid}_q{query_index:02d}_page{page}.json"; response = read(path)
                response_hashes[str(path.relative_to(SOURCE))] = sha(path)
                hits = [{"rank": rank, "title": hit.get("title", ""), "snippet": hit.get("snippet", ""), "link": hit.get("link", ""), "arxiv_id": parsed_id(hit.get("link", ""))} for rank, hit in enumerate(response["structured_response"].get("organic", []), 1)]
                pages.append({"page": page, "response_path": str(path.relative_to(SOURCE)), "response_sha256": response_hashes[str(path.relative_to(SOURCE))], "hits": hits})
                documents.extend(hit["title"] + " " + hit["snippet"] for hit in hits)
            query_records.append({"query_index": query_index, "native_query": query, "pages": pages}); documents.append(query)
        metadata = record["title"] + " " + record.get("abstract", "")
        documents += [sample["question"], gold["title"], metadata]
        raw_cases.append({"question_id": qid, "group": sample["group"], "row_index": sample["row_index"], "question": sample["question"], "gold": {"corpusid": gold["corpusid"], "arxiv_id": gold["arxiv_id"], "title": gold["title"], "normalized_title": gold["normalized_title"], "local_title": record["title"], "abstract": record.get("abstract", ""), "local_source": record.get("source")}, "diagnostic_core_phrase": core_phrase(gold["title"]), "generation_path": str(generation_path.relative_to(SOURCE)), "generation_sha256": sha(generation_path), "queries": query_records})
    archive.close()
    weights = idf(documents); cases = []
    for case in raw_cases:
        question, gold = case["question"], case["gold"]; metadata = gold["title"] + " " + gold["abstract"]
        question_tokens, title_tokens, metadata_tokens = token_set(question), token_set(gold["title"]), token_set(metadata)
        supported = question_tokens & metadata_tokens; query_union = set(); query_features = []; result_records = []
        for query in case["queries"]:
            query_union |= token_set(query["native_query"]); hits = [hit for page in query["pages"] for hit in page["hits"]]; similarities = []
            for page_record in query["pages"]:
                for hit in page_record["hits"]:
                    text = hit["title"] + " " + hit["snippet"]; metric = lexical_metrics(text, metadata, weights); similarities.append(metric["tfidf_cosine"])
                    result_records.append({**hit, "query_index": query["query_index"], "page": page_record["page"], "gt_metadata_similarity": metric["tfidf_cosine"], "question_similarity": lexical_metrics(text, question, weights)["tfidf_cosine"]})
            query_features.append({"query_index": query["query_index"], "native_query": query["native_query"], "query_to_question": lexical_metrics(query["native_query"], question, weights), "query_to_gt_title": lexical_metrics(query["native_query"], gold["title"], weights), "query_to_gt_metadata": lexical_metrics(query["native_query"], metadata, weights), "question_supported_gt_element_coverage": recall(supported, token_set(query["native_query"])), "result_gt_similarity_max": max(similarities, default=0.0), "result_gt_similarity_mean": statistics.mean(similarities) if similarities else 0.0, "arxiv_hit_count": sum(hit["arxiv_id"] is not None for hit in hits), "organic_hit_count": len(hits), "pages": query["pages"]})
        question_metric = lexical_metrics(question, metadata, weights); best = max((row["query_to_gt_metadata"]["tfidf_cosine"] for row in query_features), default=0.0); result_sims = [row["gt_metadata_similarity"] for row in result_records]
        case.update({"lexical": {"question_to_gt_title": lexical_metrics(question, gold["title"], weights), "question_to_gt_metadata": question_metric, "question_content_tokens": sorted(question_tokens), "gold_title_content_tokens": sorted(title_tokens), "question_supported_gt_elements": sorted(supported), "native_query_union_tokens": sorted(query_union), "native_union_question_supported_gt_element_coverage": recall(supported, query_union), "native_union_question_content_coverage": recall(question_tokens, query_union), "native_union_gt_title_coverage": recall(title_tokens, query_union), "best_native_query_to_gt_metadata_tfidf": best, "query_reformulation_gt_similarity_delta": best - question_metric["tfidf_cosine"], "result_to_gt_metadata_similarity_max": max(result_sims, default=0.0), "result_to_gt_metadata_similarity_mean": statistics.mean(result_sims) if result_sims else 0.0, "result_arxiv_ratio": sum(row["arxiv_id"] is not None for row in result_records) / len(result_records) if result_records else 0.0}, "query_features": query_features, "result_evidence": sorted(result_records, key=lambda row: (-row["gt_metadata_similarity"], row["query_index"], row["page"], row["rank"]))[:15], "frozen_result_counts": {"organic": len(result_records), "arxiv_parseable": sum(row["arxiv_id"] is not None for row in result_records), "unique_arxiv_ids": len({row["arxiv_id"] for row in result_records if row["arxiv_id"]})}}); cases.append(case)
    save(ROOT / "input_manifest.json", {"experiment": "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004", "created_utc": now(), "source_experiment": "PAGE2_ROUTING_PREREG_VALIDATION_003B", "source_snapshot_id": snapshots["snapshot_id"], "source_files": {name: sha(SOURCE / name) for name in ["PREREGISTRATION.md", "MAPPING_AMENDMENT.md", "dataset_manifest.json", "snapshot_manifest.json", "states.json", "decisions.json", "results.json", "validation.json", "evaluation_question_outcomes.json"]}, "response_files": response_hashes, "miss_definition": "base_gt_found == 0 and always_gain == 0", "miss_question_ids": [case["question_id"] for case in cases], "miss_count": len(cases), "group_counts": dict(Counter(case["group"] for case in cases)), "new_model_calls": 0, "new_search_requests_at_freeze": 0})
    save(ROOT / "offline_evidence.json", {"created_utc": now(), "input_manifest_sha256": sha(ROOT / "input_manifest.json"), "lexical_method": {"tokenization": "Lowercase [a-z0-9]+; fixed stopword list in common.py", "similarity": "Token Jaccard/coverage, character trigram Jaccard, IDF-weighted bag-of-token cosine", "question_supported_gt_elements": "Question content tokens also occurring in local GT title+abstract", "result_theme": "Frozen title+snippet similarity to local GT title+abstract", "idf_document_count": len(documents), "idf_sha256": object_digest(weights)}, "cases": cases})
    print(f"Frozen {len(cases)} misses; offline evidence only; no model or Search calls.")

if __name__ == "__main__": main()
