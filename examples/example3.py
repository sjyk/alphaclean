"""
Example 3: Election data.
Run this example with `python examples/example3.py` from the `alphaclean`
directory.
"""

import environ
import pandas as pd
from alphaclean.search import *

df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False)

from alphaclean.misc import generateCodebook
codes = generateCodebook(df, 'contbr_occupation')
#print(codes)

config = DEFAULT_SOLVER_CONFIG
config['dependency']['similarity'] = {'contbr_occupation': 'semantic'}
config['dependency']['operations'] = [Swap, Delete]
config['dependency']['depth'] = 1


from alphaclean.constraint_languages.ic import DictValue


operation, output = solve(df, [], dependencies=[DictValue('contbr_occupation', codes)],
                  partitionOn='contbr_occupation', config=config)

print(operation, output)

