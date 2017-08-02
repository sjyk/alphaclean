"""
This module implements the core elements of the optclean packaged
"""

import pandas as pd
import numpy as np
import random
from sklearn.manifold import spectral_embedding
from sklearn.neighbors import BallTree
import distance 
from sklearn import tree
from constraints import *
from type_inference import *


class Dataset:

    """
    A dataset takes a data frame as input and a list of
    quality functions
    """
    def __init__(self, df, provenance=-1):
        self.df = df

        try:
            self.provenance = pd.DataFrame.copy(df)
        except:
            self.provenance = provenance



        self.types = getDataTypes(df, df.columns.values)


        self.featurizers = {}



    """
    Internal function that creates a new dataset
    with fn mapped over all records
    """
    def _map(self, fn, attr):
        newDf = pd.DataFrame.copy(self.df)
        rows, cols = self.df.shape

        j = newDf.columns.get_loc(attr)
        for i in range(rows):
            newDf.iloc[i,j] = fn(newDf.iloc[i,:])
            #print("++",j,newDf.iloc[i,j], fn(newDf.iloc[i,:]))

        return Dataset(newDf, 
                       self.qfnList, 
                       self.provenance)

    def _sampleRow(self):
        newDf = pd.DataFrame.copy(self.df)
        rows, cols = self.df.shape
        i = np.random.choice(np.arange(0,rows))
        return newDf.iloc[i,:]


    """
    Executes fixes over all attributes in a random
    order
    """
    def _allmap(self, fnList,  attrList):

        dataset = self
        for i, f in enumerate(fnList):
            dataset = dataset._map(f,attrList[i])

        return dataset
        


    def getPredicatesDeterministic(self, qfn, col, granularity=None):
        q_array = np.sign(qfn(self.df))
        vals_inside = set()
        vals_outside = set()
        tuples_inside = set()

        for i in range(self.df.shape[0]):

            val = self.df[col].iloc[i]


            if val != val:
                val = 'NaN'

            if q_array[i] == 1.0:
                vals_inside.add(val)
                tuples_inside.add(tuple(self.df.iloc[i].dropna()))
            else:
                vals_outside.add(val)

        def _translateNaN(x):
            if x == 'NaN' or x != x:
                return np.nan
            else:
                return x


        #print(tuples_inside)

        return [(col, set([ _translateNaN(p)]), tuples_inside) for p in vals_inside]





 