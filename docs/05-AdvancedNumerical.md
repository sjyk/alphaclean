# 5. More Advanced Numerical Cleaning
Now, we will illustrate some more sophisticated approaches to modeling numerical data. This section largely focuses on the module `from alphaclean.constraint_languages.statistical`. The word constraint is admittedly a misnomer for this module. Most of the classes in this module define soft constraints (i.e., quality functions that fire more strongly based on degree of violation). We will overview two such classes.


A correlation constraint is a soft hint on a positive or negative relationship between
two attributes. For example, if we expect a positive correlation between two attributes
we could write the following constraint:
```
from alphaclean.constraint_languages.statistical import Correlation

Correlation(["attr1", "attr2"], ctype="positive")
```
What this means is that values for attr2 that are above the mean value should imply that the corresponding value for att1 is also above the mean value. This constraint creates a quality function that penalizes failures to respect this relationship.


A NumericalRelationship constraint is another soft constraint. A numerical relationship is a soft hint on a relationship between two numerical
 attributes. You write a function and the constraint fires more strongly for values whose deviaiton from this function is high. For example, if we expect that two attributes should be `close`, we can write:
```
from alphaclean.constraint_languages.statistical import NumericalRelationship

NumericalRelationship(["attr1", "attr2"], lambda x: x)
```
This would penalize the difference between the two attributes.
