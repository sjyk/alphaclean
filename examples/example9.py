"""
Example 9: Election data.
Run this example with `python examples/example3.py` from the `alphaclean`
directory.
"""

import environ
import pandas as pd
from alphaclean.search import *

#loads the dataset into a dataframe, this dataset has 200k rows
df = pd.read_csv('datasets/elections.txt-big', quotechar='\"', index_col=False)


#Generates a code book by selecting the top-k features most correlated with the label you 
#are trying to predict. 
#generateCorrelationCodebook(dataframe, categorical_attribute, binary vector of labels, size)
from alphaclean.misc import generateCorrelationCodebook

#suppose I'm predicting that the contributor lives in alaska
codes = generateCorrelationCodebook(df, 'contbr_occupation', df['contbr_st'] == 'AK', size=100)

#or contributed ammount greater than 200$
#codes = generateCorrelationCodebook(df, 'contbr_occupation', df['contb_receipt_amt'] > 200, size=100)


#this sets the solver configuration, for your problem we only want replacements no deletes
config = DEFAULT_SOLVER_CONFIG
config['dependency']['similarity'] = {'contbr_occupation': 'semantic'} #similarity metrics can be edit, jaccard, or semantic (semantic is a word2vec model)
config['dependency']['w2v'] = 'resources/GoogleNews-vectors-negative300.bin' #path to the pre-trained model, http://automation.berkeley.edu/archive/GoogleNews-vectors-negative300.bin
config['dependency']['operations'] = [Swap]
config['dependency']['depth'] = 1 #do not chain operations map a -> b, then b -> c
#config['dependency']['editCost'] = 50 #set some penalty for making changes


from alphaclean.constraint_languages.ic import DictValue

#solver operates in blocks and since these problems don't affect multiple rows, you can block on the same attribute you are cleaning
operation, output = solve(df, [], dependencies=[DictValue('contbr_occupation', codes)], partitionOn='contbr_occupation', config=config)

print(operation, output)

