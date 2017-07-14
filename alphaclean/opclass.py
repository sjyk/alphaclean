
"""
An operation class defines a set of operations
"""

from ops import *
from itertools import combinations
import re
import numpy as np


class OperationClass(object):

    def __init__(self, df, scopeAttrs=set(), targetAttrs=set(), empty=False, trigger=None, **kw):
        
        self.df = df
        self.trigger = trigger
        self.kw = kw

        if len(scopeAttrs) == 0:
            self.scopeAttrs = df.keys()
        else:
            self.scopeAttrs = scopeAttrs


        if len(targetAttrs) == 0:
            self.targetAttrs = df.keys()
        else:
            self.targetAttrs = targetAttrs

        if not empty:
            self.operations = self.generate(df, trigger)
        else:
            self.operations = set()


    def __add__(self, a):

        opclass = OperationClass(df=self.df,  
                                 scopeAttrs=self.scopeAttrs, 
                                 targetAttrs=self.targetAttrs, 
                                 empty=True, 
                                 trigger=self.trigger,
                                 **self.kw)

        opclass.operations = self.operations.union(a.operations)

        opclass._generate = lambda df, trigger: self._generate(df, trigger).union(a._generate(df, trigger))

        return opclass


    def generate(self, dataFrame, trigger):

        #return null if there is nothing to do
        try:
            if trigger == None:
                return set()
        except:
            pass

        return self._generate(dataFrame, trigger)


    def regenerate(self, dataFrame, trigger):
        self.operations = self.generate(dataFrame, trigger)


    def _generate(self, dataFrame, trigger):
        raise NotImplemented("Must implement a generate() function")

    def __iter__(self):
        return self.operations.__iter__()

    def next(self): 
        return self.operations.next()





class FindAndReplaceClass(OperationClass):

    def __init__(self, *args, **kw):
        self.attrScopeLimit = kw['attrLimit']
        super(FindAndReplaceClass, self).__init__(*args, **kw)


    def _generate(self, dataFrame, trigger):

        attrs = self.targetAttrs

        operations = set()

        for a in attrs:

            target_values = set(dataFrame[a].tolist())

            for s in range(1,self.attrScopeLimit+1):

                for b in combinations(self.scopeAttrs, s):

                    trigger_projection = dataFrame.iloc[trigger,:][list(b)]

                    trigger_tuples = set([tuple(x) for x in trigger_projection.to_records(index=False)])

                    for scope in trigger_tuples:

                        for t in target_values:

                            operations.add(FindAndReplace(b, scope, a, t))



        return operations





class CastingClass(OperationClass):

    def __init__(self, *args, **kw):
        super(CastingClass, self).__init__(*args, **kw)



    def _generate(self, dataFrame, trigger):

        attrs = self.targetAttrs
        casts = [str, int, float]

        operations = set()

        for a in attrs:

            for c in casts:
                operations.add(Cast(a, c))
            
        return operations





class FormattingClass(OperationClass):

    def __init__(self, *args, **kw):
        super(FormattingClass, self).__init__(*args, **kw)


    def _generate(self, dataFrame, trigger):

        attrs = self.targetAttrs

        casts = [lambda s: s.strip(), 
                 lambda s: re.sub(r'\W+', '', s), 
                 lambda s: re.sub(r'[^0-9]','', s), 
                 lambda s: re.sub(r'[^a-zA-Z]','', s)]

        operations = set()

        for a in attrs:

            for c in casts:
                operations.add(Cast(a, c))
            
        return operations




class ERClass(OperationClass):

    def __init__(self, *args, **kw):
        
        self.similarityFn = kw['similarityFunction']
        self.steps = kw['steps']

        super(ERClass, self).__init__(*args, **kw)


    def _generate(self, dataFrame, trigger):

        attrs = self.targetAttrs

        thresh_vals = np.arange(0,1,self.steps)

        operations = set()

        for a in attrs:

            for t in thresh_vals:
            
                operations.add(ER(a, self.similarityFn, t))

            
        return operations

