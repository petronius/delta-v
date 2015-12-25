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
    # values and arithmatic functions
    pi,
    sqrt,
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

from .helpers import kepler, Rx, Rz, Ry

cbrt = lambda x: x**(1/3.0)


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
    I = array([1, 0, 0])
    J = array([0, 1, 0])
    K = array([0, 0, 1])

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
            self.mag(self.v_eccentricity),
            self.inclination,
            self.long_of_asc_node,
            self.argument_of_periapsis,
            self.true_anomaly,
        )

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
        # fixme: not sure if correct
        true_anomaly = arccos(
            inner(self.v_eccentricity, self.v_position)
            /
            (self.eccentricity*self.mag(self.v_position))
        )
        if dot(self.v_position, self.v_velocity) < 0:
            true_anomaly = 2 * pi - true_anomaly
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
        return self.mag(self.v_eccentricity)

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
            return 2 * arctan(
                tan(true_anomaly/2)
                /
                sqrt((1 + eccentricity) / (1 - eccentricity))
            )
        elif self.is_parabolic:
            # "D"
            return tan(true_anomaly/2)
        elif self.is_hyperbolic:
            # F
            return arccosh(
                (eccentricity + cos(true_anomaly))
                /
                (1 + eccentricity * cos(true_anomaly))
            )
        else:
            raise Exception("Are you in the right spacetime?")

    @property
    def long_of_asc_node(self):
        """
        Longitude of the ascending node (Ω).
        """
        long_of_asc_node = arccos(self.v_node[0]/self.mag(self.v_node))
        if self.v_node[1] < 0:
            long_of_asc_node = 2 * pi - long_of_asc_node
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
            (self.mag(self.v_node)*self.mag(self.v_eccentricity))
        )
        if self.v_eccentricity[2] < 0:
            argument_of_periapsis = 2 * pi - argument_of_periapsis
        return argument_of_periapsis

    @property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).

        Units are probably whatever units the original positional vector is in?
        """
        return 1 / ((2/self.mag(self.v_position)) - (self.mag(self.v_velocity)**2/self.gravitational_parameter))

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
            return 2 * pi * sqrt(
                self.semi_major_axis**3 / self.gravitational_parameter
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
            return eccentric_anomaly + eccentric_anomaly**3/3
        elif self.is_hyperbolic:
            return eccentricity * sinh(eccentric_anomaly) - eccentric_anomaly


    @property
    def periapsis_distance(self):
        # http://www.bogan.ca/orbits/kepler/orbteqtn.html
        # http://scienceworld.wolfram.com/physics/SemilatusRectum.html
        if self.is_circular:
            return self.semi_major_axis
        elif self.is_parabolic:
            return self.mag(self.v_angular_momentum)**2 / (2 * self.gravitational_parameter)
        else:
            return self.semi_major_axis * (1 - self.eccentricity)

    @property
    def semi_latus_rectum(self):
        """
        Return the semi-latus rectum for the current orbit (p). (Units?)
        """
        # http://scienceworld.wolfram.com/physics/SemilatusRectum.html
        if self.eccentricity < 1:
            return self.semi_major_axis * (1 - self.eccentricity**2)
        elif self.eccentricity == 1:
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
            return self.mean_anomaly * (self.period/(2*pi))
        elif self.is_parabolic:
            return sqrt(
                2 * (self.periapsis_distance**3/self.gravitational_parameter)
            ) * self.mean_anomaly
        elif self.is_hyperbolic:
            return sqrt(
                (-self.semi_major_axis)**3
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

        eccentric_anomaly = kepler(mean_anomaly, eccentricity)

        arg1 = sqrt(1 + eccentricity) * sin(eccentric_anomaly/2)
        arg2 = sqrt(1 - eccentricity) * cos(eccentric_anomaly/2)
        true_anomaly = 2 * arctan2(arg1, arg2)

        distance = semi_major_axis * (1 - eccentricity * cos(eccentric_anomaly))

        v_position = distance * array([
            cos(true_anomaly),
            sin(true_anomaly),
            0,
        ])

        v_position = cls.rotate(v_position, long_of_asc_node, inclination, argument_of_periapsis)

        v_velocity = (
            sqrt(gravitational_parameter * semi_major_axis)
            /
            distance
        ) * array([
            -sin(eccentric_anomaly),
            sqrt(1-eccentricity**2) * cos(eccentric_anomaly),
            0,
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
            mean_anomaly = self.mean_anomaly + seconds * sqrt(self.gravitational_parameter/self.semi_major_axis**3)
            mean_anomaly = self.normalize(mean_anomaly, 0, 2*pi)

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

            A = (3/2) * sqrt(
                self.gravitational_parameter / (2 * self.periapsis_distance**3)
            ) * current_time

            B = cbrt(
                A + sqrt(
                    A**2 + 1
                )
            )

            true_anomaly = 2 * arctan(B - 1/B)

            # Re-derive the eccentric, thence the mean anomaly.
            eccentric_anomaly = self._eccentric_anomaly(true_anomaly, self.eccentricity)
            mean_anomaly = self._mean_anomaly(eccentric_anomaly, self.eccentricity)


            distance = self.semi_major_axis * (1 - self.eccentricity * cos(eccentric_anomaly))

            v_position = distance * array([
                cos(true_anomaly),
                sin(true_anomaly),
                0,
            ])

            v_position = self.rotate(v_position, self.long_of_asc_node, self.inclination, self.argument_of_periapsis)

            v_velocity = self.v_velocity



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
            step_size = self.mean_anomaly * 10
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
        """
        Simple check to see if an orbit is circular, before you go playing
        with it.
        """
        return self.semi_major_axis == float("inf")

    @property
    def is_parabolic(self):
        # FIXME: this whole class needs to handle Parabolic orbits.
        return self.mag(self.v_eccentricity) == 1

    @property
    def is_hyperbolic(self):
        # FIXME: this whole class needs to handle Hyperbolic orbits.
        return self.mag(self.v_eccentricity) > 1

    @property
    def is_elliptical(self):
        if self.is_hyperbolic or self.is_parabolic:
            return False
        return True

