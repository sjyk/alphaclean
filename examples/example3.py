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
print(codes)

config = DEFAULT_SOLVER_CONFIG
config['dependency']['similarity'] = {'contbr_occupation': 'semantic'}
config['dependency']['operations'] = [Swap, Delete]

operation = solve(df, [], dependencies=[DictValue('contbr_occupation', codes)],
                  partitionOn='contbr_nm', config=config)

print(operation.run(df))

print(operation)
