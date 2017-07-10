
"""
Core search routine
"""

from generators import *
from heapq import *
import numpy as np

import datetime



def treeSearch(df, 
               costFn, 
               operations, 
               init=NOOP(),
               evaluations=3,
               inflation=5,
               predicate_granularity=2,
               editCost=0):


    efn = CellEdit(df.copy()).qfn

    now = datetime.datetime.now()

    best = (2.0, NOOP())

    heap = []

    heappush(heap, (init.depth + 1, init ) )

    branch_hash = set()
    branch_value = hash(str(df.values))
    branch_hash.add(branch_value)


    for i in range(evaluations):

        if len(heap) == 0:
            print(i, best[0])
            return best[1]
        
        value, op = heappop(heap)[0:2]

        #print(value-op.depth, best[0]*inflation)

        #prune
        if (value-op.depth) > best[0]*inflation:
            continue

        bfs_source = op.run(df).copy()

        p = ParameterSampler(bfs_source, costFn, operations, predicate_granularity)

        costEval = costFn(bfs_source)
        opDirtyIndices = set(np.squeeze(np.argwhere(costEval > 0).tolist()))

        orthogonal_fixes = set()
        orthogonal_fixes_op = []

        #print(p.getAllOperations())

        for opbranch in p.getAllOperations():

            nextop = op * opbranch


            #disallow trasforms that cause an error
            try:
                
                output = nextop.run(df)

            except:

                continue


            #evaluate pruning
            if pruningRules(output):
                continue


            branch_value = hash(str(output.values))

            #optimization 1 (branch hashing)
            if branch_value in branch_hash:
                continue
            else:
                branch_hash.add(branch_value)


            #optimization 2 (value pruning)
            costEval = costFn(output)
            n = (np.sum(costEval) + editCost*np.sum(efn(output)))/output.shape[0]
            dirtyIndices = set(np.squeeze(np.argwhere(costEval > 0).tolist()))


            #branch merging--best dominating fix if one exists
            if len(opDirtyIndices-dirtyIndices) > 0 and dirtyIndices <= opDirtyIndices:
                orthogonal_fixes_op.append((n, nextop, opDirtyIndices-dirtyIndices))
                #print(i, opbranch.name, opDirtyIndices-dirtyIndices)
                #orthogonal_fixes = orthogonal_fixes.union(opDirtyIndices-dirtyIndices)
                #print(n, )


            #return early if found
            if n == 0:

                return nextop
            
            elif len(heap) == 0:
            
                heappush(heap, (nextop.depth + n, nextop))

                best = (n, nextop)
            
            else:

                heappush(heap, (nextop.depth + n, nextop))

                if n < best[0]:
                    best = (n, nextop)



        #best dominating fix
        if len(orthogonal_fixes_op) > 0:
            n, nextop = sorted(orthogonal_fixes_op)[0][0:2]
            heap = []
            heappush(heap, (nextop.depth + n, nextop) )
            best = (n, nextop)


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




