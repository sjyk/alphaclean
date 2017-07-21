
"""
Core search routine
"""

from generators import *
from heapq import *
import numpy as np

import datetime



DEFAULT_SOLVER_CONFIG = {'pattern': {'depth': 10, 'gamma': 5, 'edit': 1, 'operations': [Delete], 'similarity': {}, 'w2v': 'resources/GoogleNews-vectors-negative300.bin'},
                         'dependency': {'depth': 10, 'gamma': 5, 'edit': 1, 'operations': [Swap], 'similarity': {}, 'w2v': 'resources/GoogleNews-vectors-negative300.bin'}}


def solve(df, patterns=[], dependencies=[], partitionOn=None, config=DEFAULT_SOLVER_CONFIG):

    op = NOOP()


    if needWord2Vec(config):
        w2vp = loadWord2Vec(config['pattern']['w2v'])
        w2vd = loadWord2Vec(config['pattern']['w2v'])
    else:
        w2vp = None
        w2vd = None


    config['pattern']['model'] = w2vp
    config['dependency']['model'] = w2vd


    if partitionOn != None:
        blocks = set(df[partitionOn].values)
        #blocks = set(['UA-1006-BOG-IAH'])

        for i, b in enumerate(blocks):

            print("Computing Block=",b, i ,"out of", len(blocks) )

            dfc = df.loc[ df[partitionOn] == b ].copy()
            
            op1 = patternConstraints(dfc, patterns, config['pattern'])

            dfc = op1.run(dfc)
            
            op2 = dependencyConstraints(dfc, dependencies, config['dependency'])

            op = op * (op1*op2)
    else:

        op1 = patternConstraints(df, patterns, config['pattern'])
        df = op1.run(df)
        op2 = dependencyConstraints(df, dependencies, config['dependency'])

        op = op * (op1*op2)

    return op


def loadWord2Vec(filename):
    from gensim.models.keyedvectors import KeyedVectors
    return KeyedVectors.load_word2vec_format(filename, binary=True)


def needWord2Vec(config):
    return ('semantic' in [config['pattern']['similarity'][k] for k in config['pattern']['similarity']]) or \
            ('semantic' in [config['dependency']['similarity'][k] for k in config['dependency']['similarity']])




def patternConstraints(df, costFnList, config):
    op = NOOP()

    for c in costFnList:

        if isinstance(c,Date): #fix
            d = DatetimeCast(c.attr, c.pattern)
            df = d.run(df)
            op = op * d

        elif isinstance(c,Pattern):
            d = PatternCast(c.attr, c.pattern)
            df = d.run(df)
            op = op * d

        op = op * treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                             inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                            word2vec=config['model'])

    return op



def dependencyConstraints(df, costFnList, config):
    
    op = NOOP()

    for c in costFnList:

        op = op * treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                            inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                            word2vec=config['model'])

    return op    





def treeSearch(df, 
               costFn, 
               operations, 
               evaluations,
               inflation,
               editCost,
               similarity,
               word2vec):


    efn = CellEdit(df.copy(), similarity, word2vec).qfn

    best = (2.0, NOOP())

    branch_hash = set()
    branch_value = hash(str(df.values))
    branch_hash.add(branch_value)

    bad_op_cache = set()


    for i in range(evaluations):

        
        value, op = best 

        #prune
        if (value-op.depth) > best[0]*inflation:
            continue

        bfs_source = op.run(df).copy()

        p = ParameterSampler(bfs_source, costFn, operations)


        costEval = costFn.qfn(bfs_source)
        
        for l, opbranch in enumerate(p.getAllOperations()):

            #prune bad ops
            if opbranch.name in bad_op_cache or \
               opbranch.name in op.provenance:
                continue

            nextop = op * opbranch


            #disallow trasforms that cause an error
            try:
                output = nextop.run(df)
            except:
                bad_op_cache.add(opbranch.name)
                continue


            #evaluate pruning
            if pruningRules(output):
                continue


            costEval = costFn.qfn(output)
            n = (np.sum(costEval) + editCost*np.sum(efn(output)))/output.shape[0]

            if n < best[0]:
                best = (n, nextop)
            
    return best[1]




def pruningRules(output):

    if output.shape[1] == 0:
        return True

    elif output.shape[0] == 0:
        return True 

    return False




