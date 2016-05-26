
from functools import partial

from numpy import longdouble, seterr, sqrt, sin, cos, tan, matrix
from numpy import array as _array

seterr(all="raise")

# set the float type for all physics calculations
_float = longdouble

array = partial(_array, dtype=_float)


def cbrt(x):
    return x**(1/_float("3.0"))

def cot(x):
    return 1/tan(x)

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

# From Paul Griffith's Pyastro library
def kepler(m_anom, eccentricity, accuracy = 1e-12):

    """Solves Kepler's equation for the eccentric anomaly
    using Newton's method.
    Arguments:
    m_anom -- mean anomaly in radians
    eccentricity -- eccentricity of the ellipse
    Returns: eccentric anomaly in radians.
    """

    e_anom = m_anom

    while True:
        diff = e_anom - eccentricity * sin(e_anom) - m_anom
        e_anom -= diff / (1 - eccentricity * cos(e_anom))
        if abs(diff) <= accuracy:
            break
    return e_anom

def Rx(theta):
    """
    Return a rotation matrix for the X axis and angle *theta*
    """
    return matrix([
        [1, 0,          0          ],
        [0, cos(theta), sin(theta)],
        [0, -sin(theta), cos(theta) ],
    ], dtype=_float)

def Ry(theta):
    """
    Return a rotation matrix for the Y axis and angle *theta*
    """
    return matrix([
        [cos(theta),  0, sin(theta)],
        [0,           1, 0         ],
        [-sin(theta), 0, cos(theta)],
    ], dtype=_float)
    
def Rz(theta):
    """
    Return a rotation matrix for the Z axis and angle *theta*
    """
    return matrix([
        [cos(theta), sin(theta), 0],
        [-sin(theta), cos(theta),  0],
        [0,          0,           1],
    ], dtype=_float)