import numpy as np
from alphaclean.constraints import *
import re
import time

"""Module: pattern

This module defines a language of pattern constraints. Pattern constraints are 
constraints on a single attribute that apply row-by-row. These are always enforced
before any other types of constraints.
"""


class Date(Predicate):
    """A Date constraint enforces that a datetime string field has a certain 
    format.
    """

    def __init__(self, attr, pattern):
        """Date constructor

        Positional arguments:
        attr -- an attribute name 
        pattern -- a standard python strftime string
        """

        self.pattern = pattern
        self.attr = attr

        def timePatternCheck(x, p):

            if x == None or x != x or  len(x.strip()) == 0:
                return False

            try:
                t = time.strptime(x,p)
                return True
            except ValueError:
                return False


        super(Date, self).__init__(attr, lambda x, p=pattern: timePatternCheck(x,p))



class Float(Predicate):
    """A Float constraint enforces that an attribute is a floating point number
    """

    def __init__(self, attr, nrange=[-np.inf, np.inf]):
        """float constructor

        Positional arguments:
        attr -- an attribute name 
        nrange -- the range of allowed values
        """

        self.attr = attr
        self.range = nrange

        def floatPatternCheck(x):

            if x == None or isinstance(x, float):
                return True
            else:
                return False

        super(Float, self).__init__(attr, lambda x: floatPatternCheck(x))




class Pattern(Predicate):
    """A pattern constraint enforces that a string field has a certain 
    format matched by a regular expression.
    """

    def __init__(self, attr, pattern):
        """Pattern constructor

        Positional arguments:
        attr -- an attribute name 
        pattern -- a standard python regular expression
        """

        self.pattern = pattern
        self.attr = attr

        def patternCheck(x, p):

            if x == None or len(x) == 0 or x != x:
                return False

            try:
                result = re.match(p, x)
                return (result != None)
            except:
                return False


        super(Pattern, self).__init__(attr, lambda x, p=pattern: patternCheck(x,p))


