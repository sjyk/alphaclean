import environ
import pandas as pd
from alphaclean.search import *

df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False)

#print(df.iloc[0,:])

from alphaclean.misc import generateCodebook

#print(generateTokenCodebook(df,'contbr_occupation'))

codes = generateCodebook(df,'contbr_occupation')
print(codes)

config = DEFAULT_SOLVER_CONFIG
config['dependency']['similarity'] = {'contbr_occupation':'semantic'}
config['dependency']['operations'] = [Swap, Delete]

operation = solve(df, [], dependencies=[DictValue('contbr_occupation', codes)], partitionOn='contbr_nm')

print(operation)






