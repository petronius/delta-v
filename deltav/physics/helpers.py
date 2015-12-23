
from numpy import matrix, cos, sin

# From Paul Griffith's Pyastro library
def kepler(m_anom, eccentricity):

    """Solves Kepler's equation for the eccentric anomaly
    using Newton's method.
    Arguments:
    m_anom -- mean anomaly in radians
    eccentricity -- eccentricity of the ellipse
    Returns: eccentric anomaly in radians.
    """

    desired_accuracy = 1e-6
    e_anom = m_anom

    while True:
        diff = e_anom - eccentricity * sin(e_anom) - m_anom
        e_anom -= diff / (1 - eccentricity * cos(e_anom))
        if abs(diff) <= desired_accuracy:
            break
    return e_anom


def Rx(theta):
    """
    Return a rotation matrix for the X axis and angle *theta*
    """
    return matrix([
        [1, 0,           0           ],
        [0, cos(theta), -1*sin(theta)],
        [0, sin(theta), cos(theta)   ],
    ], dtype="float64")

def Ry(theta):
    """
    Return a rotation matrix for the Y axis and angle *theta*
    """
    return matrix([
        [cos(theta),    0, sin(theta)],
        [0,             1, 0         ],
        [-1*sin(theta), 0, cos(theta)],
    ], dtype="float64")
    
def Rz(theta):
    """
    Return a rotation matrix for the Z axis and angle *theta*
    """
    return matrix([
        [cos(theta), -1*sin(theta), 0],
        [sin(theta), cos(theta),    0],
        [0,          0,             1],
    ], dtype="float64")
    