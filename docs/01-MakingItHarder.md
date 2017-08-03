# 1. More Advanced Features
This example is to illustrate more complex functionality and the concepts in AlphaClean. Not all data models are as simple as a one-to-one relationship. Sometimes we have more complex constraints we would like to enforce. This example is in `examples/example8.py`.

Let's consider the following data:
```
data = [{'title': 'Employee 1' , 'salary': 100.0}, 
         {'title': 'Employee 2' , 'salary': 100.0},
         {'title': 'Employee 3' , 'salary': 100.0},
         {'title': 'Employee 4' ,'salary': 100.0},
         {'title': 'Manager 1' ,'salary': 500.0},
         {'title': 'Manager 2' ,'salary': 80.0}]
```
There are two types of records in this table Employees and Managers. Suppose, we want to enforce that there does not exist a manager who makes less than an employee. This type of constraint can be expressed in a formal language called a denial constraint (a set of database predicates that cannot all be true).

AlphaClean provides an API for specifying such constraints on a DataFrame.
The basic structure of a predicate is as follows:
    * This predicate is applied to every row of the dataframe.
    * For each row, we can query an attribute called the "local attribute"
    * then, we can evaluate a boolean expression over this value and over the entire dataframe

```
from alphaclean.constraint_languages.ic import DenialConstraint, DCPredicate

#Employee is a manager
predicate1 = DCPredicate(local_attr='title', expression= lambda value, data_frame: 'Manager' in value)

#There exists an employee with a salary greater than the given manager's salary
predicate2 = DCPredicate(local_attr='salary', expression= lambda value, data_frame: \
                                                        data_frame[ (data_frame['salary'] > value) & \
                                                        data_frame['title'].str.contains("Employee", na=False) ].shape[0] > 0)

constraint = DenialConstraint([predicate1, predicate2])                                                    
```

As before, we can solve to find a program that enforces the constraints:
```
from alphaclean.search import solve

dcprogram, output = solve(df, patterns=[] ,dependencies=[constraint])
```
We can see the output like this:
```
print(dcprogram)
df = swap(df,'salary','500.0',('salary', set([80.0])))

print(output)
salary       title
0   100.0  Employee 1
1   100.0  Employee 2
2   100.0  Employee 3
3   100.0  Employee 4
4   500.0   Manager 1
5   500.0   Manager 2
```

## Changing the search language

One problem here is that while the constraint is enforced it may not be semantically meaningful to do this. Setting the salary of the manager to 500 may not be accurate. Suppose, we just wanted to delete those cells that caused these violations. We can do this in AlphaClean very easily where we switch search language to only consider deletion operations and no modifications to the data:
```
from alphaclean.search import DEFAULT_SOLVER_CONFIG
from alphaclean.ops import Delete

config = DEFAULT_SOLVER_CONFIG
config['dependency']['operations'] = [Delete]
```
The above config object restricts the operations to only consider Deletions. 
The result is:
```
dcprogram2, output2 = solve(df, patterns=[] ,dependencies=[constraint], config=config)

print(dcprogram2)
df = delete(df,'title',('salary', set([80.0]))

print(output2)
0   100.0  Employee 1
1   100.0  Employee 2
2   100.0  Employee 3
3   100.0  Employee 4
4   500.0   Manager 1
5    80.0        None)
```

## Edit Costs
We may want to flexibly move between deletion and replacement depending on how severe we believe the error is. Consider the table where the second manager's salary is 50.0:
```
salary       title
0   100.0  Employee 1
1   100.0  Employee 2
2   100.0  Employee 3
3   100.0  Employee 4
4   500.0   Manager 1
5    50.0   Manager 2
```
Maybe a reasonable assumption is that this is a typo and can safely be updated to 500.0. We can express logic like this in AlphaClean by changing the edit cost, a penalty on modifying the data. Let's first create a new dataset:
```
data = [{'title': 'Employee 1' , 'salary': 100.0}, 
         {'title': 'Employee 2' , 'salary': 100.0},
         {'title': 'Employee 3' , 'salary': 100.0},
         {'title': 'Employee 4' ,'salary': 100.0},
         {'title': 'Manager 1' ,'salary': 500.0},
         {'title': 'Manager 2' ,'salary': 50.0}]

df = pd.DataFrame(data)
```

And configure the solver to use both replacement (called a Swap) and deletions:
```
from alphaclean.search import DEFAULT_SOLVER_CONFIG
from alphaclean.ops import Delete, Swap

config = DEFAULT_SOLVER_CONFIG
config['dependency']['operations'] = [Swap, Delete]
```

The editing cost can be modified with the following configuration option, let's first set it to 0:
```
config['dependency']['edit'] = 0
```
If we run the solver, we can see that the solver favors replacing the element
```
dcprogram3, output3 = solve(df, patterns=[] ,dependencies=[constraint], config=config)

print(dcprogram3)
df = swap(df,'salary','500.0',('salary', set([50.0])))   

print(output3)
salary       title
0   100.0  Employee 1
1   100.0  Employee 2
2   100.0  Employee 3
3   100.0  Employee 4
4   500.0   Manager 1
5   500.0   Manager 2
```

If we make the edit cost 10:
```
config['dependency']['edit'] = 10
```

We can get the deleted result:
```
df = delete(df,'title',('salary', set([80.0]))

0   100.0  Employee 1
1   100.0  Employee 2
2   100.0  Employee 3
3   100.0  Employee 4
4   500.0   Manager 1
5    80.0        None)
```

## Debugging
Every execution of the example files will create a random log file, you can configure logging by taking a look at the `environ` import at the top of each example:
```
import logging 
import string
import random

logfilename =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) +'.log'

logging.basicConfig(level=logging.INFO, filename=logfilename) 

logging.warn("Logs saved in " + logfilename)
```

If you change that to logging.DEBUG, you will get much more verbose logs about the decisions the algorithm is taking.



