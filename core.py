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

        for t in self.types:

            if self.types[t] == 'num':
                self.featurizers[t] = NumericalFeatureSpace(df, t)
            elif self.types[t] == 'cat':
                self.featurizers[t] = CategoricalFeatureSpace(df, t)
            elif self.types[t] == 'string':
                self.featurizers[t] = StringFeatureSpace(df, t)

        #print(self.featurizers)

        #initializes the data structure
        tmp = self._row2featureVector(self.df.iloc[0,:])
        self.shape = tmp.shape



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

        for i in range(self.df.shape[0]):
            if q_array[i] == 1.0:
                vals_inside.add(self.df[col].iloc[i])
            else:
                vals_outside.add(self.df[col].iloc[i])

        return [(col, set([p])) for p in vals_inside.difference(vals_outside)]










    """
    Evaluates the quality metric
    """
    def getPredicatesLearned(self, qfn, granularity):

        #todo easy way to scale parameters
        from sklearn.cluster import Birch

        if granularity == None:
            cluster = Birch(compute_labels=False)
        else:
            cluster = Birch(compute_labels=False, n_clusters=granularity)

        q_array = np.sign(qfn(self.df))

        q_hash = {}


        N = self.df.shape[0]
        Np = int(np.round(np.sum(q_array)))
        
        if Np == 0:
            return [lambda row: False]

        X = np.zeros((Np,self.shape[0]))

        j = 0

        for i in range(N):

            if q_array[i] > 0 :
                X[j,:] = self._row2featureVector(self.df.iloc[i,:])
                j = j + 1

            q_hash[tuple(self._row2featureVector(self.df.iloc[i,:]))] = int(q_array[i])

        #print(q_hash)

        cluster.fit(X)

        K = cluster.subcluster_centers_.shape[0]

        def cluster2predicate(row, model, q_hash, index):
            
            key = tuple(self._row2featureVector(row))

            if key in q_hash and q_hash[key] == 0:
                return False
            else:
                res = cluster.predict(self._row2featureVector(row).reshape(1, -1))[0]
                if res == index:
                    return True
                else:
                    return False

        return [lambda row, model=cluster, q_hash=q_hash, index=i: cluster2predicate(row, model, q_hash, index) for i in range(K)]





    """
    This function converts a row into a feature vector
    """
    def _row2featureVector(self, row):

        vlist = []

        self.attrIndex = {}
        start = 0

        for t in self.types:
            #print(t, row[t])
            v = np.array(self.featurizers[t].val2feature(row[t]))
            
            if self.types[t] == 'cat':
                dims = np.squeeze(v.shape)
            else:
                dims = 1

            self.attrIndex[t] = (start, start+dims)
            start = start + dims
            vlist.append(v)

        return np.hstack(tuple(vlist))


    """
    This function converts a row into a val for the desired attribute
    """
    def _featureVector2attr(self, f, attr):
        vindices = self.attrIndex[attr]
        return self.featurizers[attr].feature2val(f[vindices[0]:vindices[1]])



"""
This class defines a categorical feature space 
"""
class StringFeatureSpace:

    """
    Initializes with hyperparams
    """
    def __init__(self, df, attr, simfn=distance.levenshtein, maxDims=2, var=1, ballTreeLeaf=2):

        self.df = df
        self.attr = attr
        self.simfn = simfn

        self.maxDims = maxDims
        self.var = var
        self.ballTreeLeaf = ballTreeLeaf

        self.values =  set(self.df[self.attr].values)

        self.tree, self.findex, self.iindex = self._calculateEmbedding()


    """
    Embeds the categorical values in a vector space
    """
    def _calculateEmbedding(self):
        values = self.values
        kernel = np.zeros((len(values), len(values)))

        for i, v in enumerate(values):
            for j, w in enumerate(values):
                if i != j:
                    kernel[i,j] = np.exp(-self.simfn(v,w)/self.var)

        embed = spectral_embedding(kernel, n_components=self.maxDims)
        tree = BallTree(embed, leaf_size=self.ballTreeLeaf)

        return tree, {v: embed[i,:] for i, v in enumerate(values)}, {i: v for i, v in enumerate(values)}


    """
    Calculates the value of a feature vector
    """
    def feature2val(self, f):
        _ , result = self.tree.query(f.reshape(1, -1), k=1)
        return self.iindex[result[0][0]]


    """
    Calculates the features of a value
    """
    def val2feature(self, val):
        #print(val)
        #snap to nearest value if not there
        if val in self.values:
            return self.findex[val]
        else:
            
            minDistance = np.inf
            minIndex = -1

            for i, v in enumerate(self.values):
                if self.simfn(val, v) < minDistance:
                    minDistance = self.simfn(val, v)
                    minIndex = i

            return self.findex[self.iindex[minIndex]]


"""
This class defines a categorical feature space 
"""
class CategoricalFeatureSpace:

    """
    Initializes with hyperparams
    """
    def __init__(self, df, attr):

        self.df = df
        self.attr = attr
        self.values =  set(self.df[self.attr].values)
        self.vindex = {i:v for i,v in enumerate(self.values)}
        self.iindex = {v:i for i,v in enumerate(self.values)}

        #print(self.vindex)


    """
    Calculates the value of a feature vector
    """
    def feature2val(self, f):
        index = np.argmax(f)
        return self.vindex[index]


    """
    Calculates the features of a value
    """
    def val2feature(self, val):
        #print(val)
        f = np.zeros((len(self.values),))
        if val in self.values:
            f[self.iindex[val]] = 1.0
        
        return f


"""
This class defines a numerical feature space 
"""
class NumericalFeatureSpace:
    """
    Initializes with hyperparams
    """
    def __init__(self, df, attr):

        self.df = df
        self.attr = attr
    
    def feature2val(self, f):
        return np.squeeze(f)

    def val2feature(self, val):
        return val


    




 