

import random

import numpy
import pyglet

from numpy.linalg import norm

from .modules import EmptyModule
from .modules.power import *
from .modules.weapons import *

from deltav.physics.body import Body
from deltav.physics.helpers import array, Rx, Ry, Rz

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

        self.pitch = 0
        self.yaw = 0
        self.roll = 0


    def accelerate(self, dv):
        # accelerate along the current direction
        vec = array([0, dv, 0])
        # FIXME: Should automagically match rendering of ADI in view, to ensure
        # consistency?
        vec = (Rz(self.roll)*Rx(self.pitch)*Ry(self.yaw)).dot(vec[:, numpy.newaxis])
        vec = numpy.squeeze(numpy.asarray(vec))
        self._orbit.accelerate(vec)


    def turn(self, x = 0, y = 0, z = 0):
        self.pitch += x
        self.yaw += y
        self.roll += z
    
    
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


    def shoot_target(self, shot):

        if shot == "bullet":
            # solve lambert's problem for the new orbit we want to create. we don't
            # care about the second delta-v, because we aren't rendezvousing
            t = 10
            while True:
                try:
                    p1, v1 = self._orbit.get_position()
                    t_orbit = self.target._orbit
                    t_epoch = t_orbit.t_delta
                    new_epoch = t_epoch + t
                    p2, v2 = self.target._orbit.get_position(new_epoch)
                    new_v, _ = self._orbit.lambert_deltas(p1, v1, p2, v2, t)
                except ValueError: # invalid orbit for the small t we are attempting
                    # FIXME: should be a better heuristic for this
                    t *= 1.1
                    continue
                break
            # FIXME: check and iterate if delta_v is too high
            #delta_v = abs(v1 - new_v)
            print(self, "time", t)

            bullet = Bullet()
            bullet.orbit(self._orbit.parent, p1, new_v)

        elif shot == "torpedo":
            p1, v1 = self._orbit.get_position()
            # get direction of bad guy
            p2 = self.target.get_position()
            # re-center on us
            direction = p2 - p1
            unit_vector = direction/norm(direction)
            # fire out the tubes at speed
            unit_vector *= 1000
            bullet = Torpedo(self.target)
            bullet.orbit(self._orbit.parent, p1, unit_vector + v1)

        else:
            raise Exception("Not a weapon! %s" % shot)

        return bullet # so the game state can track it


    def explode(self, impact_vector = None):
        objs = []
        for _ in range(random.randint(2, 10)):
            p1, v1 = self._orbit.get_position()
            delta_v = array([0,0,0])
            if impact_vector is not None:
                delta_v += impact_vector
            delta_v *= random.random()
            debris = Debris()
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



    


class PlayerShip(BaseShip):
    pass

class MobShip(BaseShip):
    pass


class Missile(BaseShip):

    invuln_time = 30
    def __init__(self, name = None):
        super(Missile, self).__init__(name or "(unknown)", 1)
        self.destructable = False
        self.clock = 0

    def game_tick(self, dt):
        super(Missile, self).game_tick(dt)
        self.clock += dt
        if self.destructable == False and self.clock > self.invuln_time:
            self.destructable = True




class Bullet(Missile):
    base_mass = 45 # kg
    
    def __init__(self):
        super(Bullet, self).__init__("250mm HE")
    
    def explode(self, *args, **kwargs):
        return []
   

class Torpedo(Missile):
    base_mass = 145 # kg

    def __init__(self, target):
        super(Torpedo, self).__init__("MK-1 (G)")
        self.target = target
        self.adjustments = 1
        self.time_to_impact = None
    
    def explode(self, *args, **kwargs):
        return []
    
    def game_tick(self, dt):
        super(Torpedo, self).game_tick(dt)
        if self.clock > 100 and self.adjustments > 0:
            self.adjust_course()
            self.clock = 0
        if self.time_to_impact is not None:
            self.time_to_impact -= dt

    def adjust_course(self):
        # solve lambert's problem for the new orbit we want to create. we don't
        # care about the second delta-v, because we aren't rendezvousing
        t = 10
        while True:
            try:
                p1, v1 = self._orbit.get_position()
                t_orbit = self.target._orbit
                t_epoch = t_orbit.t_delta
                new_epoch = t_epoch + t
                p2, v2 = self.target._orbit.get_position(new_epoch)
                new_v, _ = self._orbit.lambert_deltas(p1, v1, p2, v2, t)
                # only adjust if new course is faster
                # FIXME: or if won't intercept
                if self.time_to_impact is None or abs(self.time_to_impact - t) < 10:
                    self._orbit.set_veloctiy(new_v)
                    self.time_to_impact = t
                    self.adjustments -= 1
            except ValueError: # invalid orbit for the small t we are attempting
                # FIXME: should be a better heuristic for this
                t *= 1.1
                continue
            break
        print(self, "time", t)
        # FIXME: this is super imba
    def _destruct_enable(self, dt, *args, **kwargs):
        self.destructable = True

     

class Debris(Missile):
    base_mass = 10 # kg
    
    def __init__(self,):
        super(Debris, self).__init__("(junk)")
    
    def explode(self, *args, **kwargs):
        return []