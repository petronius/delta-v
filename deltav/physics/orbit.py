"""
Two-body Keplarian orbit modelling.
"""

#TODO: https://en.wikipedia.org/wiki/Hill_sphere
# TODO: clear plot and is_* properties only during acceleration, not on every
#       position update
# TODO: move to just mpmath?
from functools import partial
from math import floor
from numpy import (
    float128,
    seterr,
    pi, Inf,
    sqrt,
    sign,
    floor,
    cos, cosh, arccosh,
    sin, sinh,
    tan, arctan,
    dot,
    log,
)
from numpy.linalg import norm
from numpy import array as _array
# not provided by numpy, for reasons which are opaque to me
from mpmath import cot

array = partial(_array, dtype=float128)

seterr(all="raise")


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
    """

    # The gravitational constant
    G = 6.674e-11

    # Used for comparisons, because of floating point rounding error
    ACCURACY = float128("1e-12")


    def __init__(self, parent, satellite, v_position, v_velocity):
        self.parent = parent
        self.satellite = satellite
        self.v_position = array(v_position)
        self.v_velocity = array(v_velocity)

        self.mag_position = norm(self.v_position)
        self.mag_velocity = norm(self.v_velocity)

        self.propery_cache = {}


    def accelerate(self, vector):
        self.v_velocity = array([
            self.v_velocity[0] + vector[0],
            self.v_velocity[1] + vector[1],
            self.v_velocity[2] + vector[2],
        ])
        del self.propery_cache["_plot"]

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
    def specific_mechanical_energy(self):
        """
        Specific mechanical energy of the orbit (ξ)
        """
        return (self.mag_velocity**2/2) - (self.gravitational_parameter / self.mag_position)


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
        if e < self.ACCURACY:
            return 0
        else:
            return e


    @cached_property
    def _alpha(self):
        """
        Used solely for calculation purposes.
        """
        alpha = -self.specific_mechanical_energy * 2.0/self.gravitational_parameter
        if abs(alpha) < self.ACCURACY:
            return 0
        return alpha

    @cached_property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).
        """
        if not self.is_parabolic:
            return 1/self._alpha
        else:
            return Inf


    @cached_property
    def period(self):
        """
        The orbital period in seconds. (P)
        """
        if self.is_elliptical:
            return 2.0 * pi * sqrt(
                abs(self.semi_major_axis)**3.0 / self.gravitational_parameter
            )
        else:
            return None


    @cached_property
    def semi_latus_rectum(self):
        """
        Return the semi-latus rectum for the current orbit (p).
        """
        return self.semi_major_axis * (1 - self.eccentricity**2)
   
    def _stumpff(self, psi):
        """
        Find the roots for the Stumpff equations (c2, c3) for a given value of 
        ψ.

        This is just for performing the integration in the "step" method.
        """
        if psi > self.ACCURACY:
            sq_psi = sqrt(psi)
            c2 = (1.0 - cos(sq_psi)) / psi
            c3 = (sq_psi - sin(sq_psi)) / sq_psi**3
        elif psi < 0 and abs(psi) > self.ACCURACY: # -ψ
            sq_psi = sqrt(-psi)
            c2 = (1.0 - cosh(sq_psi)) / psi
            c3 = (sinh(sq_psi) - sq_psi) / sqrt(-psi**3)
        else:
            # Constants as given in the original source code.
            c2 = 0.5
            c3 = 1.0/6.0
        return c2, c3

    #
    # Things the game needs
    #

    def step(self, delta_seconds, update = True):
        """
        Update the position of the craft based on the number of seconds that
        have passed.
        """
        if abs(delta_seconds) < self.ACCURACY:
            return self.v_position, self.v_velocity
        #
        # Determine a new position and velocity, given a delta-t in seconds,
        # using the universal variable formulation.
        #
        # This routine is based on the "kepler" function from the as2body.cpp
        # implementation available here: https://celestrak.com/software/vallado-sw.asp
        # and some reference to the 2nd edition of the book (§2.2 up to p. 101).
        #

        _dot_rv = dot(self.v_position, self.v_velocity) # convenience variable

        if self.is_elliptical: # fixme, these should use cached methods/values
            
            # FIXME: should floor out delta_seconds vs period

            chi = sqrt(self.gravitational_parameter) * delta_seconds * self._alpha

            if abs(self._alpha) - 1 < self.ACCURACY:
                # Fuzz the guess. This number taken from the source code. But if
                # the initial value is too close, then (so I am told), it will
                # not converge in the integration step.
                chi *= 0.97


        elif self.is_parabolic:

            _s = (
                (pi/2) - arctan(
                    delta_seconds * 3.0 * sqrt(
                        self.gravitational_parameter / self.semi_latus_rectum**3
                    )
                )
            ) / 2
            _w = arctan(tan(_s)**(1.0/3.0))

            chi = sqrt(self.semi_latus_rectum) * (2.0 * cot(2.0 * _w))
            # mpmath and numpy don't always play nicely together
            chi = float128(str(chi))

        elif self.is_hyperbolic: # hyperbolic

            _num = (-2.0 * self.gravitational_parameter * delta_seconds * self._alpha) / (
                _dot_rv + sign(delta_seconds) * sqrt(-self.gravitational_parameter * self.semi_major_axis) *
                (1 - self.mag_position * self._alpha)
            )

            chi = sign(delta_seconds) * sqrt(-self.semi_major_axis) * log(_num)

        else:
            raise Exception("Wrong spacetime")

        iterations = 0
        print("-"*80, self._alpha)
        while iterations < 100:

            print(chi)

            iterations += 1

            psi = chi**2 * self._alpha # greek alphabet soup

            c2, c3 = self._stumpff(psi)

            _r = chi**2 * c2 +  \
                (_dot_rv/sqrt(self.gravitational_parameter)) * chi * (1 - psi*c3) + \
                self.mag_position * (1 - psi*c2)

            chi_ = chi + \
                (
                    sqrt(self.gravitational_parameter) * delta_seconds -
                    chi **3 * c3 -
                    _dot_rv/sqrt(self.gravitational_parameter) * chi**2 * c2 -
                    self.mag_position * chi * (1.0 - psi*c3)
                ) / _r

            # TODO: adjustments for circular orbits or large (> 2pi * sqrt(a))
            # values of chi_ may cause problems. See original source for fix.

            # Reassign for next iteration
            _chi = chi
            chi = chi_
            
            print(">> ", abs(chi - _chi), chi > 2*pi*sqrt(self.semi_major_axis))

            if abs(chi - _chi) < self.ACCURACY:
                break

        if iterations > 99:
            s = delta_seconds/10.0
            for _ in range(10):
                p, v = self.step(s, update = update)
            return p, v

        # At long last, we calculate the new position and velocity

        f = 1.0 - (chi**2 * c2 / self.mag_position)
        g = delta_seconds - chi**3 * c3/sqrt(self.gravitational_parameter)

        v_position = array([
            (f * self.v_position[i] + g * self.v_velocity[i]) for i in range(3)
        ])

        mag_position = norm(v_position)
        g_dot = 1.0 - (chi**2 * c2/mag_position)
        f_dot = (sqrt(self.gravitational_parameter) * chi / (self.mag_position * mag_position)) * (psi * c3 - 1.0)

        v_velocity = array([
            (f_dot * self.v_position[i] + g_dot * self.v_velocity[i]) for i in range(3)
        ])
        
        #assert f * g_dot - f_dot * g - 1 < self.ACCURACY

        if update:
            self.v_position, self.v_velocity = v_position, v_velocity
            self.propery_cache = {}

        return v_position, v_velocity

    #
    # Get orbit plot. TODO: only plot this once, not on every draw frame.
    #

    def get_plot(self, n):
        """
        Get *n* points (position vectors relative to the orbit's frame of
        reference) for how to plot this orbit.
        """
        if not self.is_elliptical:
            m = int(floor(n/2))
            if m*2 < n:
                n = m
                m += 1
            else:
                n = m
            step_size = 30
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
    def is_parabolic(self):
        return abs(self._alpha) < self.ACCURACY

    @cached_property
    def is_hyperbolic(self):
        return self._alpha < 0 and not self.is_parabolic

    @cached_property
    def is_elliptical(self):
        return self._alpha > 0 and not self.is_parabolic
