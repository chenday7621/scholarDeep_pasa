"""Reuse the frozen offline guard and native parser; no model dependencies."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PREVIOUS = REPO / 'adaptive_page2_controller_offline_001'
sys.path.insert(0, str(PREVIOUS))
from common import Guard, read, save, sha, digest, hits, check_response, PLAN, SOURCE

PROMPTS = Path('/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0/run')
SHARED_CODE = [PREVIOUS / 'common.py', HERE / 'audit_common.py']

PLAN_SPEC = {
    'experiment': 'page2_routing_signal_audit_002',
    'unit': '248 native queries from the frozen 50-question snapshot',
    'label': 'positive iff isolated Page2 gain relative to all native Page1 of the same question is at least 1',
    'features': 'Existing Page1 set statistics plus model-free lexical TF-IDF similarities to question/query. Embedding semantics unavailable.',
    'text': 'Original saved user question and native query versus Page1 parsed organic title + snippet; no GT, Page2, paper metadata or full text.',
    'rank_windows': 'top1, positions 1-3, positions 8-10, mean, max; top3-tail3 decay and OLS score slope per rank',
    'missing': 'Empty windows -> null, never zero relevance; report valid sample count and label-specific missingness.',
    'orientation': 'Report both high-positive and low-positive single-feature AUC/AP; descriptive only, no selected deployable orientation.',
    'statistics': 'Group distributions, Hedges g, Cliff delta; ROC-AUC, AP (primary PR area) and trapezoidal PR-AUC; Pearson/Spearman with integer gain.',
    'stratification': 'Pooled label-blind quintile cutpoints; do not split ties; repeated cutpoints collapse.',
    'dependence': '1000 question-cluster bootstrap draws, seed 20260917; conditional within-question AUC and centered correlations.',
    'multiplicity': 'Exploratory simultaneous feature inspection. Marginal 95% CIs are not multiplicity-adjusted significance claims.',
    'prohibitions': ['no model calls', 'no network', 'no threshold tuning', 'no weight tuning', 'no policy output', 'no source changes'],
}
