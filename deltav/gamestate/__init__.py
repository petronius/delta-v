"""
Object for handling game state. Initialized by the GameView when it is ready
to start a new game (or load an old one).

Receives user input from UI, manages simulation. UI can inspect it to display
information.
"""
import time
import pyglet

import threading

from multiprocessing.managers import BaseManager


from numpy.linalg import norm

from deltav.ships import MobShip, PlayerShip, Bullet, Debris
from deltav.physics.body import Body
from deltav.physics.helpers import distance

_debug_boxes = []

class GameState(object):

    collision_tolerance = 1000 # m. FIXME: should use obj sizes

    def __init__(self):

        self.speed = 1
        self.paused = False

        planet = Body(5.972e24, 6371000) 

        player = PlayerShip('SASE C-3402 <font face="Droid Sans Fallback">黄河</font> Yellow River')
        player.orbit(planet, (6524.834 * 1200,0,0), (0,7.81599286557539 * 1200,0))

        shuttle, station = (
            MobShip("OV-103 Discovery"),
            MobShip("ISS"),
        )

        v_position = (
            -9.389136074764635E+02 * 1200,
            -5.116319908091118E+03 * 1200,
            4.342059664304661E+03 * 1200,
        )

        v_velocity = (
            6.628784989010491E+00 * 1200,
            1.718224103100249E+00 * 1200,
            3.457710395445335E+00 * 1200,
        )

        station.orbit(planet, v_position, v_velocity)
        shuttle.orbit(planet, (
            0,
            6524.834 * 1000,
            0
        ), (
            -30 * 1000,
            0,
            0,
        ))

        ships = [player, station] # shuttle, station)

        self.player = player

        self.scene = {
            "ships": ships,
            "bodies": [planet,],
            "debris": [],
            "bullets": [],
        }

        self.current_time = 0.0

    def get_debug_boxes(self):
        return _debug_boxes

    def get_player_orbit_data(self, keys):
        data = {}
        for key in keys:
            data[key] = getattr(self.player._orbit, key)
        return data

    def get_scene_data(self):
        data = {}
        for k, v in self.scene.items():
            data[k] = {}
            for o in v:
                if o._orbit:
                    orbit = {
                        "plot": o._orbit.plot if o._orbit else [],
                        "is_elliptical": o._orbit.is_elliptical,
                        "is_parabolic": o._orbit.is_parabolic,
                        "is_hyperbolic": o._orbit.is_hyperbolic,
                    }
                else:
                    orbit = {}
                data[k][o.uuid] = {
                    "name": o._name,
                    "position": o.get_position(),
                    "orbit": orbit,
                    "radius": o.radius,
                    "target": o.target.uuid if hasattr(o, "target") and o.target else None,
                }
        return data


    def remove_from_scene(self, *args):
        for arg in args:
            for k in self.scene:
                vs = self.scene[k]
                if arg in vs:
                    idx = vs.index(arg)
                    del self.scene[k][idx]
        for ship in self.scene["ships"]:
            if ship.target and not self.in_scene(ship.target):
                ship.target = None


    def in_scene(self, arg):
        for k, vals in self.scene.items():
            if arg in vals:
                return True
        return False


    def cycle_target(self, ship):
        if ship == "player":
            ship = self.player
        target_list = list(filter(lambda x: x is not ship, self.scene["ships"][:]))
        target_list += self.scene["debris"]+self.scene["bullets"]
        ship.cycle_target(target_list)
        print(ship, "targetting", ship.target)


    def shoot_at_target(self, ship, shot):
        if ship == "player":
            ship = self.player
        target = ship.target
        if target:
            bullet = ship.shoot_target(shot)
            self.scene["bullets"].append(bullet)
        else:
            print("no target")


    def set_speed(self, s = None, multiplier = None):
        if s:
            self.speed = s
        elif multiplier:
            self.speed *= multiplier
        if self.speed < 1:
            self.speed = 1
        elif self.speed > 2000:
            self.speed = 2000


    def toggle_pause(self):
        self.paused = not self.paused
        print("paused", self.paused)

    def start(self):
        self.thread = threading.Thread(target=self.simulate)
        self._running = True
        self.thread.start()
        print("Sim started!")

    def stop(self):
        self._running = False

    def simulate(self):
        while self._running:
            self.tick()
        return True

    def poll(self):
        return self._running

    def tick(self):
        time.sleep(1/(10*self.speed))
        global _debug_boxes
        game_dt = 1
        self.current_time += game_dt
        objs = self.scene["ships"] + self.scene["debris"] + self.scene["bullets"]
        if not self.paused:
            collision_checks = []
            # build list of destructables to check
            for o1 in objs:
                p0 = o1.get_position()
                if hasattr(o1, "game_tick"):
                    o1.game_tick(game_dt) # let it update internal state
                p1 = o1.get_position()
                p_norm = norm(p0)
                # check for surface impact
                if p_norm < o1._orbit.parent.radius:
                    self.remove_from_scene(o1)
                else:
                    if o1.destructable:
                        collision_checks.append((o1, p0, p1, p_norm))
            # now check list
            for idx, (o1, p0, p1, p_norm) in enumerate(collision_checks):
                try:
                    for o2, p0_, p1_, p_norm_ in collision_checks[idx+1:]:
                        # so that we don't have to simulate every instant in
                        # between, draw two cubes using previous and next position.
                        # if the cubes intersect, then we count it as a collision.
                        # this is approximate, but there should be no situations
                        # so extreme that this fails, so long as the step size
                        # is relatively small (< 1s).
                        #
                        # we only check against objects with a position vector
                        # whose magnitude is close to ours, otherwise we can
                        # assume it is nowhere near us. this tolerance is an
                        # arbitrary value.
                        if True: #abs(p_norm_ - p_norm) < self.collision_tolerance:
                            # _debug_boxes.append(box_diagonals(p0, p1))
                            # _debug_boxes.append(box_diagonals(p0_, p1_))
                            #print(o1, o2, (tuple(p0), tuple(p1)), (tuple(p0_), tuple(p1_)))
                            if boxes_intersect((p0, p1), (p0_, p1_)):
                                impact_vector1 = o2.get_velocity()
                                impact_vector2 = o1.get_velocity()
                                self.scene["debris"] += o1.explode(impact_vector1)
                                self.scene["debris"] += o2.explode(impact_vector2)
                                self.remove_from_scene(o1, o2)
                                continue # dont add o1 to collision checks, it blew up (FIXME: breaks 3-way collisions)
                except KeyError:
                    pass # end of list


def box_diagonals(*pts):
    top_right = (
        max([pt[0] for pt in pts]),
        max([pt[1] for pt in pts]),
        max([pt[2] for pt in pts]),
    )
    bottom_left = (
        min([pt[0] for pt in pts]),
        min([pt[1] for pt in pts]),
        min([pt[2] for pt in pts]),
    )
    return top_right, bottom_left

def boxes_intersect(c1, c2):
    """
    Check if two boxes (defined by the endpoints of their diagonals)
    intersect.

    Inelegant, but hopefully fast.
    """
    c1_top_right, c1_bottom_left = box_diagonals(*c1)
    c2_top_right, c2_bottom_left = box_diagonals(*c2)
    if c1_top_right[0] < c2_bottom_left[0] or \
       c1_top_right[1] < c2_bottom_left[1] or \
       c1_top_right[2] < c2_bottom_left[2] or \
       c1_bottom_left[0] > c2_top_right[0] or \
       c1_bottom_left[1] > c2_top_right[1] or \
       c1_bottom_left[2] > c2_top_right[2]:
        return False
    return True


class GameManager(BaseManager):
    pass

GameManager.register("GameState", GameState)

def new_game_state():
    manager = GameManager()
    manager.start()
    state = manager.GameState()
    return state