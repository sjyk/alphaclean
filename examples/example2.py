"""
Example 2: Flight data.
Run this example with `python examples/example2.py` from the `alphaclean`
directory.
"""

import environ
import pandas as pd

f = open('datasets/airplane.txt', 'r')
data = []
for line in f.readlines():
    parsed = line.strip().split('\t')
    data.append({str(i): j for i, j in enumerate(parsed)})
df = pd.DataFrame(data)


from alphaclean.constraint_languages.pattern import Date, Pattern

patterns = [Date("2", "%m/%d/%Y %I:%M %p"),
            Date("3", "%m/%d/%Y %I:%M %p"),
            Pattern("4", '^[a-zA-Z][0-9]+'),
            Date("5", "%m/%d/%Y %I:%M %p"),
            Date("6", "%m/%d/%Y %I:%M %p"),
            Pattern("7", '^[a-zA-Z][0-9]+')]

from alphaclean.constraint_languages.ic import OneToOne

dependencies = [OneToOne(["1"], [str(i)]) for i in range(2, 8)]


from alphaclean.search import *

config = DEFAULT_SOLVER_CONFIG
config['dependency']['depth'] = 1
config['dependency']['similarity'] = {'a':'jaccard'}
config['dependency']['operations'] = [Swap]

operation, output = solve(df, patterns, dependencies, partitionOn="1")

print(operation, output)
