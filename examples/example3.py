import environ
import pandas as pd
from alphaclean.search import *



df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False)

from collections import Counter
s = Counter(df['contbr_occupation'].values)
l = [i for i in sorted([(s[k],k) for k in s], reverse=True)]

codebook = set([occ[1] for occ in l][0:8])


operation = solve(df, [Pattern("contbr_zip", '[0-9]+')], [DictValue('contbr_occupation', codebook), FD(['contbr_zip'],['contbr_st']), OneToOne(['contbr_nm'], ['contbr_occupation'])], partitionOn='contbr_nm')

print(df)

print(operation.run(df))

print(operation.name)






