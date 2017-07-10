import pandas as pd
from search import *

h2 = []

data2 = [{'a': 'New Yorks', 'b': 'NY'}, 
         {'a': 'New York', 'b': 'NY'}, 
         {'a': 'San Francisco', 'b': 'SF'},
         {'a': 'San Francisco', 'b': 'SF'},
         {'a': 'San Jose', 'b': 'SJ'},
         {'a': 'New York', 'b': 'NY'},
         {'a': 'San Francisco', 'b': 'SFO'},
         {'a': 'Berkeley City', 'b': 'Bk'},
         {'a': 'San Mateo', 'b': 'SFO'},
         {'a': 'Albany', 'b': 'AB'},
         {'a': 'San Mateo', 'b': 'SM'}]

data2 = data2*5



"""
df = pd.DataFrame(data3)

f = FD(["a"], ["b"])

g = FD(["b"], ["a"])





operation = treeSearch(df, (f*g + h*2).qfn, [Swap])

print(operation.run(df))
"""

df = pd.DataFrame(data2)

f = FD(["a"], ["b"])

g = FD(["b"], ["a"])

h = DictValue("a", ["New"])

i = DictValue("b", ["City"])


#pareto

operation = treeSearch(df, (f*g).qfn, [Swap], editCost=2)

print(operation.name)

print(operation.run(df))

"""
df = operation.run(df).copy()

operation = treeSearch(df, (f*g).qfn, [Swap], editCost=2)

print(operation.run(df))
"""

#print((f+h).qfn(operation.run(df)))