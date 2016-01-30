"""
Two-body Keplarian orbit modelling.
"""

#TODO: https://en.wikipedia.org/wiki/Hill_sphere

from math import floor
from numpy import (
    # objects and modules
    array,
    matrix,
    asarray,
    squeeze,
    float128,
    allclose,
    seterr,
    # values and arithmatic functions
    pi, NaN, Inf,
    sqrt,
    sign,
    cos, arccos, cosh, arccosh,
    sin, arcsin, sinh,
    tan, arctan, arctan2,
    # matrix functions and helpers
    dot,
    inner,
    cross,
    newaxis,
)
from numpy.linalg import norm
import textwrap

from .helpers import kepler, keplerh, Rx, Rz, Ry

seterr(all="raise")

cbrt = lambda x: x**(float128("1.0")/float128("3.0"))


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


class OrbitCalculationException(Exception):
    pass

class Orbit(object):
    """
    Set up an orbit from spacecraft position and speed data. The game here is
    essentially the same as determining a satellite's orbit from earth only
    from objserved information.

    For humans (programmers and players) this will provide an easy way to know
    where above a planet we are putting our ships, and then we can go on to
    solve for the important orbital information later.

    All calculations should assume radians, and return radians.

    Use these:
        https://downloads.rene-schwarz.com/download/M002-Cartesian_State_Vectors_to_Keplerian_Orbit_Elements.pdf
        https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf

    Help with Hyperbolic and Parabolic:

        http://www.bogan.ca/orbits/kepler/orbteqtn.html

    "Fundaments of Orbital Mechanics for Engineering Students":

        https://docs.google.com/file/d/0B7WvmGcRs5CzMDVPT3JnV25OdTg/edit

    A MATLAB implementation of all of this (in theory):

        http://de.mathworks.com/matlabcentral/fileexchange/35455-convert-keplerian-orbital-elements-to-a-state-vector

    """

    TPL = """<Orbit: period %s s
    a = %s m
    e = %s
    i = %s r
    Ω = %s r
    ω = %s r
    ν = %s r
>"""

    # The gravitational constant
    G = 6.674e-11

    # Maximum number of radians in a circle
    _2PI = 2 * pi

    # unit vectors for axes x, y, z
    I = array([1.0, 0.0, 0.0])
    J = array([0.0, 1.0, 0.0])
    K = array([0.0, 0.0, 1.0])

    # Used for comparisons, because of floating point rounding error
    ONE = float128("1.0")
    ACCURACY = float128("1e-12")


    def __init__(self, parent, satellite, v_position, v_velocity):
        self.parent = parent
        self.satellite = satellite
        self.v_position = array(v_position)
        self.v_velocity = array(v_velocity)

        self.mag_position = self.mag_position
        self.mag_veloctiy = norm(self.v_veloctiy)

        self.propery_cache = {}


    def __repr__(self):
        return self.TPL % (
            self.period,
            self.semi_major_axis,
            self.eccentricity,
            self.inclination,
            self.long_of_asc_node,
            self.argument_of_periapsis,
            self.true_anomaly,
        )


    def accelerate(self, vector):
        self.v_velocity = array([
            self.v_velocity[0] + vector[0],
            self.v_velocity[1] + vector[1],
            self.v_velocity[2] + vector[2],
        ])

    #
    # Define properties for the classical orbital elements
    #

    @cached_property
    def gravitational_parameter(self):
        """
        Gravitational parameter (2-body)
        """
        return self.G * self.parent.mass


    @cached_property
    def v_angular_momentum(self):
        """
        Angular momentum vector, in m**2/s (h')
        """
        return cross(self.v_position, self.v_velocity)


    @cached_property
    def angular_momentum(self):
        """
        Magnitude of h'. (h)
        """
        return norm(self.v_angular_momentum)


    @cached_property
    def v_eccentricity(self):
        """
        Eccentricity vector. (e')
        """
        return (
            1/self.gravitational_parameter
        ) * (
            ((self.mag_velocity**2 - self.gravitational_parameter/self.mag_position) * self.v_position)
            -
            (dot(self.v_position, self.v_velocity) * self.v_velocity)
        )


    @cached_property
    def eccentricity(self):
        """
        The eccentricity of the orbital ellipse. (e)
        """
        e = norm(self.v_eccentricity)
        # Below the accuracy threshold, just revert to 0 to avoid rounding
        # errors causing unexpected problems.
        if self.eq(e, 0):
            return 0
        else:
            return e


    @cached_property
    def v_node(self):
        """
        Node (of ascension) vector (m**2 / s) (n')
        """
        result = cross(self.K, self.v_angular_momentum)
        #
        # "For non-inclined orbits (with inclination equal to zero), Ω is 
        #  undefined. For computation it is then, by convention, set equal to 
        #  zero; that is, the ascending node is placed in the reference 
        #  direction, which is equivalent to letting n point towards the 
        #  positive x-axis."
        #
        #  https://en.wikipedia.org/wiki/Longitude_of_the_ascending_node
        #
        if (result == array([0,0,0])).all():
            return self.K
        return result


    @cached_property
    def node(self):
        """
        Magniture of the node vector. (n)
        """
        return self.node


    @cached_property
    def true_anomaly(self):
        """
        True anomaly (angle from the focus at the barycentre of the orbit, ν).
        """
        res = (
            dot(self.v_eccentricity, self.v_position)
            /
            (self.eccentricity*self.mag_position)
        )
        if self.eq(res, 1.0):
            res = 1.0
        true_anomaly = arccos(res)
        if self.lt(dot(self.v_position, self.v_velocity), 0.0):
            true_anomaly = 2.0 * pi - true_anomaly
        return true_anomaly


    @cached_property
    def inclination(self):
        """
        Inclination of the orbit (i).
        """
        return arccos(
            self.v_angular_momentum[2]
            /
            self.angular_momentum
        )


    @cached_property
    def eccentric_anomaly(self):
        """
        Like the true anomaly, but measured about the center of the ellipse.

        (E for elliptical orbits. D, F for hyperbolic and parabolic.)
        """
        if self.is_circular:
            return self.true_anomaly
        elif self.is_elliptical:
            return 2.0 * arctan(
                tan(self.true_anomaly/2.0)
                /
                sqrt((1.0 + self.eccentricity) / (1 - self.eccentricity))
            )
        elif self.is_parabolic:
            # "D"
            return tan(true_anomaly/2.0)
        elif self.is_hyperbolic:
            # F
            return arccosh(
                (self.eccentricity + cos(self.true_anomaly))
                /
                (1.0 + self.eccentricity * cos(self.true_anomaly))
            )
        else:
            raise Exception("Are you in the right spacetime?")


    @cached_property
    def long_of_asc_node(self):
        """
        Longitude of the ascending node (Ω).
        """
        long_of_asc_node = arccos(self.v_node[0]/self.node)
        if self.lt(self.v_node[1], 0):
            long_of_asc_node = 2.0 * pi - long_of_asc_node
        return long_of_asc_node


    @cached_property
    def argument_of_periapsis(self):
        """
        Argument of periapsis (ω).
        """
        argument_of_periapsis = arccos(
            dot(self.v_node, self.v_eccentricity)
            /
            (self.node*self.eccentricity)
        )
        if self.lt(self.v_eccentricity[2], 0):
            argument_of_periapsis = 2.0 * pi - argument_of_periapsis
        return argument_of_periapsis


    @cached_property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).
        """
        if not self.is_parabolic:
            # elliptical and hyperbolic
            zeta = (self.mag_velocity**2/2) - self.gravitational_parameter/self.mag_position
            return -self.gravitational_parameter/(2*zeta)
        else:
            return Inf


    @cached_property
    def period(self):
        """
        The orbital period in seconds. (P)
        """
        # https://en.wikipedia.org/wiki/Orbital_period#Small_body_orbiting_a_central_body
        if self.is_elliptical:
            return 2.0 * pi * sqrt(
                self.semi_major_axis**3.0 / self.gravitational_parameter
            )
        else:
            return None


    @cached_property
    def mean_anomaly(self):
        """
        Mean anomaly. (M)
        """
        if self.is_circular:
            return self.eccentric_anomaly
        elif self.is_elliptical:
            return self.eccentric_anomaly - (
                self.eccentricity * sin(self.eccentric_anomaly)
            )
        elif self.is_parabolic:
            return self.eccentric_anomaly + self.eccentric_anomaly**3.0/3.0
        elif self.is_hyperbolic:
            return self.eccentricity * sinh(self.eccentric_anomaly) - self.eccentric_anomaly


    @cached_property
    def periapsis_distance(self):
        """
        Distance from the periapsis at the current moment.
        """
        # http://www.bogan.ca/orbits/kepler/orbteqtn.html
        # http://scienceworld.wolfram.com/physics/SemilatusRectum.html
        if self.is_circular:
            return self.semi_major_axis
        elif self.is_parabolic:
            return self.angular_momentum**2.0 / self.gravitational_parameter * .5
        else:
            return self.semi_major_axis * (1.0 - self.eccentricity)


    @cached_property
    def semi_latus_rectum(self):
        """
        Return the semi-latus rectum for the current orbit (p).
        """
        if not self.is_parabolic:
            return self.semi_major_axis * (1 - self.eccentricity**2)
        else:
            return self.angular_momentum**2/self.gravitational_parameter
    
    #
    # Math helper functions
    #


    @classmethod
    def eq(cls, a, b):
        """
        Floating point equality for tests
        """
        return allclose([a], [b], cls.ACCURACY, cls.ACCURACY)


    @classmethod
    def lt(cls, a, b):
        """
        Floating point less-than for tests
        """
        if allclose([a], [b], cls.ACCURACY):
            return False # equal
        else:
            return a < b


    @classmethod
    def gt(cls, a, b):
        """
        Floating point greater-than for tests
        """
        if allclose([a], [b], cls.ACCURACY):
            return False # equal
        else:
            return a > b

    #
    # Coordinate bullshit
    #

    @staticmethod
    def rotate(vector, O, i, w):
        """
        Peform a rotation on *vector* using the angles *Ω*, *i*, and *ω*.
        """
        vector = vector[:, newaxis]
        res = (Rz(-O) * Rx(-i) * Rz(-w)).dot(vector)
        return squeeze(asarray(res))


    @classmethod
    def reverse(cls,
            semi_latus_rectum,       # p
            eccentricity,            # e
            inclination,             # i
            long_of_asc_node,        # Ω
            argument_of_periapsis,   # ω
            true_anomaly,            # ν
            gravitational_parameter, # μ
        ):

        # based on http://de.mathworks.com/matlabcentral/fileexchange/35455-convert-keplerian-orbital-elements-to-a-state-vector/content/orb2rv.m

        long_of_periapsis = argument_of_periapsis + long_of_asc_node # ϖ
        true_longitude = true_anomaly + long_of_periapsis            # l
        argument_of_latitude = true_anomaly + argument_of_periapsis  # u

        circular = cls.eq(eccentricity, 0)
        flat = cls.eq(inclination % pi, 0)

        if circular and flat:
            argument_of_periapsis = 0
            long_of_asc_node = 0
            true_anomaly = true_longitude

        if circular and not flat:
            argument_of_periapsis = 0
            true_anomaly = argument_of_latitude

        if flat and not circular:
            long_of_asc_node = 0
            argument_of_periapsis = long_of_periapsis

        pos_perifocal = array([
            semi_latus_rectum * cos(true_anomaly) / (1 + eccentricity * cos(true_anomaly)),
            semi_latus_rectum * sin(true_anomaly) / (1 + eccentricity * cos(true_anomaly)),
            0,
        ])

        vel_perifocal = array([
           -sqrt(gravitational_parameter/semi_latus_rectum) * sin(true_anomaly),
            sqrt(gravitational_parameter/semi_latus_rectum) * (eccentricity + cos(true_anomaly)),
            0
        ])

        # Rotate that shit
        v_position = cls.rotate(pos_perifocal, long_of_asc_node, inclination, argument_of_periapsis)
        v_velocity = cls.rotate(vel_perifocal, long_of_asc_node, inclination, argument_of_periapsis)

        return v_position, v_velocity

    #
    # Things the game needs
    #

    def step(self, seconds, update = True):
        """
        Update the position of the craft based on the number of seconds that
        have passed.
        """
        if self.is_parabolic:
            # https://en.wikipedia.org/wiki/Parabolic_trajectory#Barker.27s_equation
            A = (3/2) * sqrt(
                self.gravitational_parameter / (2.0 * self.periapsis_distance**3.0)
            ) * seconds
            B = cbrt(
                A + sqrt(
                    A**2.0 + 1.0
                )
            )
            true_anomaly = 2.0 * arctan(B - 1.0/B)

        elif self.is_hyperbolic:
            # Fundamentals of Orbital Mechanics for Engineering Students.
            # 3.34 (p.174)
            mean_anomaly = (
                self.gravitational_parameter**2.0/self.angular_momentum
            ) * (
                self.eccentricity**2.0 - 1.0
            )**(3.0/2.0) * seconds
            mean_anomaly %= self._2PI
            # 3.45 (p. 178)
            eccentric_anomaly = keplerh(mean_anomaly, self.eccentricity, self.ACCURACY)
            # 3.41b (p 177)
            true_anomaly = arccos(
                (cosh(eccentric_anomaly) - self.eccentricity)
                /
                (1.0 - self.eccentricity * cosh(eccentric_anomaly))
            )

        else:
            # https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
            # M
            mean_anomaly = self.mean_anomaly + seconds * sqrt(self.gravitational_parameter/self.semi_major_axis**3.0)
            mean_anomaly %= self._2PI
            # E
            eccentric_anomaly = kepler(mean_anomaly, self.eccentricity, self.ACCURACY)
            # theta
            arg1 = sqrt(1.0 + self.eccentricity) * sin(eccentric_anomaly/2.0)
            arg2 = sqrt(1.0 - self.eccentricity) * cos(eccentric_anomaly/2.0)
            true_anomaly = 2.0 * arctan2(arg1, arg2)


        v_position, v_velocity = self.reverse(
            self.semi_latus_rectum,
            self.eccentricity,
            self.inclination,
            self.long_of_asc_node,
            self.argument_of_periapsis,
            true_anomaly,
            self.gravitational_parameter,
        )

        if update:
            self.v_position, self.v_velocity = v_position, v_velocity
            self._property_cache = {}

        return v_position, v_velocity

    #
    # Get orbit plot
    #

    def get_plot(self, n):
        """
        Get *n* points (position vectors relative to the orbit's frame of
        reference) for how to plot this orbit.
        """
        if not self.is_elliptical:
            m = floor(n/2)
            if m*2 < n:
                n = m
                m += 1
            else:
                n = m
            step_size = 500
            backward = [0 - step_size * i for i in range(1, m + 1)]
            forwards = [step_size * i for i in range(n)]
            steps = backward[::-1] + forwards
            for step in steps:
                position, _ = self.step(step, update = False)
                yield tuple(position)
        else:
            period = self.period
            step_size = period/n
            for step in range(n):
                position, _ = self.step(step_size * step, update = False)
                yield tuple(position)


    #
    # Miscellaneous helper properties for humans
    #

    @cached_property
    def is_circular(self):
        return self.eq(self.eccentricity, 0)

    @cached_property
    def is_parabolic(self):
        return self.eq(self.eccentricity, self.ONE)

    @cached_property
    def is_hyperbolic(self):
        # Check parabolic for the floating point check
        return not self.is_parabolic and self.eccentricity > self.ONE

    @cached_property
    def is_elliptical(self):
        # Check parabolic for the floating point check
        return not self.is_parabolic and self.eccentricity < self.ONE
