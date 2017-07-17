import environ
import pandas as pd
from alphaclean.search import *

df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False, nrows=50)

print(df.iloc[0,:])

from alphaclean.misc import generateTokenCodebook

print(generateTokenCodebook(df,'contbr_occupation'))

codes = generateTokenCodebook(df,'contbr_occupation')

operation = solve(df, [Pattern("contbr_zip", '[0-9]+')], dependencies=[DictValue('contbr_occupation', codes)], partitionOn='contbr_nm')

print(operation)






