"""
Two-body Keplarian orbit modelling.
"""

from __future__ import print_function


from numpy import (
    # objects and modules
    array,
    matrix,
    linalg,
    asarray,
    squeeze,
    # values and arithmatic functions
    pi,
    sqrt,
    cos, arccos,
    sin, arcsin,
    tan, arctan, arctan2,
    # matrix functions and helpers
    dot,
    cross,
    newaxis,
)
import textwrap

from .helpers import kepler, Rx, Rz, Ry


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
    
        http://space.stackexchange.com/questions/1904/how-to-programmatically-calculate-orbital-elements-using-position-velocity-vecto
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
        self.v_position = v_position
        self.v_velocity = v_velocity


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
        return self.G * (self.parent.mass) # - self.satellite.mass)

    @property
    def v_angular_momentum(self):
        """
        Angular momentum vector, in m**2/s
        """
        return cross(self.v_position, self.v_velocity)

    @property
    def v_node(self):
        """
        Node (of ascension) vector (m**2 / s)
        """
        return cross(self.K, self.v_angular_momentum)

    @property
    def v_eccentricity(self):
        """
        Eccentricity vector. The e orbital parameter is derived as the magnitude
        of this vector, so if ``o`` is an orbit object:

        >>> e = o.mag(o.v_eccentricity)
        """
        return (cross(self.v_velocity, self.v_angular_momentum) / self.gravitational_parameter) - \
               (self.v_position/self.mag(self.v_position))

    @property
    def eccentricity(self):
        """
        The eccentricity of the orbital ellipse.
        """
        return self.mag(self.v_eccentricity)

    @property
    def specific_mechanical_energy(self):
        """
        What it says on the tin
        """
        return (self.mag(self.v_velocity)/2) - (self.gravitational_parameter/self.mag(self.v_position))

    @property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).

        Units are probably whatever units the original positional vector is in?
        """
        return 1 / ((2/self.mag(self.v_position)) - (self.mag(self.v_velocity)**2/self.gravitational_parameter))

    @property
    def period(self):
        """
        The orbital period in seconds.

        https://en.wikipedia.org/wiki/Orbital_period#Small_body_orbiting_a_central_body
        """
        if self.semi_major_axis < 1:
            raise OrbitCalculationException("Hyperbolic and parabolic orbits don't have a period!")
        return 2 * pi * sqrt(
            self.semi_major_axis**3 / self.gravitational_parameter
        )

    @property
    def inclination(self):
        """
        Inclination of the orbit (i).
        """
        return arccos(self.v_angular_momentum[2]/self.mag(self.v_angular_momentum))

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
        argument_of_periapsis = arccos(dot(self.v_node, self.v_eccentricity)/(self.mag(self.v_node)*self.eccentricity))
        if self.v_eccentricity[2] < 0:
            argument_of_periapsis = 2 * pi - argument_of_periapsis
        return argument_of_periapsis

    @property
    def true_anomaly(self):
        """
        True anomaly (angle from the focus at the barycentre of the orbit, ν).
        """
        true_anomaly = arccos(dot(self.v_eccentricity, self.v_position)/(self.eccentricity*self.mag(self.v_position)))
        if dot(self.v_position, self.v_velocity) < 0:
            true_anomaly = 2 * pi - true_anomaly
        return true_anomaly

    @property
    def eccentric_anomaly(self):
        """
        Like the true anomaly, but measured about the center of the ellipse.
        """
        return 2 * arctan(
            tan(self.true_anomaly/2)
            /
            sqrt((1 + self.eccentricity) / (1 - self.eccentricity))
        )

    @property
    def mean_anomaly(self):
        """
        Mean anomaly.
        """
        return self.eccentric_anomaly - self.eccentricity * sin(self.eccentric_anomaly)
    

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
        Peform a Euler rotation on *vector* using the angles *Ω*, *i*, and *ω*
        (ie, the Euler angles α, β, γ).
        """
        #
        # FIXME: This method doesn't work. Rotating by the inclination (ie,
        #        doing ``dot(Rx(-1*i), vector)``) works fine, but adding in the
        #        other terms fails.
        #
        #        I am currently completely stumped as to why.
        #
        # https://en.wikipedia.org/wiki/Rotation_matrix
        # need a column vector here
        vector = vector[:, newaxis]
        R = Rz(-1*O) * Rx(-1*i) * Rz(-1*w) # this produces weird results for some reason
        #R = Rx(-1*i)
        result = dot(R, vector)
        # transform back into expected format and return
        return squeeze(asarray(result))


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

    def step(self, seconds):
        """
        Update the position of the craft based on the number of seconds that
        have passed.
        """
        # Basic procedure from https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
        mean_anomaly = self.mean_anomaly + seconds * sqrt(self.gravitational_parameter/self.semi_major_axis**3)
        mean_anomaly = self.normalize(mean_anomaly, 0, 2*pi)
        
        # I don't feel like I lose out on anything for not writing a Newton-Raphson solver myself.
        eccentric_anomaly = kepler(mean_anomaly, self.eccentricity)

        arg1 = sqrt(1 + self.eccentricity) * sin(eccentric_anomaly/2)
        arg2 = sqrt(1 - self.eccentricity) * cos(eccentric_anomaly/2)
        true_anomaly = 2 * arctan2(arg1, arg2)

        distance = self.semi_major_axis * (1 - self.eccentricity * cos(eccentric_anomaly))

        v_position = distance * array([
            cos(true_anomaly),
            sin(true_anomaly),
            0,
        ])

        v_velocity = (sqrt(self.gravitational_parameter * self.semi_major_axis)/distance) * array([
            -1 * sin(eccentric_anomaly),
            sqrt(1-self.eccentricity**2) * cos(eccentric_anomaly),
            0,
        ])

        # Now we have to rotate these relative to the reference plane using the
        # Euler rotations
        #
        # Set self.v_position = v_position
        #     self.v_velocity = v_velocity
        #
        # to get orbit shapes without rotation.
        #
        self.v_position = self.rotate(v_position, self.long_of_asc_node, self.inclination, self.argument_of_periapsis)
        self.v_velocity = self.rotate(v_velocity, self.long_of_asc_node, self.inclination, self.argument_of_periapsis)


if __name__ == "__main__":


    class Body(object):
        def __init__(self, mass, radius):
            self.mass = mass
            self.radius = radius

    earth = Body(5.972e24, 1) # kg, m
    iss = Body(419600, 1) # kg, m
    o2_position = array([400000, 10, 10], dtype="float64") # meters
    o2_velocity = array([7660, 1, 1], dtype="float64") # m/s
    o = Orbit(earth, iss, o2_position, o2_velocity)
    print(o, o.v_position)
    o.step(200)
    print(o, o.v_position)
    o.step(200)
    print(o, o.v_position)
    o.step(200)
    print(o, o.v_position)
    o.step(200)
    print(o, o.v_position)