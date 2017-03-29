
from deltav.physics.body import Body
from deltav.ships import MobShip
from deltav.physics.util import load_tle_file
from deltav.physics.orbit import Orbit

from deltav.maps._base import BaseScene


class EarthMoonSystem(BaseScene):

    def setup(self): 
        earth = Body(5.972e24, 6371000)

        self.add_body(earth)

        shuttle = MobShip("OV-103 Discovery")
        shuttle.orbit(earth, (
            0,
            0,
            6524.834 * 1200,
        ), (
            7.81599286557539 * 1000,
            0,
            0,
        ))
        self.add(shuttle)

        for tle in load_tle_file("data/celestrak/stations.txt", max=30): # 17 or greater causes collisions?
            ship = MobShip(tle["name"])
            vecs = Orbit.vecs_from_tle(tle, earth, ship)
            ship.orbit(earth, *vecs)
            self.add(ship)