"""
Example 1: City names.
Run this example with `python examples/example1.py` from the `alphaclean`
directory.
"""

import environ

data = [{'a': 'New Yorks',     'b': 'NY'},
        {'a': 'New York',      'b': 'NY'},
        {'a': 'San Francisco', 'b': 'SF'},
        {'a': 'San Francisco', 'b': 'SF'},
        {'a': 'San Jose',      'b': 'SJ'},
        {'a': 'New York',      'b': 'NY'},
        {'a': 'San Francisco', 'b': 'SFO'},
        {'a': 'Berkeley City', 'b': 'Bk'},
        {'a': 'San Mateo',     'b': 'SMO'},
        {'a': 'Albany',        'b': 'AB'},
        {'a': 'San Mateo',     'b': 'SM'}]

import pandas as pd
df = pd.DataFrame(data)


from alphaclean.constraint_languages.ic import OneToOne
constraint = OneToOne(["a"], ["b"])


from alphaclean.search import solve, DEFAULT_SOLVER_CONFIG
config = DEFAULT_SOLVER_CONFIG
config['dependency']['depth'] = 3
config['dependency']['similarity'] = {'a': 'jaccard'}


dcprogram, output = solve(df, dependencies=[constraint], config=config)

print(dcprogram, output)

