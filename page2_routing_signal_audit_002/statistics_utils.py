"""Dependency-free, tie-aware descriptive statistics; no fitting or routing."""
from bisect import bisect_left
from collections import Counter, defaultdict
from math import sqrt
from statistics import mean, variance


def quantile(values, p):
    xs = sorted(values)
    if not xs:
        return None
    index = (len(xs)-1)*p
    lo = int(index)
    hi = min(lo+1, len(xs)-1)
    return xs[lo] + (xs[hi]-xs[lo])*(index-lo)


def summarize(xs):
    return {'n': len(xs), 'mean': mean(xs) if xs else None,
            'std_sample': sqrt(variance(xs)) if len(xs)>1 else None,
            **{name: quantile(xs, p) for name, p in [('min',0), ('p10',.1), ('q25',.25), ('median',.5), ('q75',.75), ('p90',.9), ('max',1)]}}


def ranks(xs):
    ordered = sorted(range(len(xs)), key=xs.__getitem__)
    result = [0.0]*len(xs)
    i = 0
    while i < len(xs):
        j = i+1
        while j < len(xs) and xs[ordered[j]] == xs[ordered[i]]:
            j += 1
        rank = (i+1+j)/2
        for k in ordered[i:j]:
            result[k] = rank
        i = j
    return result


def pearson(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    xx = sum((v-mx)**2 for v in xs)
    yy = sum((v-my)**2 for v in ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sqrt(xx*yy) if xx and yy else None


def discrimination(xs, labels):
    positives, negatives = sum(labels), len(labels)-sum(labels)
    if not positives or not negatives:
        return {'roc_auc': None, 'average_precision': None, 'pr_auc_trapezoidal': None}
    rs = ranks(xs)
    auc = (sum(r for r,y in zip(rs,labels) if y)-positives*(positives+1)/2)/(positives*negatives)
    buckets = defaultdict(lambda: [0,0])
    for x,y in zip(xs,labels):
        buckets[x][0] += y
        buckets[x][1] += 1-y
    tp=fp=0
    last_recall, last_precision, ap, trap = 0.0, 1.0, 0.0, 0.0
    for score in sorted(buckets, reverse=True):
        p,n = buckets[score]
        tp += p
        fp += n
        recall, precision = tp/positives, tp/(tp+fp)
        ap += (recall-last_recall)*precision
        trap += (recall-last_recall)*(precision+last_precision)/2
        last_recall,last_precision = recall,precision
    return {'roc_auc': auc, 'average_precision': ap, 'pr_auc_trapezoidal': trap}


def hedges_g(xs, labels):
    pos = [x for x,y in zip(xs,labels) if y]
    neg = [x for x,y in zip(xs,labels) if not y]
    if len(pos)<2 or len(neg)<2:
        return None
    df = len(xs)-2
    sd = sqrt(((len(pos)-1)*variance(pos)+(len(neg)-1)*variance(neg))/df)
    return (1-3/(4*df-1))*(mean(pos)-mean(neg))/sd if sd else None


def metric_bundle(xs, gains):
    labels = [int(g>0) for g in gains]
    high = discrimination(xs,labels)
    low = discrimination([-x for x in xs],labels)
    return {'auc_high': high['roc_auc'], 'ap_high': high['average_precision'],
            'ap_low': low['average_precision'], 'pearson_gain': pearson(xs,gains),
            'spearman_gain': pearson(ranks(xs),ranks(gains)), 'hedges_g': hedges_g(xs,labels)}


def conditional(xs, gains, questions):
    groups = defaultdict(list)
    for x,g,q in zip(xs,gains,questions):
        groups[q].append((x,g))
    numerator=denominator=0
    question_aucs=[]
    dx=[]; dg=[]; rx=[]; rg=[]
    for q,pairs in groups.items():
        xx,gg = map(list,zip(*pairs))
        yy=[int(g>0) for g in gg]
        auc=discrimination(xx,yy)['roc_auc']
        if auc is not None:
            weight=sum(yy)*(len(yy)-sum(yy))
            numerator += auc*weight
            denominator += weight
            question_aucs.append(auc)
        xr,gr=ranks(xx),ranks(gg)
        dx.extend(v-mean(xx) for v in xx)
        dg.extend(v-mean(gg) for v in gg)
        rx.extend(v-mean(xr) for v in xr)
        rg.extend(v-mean(gr) for v in gr)
    return {'pair_weighted_within_question_auc_high': numerator/denominator if denominator else None,
            'macro_within_question_auc_high': mean(question_aucs) if question_aucs else None,
            'mixed_label_question_count': len(question_aucs), 'positive_negative_pair_count': denominator,
            'question_centered_pearson_gain': pearson(dx,dg),
            'within_question_rank_centered_correlation_gain': pearson(rx,rg)}


def strata(xs,gains):
    cuts=sorted(set(quantile(xs,p) for p in [.2,.4,.6,.8]))
    groups=defaultdict(list)
    for x,g in zip(xs,gains):
        groups[bisect_left(cuts,x)].append((x,g))
    bins=[]
    for i,pairs in sorted(groups.items()):
        xx,gg=map(list,zip(*pairs))
        pos=sum(g>0 for g in gg)
        bins.append({'bin_index':i,'lower_exclusive':cuts[i-1] if i else None,
                     'upper_inclusive':cuts[i] if i<len(cuts) else None,
                     'observed_min':min(xx),'observed_max':max(xx),'n':len(xx),
                     'positive_count':pos,'negative_count':len(xx)-pos,
                     'positive_rate':pos/len(xx),'mean_query_gain':mean(gg)})
    return {'label_blind_pooled_quantile_cuts':cuts,'ties_split':False,'bins':bins}


def self_test():
    assert discrimination([0,1],[0,1])['roc_auc']==1
    assert discrimination([0,1],[1,0])['roc_auc']==0
    assert discrimination([1,1],[0,1])['roc_auc']==.5
    assert discrimination([1,1],[0,1])['average_precision']==.5
    assert discrimination([0,1],[0,1])['average_precision']==1
    assert discrimination([0,1],[1,0])['average_precision']==.5
    assert ranks([1,2,2,4])==[1,2.5,2.5,4]
    assert pearson([1,1],[1,2]) is None
    assert abs(pearson([1,2,3],[6,4,2])+1)<1e-12
    assert discrimination([1,2],[0,0])['roc_auc'] is None
    assert len(strata([1,1,1],[0,1,2])['bins'])==1
    # Cross-question discrimination can be perfect while within-question values tie.
    c=conditional([0,0,1,1],[0,1,0,1],[0,0,1,1])
    assert c['pair_weighted_within_question_auc_high']==.5
    assert c['question_centered_pearson_gain'] is None
    return True
