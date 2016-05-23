
import pyglet

import random

from numpy.linalg import norm

from .modules import EmptyModule
from .modules.power import *
from .modules.weapons import *

from deltav.physics.body import Body
from deltav.physics.helpers import array

#
# Nothing to see here yet
#


class BaseShip(Body):

    base_mass = 15000

    def __init__(self, ship_name, radius = 1):
        super(BaseShip, self).__init__()
        self._name = ship_name
        self._radius = radius

        self.target = None # other objects

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

        self.destructable = True

        self._orbit = None
    
    
    def cycle_target(self, target_list):
        if self.target is None and len(target_list):
            self.target = target_list[0]
        elif len(target_list):
            idx = target_list.index(self.target)
            try:
                self.target = target_list[idx+1]
            except IndexError:
                self.target = None
        else:
            self.target = None
        print(self, "targetting", self.target)


    def shoot_target(self, shot):
        p1, v1 = self._orbit.get_position()

        if shot == "bullet":
            # solve lambert's problem for the new orbit we want to create. we don't
            # care about the second delta-v, because we aren't rendezvousing
            t = 10
            while True:
                try:
                    t_orbit = self.target._orbit
                    t_epoch = t_orbit.t_delta
                    new_epoch = t_epoch + t
                    p2, v2 = self.target._orbit.get_position(new_epoch)
                    new_v, _ = self._orbit.lambert_deltas(p2, v2, t)
                    print("time", t)
                except ValueError: # invalid orbit for the small t we are attempting
                    # FIXME: should be a better heuristic for this
                    t *= 1.1
                    continue
                break
            # FIXME: check and iterate if delta_v is too high
            #delta_v = abs(v1 - new_v)

            bullet = Bullet()
            bullet.orbit(self._orbit.parent, p1, new_v)

        elif shot == "torpedo":
            # get direction of bad guy
            p2 = self.target.get_position()
            # re-center on us
            direction = p2 - p1
            unit_vector = direction/norm(direction)
            # fire out the tubes at speed
            unit_vector *= 500
            bullet = Torpedo(self.target)
            bullet.orbit(self._orbit.parent, p1, unit_vector + v1)

        else:
            raise Exception("Not a weapon! %s" % shot)

        return bullet # so the game state can track it


    def explode(self, impact_vector = None):
        print(self, "exploded!")
        objs = []
        for _ in range(random.randint(2, 10)):
            p1, v1 = self._orbit.get_position()
            delta_v = array([0,0,0])
            if impact_vector is not None:
                delta_v += impact_vector * random.random()
            delta_v += array([
                random.randint(-100, 100),
                random.randint(-100, 100),
                random.randint(-100, 100),
            ])
            debris = Debris()
            print("spawning", debris, delta_v, v1)
            debris.orbit(self._orbit.parent, p1, delta_v + v1)
            objs.append(debris)
        return objs


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


class Missile(BaseShip):

    invuln_time = 2
    def __init__(self):
        super(Missile, self).__init__("blap", 1)
        self.destructable = False
        self.clock = 0

    def tick(self, dt):
        self.clock += dt
        if self.clock > self.invuln_time:
            self.destructable = True




class Bullet(Missile):
    base_mass = 45 # kg
    
    def __init__(self):
        super(Bullet, self).__init__()
    
    def explode(self, *args, **kwargs):
        return []
   

class Torpedo(Missile):
    base_mass = 145 # kg

    def __init__(self, target):
        super(Torpedo, self).__init__()
        self.target = target
        self.adjustments = 3
    
    def explode(self, *args, **kwargs):
        return []
    
    def tick(self, dt):
        super(Torpedo, self).tick(dt)
        if self.clock > 10 and self.adjustments > 0:
            self.adjust_course()
            self.clock = 0
            self.adjustments -= 1

    def adjust_course(self):
        # solve lambert's problem for the new orbit we want to create. we don't
        # care about the second delta-v, because we aren't rendezvousing
        t = 10
        while True:
            try:
                t_orbit = self.target._orbit
                t_epoch = t_orbit.t_delta
                new_epoch = t_epoch + t
                p2, v2 = self.target._orbit.get_position(new_epoch)
                new_v, _ = self._orbit.lambert_deltas(p2, v2, t)
                print("time", t)
            except ValueError: # invalid orbit for the small t we are attempting
                # FIXME: should be a better heuristic for this
                t *= 1.1
                continue
            break
        # FIXME: this is super imba
        self._orbit.set_veloctiy(new_v)
    def _destruct_enable(self, dt, *args, **kwargs):
        self.destructable = True

     

class Debris(Missile):
    base_mass = 10 # kg
    
    def __init__(self,):
        super(Debris, self).__init__()
    
    def explode(self, *args, **kwargs):
        return []