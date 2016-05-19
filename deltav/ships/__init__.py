
from .modules import EmptyModule
from .modules.power import *
from .modules.weapons import *

from deltav.physics.orbit import Orbit

#
# Nothing to see here yet
#


class BaseShip(object):

    base_mass = 15000

    def __init__(self, ship_name, radius = 1):
        super(BaseShip, self).__init__()
        self._name = ship_name
        self._radius = radius

        self.modules = []

        self._internal_space = 0

        self.modules = {
            "powersrc": FusionCore(),
            "computer": EmptyModule(),

            "shielding": EmptyModule(),

            "engines": EmptyModule(),
            "sensors": EmptyModule(),
            "weapons": EmptyModule(),
        }

        self._orbit = None

    @property
    def mass(self):
        return self.base_mass + sum([m.mass for m in self.modules.values()])
    

    # @property
    # def mass(self):
    #     # FIXME: Cache this propery until modules change
    #     return sum([m.mass for m in self.modules.values()]) + self.base_mass

    def _get_module_output(self, obj_direction, m_distance):
        """
        Iterate the modules and get the current em output
        """
        obj_elevn, obj_declinn = obj_direction
        for module in self._modules:
            for spectrum, values in module.em_output.items():
                mag, em_direction = values
                if em_direction:
                    # check to see whether we will see it
                    elevation, declination, ang_size = em_direction
                    if elevation - ang_size < obj_elevn < elevation + ang_size and \
                       declination - ang_size < obj_elevn < declination + ang_size:
                        # for directional emissions, the spread is only over the
                        # area of ang_size (theta * r**2)
                        yield spectrum, mag / (ang_size * (m_distance**2))
                    else:
                        continue
                else:
                    # simple inverse square
                    yield spectrum, mag * (1/(m_distance**2))

    def em_output(self, obj_direction, m_distance):
        """
        Get the observed output for each spectrum from the direction and
        distance of the observer.
        """
        # FIXME: don't return values that don't rise above the planetary sytem's
        # background radiation.
        out = {}
        for spectrum, val in self._get_module_output():
            if spectrum not in out:
                out[spectrum] = val
            else:
                out[spectrum] += val
        return out


    def orbit(self, parent, position, velocity):
        """
        Set the orbit of the ship around an object
        """
        self._orbit = Orbit(parent, self, position, velocity)

    @property
    def position(self):
        """
        Return the position of the ship, relative to the body it is orbiting.
        """
        position, velocity = self._orbit.get_position()
        return tuple(position)


    def accelerate(self, vector):
        print("--")
        print(self._orbit.v_velocity)
        self._orbit.v_velocity += vector
        print(self._orbit.v_velocity)
        self._orbit._property_cache = {}
        print(self._orbit.v_velocity)



    


class PlayerShip(BaseShip):
    pass

class MobShip(BaseShip):
    pass