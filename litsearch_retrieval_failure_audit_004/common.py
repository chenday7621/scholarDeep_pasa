"""Shared deterministic helpers for LitSearch retrieval failure audit."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SOURCE = REPO / "page2_routing_prereg_validation_003b"
END_DATE = "2026-09-17"
ARXIV_PATTERN = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)")
STOPWORDS = set("a an and are as at be been being by can could did do does doing for from had has have having he her hers him his how i if in into is it its may might more most of on or our ours should so some such than that the their theirs them then there these they this those through to too under up use used using via was we were what when where which who why will with would you your yours any paper papers work works research article articles study studies suggest recommend find first propose proposed explores explored investigate investigated toward towards based new approach method methods model models system systems task tasks data dataset datasets framework language large neural learning training generation text author arxiv survey".split())

def now():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text())

def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def object_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def tokens(text, keep_stopwords=False):
    values = re.findall(r"[a-z0-9]+", (text or "").casefold().replace("’", "'"))
    if keep_stopwords:
        return values
    return [value for value in values if value not in STOPWORDS and (len(value) > 1 or value.isdigit())]

def token_set(text):
    return set(tokens(text))

def jaccard(left, right):
    left, right = set(left), set(right)
    return len(left & right) / len(left | right) if left | right else 0.0

def recall(reference, candidate):
    reference, candidate = set(reference), set(candidate)
    return len(reference & candidate) / len(reference) if reference else 0.0

def idf(documents):
    sets = [set(tokens(document)) for document in documents]
    counts = Counter(token for document in sets for token in document)
    size = len(sets)
    return {token: math.log((size + 1) / (frequency + 1)) + 1 for token, frequency in counts.items()}

def cosine(left_text, right_text, weights):
    left, right = Counter(tokens(left_text)), Counter(tokens(right_text))
    numerator = sum(left[token] * right[token] * weights.get(token, 1) ** 2 for token in set(left) & set(right))
    left_norm = math.sqrt(sum(count ** 2 * weights.get(token, 1) ** 2 for token, count in left.items()))
    right_norm = math.sqrt(sum(count ** 2 * weights.get(token, 1) ** 2 for token, count in right.items()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0

def char_ngrams(text, n=3):
    normalized = " ".join(tokens(text, keep_stopwords=True))
    return {normalized[index:index + n] for index in range(max(0, len(normalized) - n + 1))}

def lexical_metrics(left, right, weights):
    left_tokens, right_tokens = token_set(left), token_set(right)
    return {"token_jaccard": jaccard(left_tokens, right_tokens), "left_token_coverage": recall(left_tokens, right_tokens), "right_token_coverage": recall(right_tokens, left_tokens), "tfidf_cosine": cosine(left, right, weights), "char_trigram_jaccard": jaccard(char_ngrams(left), char_ngrams(right)), "shared_content_tokens": sorted(left_tokens & right_tokens)}

def core_phrase(title):
    generic = {"analysis", "evaluation", "performance", "improving", "enhancing", "effective", "efficient", "toward", "towards", "via", "using", "based", "pretrained"}
    values = [token for token in tokens(title) if token not in generic]
    return " ".join(values[:6] if len(values) >= 3 else tokens(title)[:6])

def parsed_id(link):
    match = ARXIV_PATTERN.search(link or "")
    return match.group(1) if match else None

def verify_source():
    validation = read(SOURCE / "validation.json")
    assert validation["status"] == "PASS"
    for name in ["snapshot_manifest.json", "states.json", "decisions.json", "results.json", "dataset_manifest.json", "validation.json"]:
        if name in validation.get("artifact_hashes", {}):
            assert sha(SOURCE / name) == validation["artifact_hashes"][name], name
    snapshots = read(SOURCE / "snapshot_manifest.json")
    assert snapshots["status"] == "COMPLETE" and snapshots["query_count"] == 222
    for item in snapshots["snapshots"].values():
        for page in ("page1", "page2"):
            assert sha(SOURCE / item[page]["path"]) == item[page]["file_sha256"]
    return validation, snapshots
