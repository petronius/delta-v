"""
Two-body Keplarian orbit modelling.
"""

from __future__ import print_function

from math import floor
from numpy import (
    # objects and modules
    array,
    matrix,
    linalg,
    asarray,
    squeeze,
    float128,
    allclose,
    seterr,
    # values and arithmatic functions
    pi,
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
import textwrap

from .helpers import kepler, keplerh, Rx, Rz, Ry

seterr(all="raise")

cbrt = lambda x: x**(float128("1.0")/float128("3.0"))


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

    """

    # FIXME: Calculation of individual elements should be cached until one of
    # the simulation methods is called.

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

    # unit vectors for axes x, y, z
    I = array([1.0, 0.0, 0.0])
    J = array([0.0, 1.0, 0.0])
    K = array([0.0, 0.0, 1.0])

    # Used for comparisons, because of floating point rounding error
    ONE = float128("1.0")
    ACCURACY = float128("1e-12")

    # fixme: a bunch of these assume ints where they should be vectors

    def __init__(self, parent, satellite, v_position, v_velocity):
        self.parent = parent
        self.satellite = satellite
        self.v_position = array(v_position)
        self.v_velocity = array(v_velocity)


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

    @property
    def gravitational_parameter(self):
        """
        Gravitational parameter (2-body)
        """
        return self.G * self.parent.mass

    @property
    def v_angular_momentum(self):
        """
        Angular momentum vector, in m**2/s
        """
        return cross(self.v_position, self.v_velocity)

    @property
    def v_eccentricity(self):
        """
        Eccentricity vector.
        """
        return (
            cross(self.v_velocity, self.v_angular_momentum) / self.gravitational_parameter
            -
            self.v_position/self.mag(self.v_position)
        )

    @property
    def v_node(self):
        """
        Node (of ascension) vector (m**2 / s)
        """
        return cross(self.K.T, self.v_angular_momentum)

    @property
    def true_anomaly(self):
        """
        True anomaly (angle from the focus at the barycentre of the orbit, ν).
        """
        res = (
            inner(self.v_eccentricity, self.v_position)
            /
            (self.eccentricity*self.mag(self.v_position))
        )
        true_anomaly = arccos(res)
        if self.lt(dot(self.v_position, self.v_velocity), 0.0):
            true_anomaly = 2.0 * pi - true_anomaly
        return true_anomaly

    @property
    def inclination(self):
        """
        Inclination of the orbit (i).
        """
        return arccos(self.v_angular_momentum[2]/self.mag(self.v_angular_momentum))

    @property
    def eccentricity(self):
        """
        The eccentricity of the orbital ellipse.
        """
        e = float128(self.mag(self.v_eccentricity))
        if self.eq(e, 0):
            return 0
        else:
            return e

    @property
    def eccentric_anomaly(self):
        return self._eccentric_anomaly(self.true_anomaly, self.eccentricity)

    def _eccentric_anomaly(self, true_anomaly, eccentricity):
        """
        Like the true anomaly, but measured about the center of the ellipse.

        (E for elliptical orbits. D, F for hyperbolic and parabolic.)
        """
        if self.is_circular:
            return true_anomaly
        elif self.is_elliptical:
            return 2.0 * arctan(
                tan(true_anomaly/2.0)
                /
                sqrt((1.0 + eccentricity) / (1 - eccentricity))
            )
        elif self.is_parabolic:
            # "D"
            return tan(true_anomaly/2.0)
        elif self.is_hyperbolic:
            # F
            return arccosh(
                (eccentricity + cos(true_anomaly))
                /
                (1.0 + eccentricity * cos(true_anomaly))
            )
        else:
            raise Exception("Are you in the right spacetime?")

    @property
    def long_of_asc_node(self):
        """
        Longitude of the ascending node (Ω).
        """
        long_of_asc_node = arccos(self.v_node[0]/self.mag(self.v_node))
        if self.lt(self.v_node[1], 0):
            long_of_asc_node = 2.0 * pi - long_of_asc_node
        return long_of_asc_node

    @property
    def argument_of_periapsis(self):
        """
        Argument of periapsis (ω). (Angle to ray from the barycenter to the node
        of ascension, relative to the reference direction.)
        """
        argument_of_periapsis = arccos(
            inner(self.v_node, self.v_eccentricity)
            /
            (self.mag(self.v_node)*self.eccentricity)
        )
        if self.lt(self.v_eccentricity[2], 0):
            argument_of_periapsis = 2.0 * pi - argument_of_periapsis
        return argument_of_periapsis

    @property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).

        Units are probably whatever units the original positional vector is in?
        """
        return 1.0 / ((2.0/self.mag(self.v_position)) - (self.mag(self.v_velocity)**2.0/self.gravitational_parameter))

    # @property
    # def specific_mechanical_energy(self):
    #     """
    #     What it says on the tin
    #     """
    #     return (self.mag(self.v_velocity)/2) - (self.gravitational_parameter/self.mag(self.v_position))

    @property
    def period(self):
        """
        The orbital period in seconds.

        https://en.wikipedia.org/wiki/Orbital_period#Small_body_orbiting_a_central_body
        """
        if self.is_elliptical:
            return 2.0 * pi * sqrt(
                self.semi_major_axis**3.0 / self.gravitational_parameter
            )
        else:
            return None

    @property
    def mean_anomaly(self):
        return self._mean_anomaly(self.eccentric_anomaly, self.eccentricity)

    def _mean_anomaly(self, eccentric_anomaly, eccentricity):
        """
        Mean anomaly.
        """
        if self.is_circular:
            return eccentric_anomaly
        elif self.is_elliptical:
            return eccentric_anomaly - (eccentricity * sin(eccentric_anomaly))
        elif self.is_parabolic:
            return eccentric_anomaly + eccentric_anomaly**3.0/3.0
        elif self.is_hyperbolic:
            return eccentricity * sinh(eccentric_anomaly) - eccentric_anomaly


    @property
    def periapsis_distance(self):
        # http://www.bogan.ca/orbits/kepler/orbteqtn.html
        # http://scienceworld.wolfram.com/physics/SemilatusRectum.html
        if self.is_circular:
            return self.semi_major_axis
        elif self.is_parabolic:
            return self.mag(self.v_angular_momentum)**2.0 / self.gravitational_parameter * (1.0/2.0)
        else:
            return self.semi_major_axis * (1.0 - self.eccentricity)

    @property
    def semi_latus_rectum(self):
        """
        Return the semi-latus rectum for the current orbit (p). (Units?)
        """
        # http://scienceworld.wolfram.com/physics/SemilatusRectum.html
        if self.is_elliptical:
            return self.semi_major_axis * (1.0 - self.eccentricity**2.0)
        elif self.is_parabolic:
            return 2 * self.periapsis_distance
        else:
            return self.semi_major_axis * (self.eccentricity**2 - 1)
    

    @property
    def time_from_periapsis(self):
        """
        Pretty much just here for doing calculations on parabolic and hyperbolic
        orbits.
        """
        if self.is_elliptical:
            return self.mean_anomaly * (self.period/(2.0*pi))
        elif self.is_parabolic:
            return sqrt(
                2.0 * (self.periapsis_distance**3.0/self.gravitational_parameter)
            ) * self.mean_anomaly
        elif self.is_hyperbolic:
            return sqrt(
                (-self.semi_major_axis)**3.0
                /
                self.gravitational_parameter
            ) * self.mean_anomaly
        else:
            raise Exception("Are you in the right spacetime?")
    

    #
    # Math helper functions
    #

    @staticmethod
    def mag(vector):
        """
        Calculate the magnitude (aka absolute value) of a vector.
        """
        return linalg.norm(vector)


    @staticmethod
    def normalize(value, lower, upper):
        """
        Normalize *value* to ``[lower, upper)``.
        """
        if value < lower or value > upper:
            value %= upper
        if value < lower:
            value += upper
        return value

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
            return False
        else:
            return a < b

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
            semi_major_axis,
            eccentricity,
            argument_of_periapsis,
            long_of_asc_node,
            inclination,
            mean_anomaly,
            gravitational_parameter,
        ):
        """
        Return state vectors (v_position, v_velocity) for the given Keplarian
        elements
        """

        eccentric_anomaly = kepler(mean_anomaly, eccentricity, cls.ACCURACY)

        arg1 = sqrt(1.0 + eccentricity) * sin(eccentric_anomaly/2.0)
        arg2 = sqrt(1.0 - eccentricity) * cos(eccentric_anomaly/2.0)
        true_anomaly = 2.0 * arctan2(arg1, arg2)

        distance = semi_major_axis * (1.0 - eccentricity * cos(eccentric_anomaly))

        v_position = distance * array([
            cos(true_anomaly),
            sin(true_anomaly),
            0.0,
        ])

        v_position = cls.rotate(v_position, long_of_asc_node, inclination, argument_of_periapsis)

        v_velocity = (
            sqrt(gravitational_parameter * semi_major_axis)
            /
            distance
        ) * array([
            -sin(eccentric_anomaly),
            sqrt(1.0 - eccentricity**2.0) * cos(eccentric_anomaly),
            0.0,
        ])

        v_velocity = cls.rotate(v_velocity, long_of_asc_node, inclination, argument_of_periapsis)


        return v_position, v_velocity

    #
    # Things the game needs
    #

    def step(self, seconds, update = True):
        """
        Update the position of the craft based on the number of seconds that
        have passed.
        """
        if self.is_elliptical:
            # Basic procedure from https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
            mean_anomaly = self.mean_anomaly + seconds * sqrt(self.gravitational_parameter/self.semi_major_axis**3.0)
            mean_anomaly = self.normalize(mean_anomaly, 0.0, 2.0*pi)

            v_position, v_velocity = self.reverse(
                self.semi_major_axis,
                self.eccentricity,
                self.argument_of_periapsis,
                self.long_of_asc_node,
                self.inclination,
                mean_anomaly,
                self.gravitational_parameter,
            )

        else:
            # For hyperbolic and parabolic orbits this is a little more 
            # complicated. The steps are as follows:
            #
            # 1. From the time from periapsis (T) we have to derive the new true
            #    anomaly (nu) using Barker's equations.
            # 2. From the new true anomaly, we can then re-derive the mean 
            #    anomaly for the new state (M).
            # 3. With the new mean anomaly, we can reverse the elements into
            #    updated state vectors.
            #
            # FIXME: do we need to update the velocity vector?
            #
            # https://en.wikipedia.org/wiki/Parabolic_trajectory#Barker.27s_equation
            current_time = self.time_from_periapsis + seconds
            if abs(current_time) < self.ACCURACY:
                current_time = 0

            if self.is_parabolic:

                A = (3/2) * sqrt(
                    self.gravitational_parameter / (2.0 * self.periapsis_distance**3.0)
                ) * current_time

                B = cbrt(
                    A + sqrt(
                        A**2.0 + 1.0
                    )
                )
                true_anomaly = 2.0 * arctan(B - 1.0/B)
                if current_time:
                    distance = (2.0 * self.periapsis_distance) / (1.0 + cos(true_anomaly))
                else:
                    distance = self.periapsis_distance

                angle_of_velocity = true_anomaly/2.0
                velocity = sqrt(self.gravitational_parameter * (2.0/distance))

            elif self.is_hyperbolic:

                mean_anomaly = (self.gravitational_parameter**2.0/self.mag(self.v_velocity)) * (self.eccentricity**2.0 - 1.0)**(3.0/2.0) * current_time
                mean_anomaly = self.normalize(mean_anomaly, 0.0, 2.0*pi)

                eccentric_anomaly = keplerh(mean_anomaly, self.eccentricity, self.ACCURACY)
                true_anomaly = arccos(
                    (cosh(eccentric_anomaly) - self.eccentricity)
                    /
                    (1.0 - self.eccentricity * cosh(eccentric_anomaly))
                )
                if current_time:
                    distance = self.semi_latus_rectum/(1.0 + self.eccentricity * cos(true_anomaly))
                else:
                    distance = self.periapsis_distance

                angle_of_velocity = arctan(
                    (self.eccentricity * sin(true_anomaly))
                    /
                    (1.0 + self.eccentricity * cos(true_anomaly))
                )
                velocity = sqrt(self.gravitational_parameter * (2.0/distance - 1.0/self.semi_major_axis))

            aov_prime = true_anomaly + (pi - angle_of_velocity)
            v_velocity = array([
                velocity,
                0.0,
                0.0,
            ])[:, newaxis]
            v_velocity = squeeze(asarray(Rx(-aov_prime) * v_velocity))

            v_position = array([
                distance,
                0.0,
                0.0,
            ])[:, newaxis]
            v_position = squeeze(asarray(Rx(true_anomaly) * v_position))

            v_velocity = self.rotate(v_velocity, self.long_of_asc_node, self.inclination, self.argument_of_periapsis)
            v_position = self.rotate(v_position, self.long_of_asc_node, self.inclination, self.argument_of_periapsis)

        if update:
            self.v_position, self.v_velocity = v_position, v_velocity

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
            step_size = 120
            out = []
            # backward
            for step in range(n):
                position, _ = self.step(-step_size * step, update = False)
                out.append(position)
            # return those
            for i in out[::-1]:
                yield tuple(i)
            # forward
            for step in range(m):
                position, _ = self.step(step_size * step, update = False)
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

    @property
    def is_circular(self):
        return self.eq(self.eccentricity, 0)

    @property
    def is_parabolic(self):
        return self.eq(self.eccentricity, self.ONE)

    @property
    def is_hyperbolic(self):
        # Check parabolic for the floating point check
        return not self.is_parabolic and self.eccentricity > self.ONE

    @property
    def is_elliptical(self):
        # Check parabolic for the floating point check
        return not self.is_parabolic and self.eccentricity < self.ONE

