# 4. "Simple" Numerical Outliers with AlphaClean
In the next example, we consider "simple" outliers. That is, single attributes that significantly deviate from the typical value in a distribution.

## Weather Dataset
The weather dataset contains 6030 records of weather readings from 30 cities:
```
0          Fri Jan 29 08:38:52 2010
1                    Austin, Texas 
2      Heavy Thunderstorms and Rain
3                                55
4                               WNW
5                                 8
6                                54
7                             29.95
8                                  
9                                94
10                              1.5
```
This dataset has a mix of numerical and categorical values. In this example, we will illustrate techniques for cleaning missing values and outliers in numerical data.
First, let's load the dataset:
```
f = open('datasets/weather.txt','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split('\t')) } for l in f.readlines()]
df = pd.DataFrame(data)
```

## Creating Constraints
Next, we want to parse each of the numerical columns as a Floating point number:
```
from alphaclean.constraint_languages.pattern import Float
patterns = [Float("3"), Float("5"), Float("6"), Float("7"),Float("8"),Float("9"), Float("10")]
```

Now, we can solve:
```
operation = solve(df, patterns,[])

output = operation.run(df)
```

If we plot the results:
```
import matplotlib.pyplot as plt

plt.hist(output["5"].dropna().values)

plt.show()
```

We see that there are large outliers polluting the data. We can further add a "model" restriction that gives the system a hint that the column represents a statistical distribution and should be concentrated around center values.
```
from alphaclean.constraint_languages.statistical import Parametric

models = [Parameteric("5")]
```

## Results
The resultant program:
```
df = numparse(df,'3')
df = numparse(df,'5')
df = numparse(df,'6')
df = numparse(df,'7')
df = numparse(df,'8')
df = numparse(df,'9')
df = numparse(df,'10')
df = delete(df,'5',('5', set([-9999.0])))
df = delete(df,'5',('5', set([33.0])))
```

