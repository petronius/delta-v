"""
Two-body Keplarian orbit modelling.
"""

from math import floor
from numpy import (
    isnan,
    cross,
    pi, Inf,
    sqrt,
    sign,
    floor,
    cos, arccos, cosh, arccosh,
    sin, sinh, arcsin,
    tan, arctan, arctan2,
    dot,
    log,
    newaxis, squeeze, asarray,
    seterr,
)
from numpy.linalg import norm

seterr(all="raise")

from deltav.physics.helpers import cached_property, _float, array, cbrt, cot, \
    kepler, Rz, Rx


class Orbit(object):
    """
    Set up an orbit from spacecraft position and speed data. The game here is
    essentially the same as determining a satellite's orbit from earth only
    from objserved information.

    For humans (programmers and players) this will provide an easy way to know
    where above a planet we are putting our ships, and then we can go on to
    solve for the important orbital information later.

    All calculations should assume radians, meters, and seconds, and return 
    the same.
    """

    # The gravitational constant
    G = _float("6.67408e-11")
    # Unit vector
    K = array([0, 0, 1])

    # Used for comparisons, because of floating point rounding error
    ACCURACY = _float("1e-12")


    def __init__(self, parent, satellite, v_position, v_velocity):
        """
        Initial position and velocity are used as a zero epoch, and all
        subsequent calculations are based on these. The values are re-set during
        acceleration, creating a new zero epoch. This avoids accumulated
        integration error over many interations.
        """
        self.parent = parent
        self.satellite = satellite
        self.v_position = array(v_position)
        self.v_velocity = array(v_velocity)

        self._property_cache = {}
        self._positions_cache = {}

        self.t_delta = _float("0")


    def accelerate(self, vec):
        """
        x = amount. positive in current direction of travel, negative in reverse

        TODO: acceleration off the plane of orbit

        This routine needs to:
        a) update velocity along a vector
        b) reset cached orbital params
        c) clear _plot cache
        d) reset the self.v_position and the self.t_delta to create a new
           zero epoch.
        """
        current_v_position, current_v_velocity = self.get_position()
        # set velocity
        self.v_velocity = current_v_velocity + vec
        # set new position
        self.v_position = current_v_position
        # reset epoch
        self.t_delta = 0
        # clear cache
        self._property_cache = {}
        self._positions_cache = {}



    def set_veloctiy(self, v_velocity):
        self.accelerate(0)
        self.v_velocity = v_velocity


    # Often used


    @cached_property
    def mag_position(self):
        return norm(self.v_position)

    @cached_property
    def mag_velocity(self):
        return norm(self.v_velocity)

    
    # Define properties for the classical orbital elements

    @cached_property
    def true_anomaly(self):
        v = arccos(dot(self.v_eccentricity, self.v_position)/(self.eccentricity * self.mag_position))
        if dot(self.v_position, self.v_velocity) < 0:
            v = 2*pi - v
        return v


    @cached_property
    def v_ascending_node(self):
        """
        Node vector for the ascending node. (n')
        """
        n = cross(self.K, self.v_angular_momentum)
        if norm(n) < self.ACCURACY: # FIXME: this doesn't seem like it should be necessary
            return array([1, 0, 0])
        return n


    @cached_property
    def long_of_ascending_node(self):
        """
        Longitude of the ascending node (Ω)
        """
        l = arccos(self.v_ascending_node[0]/norm(self.v_ascending_node))
        if abs(self.v_ascending_node[1]) < self.ACCURACY:
            l = 2*pi - l
        return l


    @cached_property
    def argument_of_periapsis(self):
        """
        Argument of periapsis (ω)
        """
        omega = arccos(
            dot(self.v_ascending_node, self.v_eccentricity)
            /
            (norm(self.v_ascending_node) * self.eccentricity)
        )
        if self.v_eccentricity[2] < 0:
            omega = 2*pi - omega
        return omega


    @cached_property
    def gravitational_parameter(self):
        """
        Standard gravitational parameter of the parent body. (μ)
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
    def eccentric_anomaly(self):
        """
        Eccentric anomaly (E)
        """
        e = arctan(
            (sqrt(1 - self.eccentricity**2) * sin(self.true_anomaly))
            /
            (self.eccentricity + cos(self.true_anomaly))
        )
        e %= 2*pi
        return e

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
        alpha = -self.specific_mechanical_energy * _float("2")/self.gravitational_parameter
        if abs(alpha) < self.ACCURACY:
            return 0
        return alpha


    @cached_property
    def semi_major_axis(self):
        """
        Calculate the semi-major axis (a).
        """
        if not self.is_parabolic:
            return _float("1")/self._alpha
        else:
            return Inf


    @cached_property
    def period(self):
        """
        The orbital period in seconds. (P)
        """
        if self.is_elliptical:
            return 2 * pi * sqrt(
                abs(self.semi_major_axis)**3 / self.gravitational_parameter
            )
        else:
            return None

    @cached_property
    def mean_motion(self):
        return 2*pi/self.period


    @cached_property
    def semi_latus_rectum(self):
        """
        Return the semi-latus rectum for the current orbit (p).
        """
        return self.semi_major_axis * (1 - self.eccentricity**2)


    @cached_property
    def inclination(self):
        return arccos(self.v_angular_momentum[2]/norm(self.v_angular_momentum))
   

    def _stumpff(self, psi):
        """
        Find the roots for the Stumpff equations (c2, c3) for a given value of 
        ψ.

        This is just for performing the integration in the "step" method.
        """
        if psi > self.ACCURACY:
            sq_psi = sqrt(psi)
            c2 = (1 - cos(sq_psi)) / psi
            c3 = (sq_psi - sin(sq_psi)) / sq_psi**3
        elif psi < 0 and abs(psi) > self.ACCURACY: # -ψ
            sq_psi = sqrt(-psi)
            c2 = (1 - cosh(sq_psi)) / psi
            c3 = (sinh(sq_psi) - sq_psi) / sqrt(-psi**3)
        else:
            # Constants as given in the original source code.
            c2 = _float("0.5") # avoid float casting
            c3 = _float("1.0")/_float("6.0") # avoid float casting
        return c2, c3

    #
    # Things the game needs
    #

    def step(self, delta_seconds):
        """
        Update the position of the craft based on the number of seconds that
        have passed.

        This just sets the epoch, and you should get the new position using
        self.get_position()
        """
        delta_seconds = _float(delta_seconds) # should be passed in as an integer
        self.t_delta += delta_seconds

    def get_position(self, delta_seconds = None):
        """
        Get the current position. If delta_seconds is passed, it will be used
        as the epoch for the calculation.

        Extremely large time deltas have the potential to slow down the
        Newton-Raphson integration (see the while loop). But at least in the
        case of spacecraft, we don't ever expect the time deltas to grow very
        large (because the zero epoch for them will be reset on each
        acceleration).
        """
        if delta_seconds is None:
            delta_seconds = self.t_delta

        # Only matters for elliptical orbits.
        if self.period is not None:
            delta_seconds = delta_seconds % self.period

        if delta_seconds in self._positions_cache:
            return self._positions_cache[delta_seconds]

        #
        # Determine a new position and velocity, given a delta-t in seconds,
        # using the universal variable formulation.
        #
        # This routine is based on the "kepler" function from the as2body.cpp
        # implementation available here: https://celestrak.com/software/vallado-sw.asp
        # and the 2nd edition of the book (§2.2 up to p. 101).
        #

        _dot_rv = dot(self.v_position, self.v_velocity) # convenience variable

        if self.is_elliptical:

            chi = sqrt(self.gravitational_parameter) * delta_seconds * self._alpha

            if abs(self._alpha) - 1 < self.ACCURACY:
                # Fuzz the guess. This number taken from the source code. But if
                # the initial value is too close, then (so I am told), it will
                # not converge in the integration step.
                chi *= _float("0.97")

        elif self.is_parabolic:

            _s = (
                (pi/2) - arctan(
                    delta_seconds * 3 * sqrt(
                        self.gravitational_parameter / self.semi_latus_rectum**3
                    )
                )
            ) / 2
            _w = arctan(tan(_s)**(_float("1")/_float("3")))
            chi = sqrt(self.semi_latus_rectum) * (2 * cot(2 * _w))

        elif self.is_hyperbolic: # hyperbolic

            _num = (-2 * self.gravitational_parameter * delta_seconds * self._alpha) / (
                _dot_rv + sign(delta_seconds) * sqrt(-self.gravitational_parameter * self.semi_major_axis) *
                (1 - self.mag_position * self._alpha)
            )

            if _num < self.ACCURACY:
                _num = self.ACCURACY

            chi = sign(delta_seconds) * sqrt(-self.semi_major_axis) * log(_num)

        else:
            raise Exception("Wrong spacetime")

        iterations = 0
        _chi = chi + _float("1") # placeholder value to make the first check pass
        while abs(chi - _chi) > self.ACCURACY:

            iterations += 1

            psi = chi**2 * self._alpha # greek alphabet soup

            c2, c3 = self._stumpff(psi)

            _r = chi**2 * c2 +  \
                (_dot_rv/sqrt(self.gravitational_parameter)) * chi * (1 - psi*c3) + \
                self.mag_position * (1 - psi*c2)

            chi_ = chi + \
                (
                    sqrt(self.gravitational_parameter) * delta_seconds -
                    chi**3 * c3 -
                    _dot_rv/sqrt(self.gravitational_parameter) * chi**2 * c2 -
                    self.mag_position * chi * (1 - psi*c3)
                ) / _r

            # TODO: adjustments for circular orbits or large (> 2pi * sqrt(a))
            # values of chi_ may cause problems. See original source for fix.

            # Reassign for next iteration
            _chi = chi
            chi = chi_

        if iterations == 0:
            psi = chi**2 * self._alpha
            c2, c3 = self._stumpff(psi)

        # At long last, we calculate the new position and velocity

        f = 1 - (chi**2 * c2 / self.mag_position)
        g = delta_seconds - chi**3 * c3/sqrt(self.gravitational_parameter)

        v_position = array([
            (f * self.v_position[i] + g * self.v_velocity[i]) for i in range(3)
        ])

        mag_position = norm(v_position)
        g_dot = 1 - (chi**2 * c2/mag_position)
        f_dot = (sqrt(self.gravitational_parameter) * chi / (self.mag_position * mag_position)) * (psi * c3 - 1)

        v_velocity = array([
            (f_dot * self.v_position[i] + g_dot * self.v_velocity[i]) for i in range(3)
        ])

        self._positions_cache[delta_seconds] = (v_position, v_velocity)

        return v_position, v_velocity


    def lambert_deltas(self, p1, v1, p2, v2, time, tm = 1):
        """
        Find the delta-vs needed to perform an intercept from the current orbit
        onto the target orbit, using the universal variable solution for
        Lambert's method.

        The second delta-v only matters for rendezvous, not for intercept.
        """
        # Vallado 7.6, algo 55
        # see also method from Sharaf, Saad, and Nouh, 2003 for another method
        mag_p1 = norm(p1)
        mag_p2 = norm(p2)
        mags = mag_p1 * mag_p2

        cos_dv = dot(p1, p2)/mags
        sin_dv = abs(cross(p1, p2))/mags

        A = tm * sqrt(mags*(1+cos_dv))
        if A == 0 and tm == 1:
            # Can't calculate. try the long way around
            return lambert_deltas(p1, v1, p2, v2, time, -1)
        elif A == 0:
            raise ValueError("Can't calculate orbit.")

        psi_n = 0
        c2 = _float(".5")
        c3 = _float("1")/_float("6")

        psi_up = 4*pi**2
        psi_low = -4*pi

        delta_t = time + 1 # junk initial value

        iterations = 0
        # FIXME: on some weird edge cases this can iterate 0 times?
        y = None
        while abs(delta_t - time) > self.ACCURACY and iterations < 100:
            y = mag_p1 + mag_p2 + ((A*(psi_n*c3-1))/sqrt(c2))
            if A > 0 and y < 0:
                raise ValueError("adjust psi_low so y > 0 (%s)" % y)
            chi = sqrt(y/c2)
            
            delta_t = (chi**3*c3 + A*sqrt(y))/sqrt(self.gravitational_parameter)

            if delta_t <= time:
                psi_low = psi_n
            else:
                psi_up = psi_n

            psi_next = (psi_up + psi_low)/2

            c2, c3 = self._stumpff(psi_next)

            psi_n = psi_next
            iterations += 1

        if y is None:
            y = mag_p1 + mag_p2 + ((A*(psi_n*c3-1))/sqrt(c2))
        elif iterations > 99:
            raise ValueError("No firing solution at this timeframe!")

        f = 1 - y/mag_p1
        g_dot = 1 - y/mag_p2
        g = A * sqrt(y/self.gravitational_parameter)

        new_v1 = (p2 - f*p1)/g
        new_v2 = (g_dot*p2 - p1)/g

        # Check to see if the orbit would impact the parent body (vallado algo 57)
        if dot(p1, new_v1) < 0 and dot(p2, new_v2) > 0:
            new_orbit = Orbit(self.parent, self.satellite, p1, new_v1)
            rp = new_orbit.semi_major_axis * (1 - new_orbit.eccentricity)
            if rp < self.parent.radius and tm == 1:
                return self.lambert_deltas(p1, v1, p2, v2, time, -1)
            elif rp < self.parent.radius and tm == -1:
                raise ValueError("No firing solution at this timeframe!")

        return new_v1, new_v2


    #
    # Get orbit plot. TODO: only plot this once, not on every draw frame.
    #

    @cached_property
    def plot(self):
        """
        Get the points (position vectors relative to the orbit's frame of
        reference) for how to plot this orbit.

        FIXME: Should really do this in OpenGL. use shader? https://www.opengl.org/discussion_boards/showthread.php/173136-drawing-hyperbola-in-openGL
        """
        points = []
        n = 36
        print(self.position_from_true_anomaly(0))
        if self.is_elliptical:
            start, limit, step = 0, 2*pi, 2*pi/n
            while start < limit:
                position, _ = self.position_from_true_anomaly(start)
                start += step
                points.append(position)
        else:
            max_ = 5.0
            start, limit, step = max_, 0, -max_/(n/2)
            while start > limit:
                dt = int(10**(start))
                position, _ = self.get_position(-dt)
                points.append(position)
                start += step
            points.append(self.v_position) # dt == 0
            start, limit, step = 0, max_, max_/(n/2)
            while start < limit:
                dt = int(10**(start))
                position, _ = self.get_position(dt)
                points.append(position)
                start += step
        return points


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

    @classmethod
    def _reverse(cls,
        true_anomaly,
        eccentric_anomaly,
        eccentricity,
        gravitational_parameter,
        semi_major_axis,
        long_of_ascending_node,
        inclination,
        argument_of_periapsis,
    ):

        r_distance = semi_major_axis * (1 - eccentricity * cos(eccentric_anomaly))

        pos_orbital = r_distance * array([
            cos(true_anomaly),
            sin(true_anomaly),
            0,
        ])

        vel_orbital = sqrt(gravitational_parameter*semi_major_axis)/r_distance * array([
            -sin(eccentric_anomaly),
            sqrt(1 - eccentricity**2) * cos(eccentric_anomaly),
            0,
        ])

        v_position = cls._rotate(pos_orbital, long_of_ascending_node, inclination, argument_of_periapsis)
        v_velocity = cls._rotate(vel_orbital, long_of_ascending_node, inclination, argument_of_periapsis)

        return v_position, v_velocity

    @classmethod
    def _rotate(cls, r, Ω, ι, ω):
        r = r[:, newaxis]
        r = (Rz(-Ω)*Rx(-ι)*Rz(-ω)).dot(r)
        return squeeze(asarray(r))

    @classmethod
    def vecs_from_tle(cls, tle, parent, satellite, epoch = None):
        """
        Only works for kepler (elliptical) orbits.
        """
        # https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
        # FIXME: make dates Julian
        delta_t = 0
        if epoch:
            interval = tle["epoch"] - epoch
            delta_t = interval.seconds + interval.days * 86400

        gravitational_parameter = cls.G * parent.mass
        semi_major_axis = cbrt((tle["mean_motion"]/(2*pi))**2*gravitational_parameter)

        mean_anomaly = tle["mean_anomaly"] + delta_t * sqrt(gravitational_parameter/semi_major_axis**3)
        mean_anomaly %= 2*pi

        eccentricity = tle["eccentricity"]

        eccentric_anomaly = kepler(mean_anomaly, eccentricity, cls.ACCURACY)

        arg1 = sqrt(1 + eccentricity) * sin(eccentric_anomaly/2)
        arg2 = sqrt(1 - eccentricity) * cos(eccentric_anomaly/2)
        true_anomaly = 2 * arctan2(arg1, arg2)

        return cls._reverse(
            true_anomaly,
            eccentric_anomaly, 
            eccentricity, 
            gravitational_parameter, 
            semi_major_axis, 
            tle["long_of_ascending_node"], 
            tle["inclination"], 
            tle["argument_of_periapsis"]
        )


    def position_from_true_anomaly(self, true_anomaly):
        """
        Get a position based on a value for the true anomaly
        """

        eccentric_anomaly = arccos(
            (self.eccentricity+cos(true_anomaly))
            /
            (1 + self.eccentricity*cos(true_anomaly))
        )

        p, v = self._reverse(
            true_anomaly,
            eccentric_anomaly, 
            self.eccentricity, 
            self.gravitational_parameter, 
            self.semi_major_axis, 
            self.long_of_ascending_node, 
            self.inclination, 
            self.argument_of_periapsis
        )

        return p, v
