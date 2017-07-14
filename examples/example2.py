import environ

import pandas as pd
f = open('datasets/airplane.txt','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split('\t')) } for l in f.readlines()]
df = pd.DataFrame(data)

from alphaclean.constraints import Date, Pattern, OneToOne
patterns = [Date("2", "%m/%d/%Y %I:%M %p"), Date("3", "%m/%d/%Y %I:%M %p"), Pattern("4", '^[a-zA-Z][0-9]+'), Date("5", "%m/%d/%Y %I:%M %p"), Date("6", "%m/%d/%Y %I:%M %p"), Pattern("7", '^[a-zA-Z][0-9]+')]

dependencies = []
for i in range(2,8):
    dependencies.append(OneToOne(["1"],[str(i)]))

from alphaclean.search import solve
operation = solve(df, patterns, dependencies, partitionOn="1")

print(operation.run(df))

print(operation)







