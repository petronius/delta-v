
from functools import partial

from numpy import longdouble, seterr, sqrt
from numpy import array as _array


seterr(all="raise")

# set the float type for all physics calculations
_float = longdouble

array = partial(_array, dtype=_float)


def cbrt(x):
    return x**(1/_float("3.0"))


def cached_property(f):
    """
    Returns a cached property that is calculated by function f
    """
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x
        
    return property(get)


def distance(p1, p2):
    return sqrt(
        (p1[0]-p2[0])**2 +
        (p1[1]-p2[1])**2 +
        (p1[2]-p2[2])**2
    )