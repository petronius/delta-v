"""

Generalized 3-d orbital mechanics equations. Two-body problems only.

- We know position and direction and energy (the latter two will yield a velocity vector)
- We know what orbit we want to go into (easy, can prepare equations)
- calculate the transfer between two orbits, if it exists

Nav computer algorithm for interception:

    - Are we in the same inclination?
        - Yes, next step
        - No, perform an inclination change
    - Are we in the same orbit?
        - No
            - Are both orbits circular?
                - Yes, Hohmann transfer
                - No, next step
            - Is the target orbit circular?
                - No, Bielliptic transfer
                - Yes,  Move to circular orbit, Hohmann transfer
        - Yes, next step
    - Are the orbits in phase?
        - Yes, done
        - No, calculate phase orbit and maneouvers, and perform

You could also:

    - Match orbit and phase, but not inclination
    - Match inclination but not the others
    - Etc.

"""


#
# Nothing to see here yet
#

class SomeKindofNavigation(Orbit):
    #
    # The name of the game. All maneuvers return a tuple of delta-v's.
    #

    def delta_v_inclination(self, target_orbit):
        """
        Return the delta v required to match the target orbit.
        """
        delta_i = self.inclination - target_orbit.inclination
        # Use the simpler equation if both orbits are circular and have the
        # same radius.
        if self.is_circular and target_orbit.is_circular and \
           self.mag(self.v_position) == self.mag(target_orbit.v_position):

            delta_v = 2*self.mag(self.v_velocity)*math.sin(delta_i/2)

        else:

        return (delta_v,)

    def hohmann_transfer(self, target_orbit):
        """
        Calculate the Hohmann transfer between the current orbit and the target
        orbit, assuming both are circular.
        """
        if self.is_circular and target_orbit.is_circular:
            raise NotImplementedError()
        else:
            raise ValueError("Both orbits must be circular")

    def bielliptic_transfer(self, target_orbit):
        """
        Calculate an elliptical transfer to the target orbit.
        """
        raise NotImplementedError()
        return (v1, v2, v3)

    def phase_orbit(self, target_anomlay):
        """
        Given a target mean anomaly in the current orbit (for the current 
        epoch), calculate the phase orbit that has to be transferred to (and
        back out of, obvs), to reach that point.
        """
        raise NotImplementedError()