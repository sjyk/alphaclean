import numpy as np
import distance 
import logging


""" Module: Constraints

The data scientist models her data with a formal language of logical constraints 
(e.g., functional dependencies, denial constraints, statistical models). AlphaClean
searches over space of transformations to best optimize the data for this model.

Release Notes: Will probably rename to 'Data Model' in the future
"""


class Constraint(object):
    """A constraint object is the basic wrapper class for translating a formal data model specification
    to a quality function.
    """


    def __init__(self, hint=set()):
        """A basic constraint object.

        Keyword arguments:
        hint -- a set of attribute names
        """

        self.hint = hint

        #this is special case code to handle constraints where the domain is not closed
        self.hintParams = {}

        try:
            self.hintParams['codebook'] = self.codebook
        except:
            pass


    def qfn(self, df):
        """Evaluates the quality function for a specific database instance. This function 
        calls the private method implemented by all the subclasses.

        Positional arguments:
        df -- a pandas dataframe
        """
        return self._qfn(df)


    def _qfn(self, df):
        raise NotImplemented("Quality fn not implemented")


    #the below methods implement a basic algebra over the quality functions


    def __add__(self, other):
        """__add__ sums two quality functions """
        c = Constraint()
        c.qfn = lambda df: (self.qfn(df) + other.qfn(df))/2

        c.hint = self.hint.union(other.hint)

        c.hintParams =  self.hintParams.copy()
        c.hintParams.update(other.hintParams)

        return c




    def __mul__(self, other):
        """__mul__ bitwise and relationship two quality functions """
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


class Predicate(Constraint):
    """A Predicate Constraint is the most basic type of a constraint, it isn't intended for direct use
    but rather an important building block for more informative higher-level constraints.
    """

    def __init__(self, attr, expr, none_penalty=0.01):
        """The constructor takes in an attribute and a lambda that maps the attribute value to a true or false.

        Positional arguments:
        attr -- a string value representing the attribute over which the predicate is applied
        expr -- a function domain(attr) -> {true, false} 

        Keyword arguments:
        none_penalty -- a penalty for none values
        """

        self.attr = attr
        self.expr = expr

        self.hint = set([attr])

        self.none_penalty = none_penalty

        super(Predicate,self).__init__(self.hint)


    def _qfn(self, df):

        N = df.shape[0]
        qfn_a = np.ones((N,))

        for i in range(N):
            val = df[self.attr].iloc[i]

            if val == None:
                qfn_a[i] = self.none_penalty

            elif self.expr(val):
                qfn_a[i] = 0

        return qfn_a



class CellEdit(Constraint):
    """CellEdit constraint is a quasi-constraint that penalizes modifications to the dataset. The user supplies a 
    source dataset and the constraint compares the edits with the current dataset and scores the changes.
    """

    def __init__(self, source, metric={}, w2vModel=None):
        """CellEdit constructor allowed similarity metrics are 'jaccard', 'semantic', 'edit'

        Positional arguments:
        source -- a dataframe

        Keyword arguments:
        metric -- a dict mapping attributes to a similarity metric. {a : metric}. allowed similarity metrics are 'jaccard', 'semantic', 'edit'
        w2vModel -- this is neccessary if 'semantic' is chosen.
        """

        self.source = source


        #default the metric to 'edit' distance
        self.metric = {s: 'edit' for s in source.columns.values}


        semantic = False

        for m in metric:
            self.metric[m] = metric[m]

            if metric[m] == 'semantic':
                semantic = True

        self.word_vectors = w2vModel

        if semantic and w2vModel == None:
            raise ValueError("Must provide a word2vec model if you are using semantic similarity")

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


                if self.metric[cname] == 'edit':

                    qfn_a[i] = self.edit(target,ref)/p + qfn_a[i]
                
                elif self.metric[cname] == 'jaccard':
                    
                    qfn_a[i] = self.jaccard(target, ref)/p + qfn_a[i]

                elif self.metric[cname] == 'semantic':
                    qfn_a[i] = self.semantic(target, ref)/p + qfn_a[i]

                else:

                    raise ValueError('Unknown Similarity Metric: ' + self.metric[cname])

        return qfn_a


    def edit(self, target,ref):
        return distance.levenshtein(target, ref, normalized=True)

    def jaccard(self, target,ref):
        ttokens = set(target.lower().split())
        rtokens = set(ref.lower().split())
        return (1.0 - (len(ttokens.intersection(rtokens))+0.)/ (len(ttokens.union(rtokens))+0.))


    def semantic(self, target, ref):
        ttokens = set(target.lower().split())
        rtokens = set(ref.lower().split())

        sim = []
        for t in ttokens:
            for r in rtokens:

                try:
                    similarity = (self.word_vectors.similarity(t,r)+ 1.0)/2
                except:
                    similarity = 0

                sim.append(similarity)

        if len(sim) > 0:
            return (1 - np.mean(sim)) 
        else:
            return 1.0




