import environ

data = [{'a': 'Employee 1' , 'b': '100.0'}, 
         {'a': 'Employee 2' , 'b': '100.0'},
         {'a': 'Employee 3' , 'b': '100.0'},
         {'a': 'Employee 4' ,'b': '100.0'},
         {'a': 'Manager 1' ,'b': '500.0'},
         {'a': 'Manager 2' ,'b': '80.0'}]


import pandas as pd
df = pd.DataFrame(data)


from alphaclean.constraints import Float, DenialConstraint

constraint = DenialConstraint([('a', lambda x, d: 'Manager' in x), 
                              ('b', lambda x, d: d[ (d['b'] > x) & \
                                                     d['a'].str.contains("Employee", na=False) ].shape[0] > 0) ])

from alphaclean.search import solve, DEFAULT_SOLVER_CONFIG
config = DEFAULT_SOLVER_CONFIG
config['dependency']['depth'] = 3
config['dependency']['similarity'] = {'a':'jaccard'}

dcprogram, output = solve(df, patterns=[Float("b")] ,dependencies=[constraint], config=config)

print(dcprogram, output)
