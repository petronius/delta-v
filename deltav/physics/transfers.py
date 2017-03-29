

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
        while abs(delta_t - time) > ACCURACY and iterations < 100:
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
