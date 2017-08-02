"""
This class defines the operations that we can search over.

Operations define a monoid
"""
from sets import Set
from dateparser import DateDataParser
import time
import re
import pandas as pd

import datetime



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


        #now = datetime.datetime.now()

        df_copy = df.copy(deep=True)

        #print((datetime.datetime.now()-now).total_seconds())

        return self.runfn(df_copy)

    """
    Defines composable operations on a data frame
    """
    def __mul__(self, other):
        new_runfn = lambda df, a=self, b=other: b.runfn(a.runfn(df))
        new_op = Operation(new_runfn, self.depth + other.depth, self.provenance + other.provenance)
        new_op.name = (self.name + "\n" + other.name).strip()

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

    def optimize(self):
        return FusedOperation(self)

    __repr__ = __str__



"""
Optimizes an operation
"""
class FusedOperation(Operation):

    def __init__(self, operation):

        def fn(df):
            N = df.shape[0]

            for i in range(N):
                row = df.iloc[i:i+1,:]
                for op in operation.provenance:
                    import datetime
                    now = datetime.datetime.now()
                    row = op.runfn(row)
                    print(op,  (datetime.datetime.now() - now).total_seconds() )
                #print(i)

            return df

        super(FusedOperation,self).__init__(fn)





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
Find an replace operation
"""
class Swap(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN, 
                                'predicate': ParametrizedOperation.PREDICATE,
                                'value': ParametrizedOperation.VALUE}

    def __init__(self, column, predicate, value):

        #print("a,b", column, value)

        logical_predicate = lambda row: (row[predicate[0]] in predicate[1]) and (tuple(row.dropna().values) in predicate[2])

        self.column = column
        self.predicate = predicate
        self.value = value

        def fn(df, 
               column=column, 
               predicate=logical_predicate, 
               v=value):

            def __internal(row):
                #print(tuple(row.values), predicate(row))
                if predicate(row):
                    return v 
                else:
                    return row[column]

            df[column] = df.apply(lambda row: __internal(row), axis=1)

            #print(df.apply(lambda row: __internal(row), axis=1))

            return df


        self.name = 'df = swap(df,'+formatString(column)+','+formatString(value)+','+str(predicate[0:2])+')'
        self.provenance = [self]

        super(Swap,self).__init__(fn, ['column', 'predicate', 'value'])


"""
Find an replace operation
"""
class Delete(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN, 
                                'predicate': ParametrizedOperation.PREDICATE}

    def __init__(self, column, predicate):


        logical_predicate = lambda row: (row[predicate[0]] in predicate[1]) and (tuple(row.dropna().values) in predicate[2])

        #print(predicate[1])

        def fn(df, 
               column=column, 
               predicate=logical_predicate):

            def __internal(row):
                if predicate(row):
                    #print(row["4"], row["81"])
                    return None
                else:
                    return row[column]

            df[column] = df.apply(lambda row: __internal(row), axis=1)

            return df


        self.name = 'df = delete(df,'+formatString(column)+','+str(predicate[0:2])+')'
        self.provenance = [self]

        super(Delete,self).__init__(fn, ['column', 'predicate'])



class DatetimeCast(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN,
                       'form': ParametrizedOperation.SUBSTR}


    def __init__(self, column, form):

        parser = DateDataParser(languages=['en'], allow_redetect_language=False)

        def fn(df, 
               column=column, 
               format=form,
               parser=parser):

            N = df.shape[0]

            for i in range(N):
                if df[column].iloc[i] != None:

                    try:
                        df[column].iloc[i] = parser.get_date_data(str(df[column].iloc[i]))['date_obj'].strftime(form)
                    except:
                        pass

            return df


        self.name = 'df = dateparse(df,'+formatString(column)+','+formatString(form)+')'
        self.provenance = [self]

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
        self.provenance = [self]

        super(PatternCast, self).__init__(fn, ['column', 'form'])




class FloatCast(ParametrizedOperation):

    paramDescriptor = {'column': ParametrizedOperation.COLUMN}


    def __init__(self, column, nrange):

        def fn(df, column=column, r=nrange):

            def __internal(row):
                try:
                    value = float(row[column])
                    if value >= r[0] and value <= r[1]:
                        return value
                    else:
                        return None 
                except:
                    return None

            df[column] = df.apply(lambda row: __internal(row), axis=1)

            return df


        self.name = 'df = numparse(df,'+formatString(column)+')'
        self.provenance = [self]

        super(FloatCast, self).__init__(fn, ['column'])



"""
No op
"""
class NOOP(Operation):

    def __init__(self):

        def fn(df):

            return df


        self.name = ""
        self.provenance = [self]

        super(NOOP,self).__init__(fn)







def formatString(s):
    return "'"+str(s)+"'"


