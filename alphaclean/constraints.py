"""
This module defines a bunch of different types of constraints
"""
import numpy as np
import distance 
import time
import re

class Constraint(object):

    def __init__(self):
        self.hint = set()

    def qfn(self, df):
        try:
            return self._qfn(df)
        except:
            N = df.shape[0]
            return np.ones((N,))


    def _qfn(self, df):
        raise NotImplemented("Quality fn not implemented")

    def __add__(self, other):
        c = Constraint()
        c.qfn = lambda df: (self.qfn(df) + other.qfn(df))/2

        c.hint = self.hint.union(other.hint)

        return c

    def __mul__(self, other):
        try: 
            fother = float(other)
            c = Constraint()
            c.qfn = lambda df: fother*self.qfn(df)
            c.hint = self.hint.union(other.hint)
            return c
        except:
            c = Constraint()
            c.qfn = lambda df: np.maximum(self.qfn(df), other.qfn(df))
            c.hint = self.hint.union(other.hint)
            return c



class FD(Constraint):

    def __init__(self, source, target):

        self.source = source
        self.target = target

        self.hint = set(source + target)


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


    def _qfn(self, df):

        N = df.shape[0]
        qfn_a = np.ones((N,))

        for i in range(N):
            val = df[self.attr].iloc[i]

            if val == None:
                qfn_a[i] = 0.01

            elif self.expr(val):
                qfn_a[i] = 0

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

    def __init__(self, source):
        self.source = source

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

                #print(target, ref, distance.levenshtein(target, ref, normalized=True))
                
                qfn_a[i] = distance.levenshtein(target, ref, normalized=True)/p + qfn_a[i]
                #print(ref, target, distance.levenshtein(target, ref, normalized=True))

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

            if x == None or len(x.strip()) == 0:
                return False

            try:
                t = time.strptime(x,p)
                #print(t)
                return True
            except ValueError:
                return False


        super(Date, self).__init__(attr, lambda x, p=pattern: timePatternCheck(x,p))



class Pattern(Predicate):

    def __init__(self, attr, pattern):

        self.pattern = pattern
        self.attr = attr

        def timePatternCheck(x, p):

            if x == None or len(x) == 0:
                return False

            try:
                result = re.match(p, x)
                return (result != None)
            except:
                return False


        super(Pattern, self).__init__(attr, lambda x, p=pattern: timePatternCheck(x,p))