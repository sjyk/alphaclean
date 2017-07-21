import environ

data = [{'a': 'New Yorks', 'b': 'NY'}, 
         {'a': 'New York', 'b': 'NY'}, 
         {'a': 'San Francisco', 'b': 'SF'},
         {'a': 'San Francisco', 'b': 'SF'},
         {'a': 'San Jose', 'b': 'SJ'},
         {'a': 'New York', 'b': 'NY'},
         {'a': 'San Francisco', 'b': 'SFO'},
         {'a': 'Berkeley City', 'b': 'Bk'},
         {'a': 'San Mateo', 'b': 'SMO'},
         {'a': 'Albany', 'b': 'AB'},
         {'a': 'San Mateo', 'b': 'SM'}]

import pandas as pd
df = pd.DataFrame(data)


from alphaclean.constraints import OneToOne
constraint = OneToOne(["a"], ["b"])


from alphaclean.search import solve
dcprogram = solve(df, dependencies=[constraint])

print(dcprogram.run(df))

print(dcprogram)