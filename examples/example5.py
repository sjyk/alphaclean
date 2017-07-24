import environ
import pandas as pd

f = open('datasets/all_villages_2010-16.csv','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split(',')) } for l in f.readlines()[2:]]
df = pd.DataFrame(data)


from alphaclean.constraints import Float, Correlation
import numpy as np
import scipy as sp

print(df.iloc[0,:])
patterns = []
for i in range(3,84):
    patterns.append(Float(str(i), [0, np.inf]))


from alphaclean.search import *

config = DEFAULT_SOLVER_CONFIG

config['pattern']['depth'] = 0

config['dependency']['operations'] = [Delete]

operation = solve(df, patterns, [Correlation([str(4), str(81)])])
output = operation.run(df)

print(operation)



"""
import matplotlib.pyplot as plt

for i in range(output.shape[0]):
    x = output["67"].iloc[i]
    y = output["57"].iloc[i]

    if np.isnan(x) or np.isnan(y):
        continue

    plt.scatter(x,y, c='r')

plt.show()
"""



"""
from alphaclean.constraints import Float, Parameteric
patterns = [Float("3"), Float("5"), Float("6"), Float("7"),Float("8"),Float("9"), Float("10")]
models = [Parameteric("5")]



from alphaclean.search import *

config = DEFAULT_SOLVER_CONFIG

config['dependency']['operations'] = [Delete]

operation = solve(df, patterns, models)

output = operation.run(df)

print(operation)




import matplotlib.pyplot as plt

plt.hist(output["5"].dropna().values)

plt.show()
"""


