
"""
Core search routine
"""

from generators import *
from heapq import *
import numpy as np
import datetime
import logging



DEFAULT_SOLVER_CONFIG = {'pattern': {'depth': 10, 'gamma': 5, 'edit': 1, 'operations': [Delete], 'similarity': {}, 'w2v': 'resources/GoogleNews-vectors-negative300.bin'},
                         'dependency': {'depth': 10, 'gamma': 5, 'edit': 1, 'operations': [Swap], 'similarity': {}, 'w2v': 'resources/GoogleNews-vectors-negative300.bin'}}




def solve(df, patterns=[], dependencies=[], partitionOn=None, config=DEFAULT_SOLVER_CONFIG):

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


    if partitionOn != None:
        
        
        logging.warning("You didn't specify any blocking rules, this might be slow")


        blocks = set(df[partitionOn].dropna().values)

        for i, b in enumerate(blocks):

            
            logging.info("Computing Block=" + str(b) + ' ' + str(i+1)  + " out of " + str(len(blocks)) )


            dfc = df.loc[ df[partitionOn] == b ].copy()


            logging.debug("Block=" + str(b) + ' size=' + str(dfc.shape[0]))


            op1, dfc = patternConstraints(dfc, patterns, config['pattern'])
            
            op2, output_block = dependencyConstraints(dfc, dependencies, config['dependency'])

            #update output block
            df.loc[ df[partitionOn] == b ] = output_block 

            op = op * (op1*op2)
    else:

        op1, df = patternConstraints(df, patterns, config['pattern'])

        op2, df = dependencyConstraints(df, dependencies, config['dependency'])

        op = op * (op1*op2)

    return op, df 



def loadWord2Vec(filename):
    from gensim.models.keyedvectors import KeyedVectors
    return KeyedVectors.load_word2vec_format(filename, binary=True)



def needWord2Vec(config):
    return ('semantic' in [config['pattern']['similarity'][k] for k in config['pattern']['similarity']]) or \
            ('semantic' in [config['dependency']['similarity'][k] for k in config['dependency']['similarity']])




def patternConstraints(df, costFnList, config):
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

        transform, df = treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                                   inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                                    word2vec=config['model'])

        op = op * transform


    return op, df



def dependencyConstraints(df, costFnList, config):
    
    op = NOOP()

    for c in costFnList:

        logging.debug('Enforcing dependency constraint='+str(c))

        transform, df = treeSearch(df, c, config['operations'], evaluations=config['depth'], \
                                   inflation=config['gamma'], editCost=config['edit'], similarity=config['similarity'],\
                                    word2vec=config['model'])

        op = op * transform

    return op, df    





def treeSearch(df, 
               costFn, 
               operations, 
               evaluations,
               inflation,
               editCost,
               similarity,
               word2vec):


    efn = CellEdit(df.copy(), similarity, word2vec).qfn

    best = (2.0, NOOP(), df)

    branch_hash = set()
    branch_value = hash(str(df.values))
    branch_hash.add(branch_value)

    bad_op_cache = set()


    search_start_time = datetime.datetime.now()


    for i in range(evaluations):

        level_start_time = datetime.datetime.now()

        logging.debug('Search Depth='+str(i))
        
        value, op, frame = best 


        #prune
        if (value-op.depth) > best[0]*inflation:
            continue

        bfs_source = frame.copy()

        p = ParameterSampler(bfs_source, costFn, operations)


        costEval = costFn.qfn(bfs_source)
        
        for l, opbranch in enumerate(p.getAllOperations()):

            logging.debug('Search Branch='+str(l)+' ' + opbranch.name)

            #prune bad ops
            if opbranch.name in bad_op_cache:
                continue

            nextop = op * opbranch


            #disallow trasforms that cause an error
            try:
                output = opbranch.run(frame)
            except:
                logging.warn('Error in Search Branch='+str(l)+' ' + opbranch.name)
                bad_op_cache.add(opbranch.name)
                continue


            #evaluate pruning
            if pruningRules(output):
                logging.debug('Pruned Search Branch='+str(l)+' ' + opbranch.name)
                continue


            costEval = costFn.qfn(output)
            n = (np.sum(costEval) + editCost*np.sum(efn(output)))/output.shape[0]

            if n < best[0]:
                logging.debug('Promoted Search Branch='+str(l)+' ' + opbranch.name)
                best = (n, nextop, output)

        logging.debug('Search Depth='+str(i) + " took " + str((datetime.datetime.now()-level_start_time).total_seconds()))

    logging.debug('Search  took ' + str((datetime.datetime.now()-search_start_time).total_seconds()))
            
    return best[1], best[2]




def pruningRules(output):

    if output.shape[1] == 0:
        return True

    elif output.shape[0] == 0:
        return True 

    return False




