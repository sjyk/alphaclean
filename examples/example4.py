import environ
import pandas as pd

f = open('datasets/weather.txt','r')
data = [  { str(i):j for i,j in enumerate(l.strip().split('\t')) } for l in f.readlines()]
df = pd.DataFrame(data)

print(df.iloc[0,:])




from alphaclean.constraint_languages.pattern import Float
patterns = [Float("3"), Float("5"), Float("6"), Float("7"),Float("8"),Float("9"), Float("10")]

from alphaclean.constraint_languages.ic import Parameteric
models = [Parameteric("5")]



from alphaclean.search import *

config = DEFAULT_SOLVER_CONFIG

config['dependency']['operations'] = [Delete]

operation, output = solve(df, patterns, models)

print(operation, output)


