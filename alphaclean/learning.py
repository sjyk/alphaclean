from alphaclean.ops import *
import distance
import numpy as np
from sklearn.linear_model import SGDClassifier 
from sklearn.metrics import classification_report


def similarityFeatures(s, t):
    
    s = str(s)
    t = str(t)

    dist1 = distance.levenshtein(s, t, normalized=True)

    stokens = set(s.lower().split())
    ttokens = set(t.lower().split())

    dist2 = (len(stokens.intersection(ttokens))+0.)/ (len(stokens.union(ttokens))+0.)

    v = np.zeros((2,1))
    v[0] = dist1
    v[1] = dist2

    return v


def getFeatures(neg, pos, df):

    schema = df.columns.values.tolist()
    N = len(pos)*2
    d =  len(schema)+2
    X = np.zeros((N,d))
    Y = np.zeros((N,1))

    #print(schema)

    i = 0 
    for p in pos:
        if isinstance(p, Swap):
            
            v = np.zeros((d,1))
            v[schema.index(p.column)] = 1

            if len(p.predicate[1]) != 0:
                v[len(schema):len(schema)+2] = similarityFeatures(p.value, next(iter(p.predicate[1])))

            X[i,:] = v.reshape((-1, d))
            Y[i,0] = 1

            i = i + 1


    if np.sum(Y) == 0.0:
        return


    Np = np.arange(len(neg))
    indices = set(np.random.choice(Np, int(np.sum(Y))))
    negl = list(neg)
    neg = [negl[j] for j in indices]

    for n in neg:
        if isinstance(n, Swap):
            
            v = np.zeros((d,1))
            v[schema.index(n.column)] = 1

            if len(n.predicate[1]) != 0:
                v[len(schema):len(schema)+2] = similarityFeatures(n.value, next(iter(n.predicate[1])))

            X[i,:] = v.reshape((-1, d))

            i = i + 1

    non_zero = np.squeeze(np.argwhere(np.sum(X,axis=1)))
    Xp = X[non_zero, :]
    Yp = Y[non_zero, 0]

    if len(non_zero.shape) == 0 or \
             non_zero.shape[0] == N:
        return None

    #print(Xp)

    if np.sum(Y) > 0:
        rf = SGDClassifier(loss='modified_huber', alpha=0.1)
        #print(X,Y)
        rf.fit(Xp,Yp)

        return rf

    return None


def predict(model, tf, df):
    schema = df.columns.values.tolist()
    d =  len(schema)+2
    X = np.zeros((1,d))

    if not isinstance(tf, Swap):
        return True

    if len(tf.predicate[1]) == 0:
        return True

    X[0,schema.index(tf.column)] = 1
    X[0, len(schema):len(schema)+2] = similarityFeatures(tf.value, next(iter(tf.predicate[1]))).reshape((2,))
    return np.squeeze(model.predict_proba(X))[1] >= 0.25


