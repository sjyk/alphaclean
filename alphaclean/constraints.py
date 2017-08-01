"""
This module defines a bunch of different types of constraints
"""
import numpy as np
import distance 
import time
import re


class Constraint(object):

    def __init__(self, hint=set()):
        self.hint = hint

        self.hintParams = {}

        try:
            self.hintParams['codebook'] = self.codebook
        except:
            pass

    def qfn(self, df):
        #try:
            return self._qfn(df)
        #except:
        #    N = df.shape[0]
        #    return np.ones((N,))


    def _qfn(self, df):
        raise NotImplemented("Quality fn not implemented")

    def __add__(self, other):
        c = Constraint()
        c.qfn = lambda df: (self.qfn(df) + other.qfn(df))/2

        c.hint = self.hint.union(other.hint)

        c.hintParams =  self.hintParams.copy()
        c.hintParams.update(other.hintParams)

        return c

    def __mul__(self, other):
        try: 
            fother = float(other)
            c = Constraint()
            c.qfn = lambda df: fother*self.qfn(df)
            c.hint = self.hint.union(other.hint)

            c.hintParams =  self.hintParams.copy()
            c.hintParams.update(other.hintParams)

            return c
        except:
            c = Constraint()
            c.qfn = lambda df: np.maximum(self.qfn(df), other.qfn(df))
            c.hint = self.hint.union(other.hint)

            c.hintParams =  self.hintParams.copy()
            c.hintParams.update(other.hintParams)

            return c



class FD(Constraint):

    def __init__(self, source, target):

        self.source = source
        self.target = target

        self.hint = set(source + target)
        self.hintParams = {}


    def _qfn(self, df):

        N = df.shape[0]
        kv = {}
        normalization = 0

        for i in range(N):
            s = tuple(df[self.source].iloc[i,:])
            t = tuple(df[self.target].iloc[i,:])

            if s in kv:
                kv[s].add(t)
            else:
                kv[s] = set([t])

            normalization = max(len(kv[s]), normalization)

        qfn_a = np.zeros((N,))
        for i in range(N):
            s = tuple(df[self.source].iloc[i,:])
            qfn_a[i] = float(len(kv[s]) - 1)/normalization

        return qfn_a


def OneToOne(source, target):
    return FD(source, target)*FD(target, source)





class Predicate(Constraint):

    def __init__(self, attr, expr):

        self.attr = attr
        self.expr = expr

        self.hint = set([attr])

        super(Predicate,self).__init__(self.hint)


    def _qfn(self, df):

        N = df.shape[0]
        qfn_a = np.ones((N,))

        for i in range(N):
            val = df[self.attr].iloc[i]

            if val == None:
                qfn_a[i] = 0.01

            elif self.expr(val):
                qfn_a[i] = 0
            #else:

                #print(val, self.codebook)

        return qfn_a



class Shape(Constraint):

    def __init__(self, rows, columns):

        self.rows = rows
        self.columns = columns


    def _qfn(self, df):

        N = df.shape[0]
        qfn_a = np.zeros((N,))

        if df.shape[0] != self.rows or \
           df.shape[1] != self.columns:
           return np.ones((N,))

        return qfn_a


class CellEdit(Constraint):

    def __init__(self, source, metric={}, w2vModel=None):
        self.source = source

        self.metric = {s: 'edit' for s in source.columns.values}

        semantic = False

        for m in metric:
            self.metric[m] = metric[m]

            if metric[m] == 'semantic':
                semantic = True

        self.word_vectors = w2vModel

        self.cache = {}


    def _qfn(self, df):
        N = df.shape[0]
        p = df.shape[1]
        qfn_a = np.zeros((N,))

        if self.source.shape != df.shape:
            return np.ones((N,))

        for i in range(N):
            for j in range(p):
                target = str(df.iloc[i,j])
                ref = str(self.source.iloc[i,j])
                cname = self.source.columns.values[j]

                #some short circuits so you don't have to eval
                if target == ref:
                    continue
                elif df.iloc[i,j] == None:
                    continue
                elif self.source.iloc[i,j] == None:
                    qfn_a[i] = 1.0/p + qfn_a[i]
                    continue 
                elif target == '' and ref != target:
                    qfn_a[i] = 1.0/p + qfn_a[i]
                    continue 
                elif ref == '' and ref != target:
                    qfn_a[i] = 1.0/p + qfn_a[i]
                    continue


                ttokens = set(target.lower().split())
                rtokens = set(ref.lower().split())

                if self.metric[cname] == 'edit':

                    qfn_a[i] = distance.levenshtein(target, ref, normalized=True)/p + qfn_a[i]
                
                elif self.metric[cname] == 'jaccard':
                    
                    qfn_a[i] = (1.0 - (len(ttokens.intersection(rtokens))+0.)/ (len(ttokens.union(rtokens))+0.))/p + qfn_a[i]

                elif self.metric[cname] == 'semantic':

                    sim = []
                    #print(j, cname, np.mean(sim))

                    for t in ttokens:
                        for r in rtokens:

                            try:
                                similarity = (self.word_vectors.similarity(t,r)+ 1.0)/2
                                #print(t,r)
                            except:
                                similarity = 0

                            sim.append(similarity)

                    #print(target,ref, np.mean(sim))

                    if len(sim) > 0:
                        qfn_a[i] = (1 - np.mean(sim))/p + qfn_a[i]
                    else:
                        qfn_a[i] = 1.0/p + qfn_a[i]




                #print(self.metric[cname], j , target, ref, self.source.columns.values, cname)

                #print(target, ref, qfn_a[i])
        return qfn_a



