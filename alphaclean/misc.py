from collections import Counter
import numpy as np


def generateCodebook(d, attr, size=100):
    """Helper method to select the top k values in the attribute by count
    """
    s = Counter([v for v in d[attr].values if v == str(v)])
    l = [i for i in sorted([(s[k],k) for k in s], reverse=True)]

    codebook = set([occ[1] for occ in l][0:size])

    return codebook


def generateCorrelationCodebook(d, attr, labels, size=100):
    values = set([v for v in d[attr].values if v == str(v)])
    
    ranked_tokens = []

    for v in values:
        corr = np.abs(np.corrcoef(d[attr]==v, labels)[0,1])
        ranked_tokens.append((corr, v))

    ranked_tokens.sort(reverse=True)

    return set([v[1] for v in ranked_tokens[:size]])
