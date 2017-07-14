import numpy as np
import re

"""
This module defines the main infrastructure for describing domains
"""



"""
A domain object describes the domain of an attribute
"""
class Domain(object):

    def __init__(self):
        super(Domain, self).__init__()


    """
    This function tests if one domain is contained
    in another.
    """
    def contains(self, other):

        if not isinstance(other, Domain):
            raise ValueError(str(other) + " is not of type domain")

        return self._contains(other)


    """
    This function tests if one domain is contained
    in another.
    """
    def equals(self, other):

        if not isinstance(other, type(self)):
            raise ValueError(str(other) + " is not of a compatible domain type")

        return (self._contains(other) and other._contains(self))



    def _contains(self, other):
        raise NotImplemented("You must implement a _contains(domain) function")


    """
    This function validates whether the given value is in the domain
    """
    def validate(self, val):
        raise NotImplemented("You must implement a validate(value) function")





"""
This class defines a numerical range domain
"""
class IntegerRangeDomain(Domain):

    def __init__(self, high=np.inf, low=-np.inf):
        
        self.high = high
        self.low = low

        if self.low > self.high:
            raise ValueError("Invalid range object")

        super(IntegerRangeDomain, self).__init__()


    def _contains(self, other):

        if self.high <= other.high and \
            self.low >= other.low:
            return True
        else:
            return False


    def validate(self, val):

        try:
            val = int(val)
            
            return (val <= self.high and val >= self.low)

        except:
            
            return False

"""
This class defines a numerical range domain
"""
class FloatRangeDomain(Domain):

    def __init__(self, high=np.inf, low=-np.inf):
        
        self.high = high
        self.low = low

        if self.low > self.high:
            raise ValueError("Invalid range object")

        super(FloatRangeDomain, self).__init__()


    def _contains(self, other):

        if self.high <= other.high and \
            self.low >= other.low:
            return True
        else:
            return False


    def validate(self, val):

        try:
            val = float(val)
            
            return (val <= self.high and val >= self.low)

        except:
            
            return False



"""
This class defines a string domain
"""
class StringDomain(Domain):

    def __init__(self, expr=".*"):

        self.expr = expr
        self.prog = re.compile(expr)

        super(StringDomain, self).__init__()


    def _contains(self, other):

        if self.expr = ".*":
            return True
        elif self.expr == other.expr:
            return True
        else:
            return False


    def validate(self, val):

        match = self.prog.match(val)
        if  match == None:
            return False
        elif match.group(0) == '':
            return False
        else:
            return True


"""
Meta domain object for multiple attributes
"""
class MultiAttributeDomain(Domain):

    def __init__(self, domains):

        self.domains = domains

        super(MultiAttributeDomain, self).__init__()


    def _contains(self, other):

        if self.expr = ".*":
            return True
        elif self.expr == other.expr:
            return True
        else:
            return False


    def validate(self, val):

        match = self.prog.match(val)
        if  match == None:
            return False
        elif match.group(0) == '':
            return False
        else:
            return True






