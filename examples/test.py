import pandas as pd
from search import *


"""
data2 = [{'a': 'New Yorks', 'b': 'NY'}, 
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


df = pd.DataFrame(data2)

f = FD(["a"], ["b"])

g = FD(["b"], ["a"])



operation = treeSearch(df, (f*g), [Swap], editCost=3)

print(operation.name)

print(operation.run(df))
"""



"""
import time

f = open('/Users/sanjayk/Downloads/clean_flight/2011-12-01-data.txt','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split('\t')) } for l in f.readlines()][0:100]
df = pd.DataFrame(data)

patterns = [Date("2", "%m/%d/%Y %I:%M %p"), Date("3", "%m/%d/%Y %I:%M %p"), Pattern("4", '^[a-zA-Z][0-9]+'), Date("5", "%m/%d/%Y %I:%M %p"), Date("6", "%m/%d/%Y %I:%M %p"), Pattern("7", '^[a-zA-Z][0-9]+')]

dependencies = []
for i in range(2,8):
    dependencies.append(OneToOne(["1"],[str(i)]))


operation = solve(df, patterns, dependencies, partitionOn="1")

print(df)

print(operation.run(df))

print(operation.name)
"""


from collections import Counter
df = pd.read_csv('/Users/sanjayk/Documents/research/boostclean/activedetect/datasets/P00000001-ALL.csv', nrows=50, quotechar='\"', index_col=False)
s = Counter(df['contbr_occupation'].values)


l = set([i[1] for i in sorted([(s[k],k) for k in s], reverse=True)[0:10]])
print(l)

operation = solve(df, [Pattern("contbr_zip", '[0-9]+')], [DictValue('contbr_occupation', l), FD(['contbr_zip'],['contbr_st']), OneToOne(['contbr_nm'], ['contbr_occupation'])], partitionOn='contbr_nm')

print(df)

print(operation.run(df))

print(operation.name)






