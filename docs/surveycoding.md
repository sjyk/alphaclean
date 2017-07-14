# Example 3: Survey Coding with AlphaClean
 Survey coding is the process of taking the open-ended responses and categorizing them into groups. In this example, we have a dataset of 1000 US 2016 presidential election contributions and want to categorize the occupations of the contributors into groups. 
 Example 3 `examples/example3.py` shows how this can be done in our framework. 

## Loading the data and initial data analysis
First, let's load the data into the system:
```
import pandas as pd
df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False)
```

Then, let's count all of the occupations that we see:
```
from collections import Counter
s = Counter(df['contbr_occupation'].values)
l = [i for i in sorted([(s[k],k) for k in s], reverse=True)]
print(l)
```
The result looks something like this:
```
[(344, 'RETIRED'), (67, 'INFORMATION REQUESTED PER BEST EFFORTS'), (58, 'ATTORNEY'), (26, 'HOMEMAKER'), (26, 'ENGINEER'), (25, 'PHYSICIAN'), (19, 'UBI'), (19, 'CONSULTANT'), (17, 'SEMI-RETIRED PHYSICIAN'), (15, 'LAWYER'), (12, 'CARPENTER'), (11, 'CEO'), (10, 'PRESIDENT'), (10, 'HOUSEWIFE'), (8, nan), (7, 'TEACHER'), (7, 'FIELD REP'), (7, 'FARMER'), (7, 'DIRECTOR OF FINANCE'), (6, 'SUPPORTED LIVING SPECIALIST... RETIRED'), (6, 'FURRIER'), (6, 'EXECUTIVE'), (6, 'CPA'), (6, 'BDC'), (6, 'ADMIN ASSISTANT'), (5, 'YMCA'), (5, 'SELF-EMPLOYED'), (5, 'OWNER'), (5, 'NORTH SLOPE BOROUGH SCHOOL DISTRICT'), (5, 'MEDICAL TRANSCRIPTIONIST'), (5, 'KFC FRANCHISEE'), (5, 'KBR'), (5, 'HVAC TECH'), (5, 'CAMPAIGN COORDINATOR'), (5, 'BUSINESS OWNER'), (4, 'SELF EMPLOYED'), (4, 'SECRETARY'), (4, 'FINANCIAL ADVISOR'), (4, 'COMMERCIAL REAL ESTATE BROKER'), (4, 'ANALYST'), (4, 'ACCOUNTANT'), (3, 'SALES'), (3, 'REAL ESTATE APPRAISER'), (3, 'PHARMACIST')
...
```

## Enforcing the constraints
In a simplified model, let's generate a code-book of the top 8 occupations:
```
codebook = set([occ[1] for occ in l][0:8])
```
In practice, you would want to do something more sophisticated here or manually design the code book.
Now, we solve:
```
operation = solve(df, [Pattern("contbr_zip", '[0-9]+')], [DictValue('contbr_occupation', codebook), FD(['contbr_zip'],['contbr_st']), OneToOne(['contbr_nm'], ['contbr_occupation'])], partitionOn='contbr_nm')
```



