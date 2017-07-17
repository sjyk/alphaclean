# alphaclean v0.1
In many data science applications, data cleaning is effectively manual with ad-hoc, single-use scripts and programs. 
This practice is highly problematic for reproducibility (sharing analysis between researchers), interpretability (explaining the findings of a particular analysis), and scalability (replicating the analyses on larger corpora).
Most existing relational data cleaning solutions are designed as stand-alone systems, often coupled with a DBMS, with poor language support for Python and R that are widely used in data science.

We designed a Python library that declaratively synthesizes data cleaning programs. 
AlphaClean is given a  specification of quality (e.g., integrity constraints or a statistical model the data must conform to) and a language of allowed data transformations, and it searches to find a sequence of transformations that best satisfices the quality specification.
The discovered sequence of transformations defines an intermediate representation, which can be easily transferred between languages or optimized with a compiler.

## Requirements
As an initial research prototype, we have not yet designed alphaclean for deployment. It is a package that researchers can locally develop and test to evaluate different data cleaning approaches and techniques. The dependencies are:
```
dateparser==0.6.0
Distance==0.1.3
numpy==1.12.1
pandas==0.20.1
pytz==2017.2
scikit-learn==0.18.1
scipy==0.19.0
six==1.10.0
sklearn==0.0
```
These can be installed with:
```
pip install -r requirements.txt
```

## Getting Started (A Simple Example)

The details of this initial tutorial are described in `examples/example1.py`. Data Scientists rarely get data that is immediately ready for analysis, some amount of pre-processing and curating is needed. We assume that you've done the hard work in acquiring the data and putting a rough relational structure around it, we help you make the most of what you have collected!

Let's start with a simple example of cities and acronyms:
```
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
```
Notice that the city names are inconsistent <b>New York</b> vs. <b>New Yorks</b> and the acronyms are inconsistent <b>SF</b> vs. <b>SFO</b> and <b>SM</b> vs. <b>SMO</b>. For a small dataset--through visual inspection--it is possible to enumerate all of the fixes, but what if this dataset was very large? 

How would we automatically fix this with AlphaClean?
First, we load the data into a Pandas DataFrame:
```
import pandas as pd
df = pd.DataFrame(data)
```
Then, we define a `OneToOne` constraint that enforces that the keys 'a' map to 'b' bijectively:
```
from alphaclean.constraints import OnetoOne
constraint = OneToOne(["a"], ["b"])
```
Next, we invoke the solver to find a program that enforces this constraint (we bound the depth of the search at 3):
```
from alphaclean.search import solve
dcprogram = solve(df, dependencies=[constraint], evaluations=3)
```
It will take a few seconds to run to find the solution. The output is an object that represents the discovered data cleaning program, which we can run on the data to see the output:
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
As you can now see the constraint has been enforced. You can see what the program is logically doing:
```
print(dcprogram)
df = swap(df,'a','New York',('a', set(['New Yorks'])))
df = swap(df,'b','SF',('a', set(['San Francisco'])))
df = swap(df,'b','SMO',('a', set(['San Mateo'])))
```
We see that there are three find-and-replace operation that sequentially set the correct values. Note, that this isn't actual code it is a print statement that gives a high-level interpretable output for debugging. 

## Harder Examples
The `docs` folder contains some harder (and more realistic) scenarios.








