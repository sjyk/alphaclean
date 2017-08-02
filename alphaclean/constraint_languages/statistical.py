import numpy as np
from alphaclean.constraints import *

"""Module: statistical

This module specifies a number of classes representing statistical
and numerical constraints.
"""


class Parameteric(Constraint):
    """A parametric constraint models the domain as roughly guassian, it fires
    on values above a certain standard deviation from the mean.
    """

    def __init__(self, attr, tolerance=5):

        """Constructor for a Parametric constraint

        Positional arguments:
        attr -- an attribute name
        tolerance -- number of standard deviations
        """

        self.tolerance = tolerance
        self.attr = attr
        self.hint = set([attr])
        self.hintParams = {}

        
        super(Parameteric, self).__init__(self.hint)

    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))
        vals = df[self.attr].dropna().values
        mean = np.mean(vals)
        std = np.std(vals)

        for i in range(N):
            val = df[self.attr].iloc[i]

            if np.isnan(val) or np.abs(val-mean) < std*self.tolerance:
                qfn_a[i] = 0.0
            else:
                qfn_a[i] = 1.0

        return qfn_a



class NonParametric(Constraint):
    """A non-parametric constraint models the domain as concentrated around the median, it fires
    on values above a certain median absolute deviation from the median.
    """

    def __init__(self, attr, tolerance=5):

        """Constructor for a NonParametric constraint

        Positional arguments:
        attr -- an attribute name
        tolerance -- number of standard deviations
        """

        self.tolerance = tolerance
        self.attr = attr
        self.hint = set([attr])
        self.hintParams = {}

        
        super(NonParametric, self).__init__(self.hint)

    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))
        vals = df[self.attr].dropna().values
        mean = np.median(vals)
        std = np.median(np.abs(vals-mean))

        for i in range(N):
            val = df[self.attr].iloc[i]

            if np.isnan(val) or np.abs(val-mean) < std*self.tolerance:
                qfn_a[i] = 0.0
            else:
                qfn_a[i] = 1.0

        return qfn_a



class Correlation(Constraint):
    """A correlation constraint is a soft hint on a positive or negative relationship between
    two attributes.
    """

    def __init__(self, attrs, ctype="positive"):
        """A constructor for the correlation constraint

        Positional arguments:
        attrs -- a tuple of attributes
        ctype -- "positive" or "negative"
        """

        self.ctype = ctype
        self.attrs = attrs
        self.hint = set(attrs)
        self.hintParams = {}

        
        super(Correlation, self).__init__(self.hint)


    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))

        x = df[self.attrs[0]].values
        y = df[self.attrs[1]].values

        mx = np.median(x[~np.isnan(x)])
        my = np.median(y[~np.isnan(y)])

        for i in range(N):
            val1 = df[self.attrs[0]].iloc[i] - mx
            val2 = df[self.attrs[1]].iloc[i] - my

            if np.isnan(val1) or np.isnan(val2):
                continue

            if self.ctype == 'positive':
                if np.sign(val1*val2) < 0:
                    qfn_a[i] = np.abs(val1) + np.abs(val2)
            else:
                if np.sign(val1*val2) > 0:
                    qfn_a[i] = math.abs(val1) + math.abs(val2)

        #normalize
        if np.sum(qfn_a) > 0:
            qfn_a = qfn_a/np.max(qfn_a)

        return qfn_a



class NumericalRelationship(Constraint):
    """A numerical relationship is a soft hint on a relationship between two numerical
    attributes. You write a function and the constraint fires more strongly for values
    whose deviaiton from this function is high.
    """

    def __init__(self, attrs, fn, tolerance=5):
        """A constructor for the numericalrelationship constraint

        Positional arguments:
        attrs -- a tuple of attributes
        fn -- a function domain(attr[1]) -> domain(attr[2])
        tolerance -- number of standard deviations
        """

        self.tolerance = tolerance
        self.attrs = attrs
        self.hint = set(attrs)
        self.hintParams = {}
        self.fn = fn

        
        super(NumericalRelationship, self).__init__(self.hint)


    def _qfn(self, df): 
        N = df.shape[0]
        qfn_a = np.zeros((N,))

        x = df[self.attrs[0]].values
        y = df[self.attrs[1]].values

        residuals = []
        for i in range(N):
            val1 = df[self.attrs[0]].iloc[i]
            val2 = df[self.attrs[1]].iloc[i]

            if np.isnan(val1) or np.isnan(val2):
                continue

            pred_val2 = self.fn(val1)
            residual = val2 - pred_val2
            residuals.append(residual)

        mean = np.mean(residuals)
        std = np.std(residuals)

        for i in range(N):
            val1 = df[self.attrs[0]].iloc[i]
            val2 = df[self.attrs[1]].iloc[i]

            if np.isnan(val1) or np.isnan(val2):
                continue

            pred_val2 = self.fn(val1)
            residual = val2 - pred_val2

            if np.abs(residual-mean) > self.tolerance*std:
                qfn_a[i] = np.abs(residual-mean)


        #normalize
        if np.sum(qfn_a) > 0:
            qfn_a = qfn_a/np.max(qfn_a)

        return qfn_a

