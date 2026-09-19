"""Fixed mechanical statistics. No GT, expansion dictionary or semantic judge."""
import collections
import itertools
import re
import statistics

THRESHOLD=.85
def tokens(text):return set(re.findall(r'[a-z0-9]+',text.casefold()))

def measure(g):
    queries=g['queries'];raw=g['raw_output']
    # Preserve names of all action-shaped bracket tokens; unknown ones require review.
    bracket_tokens=re.findall(r'\[([A-Za-z][A-Za-z0-9_]*)\]',raw)
    nonsearch=[x for x in bracket_tokens if x not in ('Search','StopSearch')]
    pairs=[]
    for i,j in itertools.combinations(range(len(queries)),2):
        a,b=tokens(queries[i]),tokens(queries[j]);score=len(a&b)/len(a|b) if a|b else 0
        exact=queries[i]==queries[j]
        pairs.append({'query_indices':[i,j],'exact_duplicate':exact,'token_jaccard':score,'high_similarity':score>=THRESHOLD,'near_duplicate':not exact and score>=THRESHOLD})
    exact_counts=collections.Counter(queries)
    return {'parse_success_at_least_one':len(queries)>0,'nonempty_parse_success':any(bool(q) for q in queries),
      'query_count':len(queries),'empty_query_count':sum(not q for q in queries),
      'strict_search_format':bool(re.fullmatch(r'\s*(?:\[Search\][^\[\]]+)+\[StopSearch\]\s*',raw,re.DOTALL)),
      'non_search_markers':nonsearch,'non_search_marker_counts':dict(collections.Counter(nonsearch)),
      'has_non_search_action':bool(nonsearch),'has_expand':any(x in ('Expand','StopExpand') for x in nonsearch),
      'exact_duplicate_query_count':sum(n-1 for n in exact_counts.values()),
      'exact_duplicate_pair_count':sum(x['exact_duplicate'] for x in pairs),
      'high_similarity_pair_count':sum(x['high_similarity'] for x in pairs),
      'near_duplicate_pair_count':sum(x['near_duplicate'] for x in pairs),
      'pair_count':len(pairs),'mean_pairwise_token_jaccard':statistics.mean(x['token_jaccard'] for x in pairs) if pairs else None,'pairs':pairs}

def summarize(qs,group):
    ms=[q['groups'][group]['metrics'] for q in qs];pairs=[x for m in ms for x in m['pairs']]
    return {'question_count':len(qs),'search_parse_success':sum(m['parse_success_at_least_one'] for m in ms),
      'search_parse_success_rate':sum(m['parse_success_at_least_one'] for m in ms)/len(qs),
      'no_search_query_questions':sum(not m['parse_success_at_least_one'] for m in ms),
      'nonempty_parse_success':sum(m['nonempty_parse_success'] for m in ms),
      'strict_search_format_questions':sum(m['strict_search_format'] for m in ms),
      'non_search_action_questions':sum(m['has_non_search_action'] for m in ms),
      'non_search_action_marker_occurrences':sum(len(m['non_search_markers']) for m in ms),
      'non_search_action_marker_distribution':dict(collections.Counter(x for m in ms for x in m['non_search_markers'])),
      'expand_questions':sum(m['has_expand'] for m in ms),'total_query_count':sum(m['query_count'] for m in ms),
      'query_count_distribution':dict(sorted(collections.Counter(str(m['query_count']) for m in ms).items())),
      'empty_query_count':sum(m['empty_query_count'] for m in ms),'exact_duplicate_query_count':sum(m['exact_duplicate_query_count'] for m in ms),
      'exact_duplicate_pair_count':sum(m['exact_duplicate_pair_count'] for m in ms),
      'high_similarity_pair_count':sum(m['high_similarity_pair_count'] for m in ms),
      'near_duplicate_pair_count':sum(m['near_duplicate_pair_count'] for m in ms),
      'questions_with_exact_duplicates':sum(m['exact_duplicate_query_count']>0 for m in ms),
      'questions_with_near_duplicates':sum(m['near_duplicate_pair_count']>0 for m in ms),
      'pair_count':len(pairs),'high_similarity_pair_rate':sum(x['high_similarity'] for x in pairs)/len(pairs) if pairs else None,
      'mean_pairwise_token_jaccard_pooled':statistics.mean(x['token_jaccard'] for x in pairs) if pairs else None,
      'mean_pairwise_token_jaccard_macro_eligible':statistics.mean(m['mean_pairwise_token_jaccard'] for m in ms if m['pair_count']) if pairs else None,
      'questions_with_at_least_two_queries':sum(m['pair_count']>0 for m in ms),
      'non_eos_generations':sum(not q['groups'][group]['ended_with_eos'] for q in qs),
      'generations_exceeding_native_query_cap':sum(bool(q['groups'][group]['discarded_queries']) for q in qs)}
