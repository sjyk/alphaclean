"""
This module generates feasible parameter settings, the settings 
are in a form of an ordered list
"""

from itertools import combinations, product
from ops import *
from constraints import *
from core import *
import copy
import string
import logging


class ParameterSampler(object):

    def __init__(self, df, qfn, operationList, similarity, substrThresh=0.1, scopeLimit=3, predicate_granularity=None):
        self.df = df
        self.qfn = qfn.qfn
        self.qfnobject = qfn
        self.substrThresh = substrThresh
        self.scopeLimit = scopeLimit
        self.operationList = operationList
        self.predicate_granularity = predicate_granularity
        self.similarity = similarity

        self.predicateIndex = {}

        self.dataset = Dataset(df)


    def getParameterGrid(self):
        parameters = []
        paramset = [(op, sorted(op.paramDescriptor.values()), op.paramDescriptor.values()) for op in self.operationList]

        for op, p, orig in paramset:

            if p[0] == ParametrizedOperation.COLUMN:

                #remove one of the cols
                origParam = copy.copy(orig)
                orig.remove(p[0])
                colParams = []


                for col in self.columnSampler():

                    grid = []

                    for pv in orig:
                        #print(pv)
                        grid.append(self.indexToFun(pv, col))

                    augProduct = []
                    for p in product(*grid):
                        v = list(p)
                        v.insert(0, col)
                        augProduct.append(tuple(v))

                    colParams.extend(augProduct)

                parameters.append((op, colParams, origParam))

            else:
                
                grid = []

                for pv in orig:

                    grid.append(self.indexToFun(pv))


                parameters.append( (op, product(*grid), orig))

        return parameters


    def getAllOperations(self):

        parameterGrid = self.getParameterGrid()
        operations = []

        for i , op in enumerate(self.operationList):
            args = {}

            #print(parameterGrid[i][1])
            
            for param in parameterGrid[i][1]:
                arg = {}
                for j, k in enumerate(op.paramDescriptor.keys()):
                    arg[k] = param[j]
                
                #optimization
                if self.pruningRules(arg):
                    continue

                operations.append(op(**arg))

        operations.append(NOOP())

        logging.debug("Library generator created "+str(len(operations)) + " operations")
        
        return operations 



    def pruningRules(self, arg):

        #remove imputes that are uncorrelated
        if 'value' in arg:

            if 'predicate' in arg and list(arg['predicate'][1])[0] == None:
                return True


            if 'codebook' in self.qfnobject.hintParams:
                sim = self.qfnobject.threshold
                
                if self.similarity.semantic(str(arg['value']), str(list(arg['predicate'][1])[0])) > sim:
                    return True


            if 'column' in arg and 'predicate' in arg and arg['column'] == arg['predicate'][0]:

                return (arg['value'] != arg['value']) or (arg['value'] == None) or (arg['value'] in arg['predicate'][1]) or (len(arg['predicate'][1]) == 0)

            else:
                return (arg['value'] != arg['value']) or (arg['value'] == None)

        if 'substr1' in arg and 'substr2' in arg:
            return (arg['substr1'] == arg['substr2'])

        return False




    def indexToFun(self, index, col=None):
        if index == ParametrizedOperation.COLUMN:
            return self.columnSampler()
        elif index == ParametrizedOperation.COLUMNS:
            return self.columnsSampler()
        elif index == ParametrizedOperation.VALUE:
            return self.valueSampler(col)
        elif index == ParametrizedOperation.SUBSTR:
            return self.substrSampler(col)
        elif index == ParametrizedOperation.PREDICATE:
            return self.predicateSampler(col)
        else:
            raise ValueError("Error in: " + index)


    def columnSampler(self):
        return list(self.qfnobject.hint)


    def columnsSampler(self):
        columns = self.columnSampler()
        result = []
        for i in range(1, min(len(columns), self.scopeLimit)):
            result.extend([list(a) for a in combinations(columns, i)])

        return result


    #brute force
    def valueSampler(self, col):
        if 'codebook' in self.qfnobject.hintParams:
            return list(self.qfnobject.hintParams['codebook'])
        else:
            return list(set(self.df[col].values))
  

    """
    def valueSampler(self, col):
        v = np.sign(self.qfn(self.df))

        values = set()

        for i in range(self.df.shape[0]):
            if v[i] == 1:
                values.add(self.df[col].iloc[i])

        return list(values)
    """



    def substrSampler(self, col):
        chars = {}
        #print(self.df[col].values)
        for v in self.df[col].values:
            if v != None:
                for c in set(str(v)):
                    if c not in chars:
                        chars[c] = 0

                    chars[c] += 1

        #print((chars[' ']+0.)/self.df.shape[0])
        #print()

        #print([c for c in chars if not c.isalnum()])
        return ['-','/']
        #return [c for c in chars if not c.isalnum()]


    """
    #Brute Force
    def predicateSampler(self, col):
        columns = self.columnSampler()
        columns.remove(col)
        projection = self.df[columns]
        tuples = set([tuple(x) for x in projection.to_records(index=False)])

        result_list = []
        for t in tuples:
            result_list.append(lambda s, p=t: (s[columns].values.tolist() == list(p)))

        return result_list
    """


    def predicateSampler(self, col):
        all_predicates = []

        for c in self.qfnobject.hint:
            #if self.dataset.types[c] == 'cat': #only take categorical values
            all_predicates.extend(self.dataset.getPredicatesDeterministic(self.qfn, c, self.predicate_granularity))

        logging.debug("Predicate Sampler has "+str(len(all_predicates)))
        
        return all_predicates
        #return self.dataset.getPredicates(self.qfn, self.predicate_granularity)


