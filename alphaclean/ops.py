"""
This class defines the operations that we can search over.

Operations define a monoid
"""
from sets import Set
import dateparser
import time
import re


"""
Allows lazy composition of Op functions
"""
class Operation(object):

    def __init__(self, runfn, depth=1, provenance=[]):
        self.runfn = lambda df: runfn(df) 
        self.depth = depth
        #self.name = 'df = Generic(df)'
        #self.activeSet = set()
        if provenance != []:
            self.provenance = provenance

    """
    This runs the operation
    """
    def run(self, df):
        df_copy = df.copy(deep=True)

        return self.runfn(df_copy)

    """
    Defines composable operations on a data frame
    """
    def __mul__(self, other):
        new_runfn = lambda df, a=self, b=other: b.runfn(a.runfn(df))
        new_op = Operation(new_runfn, self.depth + other.depth, self.provenance + other.provenance)
        new_op.name = self.name + "\n" + other.name

        return new_op

    """
    Easy to specify fixed point iteration
    """
    def __pow__(self, b):
        op = self

        for i in range(b):
            op *= self
        
        return op


    def __str__(self):
        return self.name

    __repr__ = __str__


"""
A parametrized operation is an operation that
takes parameters
"""
class ParametrizedOperation(Operation):

    COLUMN = 0
    VALUE = 1
    SUBSTR = 2
    PREDICATE = 3
    COLUMNS = 4

    def __init__(self, runfn, params):

        self.validateParams(params)
        super(ParametrizedOperation,self).__init__(runfn)



    def validateParams(self, params):

        try:
            self.paramDescriptor
        except:
            raise NotImplemented("Must define a parameter descriptor")

        for p in params:

            if p not in self.paramDescriptor:
                raise ValueError("Parameter " + str(p) + " not defined")

            if self.paramDescriptor[p] not in range(5):
                raise ValueError("Parameter " + str(p) + " has an invalid descriptor")



"""
Potter's wheel operations
"""

class Split(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN, 'delim': ParametrizedOperation.SUBSTR}

    def __init__(self, column, delim):

        def fn(df, column=column, delim=delim):

            args = {}

            #get the split length
            length = df[column].map(lambda x: len(x.split(delim))).max()

            def safeSplit(s, delim, index):
                splitArray = s.split(delim)
                if index >= len(splitArray):
                    return None
                else:
                    return splitArray[index]

            for l in range(length):
                key = column+str(l)

                if column+str(l) in df.columns.values:
                    key = key + '_1' 

                args[key] = df[column].map(lambda x, index=l: safeSplit(x, delim, l))

            return df.assign(**args)


        self.name = 'df = split(df,'+formatString(column)+','+formatString(delim)+')'
        self.provenance = [self.name]

        super(Split,self).__init__(fn, ['column', 'delim'])


class Merge(ParametrizedOperation):

    paramDescriptor = {'column1': ParametrizedOperation.COLUMN, 
                       'column2': ParametrizedOperation.COLUMN}

    def __init__(self, column1, column2):

        def fn(df, c1=column1, c2=column2):

            df[c1] = df[c2].copy()

            return df


        self.name = 'df = merge(df,'+formatString(column1)+','+formatString(column2)+')'
        self.provenance = [self.name]

        super(Merge,self).__init__(fn, ['column1', 'column2'])



"""
Find an replace operation
"""
class Swap(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN, 
                                'predicate': ParametrizedOperation.PREDICATE,
                                'value': ParametrizedOperation.VALUE}

    def __init__(self, column, predicate, value):

        #print("a,b", column, value)

        logical_predicate = lambda row: row[predicate[0]] in predicate[1]

        self.column = column
        self.predicate = predicate
        self.value = value

        def fn(df, 
               column=column, 
               predicate=logical_predicate, 
               v=value):

            N = df.shape[0]

            for i in range(N):
                if predicate(df.iloc[i,:]): #type issues
                    df[column].iloc[i] = v

            return df


        self.name = 'df = swap(df,'+formatString(column)+','+formatString(value)+','+str(predicate)+')'
        self.provenance = [self.name]

        super(Swap,self).__init__(fn, ['column', 'predicate', 'value'])


"""
Find an replace operation
"""
class Delete(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN, 
                                'predicate': ParametrizedOperation.PREDICATE}

    def __init__(self, column, predicate):


        logical_predicate = lambda row: row[predicate[0]] in predicate[1]

        def fn(df, 
               column=column, 
               predicate=logical_predicate):

            N = df.shape[0]

            for i in range(N):
                if predicate(df.iloc[i,:]): #type issues
                    df[column].iloc[i] = None

            return df


        self.name = 'df = delete(df,'+formatString(column)+','+str(predicate)+')'
        self.provenance = [self.name]

        super(Delete,self).__init__(fn, ['column', 'predicate'])



class TR(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN,
                       'substr1': ParametrizedOperation.SUBSTR, 
                       'substr2': ParametrizedOperation.SUBSTR}


    def __init__(self, column, substr1, substr2):

        def fn(df, 
               column=column, 
               substr1=substr1,
               substr2=substr2):

            N = df.shape[0]

            for i in range(N):
                if df[column].iloc[i] != None:

                    df[column].iloc[i] = str(df[column].iloc[i]).replace(substr1, substr2)

            return df


        self.name = 'df = tr(df,'+formatString(column)+','+formatString(substr1)+','+formatString(substr2)+')'
        self.provenance = [self.name]

        super(TR,self).__init__(fn, ['column', 'substr1', 'substr2'])




class DatetimeCast(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN,
                       'form': ParametrizedOperation.SUBSTR}


    def __init__(self, column, form):

        def fn(df, 
               column=column, 
               format=form):

            N = df.shape[0]

            for i in range(N):
                if df[column].iloc[i] != None:

                    try:
                        df[column].iloc[i] = dateparser.parse(str(df[column].iloc[i])).strftime(form)
                    except:
                        pass

            return df


        self.name = 'df = dateparse(df,'+formatString(column)+','+formatString(form)+')'
        self.provenance = [self.name]

        super(DatetimeCast, self).__init__(fn, ['column', 'form'])





class PatternCast(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN,
                       'form': ParametrizedOperation.SUBSTR}


    def __init__(self, column, form):

        def fn(df, 
               column=column, 
               format=form):

            N = df.shape[0]

            for i in range(N):

                if df[column].iloc[i] != None:

                    try:
                        df[column].iloc[i] = re.search(form, str(df[column].iloc[i])).group(0)
                    except:
                        df[column].iloc[i] = None


                if df[column].iloc[i] == '':
                    df[column].iloc[i] = None

            return df


        self.name = 'df = pattern(df,'+formatString(column)+','+formatString(form)+')'
        self.provenance = [self.name]

        super(PatternCast, self).__init__(fn, ['column', 'form'])







"""
No op
"""
class NOOP(Operation):

    def __init__(self):

        def fn(df):

            return df


        self.name = ""
        self.provenance = [self.name]

        super(NOOP,self).__init__(fn)







def formatString(s):
    return "'"+str(s)+"'"


