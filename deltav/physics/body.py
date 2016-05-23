"""
Base class for all objects that have to interact with the physics simulation.
"""

import uuid

from numpy import Inf
from numpy.linalg import norm

from deltav.physics.orbit import Orbit
from deltav.physics.helpers import cbrt, cached_property


class Body(object):

    
    def __init__(self, mass = 0, radius = 0):
        self._mass = mass
        self._radius = radius
        self._orbit = None

        self.id = uuid.uuid4()

        self.propery_cache = {}


    def get_position(self):
        if self._orbit:
            p, v = self._orbit.get_position()
            return p
        else:
            return (0, 0, 0)

    #
    # For subclassing
    #

    @cached_property
    def radius(self):
        return self._radius


    @cached_property
    def mass(self):
        return self._mass


    @cached_property
    def hill_radius(self):
        """
        The radius of the "sphere of influence" (Hill sphere) for the object
        as it orbits the parent.
        """
        if not self._orbit:
            return Inf
        else:
            parent_mass = self._orbit.parent.mass
            semi_major_axis = self._orbit.semi_major_axis
            eccentricity = self._orbit.eccentricity

            return semi_major_axis * (1 - eccentricity) * cbrt(-3, self.mass / (3 * parent_mass))


    @property
    def inside_hill_sphere(self):
        """
        Check to see if the object has left the hill radius of its parent.
        """
        distance = norm(self.get_position())
        return distance > self.hill_radius


    def update_parent(self):
        """
        If we are not inside the Hill sphere of our parent body, then update
        the reference to the parent to the one we should be orbiting, and update
        orbital data accordingly.
        """ 
        if not self.inside_hill_sphere:
            old_parent = self._orbit.parent
            try:
                new_parent = self.parent._orbit.parent
            except AttributeError:
                return
            # get the position of the old parent relative to the new parent,
            # and add it to our state vectors, so the offset is correct
            p_pos, p_vel = old_parent._orbit.get_position()
            pos, vel = self._orbit.get_position()
            position = p_pos + pos
            velocity = p_pos + vel + p_vel # ?
            # set up the new orbit
            self.orbit(new_parent, position, velocity)


    def orbit(self, parent, position, velocity):
        """
        Set the orbit of the ship around an object
        """
        self._orbit = Orbit(parent, self, position, velocity)