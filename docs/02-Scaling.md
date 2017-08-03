# 2. Scaling AlphaClean
This example will show how to scale the search algorithm to larger datasets and will work with some real data.
There are often discrepancies in data acquired from different Web sources. A common data cleaning task is to reconcile these discrepencies into a cannonical source of truth. Example 2 `examples/example2.py` shows how this can be done in our framework. It will leverage the same basic tools as the toy example.

We have a dataset of airline 1000 arrival and departure times:
```
import pandas as pd
f = open('datasets/airplane.txt','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split('\t')) } for l in f.readlines()]
df = pd.DataFrame(data)
```

If we load it into a pandas dataframe, we get a dataset with a large number of inconsistencies in formatting, value, and completeness:
```
                0                1                    2                3  \
10         panynj  AA-1007-TPA-MIA                         2:07 PMDec 01   
11          gofox  AA-1007-TPA-MIA                         2:07 PMDec 01   
12    foxbusiness  AA-1007-TPA-MIA                         2:07 PMDec 01   
13   allegiantair  AA-1007-TPA-MIA                         2:07 PMDec 01   
14         boston  AA-1007-TPA-MIA                         2:07 PMDec 01   
15    travelocity  AA-1007-TPA-MIA      Dec 01 - 1:55pm  Dec 01 - 1:57pm   
16         orbitz  AA-1007-TPA-MIA           1:55pDec 1       1:57pDec 1   
17        weather  AA-1007-TPA-MIA  2011-12-01 01:55 PM                    
18            mia  AA-1007-TPA-MIA                                         
19  mytripandmore  AA-1007-TPA-MIA           1:55pDec 1       1:57pDec 1   

       4                    5                  6    7  
10                                 2:57 PMDec 01  NaN  
11                                 2:57 PMDec 01  NaN  
12                                 2:57 PMDec 01  NaN  
13                                 2:57 PMDec 01  NaN  
14                                 2:49 PMDec 01  NaN  
15   F78      Dec 01 - 3:00pm    Dec 01 - 2:57pm   D5  
16   F78           3:00pDec 1         2:57pDec 1   D5  
17        2011-12-01 03:00 PM                NaN  NaN  
18             3:00P 12-01-11  2011-12-01  2:57P  NaN  
19   F78           3:00pDec 1         2:57pDec 1   D5 
```

## Creating the Data Model
We would like to fix this with AlphaClean. First, we isolate all of the date/time attributes 2, 3, 5,6. We have a special constraint that enforces patterns on date/time attributes in a standard strftime format.
```
from alphaclean.constraint_languages.pattern import Date
patterns = [Date("2", "%m/%d/%Y %I:%M %p"), Date("3", "%m/%d/%Y %I:%M %p"), Date("5", "%m/%d/%Y %I:%M %p"), Date("6", "%m/%d/%Y %I:%M %p")]
```
This enforces that values should be of the form 'MM-DD-YYYY HH:MM {AM,PM}'. Next, we have to enforce a pattern on the gate number:
```
from alphaclean.constraint_languages.pattern import Pattern
patterns += [Pattern("4", '^[a-zA-Z][0-9]+'), Pattern("7", '^[a-zA-Z][0-9]+')]
```
Then, we introduce a One-to-One constraint between the flight code (attribute 1) and all other attributes:
```
from alphaclean.constraint_languages.ic import OneToOne
dependencies = []
for i in range(2,8):
    dependencies.append(OneToOne(["1"],[str(i)]))
```

## Scaling the Solver
Now it's time to solve, since this dataset is substantially larger, we are going to solve it in blocks. Blocks partition decoupled units of data to speed up the search algorithm. In this case, the flight-code is a reasonable blocking rule:
```
from alphaclean.search import solve
operation = solve(df, patterns, dependencies, partitionOn="1")
```
What this means is that the solver will apply a divide-and-conqueor strategy solving the problem in blocks partitioned by the first attribute (the flight key).

This should take about 30 minutes to run, and will output a very long program to fix all the data, here is a sample of the result:
```

10                panynj  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
11                 gofox  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
12           foxbusiness  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
13          allegiantair  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
14                boston  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
15           travelocity  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
16                orbitz  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
17               weather  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
18                   mia  AA-1007-TPA-MIA  12/01/2011 01:55 PM   
19         mytripandmore  AA-1007-TPA-MIA  12/01/2011 01:55 PM


10  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
11  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
12  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
13  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
14  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
15  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
16  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
17  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
18  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
19  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5  
20  12/01/2011 02:07 PM  F78  12/01/2011 03:00 PM  12/01/2011 02:51 PM    D5
```
A snippet of the synthesized program:
```
...

df = delete(df,'6',('6', set([nan])))
df = delete(df,'6',('6', set(['2:57pDec 1'])))
df = pattern(df,'7','^[a-zA-Z][0-9]+')

df = delete(df,'7',('7', set([None])))


df = swap(df,'2','12/01/2011 12:10 PM',('1', set(['AA-1518-DFW-SDF'])))

df = swap(df,'3','12/01/2011 12:18 PM',('1', set(['AA-1518-DFW-SDF'])))

df = swap(df,'4','C20',('1', set(['AA-1518-DFW-SDF'])))

df = swap(df,'5','12/01/2011 03:10 PM',('1', set(['AA-1518-DFW-SDF'])))

df = swap(df,'6','12/01/2011 02:57 PM',('1', set(['AA-1518-DFW-SDF'])))

df = swap(df,'7','A15',('1', set(['AA-1518-DFW-SDF'])))

df = dateparse(df,'2','%m/%d/%Y %I:%M %p')

...

```

