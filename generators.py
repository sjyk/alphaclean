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


class ParameterSampler(object):

    def __init__(self, df, qfn, operationList, substrThresh=0.1, scopeLimit=3, predicate_granularity=None):
        self.df = df
        self.qfn = qfn
        self.substrThresh = substrThresh
        self.scopeLimit = scopeLimit
        self.operationList = operationList
        self.predicate_granularity = predicate_granularity

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

                        grid.append(self.indexToFun(pv, col))

                    
                    #todo fix
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

        #print(parameters)

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
                #if self.pruningRules(arg):
                #    continue

                operations.append(op(**arg))

        operations.append(NOOP())

        #print(len(operations))
        
        return operations 


    """
    def pruningRules(self, arg):

        #remove imputes that are uncorrelated
        if 'predicate' in arg and 'value' in arg:
            N = self.df.shape[0]
            allowedValues = set()

            if arg['predicate'] in self.predicateIndex:
                allowedValues = self.predicateIndex[arg['predicate']] 
            else:
                for i in range(N):
                    if arg['predicate'](self.df.iloc[i,:]):
                        allowedValues.add(self.df[arg['column']].iloc[i])

                self.predicateIndex[arg['predicate']] = allowedValues

            return (arg['value'] not in allowedValues)
    """



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
        #print('--',self.df.columns.values.tolist())
        return self.df.columns.values.tolist()


    def columnsSampler(self):
        columns = self.columnSampler()
        result = []
        for i in range(1, min(len(columns), self.scopeLimit)):
            result.extend([list(a) for a in combinations(columns, i)])

        return result


    #brute force
    def valueSampler(self, col):
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
                for c in set(v):
                    if c not in chars:
                        chars[c] = 0

                    chars[c] += 1

        #print((chars[' ']+0.)/self.df.shape[0])
        #print()
        return [c for c in chars if not c.isalnum()]


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

        for c in self.df.columns.values:
            all_predicates.extend(self.dataset.getPredicatesDeterministic(self.qfn, c, self.predicate_granularity))

        return all_predicates
        #return self.dataset.getPredicates(self.qfn, self.predicate_granularity)


