"""
So, orbital mechanics.

Base assumptions just to get the game working:

- All orbits are circular.

- Initial position is set with "lat" and "long", but  for now it is always (0. 0)

- And all orbits are equatorial anyway

- The reference frame for "lat" and "long" is locked and the same for all bodies
  (that is, if it rotates, the lat/long of poitns on the surface is also moving,
  if that makes sense). If we need "real" surface coordinates later, we can add
  that in.

  The nice thing about programming is being able to have a Great Divine 
  Reference Frame.

- Orbital speed is "meters" per "second", where a second is one tick, and a
  meter is the circumference of the orbit around a size 0 object at an altitude
  of 1.

  That is, altitude/speed = ticks per orbit.


There's a whole fuckin' bunch of trigonometry in this file.

"""

import functools
import log
import math

from utils import random_planet_name


class BaseOrbitalObject(object):

    _type = "BaseOrbitalObject"

    def __init__(self, name = None, radius = 1):
        self._name = name or random_planet_name()
        self._lat = self._long = self._period = self._altitude = self._parent = None
        self.radius = radius

    def __repr__(self):
        return '<{} "{}">'.format(self._type, self._name)

    def set_orbit(self, parent_body, mean_distance, orbital_period, position = (0, 0)):
        self._lat, self._long = map(float, position)
        self._altitude = self.radius + float(mean_distance)
        self._period = float(orbital_period)
        self._parent = parent_body
        
    def simulate_step(self):
        if not self._parent:
            raise ValueError("Orbit not specified for {}".format(repr(self)))
        # How much to incriment the latitude by
        delta_deg = 360 / self._period
        # Update the actual latitude
        self._lat = self._normalize_angle(self._lat + delta_deg)
        log.debug("{} at lat/long: {}, {} alt: {} p: {} over {}".format(
            repr(self), self._lat, self._long, self._altitude, self._period, repr(self._parent)
        ))


    def visible_objects(self, object_list):
        """
        Yields tuples of (object, visibility %, (heading, distance), angular_size)
        """
        pos_map = {obj: self.get_relative_position(obj) for obj in object_list}
        dist_map = {pos[1]: (obj, pos[0]) for obj, pos in pos_map.items()}
        occluded_angles = []
        # Now eliminate any objects which are:
        # a) further away than any others, AND
        # b) which are behind something else
        # starting with the closest first
        for distance in sorted(dist_map.keys()):
            visible_portion = 0
            obj, angle = dist_map[distance]
            # get the angular size. distance is to the center of an idealized
            # sphere, so using the second formula from wikipedia
            # print(obj, obj.radius, distance, 2 *obj.radius / (2 * (distance + obj.radius)))
            angs = 2 * math.asin(2 * obj.radius / (2 * (distance + obj.radius)))
            angs = math.degrees(angs)
            log.debug("obj {} is {} distant and {} big = {}".format(obj, distance, obj.radius, angs))
            # Figure out what part of the fov is blocked
            delta = angs / 2
            start, end = map(self._normalize_angle, (angle - delta, angle + delta))
           
            # check against existing occlusions 
            for idx, occlusion in enumerate(occluded_angles):
                astart, aend = occlusion
                # collision!
                if end > astart and start < aend:
                    # get the size of the overlap as a percentage
                    visible_portion = angs - (min(end, aend) - max(start, astart)) / angs
                    if visible_portion > 0:
                        yield obj, visible_portion, pos_map[obj], angs
                        # extend the occlusion
                        new_start = min(start, astart)
                        new_end = max(end, aend)
                        occluded_angles[idx] = (new_start, new_end)
                    else:
                        pass
                        # log.debug("Size {} occlusion blocking size {} object {}".format(aend-astart, angs, obj))
                    break
            else:
                # no collusion at all
                yield obj, 1, pos_map[obj], angs

            # no collision!n add the occlusion for the next check
            # log.debug("Adding size {} occlusion for {}".format(end-start, obj))
            occluded_angles.append((start, end))




    def get_relative_position(self, obj):
        """
        For each obj, walk up the tree of celestials and compute the various
        angles somehow.

        Returns (angle, distance)
        """
        if self._parent is obj._parent:

            return self._compute_ang_and_dist(self._lat, self._altitude, obj._lat, obj._altitude)

        elif self._parent is obj:

            return self._lat, self._altitude

        else:
            # This doesn't need to be too advanced, because the graph that's
            # being traversed has to be a very simple tree.
            own_ancestors, obj_ancestors = self.all_ancestors(), obj.all_ancestors()

            for idx, ancestor in enumerate(own_ancestors):
                if ancestor in obj_ancestors:
                    obj_ancestor_chain = obj_ancestors[:obj_ancestors.index(ancestor) ]
                    own_ancestor_chain = own_ancestors[:idx]
                    break
            else:
                raise RuntimeError("No common ancestors between {} and {}".format(self, obj))

            # log.debug("Object chain: "+repr(obj_ancestor_chain))
            # log.debug("Own chain: "+repr(own_ancestor_chain))

            # FIXME: There must be a way to generalize this into the else clause
            if obj in own_ancestors:

                angle, dist = self._lat, self._altitude

                for ancestor in own_ancestor_chain[1:]:
                    if ancestor._parent:
                        angle, dist = self._compute_ang_and_dist(angle, dist, ancestor._lat, ancestor._altitude)

                return angle, dist



            else:
                # Rearrange them to include obj and self, and reverse for easier
                # traversal. The first item of each list will now have a common
                # ancestor
                obj_ancestor_chain.reverse()
                own_ancestor_chain.reverse()

                # Now that we have a common ancestor, start there and recursively
                # calculate the relative positions for the endpoints.
                obj_head = obj_ancestor_chain.pop()
                own_head = own_ancestor_chain.pop()

                #log.debug("Angle between {} {}".format(*map(repr, (own_head, obj_head))))

                angle, dist = self._compute_ang_and_dist(own_head._lat, own_head._altitude, obj_head._lat, obj_head._altitude)

                # First up one branch
                for obj_head in obj_ancestor_chain:
                    angle, dist = self._compute_ang_and_dist(angle, dist, obj._lat, obj._altitude)
                # aaand then up the other
                for own_head in own_ancestor_chain:
                    angle, dist = self._compute_ang_and_dist(own_head._lat, own_head._altitude, angle, dist)

            return angle, dist



    @staticmethod
    def cartesian_position(lat, altitude):
        """
        Shit has to get converted from polar to cartesian because the Great
        Divine Reference Frame is what all of these coordinates are ultimately
        relative to, and because I am not smart enough to do it otherwsie.
        """
        # Relative to the parent
        r = math.radians(float(lat))
        return math.cos(r) * altitude, math.sin(r) * altitude

    @staticmethod
    #@functools.lru_cache(maxsize=2 ** 20, typed = False)
    def _compute_ang_and_dist(p1, r1, p2, r2):
        x1, y1 = BaseOrbitalObject.cartesian_position(p1, r1)
        x2, y2 = BaseOrbitalObject.cartesian_position(p2, r2)
        op, adj = x2 - x1, y2 - y1
        if not op or not adj:
            angle = 0
        else:
            # inverse tangent yields the angle from obj to us, so subtract from
            # 360 for the reverse
            angle = 360 - math.atan(op/adj)
        dist = math.hypot(op, adj)
        return BaseOrbitalObject._normalize_angle(angle), dist

    @staticmethod
    def _normalize_angle(angle):
        return angle % 360


    @property
    def position(self):
        return self._lat, self._long, self._altitude

    def all_ancestors(self):
        ancestor_list = [self, ]
        head = self
        while True:
            head = head._parent
            if head:
                ancestor_list.append(head)
            else:
                break
        return ancestor_list
    
    


class Planet(BaseOrbitalObject):
    _type = "Planet"

class Star(BaseOrbitalObject):
    _type = "Star"
    def simulate_step(self):
        pass

class Moon(BaseOrbitalObject):
    _type = "Moon"