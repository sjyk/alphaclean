# Example 3: Survey Coding with AlphaClean
 Survey coding is the process of taking the open-ended responses and categorizing them into groups. In this example, we have a dataset of 1000 US 2016 presidential election contributions and want to categorize the occupations of the contributors into groups. 
 Example 3 `examples/example3.py` shows how this can be done in our framework. 

## Loading the data and initial data analysis
First, let's load the data into the system:
```
import pandas as pd
df = pd.read_csv('datasets/elections.txt', quotechar='\"', index_col=False)
```
Let's print a sample record:
```
print(df.iloc[0,:])

cmte_id                                          C00458844
cand_id                                          P60006723
cand_nm                                       Rubio, Marco
contbr_nm                                    BLUM, MAUREEN
contbr_city                                     WASHINGTON
contbr_st                                               20
contbr_zip                                              DC
contbr_employer      STRATEGIC COALITIONS & INITIATIVES LL
contbr_occupation                        OUTREACH DIRECTOR
contb_receipt_amt                                      175
contb_receipt_dt                                 15-MAR-16
receipt_desc                                           NaN
memo_cd                                                NaN
memo_text                                              NaN
form_tp                                              SA17A
file_num                                           1082559
tran_id                                       SA17.1152124
election_tp                                          P2016
```
The interesting attribute is `contbr_occupation`--we may want to analyze contributions by occupation. If we want to categorize the people in this database, we will have to normalize these different attribute values.
In our misc folder, we have a helper method that builds a "code book":
```
from alphaclean.misc import generateTokenCodebook

print(generateTokenCodebook(df,'contbr_occupation'))
```

The result looks something like this:
```
set(['SLOPE', 'REQUESTED', 'ATTORNEY', 'LAW', 'RETIRED', 'PHYSICIAN', 'ASSISTANT', 'CARPENTER', 'US', 'SALES', 'DEVELOPER', 'PRIVATE', 'OFFICER', 'MILITARY', 'OUTREACH', 'ENGINEER', 'TEACHER', 'HOMEMAKER', 'PILOT'])
```

## Enforcing the constraints
In practice, you would want to do something more sophisticated here or manually design the code book.
Now, we solve:
```
operation = solve(df, [Pattern("contbr_zip", '[0-9]+')], [DictValue('contbr_occupation', codes), FD(['contbr_zip'],['contbr_st']), OneToOne(['contbr_nm'], ['contbr_occupation'])], partitionOn='contbr_nm')
```



