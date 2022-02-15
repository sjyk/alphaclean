"""
Module: search

A best-first search expands the most promising nodes cho-sen  according  to  a  specified  cost  function.   
We  consider  ag reedy  version  of  this  algorithm,  which  removes  nodes  on the frontier that are more than 
\gamma times worse than the current  best  solution.   Making \gamma larger  makes  the  algorithm asympotically  
consistent,  whereas \gamma=  1  is  a  pure  greedy search.
"""

import numpy as np
import datetime

from .generators import *
from heapq import *

from alphaclean.learning import *

#special case optimizations require references to the pattern objects
from alphaclean.constraint_languages.pattern import *


#Configuration schema
DEFAULT_SOLVER_CONFIG = {}

DEFAULT_SOLVER_CONFIG['pattern'] = {
    'depth': 10,
    'gamma': 5,
    'edit': 1,
    'operations': [Delete],
    'similarity': {},
    'w2v': 'resources/GoogleNews-vectors-negative300.bin'
}

DEFAULT_SOLVER_CONFIG['dependency'] = {
    'depth': 10,
    'gamma': 5,
    'edit': 1,
    'operations': [Swap],
    'similarity': {},
    'w2v': 'resources/GoogleNews-vectors-negative300.bin'
}



def solve(df, patterns=[], dependencies=[], partitionOn=None, config=DEFAULT_SOLVER_CONFIG):
    """The solve function takes as input a specification in terms of a list of patterns and 
    a list of depdencies and returns a cleaned instance and a data cleaning program.

    Release notes: patterns have precedence over dependenceis should do this properly in the future

    Positional arguments:
    df -- Pandas DataFrame
    patterns -- a list of single attribute pattern constraints
    dependencies -- a list of single or multiple attribute constraints that are run after the pattern constraints
    patitionOn -- a blocking rule to partition the dataset
    config -- a config object
    """

    op = NOOP()

    logging.debug('Starting the search algorithm with the following config: ' + str(df.shape) + " " + str(config))


    if needWord2Vec(config):
        w2vp = loadWord2Vec(config['pattern']['w2v'])
        w2vd = loadWord2Vec(config['pattern']['w2v'])

        logging.debug('Using word2vec for semantic similarity')

    else:
        w2vp = None
        w2vd = None

    config['pattern']['model'] = w2vp
    config['dependency']['model'] = w2vd

    training_set = (set(), set())
    pruningModel = None

    if partitionOn != None:
        
        
        logging.warning("You didn't specify any blocking rules, this might be slow")


        blocks = set(df[partitionOn].dropna().values)

        #df = df.set_index(partitionOn)

        for i, b in enumerate(blocks):

            
            logging.info("Computing Block=" + str(b) + ' ' + str(i+1)  + " out of " + str(len(blocks)) )

            print("Computing Block=" + str(b) + ' ' + str(i+1)  + " out of " + str(len(blocks)))


            dfc = df.loc[ df[partitionOn] == b ].copy()

            logging.debug("Block=" + str(b) + ' size=' + str(dfc.shape[0]))


            op1, dfc = patternConstraints(dfc, patterns, config['pattern'])
            
            op2, output_block, training = dependencyConstraints(dfc, dependencies, config['dependency'], pruningModel)

            #update output block
            now = datetime.datetime.now()
            df.loc[ df[partitionOn] == b ] = output_block 
            print((datetime.datetime.now()-now).total_seconds())

            training_set = (training_set[0].union(training[0]), training_set[1].union(training[1]))


            #pruningModel = getFeatures(training_set[0], training_set[1], df)

            #if len(training_set[0]) > 10000:
            #    exit()



            op = op * (op1 * op2)

    else:
       
        op1, df = patternConstraints(df, patterns, config['pattern'])

        op2, df, _ = dependencyConstraints(df, dependencies, config['dependency'])

        op = op * (op1*op2)

    return op, df 



def loadWord2Vec(filename):
    """Loads a word2vec model from a file"""
    from gensim.models.keyedvectors import KeyedVectors
    return KeyedVectors.load_word2vec_format(filename, binary=True)



