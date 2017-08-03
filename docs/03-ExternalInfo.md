# 3. Survey Coding with AlphaClean
 Survey coding is the process of taking the open-ended responses and categorizing them into groups. In this example, we have a dataset of 1000 US 2016 presidential election contributions and want to categorize the occupations of the contributors into groups. 
 Example 3 `examples/example3.py` shows how this can be done in our framework. This example requires at least 8GB of available memory.

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
from alphaclean.misc import generateCodebook

codes = generateCodebook(df,'contbr_occupation')
print(codes)
```

The result looks something like this:
```
set(['CPA', 'LAWYER', 'WEALTH MANAGEMENT ADVISOR', 'SEMI-RETIRED PHYSICIAN', 'CHAIRMAN/CEO', 'RETIRED', 'FRANCHISEE', 'EDUCATION CHIEF', 'SHERIFF OF ETOWAH CO', 'VICE PRESIDENT/OWNER', 'UBI', 'HOMEMAKER', 'ATTORNEY', 'TRANSPORTATION', 'HEALTH CARE', 'E.E.', 'SUPPORTED LIVING SPECIALIST... RETIRED', 'ATHLETICS COMMUNICATIONS ASSOCIATE', 'CEO', 'PRESIDENT AND CEO', 'VP FOR GOVERNMENT AFFAIRS & SPECIAL CO', 'DIRECTOR OF FINANCE', 'CONTRACTOR', 'MANAGER', 'BUSINESS OWNER', 'M.D.', 'KBR', 'ADMIN ASSISTANT', 'YMCA', 'BDC', 'EXPERIANCED HOSPITAL CEO', 'FUNERAL DIRECTOR', 'THEATRE OWNER', 'HOUSEWIFE', 'MEDICAL TRANSCRIPTIONIST', 'OWNER', 'INSURANCE AGENT', 'REAL ESTATE BROKER', 'ACCOUNTANT', 'CUSTOMER SERVICE', 'PARTNER', 'TEACHER', 'VOLUNTEER', 'BUSINESS FARMS SALES', 'SMALL BUSINESS OWNER', 'FINANCIAL ADVISOR', 'ENGINEER', 'MULTIFAMILY REAL ESTATE', 'MANAGEMENT', 'FINANCE', 'VICE PRESIDENT', 'EXECUTIVE', 'CARPENTER', 'NORTH SLOPE BOROUGH SCHOOL DISTRICT', 'CAMPAIGN COORDINATOR', 'PRESIDENT', 'PHARMACIST', 'ANALYST', 'STATE REPRESENTATIVE', 'KFC FRANCHISEE', 'CONSTRUCTION', 'HUMAN RESOURCE OFFICER', 'INFORMATION REQUESTED PER BEST EFFORTS', 'SELF EMPLOYED', 'US GOVERNMENT', 'PND ENGINEERS', 'CONSULTANT', 'CLERK', 'WRITER', 'COMMUNICATIONS', 'STUDENT', 'R.N.', 'REAL ESTATE/OWNER', 'CONSULTING', 'SYSTEMS ANALYST', 'SALES REPRESENTATIVE', 'FARM', 'DAVIS HEATING & COOLING', 'SPEECH PATHALOGIST', 'ATTORNEY/REAL ESTATE DEVELOPER', 'CARDIOTHORACIC SURGEONS PC', 'SECRETARY', 'FURRIER', 'FARMER', 'AVIATOR', 'PILOT', 'COMMERCIAL REAL ESTATE BROKER', 'PHYSICIAN', 'IT', 'SUPERVISORY ADMINISTRATIVE OFFICER', 'FIELD REP', 'REAL ESTATE APPRAISER', 'CFO', 'REAL-ESTATE INVESTOR', 'SELF-EMPLOYED', 'SELF', 'SALES', 'HVAC TECH', 'SALES DIRECTOR'])
```

## Defining Constraints
We want to enforce that all values from the attribute exist in the codebook. This can be specified by what we call a DictValue constraint:
```
DictValue('contbr_occupation', codes)]
```
We want to use AlphaClean to find the minimize cost replacement of values to satisfy this constraint. However, we need to be a little smart about how we define the cost function.
For example, the values `MEDICAL DOCTOR` and `PHYSICIAN` are very similar but will greatly differ on most string similarity metrics. Lucklily, AlphaClean provides a pre-trained edit cost function of 100B entities on a Google News corpus.
```
mkdir -p resources
wget http://automation.berkeley.edu/archive/GoogleNews-vectors-negative300.bin
mv GoogleNews-vectors-negative300.bin resources
```

To use this cost function, we modify the constraints in the following way:
```
config = DEFAULT_SOLVER_CONFIG
config['dependency']['similarity'] = {'contbr_occupation':'semantic'}
```
We further may want to allow the solver to delete records (ones that don't seem to match anything in the code book):
```
config['dependency']['operations'] = [Swap, Delete]
```

## Running the solver
This will take a while to run because it has to load the entire Word2Vec model into memory.

```
operation = solve(df, [], dependencies=[DictValue('contbr_occupation', codes)], partitionOn='contbr_nm', config=config)
```
The result will look something like this:
```
df = delete(df,'contbr_occupation',('contbr_occupation', set(['PHYSICAL THERAPIST'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INVESTMENT BUSINESS'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['A PRINCIPAL'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CITY PLANNER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CHAIRMAN & CEO'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['PROPERTY INVESTMENT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CHIEF FINANCIAL OFFICER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EVP'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INVESTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INSURANCE & REAL ESTATE'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CIO'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['C.E.O.'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ENVIRONMENTAL ADVISOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['NURSE PRACTITIONER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['PRIVATE MORTGAGE BANKING'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EXECUTIVE INSURANCE BROKER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INVESTMENTS'])))
df = swap(df,'contbr_occupation','BUSINESS OWNER',('contbr_occupation', set(['BUSINESS'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['C.E.O./OWNER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['FINANCIAL CONSULATANT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['REAL ESTATE/CEO'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['AUTO DEALER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['FINANCIAL ADVISORS'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['OPERATIONS DIRECTOR'])))
df = swap(df,'contbr_occupation','COMMUNICATIONS',('contbr_occupation', set(['COMMUNICATIONS DIRECTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ORTHODONTIST'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['MILITARY'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['PRESIDENT/CEO'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ENGINEER (RET.)'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['GEOLOGIST'])))
df = swap(df,'contbr_occupation','MANAGEMENT',('contbr_occupation', set(['INVESTMENT MANAGEMENT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['OWNER CEO'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EXECUTIVE SENIOR VP'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['GOVERNMENTAL AFFAIRS'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['DERMATOLOGIST'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EDUCATOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['REAL ESTATE INVESTMENT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CHIEF HUMAN RELATIONS OFFICER'])))
df = swap(df,'contbr_occupation','ENGINEER',('contbr_occupation', set(['CIVIL ENGINEER'])))
df = swap(df,'contbr_occupation','EXECUTIVE',('contbr_occupation', set(['EXECUTIVE DIRECTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['PRODUCTION'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['MANUFACTURER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['BENNETT LUMBER COMPANY PIEDMONT AL'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['BENNETT LUMBER COMPANY'])))
df = swap(df,'contbr_occupation','CLERK',('contbr_occupation', set(['GROCERY CLERK'])))
df = swap(df,'contbr_occupation','CONSTRUCTION',('contbr_occupation', set(['ELECTRICAL CONSTRUCTION'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INS SALES'])))
df = swap(df,'contbr_occupation','PHYSICIAN',('contbr_occupation', set(['DOCTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['LAW CLERK'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['CIVIL SERVANT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['LIFE SAVVY WEIGHT LOSS CLINIC'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['COA'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EXEUCTIVE'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['COMPUTER PROGRAMMER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ADVISOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['OUTREACH DIRECTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['BOOKEEPER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['INSURANCE'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['DEVELOPMENT OFFICER'])))
df = swap(df,'contbr_occupation','PHYSICIAN',('contbr_occupation', set(['MEDICAL DOCTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ASTROPHYSICIST'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['EQUIPMENT OPERATOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ATTORNEY/SHAREHOLDER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['AUTHOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['POLICE OFFICER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['FOREIGN SERVICE OFFICER'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['ADMINISTRATION'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['FIRE DEPARTMENT'])))
df = swap(df,'contbr_occupation','CONTRACTOR',('contbr_occupation', set(['CONSTRUCTION CONTRACTOR'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['LAW ENFORCEMENT'])))
df = delete(df,'contbr_occupation',('contbr_occupation', set(['COMMUNITY BUSINESS DEVELOPER'])))
df = swap(df,'contbr_occupation','HEALTH CARE',('contbr_occupation', set(['HEALTH'])))
```
Where possible the solver will merge otherwise it will delete. You can play around with the configuration parameters making the following larger or smaller:
```
config['dependency']['edit'] = 1
```
This will make the edits more or less aggressive at merging.





