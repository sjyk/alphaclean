# 0. City Names & Abbreviations
This example is to illustrate the basic functionality and the concepts in AlphaClean.
You can run this example on your own, by running `python examples/example1.py` from the `alphaclean` directory.

Let's start with a simple example of city names and abbreviations:
```
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
```
Notice that the city names are inconsistent (<b>New York</b> vs. <b>New Yorks</b>), as are the acronyms (<b>SF</b> vs. <b>SFO</b>, and <b>SM</b> vs. <b>SMO</b>). For a small dataset, it is possible to enumerate all of the fixes through visual inspection -- but what if the dataset is very large? 


## Loading the Data
AlphaClean operates on Pandas, this gives us a lightweight table abstraction called a DataFrame.
First, we load the data into a Pandas DataFrame:
```
import pandas as pd
df = pd.DataFrame(data)
```
You can query this DataFrame with python code:
```
df['a'].values

> array(['New Yorks', 'New York', 'San Francisco', 'San Francisco',
       'San Jose', 'New York', 'San Francisco', 'Berkeley City',
       'San Mateo', 'Albany', 'San Mateo'], dtype=object)
```

## Specifying the data model
The philosopy of AlphaClean is that user should not write code by hand to correct all of the errors. Instead, she should specify a high-level data model, and the system automatically generates code to best satisfy that model. For example, in this dataset, we know that the attributes 'a' and 'b' should have a one-to-one relationship.
A `OneToOne` constraint that enforces that the keys 'a' map to 'b' bijectively:
```
from alphaclean.constraint_languages.ic import OneToOne

constraint = OneToOne(["a"], ["b"])
```

## Solving for the program
Next, we invoke the solver to find a program that enforces this constraint.
AlphaClean converts these constraints into a cost function.
A best-first search expands the most promising nodes chosen  according  to  a  specified  cost  function.  
The solver takes in a list of pattern constraints (single attribute constraints) and dependencies (constraints across multiple columns).
Patterns take precendence as they are often things like enforce the column is a floating point number etc. 
```
from alphaclean.search import solve

dcprogram, clean_instance = solve(df, patterns=[], dependencies=[constraint])
```
`dcprogram` is an object that represents the program that the solver found.
```
print(dcprogram)
df = swap(df,'a','New York',('a', set(['New Yorks'])))
df = swap(df,'b','SF',('a', set(['San Francisco'])))
df = swap(df,'b','SMO',('a', set(['San Mateo'])))
```
There are three find-and-replace operations that sequentially set the correct values. Note, this isn't actual code. It is a print statement that gives a high-level interpretable output for debugging. 

`clean_instance` gives you the cleaned dataset:
```
print(clean_instance)

                a    b
0        New York   NY
1        New York   NY
2   San Francisco   SF
3   San Francisco   SF
4        San Jose   SJ
5        New York   NY
6   San Francisco   SF
7   Berkeley City   Bk
8       San Mateo  SMO
9          Albany   AB
10      San Mateo  SMO
```
As you can see, the constraint has been enforced. You can re-run `dcprogram` on new data:
```
print(dcprogram.run(df))
                a    b
0        New York   NY
1        New York   NY
2   San Francisco   SF
3   San Francisco   SF
4        San Jose   SJ
5        New York   NY
6   San Francisco   SF
7   Berkeley City   Bk
8       San Mateo  SMO
9          Albany   AB
10      San Mateo  SMO
```

## Solver Configuration
The search algorithm takes about 30 seconds to run, even on a relatively simple problem. This is because the default search depth is 10, but we can optimize the performance of the algorithm by limiting the depth of the search if we know the cleaning problem is relatively easy.
The `solve` command optionally takes in a config object. One can query the default config as such:
```
from alphaclean.search import DEFAULT_SOLVER_CONFIG
config = DEFAULT_SOLVER_CONFIG
print(config['dependency']['depth'])

>>> 10
```
Here's how we might set this config parameter to 3, instead:
```
config['dependency']['depth'] = 3
```
Another source of inefficiency is the the similarity metric used to penalize repairs that modify too much data. By default this is a Levenstein distance calculation. On simpler problems, we can use a much more efficient Jaccard similarity:
```
config['dependency']['similarity'] = {'a': 'jaccard'}
```
The search optimizes a little bit faster, if you invoke the solver with these parameters:
```
dcprogram = solve(df, patterns=[], dependencies=[constraint], config=config)
```

## Harder Examples
The `docs` folder contains some harder, and more realistic, scenarios. You should run all the examples from the `alphaclean` folder with `python examples/example1.py`.
This is to keep the default paths for toy datasets and models consistent, but you are of course free to modify these paths!