def needWord2Vec(config):
    """Determines whether word2vec is needed"""
    semantic_in_pattern = 'semantic' in [config['pattern']['similarity'][k] for k in config['pattern']['similarity']]
    semantic_in_dependency = 'semantic' in [config['dependency']['similarity'][k] for k in config['dependency']['similarity']]
    return semantic_in_pattern or semantic_in_dependency




def patternConstraints(df, costFnList, config):
    """Enforces pattern constrains"""

    op = NOOP()

    for c in costFnList:

        logging.debug('Enforcing pattern constraint='+str(c))

        if isinstance(c,Date):
            d = DatetimeCast(c.attr, c.pattern)
            df = d.run(df)
            op = op * d

        elif isinstance(c,Pattern):
            d = PatternCast(c.attr, c.pattern)
            df = d.run(df)
            op = op * d

        elif isinstance(c, Float):
            d = FloatCast(c.attr, c.range)
            df = d.run(df)
            op = op * d

        transform, df, _ = treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                                   inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                                    word2vec=config['model'])

        op = op * transform


    return op, df


def dependencyConstraints(df, costFnList, config, pruningModel=None):
    """enforces dependency constraints"""

    op = NOOP()

    for c in costFnList:

        logging.debug('Enforcing dependency constraint='+str(c))

        transform, df, training = treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                                   inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                                    word2vec=config['model'],
                                    pruningModel=pruningModel)

        op = op * transform

    return op, df, training    




def treeSearch(df, costFn, operations, evaluations, inflation, editCost,
               similarity, word2vec, pruningModel=None):
    """This is the function that actually runs the treesearch

    Positional arguments:
    df -- Pandas DataFrame
    costFn -- a cost function
    operations -- a list of operations
    evaluation -- a total number of evaluations
    inflation -- gamma
    editCost -- scaling on the edit cost
    similarity -- a dictionary the specified similarity metrics to use
    word2vec -- a word2vec model (avoid reloading things)
    """

    editCostObj = CellEdit(df.copy(), similarity, word2vec)
    efn = editCostObj.qfn

    best = (2.0, NOOP(), df)

    branch_hash = set()
    branch_value = hash(str(df.values))
    branch_hash.add(branch_value)

    bad_op_cache = set()

    search_start_time = datetime.datetime.now()

    all_operations = set()


    for i in range(evaluations):

        level_start_time = datetime.datetime.now()

        logging.debug('Search Depth='+str(i))
        
        value, op, frame = best 

        #prune
        if (value-op.depth) > best[0]*inflation:
            continue

        bfs_source = frame.copy()

        p = ParameterSampler(bfs_source, costFn, operations, editCostObj)

        costEval = costFn.qfn(bfs_source)
        
        for l, opbranch in enumerate(p.getAllOperations()):

            logging.debug('Search Branch='+str(l)+' ' + opbranch.name)

            if not isinstance(opbranch, NOOP):
                all_operations.add(opbranch)

            #prune bad ops
            if opbranch.name in bad_op_cache:
                continue

            #if pruningModel != None and not predict(pruningModel, opbranch, df):
            #    #print("Pruned: ", opbranch)
            #    continue

            nextop = op * opbranch

            #disallow trasforms that cause an error
            try:
                output = opbranch.run(frame)
            except:
                logging.warn('Error in Search Branch='+str(l)+' ' + opbranch.name)
                bad_op_cache.add(opbranch.name)
                continue

            editfn = np.sum(efn(output))

            #evaluate pruning
            if pruningRules(output):
                logging.debug('Pruned Search Branch='+str(l)+' ' + opbranch.name)
                continue

            costEval = costFn.qfn(output)
            n = (np.sum(costEval) + editCost*editfn)/output.shape[0]

            if n < best[0]:
                logging.debug('Promoted Search Branch='+str(l)+' ' + opbranch.name)
                best = (n, nextop, output)

        logging.debug('Search Depth='+str(i) + " took " + str((datetime.datetime.now()-level_start_time).total_seconds()))

    logging.debug('Search  took ' + str((datetime.datetime.now()-search_start_time).total_seconds()))
            
    return best[1], best[2], (all_operations.difference(set(best[1].provenance)), set(best[1].provenance))


def pruningRules(output):

    if output.shape[1] == 0:
        return True

    elif output.shape[0] == 0:
        return True 

    return False
