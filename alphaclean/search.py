
"""
Core search routine
"""

from generators import *
from heapq import *
import numpy as np

import datetime


def solve(df, pC, dC, partitionOn=None, evaluations=10):

    op = NOOP()

    if partitionOn != None:
        blocks = set(df[partitionOn].values)

        for i, b in enumerate(blocks):
            print("Computing Block=",b, i ,"out of", len(blocks) )

            dfc = df.loc[ df[partitionOn] == b ].copy()
            op1 = patternConstraints(dfc, pC)
            dfc = op1.run(dfc)
            op2 = dependencyConstraints(dfc, dC, evaluations=evaluations)

            op = op * (op1*op2)
    else:

        op1 = patternConstraints(df, pC)
        df = op1.run(df)
        op2 = dependencyConstraints(df, dC, evaluations=evaluations)

        op = op * (op1*op2)

    return op



def patternConstraints(df, costFnList):
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

        op = op * treeSearch(df, c, [Delete], evaluations=df.shape[0])

    return op


def dependencyConstraints(df, costFnList, evaluations=10, inflation=5, predicate_granularity=2, editCost=1):
    
    op = NOOP()

    for c in costFnList:

        op = op * treeSearch(df, c, [Swap], 
                            evaluations=evaluations, 
                            inflation=inflation, 
                            predicate_granularity=predicate_granularity,
                            editCost=editCost)

    return op    





def treeSearch(df, 
               costFn, 
               operations, 
               init=NOOP(),
               evaluations=10,
               inflation=5,
               predicate_granularity=2,
               editCost=0):


    efn = CellEdit(df.copy()).qfn

    now = datetime.datetime.now()

    best = (2.0, NOOP())

    #heap = []

    #heappush(heap, (init.depth + 1, init ) )


    branch_hash = set()
    branch_value = hash(str(df.values))
    branch_hash.add(branch_value)

    bad_op_cache = set()


    for i in range(evaluations):

        #if len(heap) == 0:
        #    return best[1]

        #print(i)
        
        value, op = best #heappop(heap)[0:2]

        #prune
        if (value-op.depth) > best[0]*inflation:
            continue

        bfs_source = op.run(df).copy()

        p = ParameterSampler(bfs_source, costFn, operations, predicate_granularity)


        costEval = costFn.qfn(bfs_source)
        #opDirtyIndices = set(np.squeeze(np.argwhere(costEval > 0),axis=1).tolist())

        #orthogonal_fixes = set()
        #orthogonal_fixes_op = []

        #print(i, len(p.getAllOperations()))

        for opbranch in p.getAllOperations():

            #prune bad ops
            if opbranch.name in bad_op_cache or \
               opbranch.name in op.provenance:
                continue

            nextop = op * opbranch


            #disallow trasforms that cause an error
            try:
                
                output = nextop.run(df.copy())

            except:
                print(opbranch.name)
                output = nextop.run(df.copy())
                bad_op_cache.add(opbranch.name)
                continue


            #evaluate pruning
            if pruningRules(output):
                continue


            #branch_value = hash(str(output.values))

            #optimization 1 (branch hashing)
            #if branch_value in branch_hash:
            #    continue
            #else:
            #    branch_hash.add(branch_value)

            #optimization 2 (value pruning)
            costEval = costFn.qfn(output)
            n = (np.sum(costEval) + editCost*np.sum(efn(output)))/output.shape[0]

            
            #if '/' in opbranch.name:
            #    print(n,i, opbranch.name, best[0])

            
            #if i == 0:
            #    print(output)
            #    print(n, opbranch.name, best[0])

            #return early if found
            if n == 0:
                #print(i)
                return nextop

            #dirtyIndices = set(np.squeeze(np.argwhere(costEval > 0),axis=1).tolist())


            #branch merging--best dominating fix if one exists
            #if len(opDirtyIndices-dirtyIndices) > 0 and dirtyIndices <= opDirtyIndices:
            #    orthogonal_fixes_op.append((n, opbranch, opDirtyIndices-dirtyIndices))
                #print("hi")
                #print(i, opbranch.name, opDirtyIndices-dirtyIndices)
                #orthogonal_fixes = orthogonal_fixes.union(opDirtyIndices-dirtyIndices)
                #print(n, )

            #print(n, best[0], opbranch.name)
            if n < best[0]:
                best = (n, nextop)
            
            """
            if len(heap) == 0:
            
                #heappush(heap, (nextop.depth + n, nextop))

                best = (n, nextop)
            
            else:

                heappush(heap, (nextop.depth + n, nextop))
            """

                


        """
        #best dominating fix
        if len(orthogonal_fixes_op) > 0:
            n, opbranch = sorted(orthogonal_fixes_op)[0][0:2]

            #print([(n,o.name) for n,o,_ in orthogonal_fixes_op])

            nextop = op * opbranch
            heap = []
            heappush(heap, (nextop.depth + n, nextop) )
            best = (n, nextop)
        """



        #heappush(heap, (nextop.depth + n, nextop) )



    print((datetime.datetime.now() - now).total_seconds())

    #print(heap)

    return best[1]




def pruningRules(output):

    if output.shape[1] == 0:
        return True

    elif output.shape[0] == 0:
        return True 

    return False




