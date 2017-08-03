from collections import Counter


def generateCodebook(d, attr, size=100):
    """Helper method to select the top k values in the attribute by count
    """
    s = Counter([v for v in d[attr].values if v == str(v)])
    l = [i for i in sorted([(s[k],k) for k in s], reverse=True)]

    codebook = set([occ[1] for occ in l][0:size])

    return codebook