#special predicates

class DictValue(Predicate):

    def __init__(self, attr, codebook):

        self.attr = attr

        self.codebook = codebook

        super(DictValue, self).__init__(attr, lambda x, codebook=codebook: x in codebook)



class Date(Predicate):

    def __init__(self, attr, pattern):

        self.pattern = pattern
        self.attr = attr

        def timePatternCheck(x, p):

            if x == None or x != x or  len(x.strip()) == 0:
                return False

            try:
                t = time.strptime(x,p)
                #print(t)
                return True
            except ValueError:
                return False


        super(Date, self).__init__(attr, lambda x, p=pattern: timePatternCheck(x,p))


class Float(Predicate):

    def __init__(self, attr, nrange=[-np.inf, np.inf]):

        self.attr = attr
        self.range = nrange

        def floatPatternCheck(x):

            if x == None or isinstance(x, float):
                return True
            else:
                return False

        super(Float, self).__init__(attr, lambda x: floatPatternCheck(x))



class Pattern(Predicate):

    def __init__(self, attr, pattern):

        self.pattern = pattern
        self.attr = attr

        def timePatternCheck(x, p):

            if x == None or len(x) == 0 or x != x:
                return False

            try:
                result = re.match(p, x)
                return (result != None)
            except:
                return False


        super(Pattern, self).__init__(attr, lambda x, p=pattern: timePatternCheck(x,p))





class Parameteric(Constraint):

    def __init__(self, attr, tolerance=5):

        self.tolerance = tolerance
        self.attr = attr
        self.hint = set([attr])
        self.hintParams = {}

        
        super(Parameteric, self).__init__(self.hint)

    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))
        vals = df[self.attr].dropna().values
        mean = np.mean(vals)
        std = np.std(vals)

        for i in range(N):
            val = df[self.attr].iloc[i]

            if np.isnan(val) or np.abs(val-mean) < std*self.tolerance:
                qfn_a[i] = 0.0
            else:
                qfn_a[i] = 1.0

        return qfn_a


class NonParametric(Constraint):

    def __init__(self, attr, tolerance=5):

        self.tolerance = tolerance
        self.attr = attr
        self.hint = set([attr])
        self.hintParams = {}

        
        super(NonParametric, self).__init__(self.hint)

    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))
        vals = df[self.attr].dropna().values
        mean = np.median(vals)
        std = np.median(np.abs(vals-mean))

        for i in range(N):
            val = df[self.attr].iloc[i]

            if np.isnan(val) or np.abs(val-mean) < std*self.tolerance:
                qfn_a[i] = 0.0
            else:
                qfn_a[i] = 1.0

        return qfn_a



class Correlation(Constraint):

    def __init__(self, attrs, ctype="positive"):

        self.ctype = ctype
        self.attrs = attrs
        self.hint = set(attrs)
        self.hintParams = {}

        
        super(Correlation, self).__init__(self.hint)


    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))

        x = df[self.attrs[0]].values
        y = df[self.attrs[1]].values

        mx = np.median(x[~np.isnan(x)])
        my = np.median(y[~np.isnan(y)])

        for i in range(N):
            val1 = df[self.attrs[0]].iloc[i] - mx
            val2 = df[self.attrs[1]].iloc[i] - my

            if np.isnan(val1) or np.isnan(val2):
                continue

            if self.ctype == 'positive':
                if np.sign(val1*val2) < 0:
                    qfn_a[i] = np.abs(val1) + np.abs(val2)
            else:
                if np.sign(val1*val2) > 0:
                    qfn_a[i] = math.abs(val1) + math.abs(val2)

        #normalize
        if np.sum(qfn_a) > 0:
            qfn_a = qfn_a/np.max(qfn_a)

        return qfn_a
