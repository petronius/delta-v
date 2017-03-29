"""
Object for handling game state. Initialized by the GameServer when it is ready
to start a new game (or load an old one).

Provides scene data to the GameClient for display in the UI. The player interacts
with the scene through the ship interface.
"""
import time
import pyglet
import flamegraph


from numpy.linalg import norm

from deltav.ships import MobShip, PlayerShip, Bullet, Debris
from deltav.physics.body import Body
from deltav.physics.helpers import distance
from deltav.physics.util import load_tle_file
from deltav.physics.orbit import Orbit
from deltav.gameserver.util import DebugClock


class GameState(object):

    GAME_TIME_TICK = 1

    def __init__(self, map_):

        self.speed = 1000

        self.paused = False

        self.scene = map_ # dunno
        self.scene.setup()
        
        self.current_time = 0.0
        self.simulation_clock = DebugClock()

    def load_player(self, client):
        # Create a ship for the client, or reconnect to their old one, and add
        # it to the game. Needs an initial orbit and position, preferrably
        # defined by the scene.
        #
        # Returns a proxy object the client can use to get info about their ship
        # or issue commands
        ship = self.scene.load_player(client)
        return Proxy(ship)

    def get_visible_objects(self, obj):
        retval = []
        for obj2 in self.scene.visible_objects(obj):
            retval.append({
                "tracking_id": obj2.tracking_id,
                "transponder": obj2.transponder,
                "position": obj2.get_position(),
            })
        return retval

    def tick(self):
        try:
            self.simulation_clock.start_timer()
            self.current_time += self.GAME_TIME_TICK

            self.scene.tick(self.GAME_TIME_TICK)

            t = self.simulation_clock.record_time()

            # Sleep for the rest of this game tick
            t_wait = (1/(10*self.speed)) - t
            if t_wait > .001:
                time.sleep(t_wait)
            else:
                time.sleep(.001)

        finally:
            self.simulation_clock.clear_timer()


    def runforever(self):
        # flamegraph.start_profile_thread(fd=open("./perf.log", "w"))
        # c = 100
        while True: #c:
            # print(c, len(self.scene.objects), self.simulation_clock)
            # c -= 1
            if not self.paused:
                self.tick()
            else:
                time.sleep(.1) # Don't nuke the CPU
