
import threading
import time

from multiprocessing.managers import BaseManager


from deltav.gameserver.gamestate import GameState
from deltav.maps.earth import EarthMoonSystem

class GameServer(object):

    def __init__(self, debug=False):
        
        self.debug = debug

        map_ = EarthMoonSystem()
        self.gamestate = GameState(map_)


    def connect(self, client):
        if self.can_connect(client):
            ship = self.gamestate.load_player(client)
            return 0, "", ship # is a proxy
        else:
            return -1, "Auth failed", None

    def can_connect(self, client):
        return True # Auth here later

    def get_scene_info(self, client):
        return {
            "game_time": self.gamestate.current_time,
            # FIXME: filter out objects the current player can't see?
            # Thisis not the final data format
            "objects": self.gamestate.get_visible_objects(client.ship),
            "debug": self.gamestate.simulation_clock.info if self.debug else {},
        }

    def run(self):
        self.thread = threading.Thread(target=self.gamestate.runforever)
        self.thread.start()


class ServerManager(BaseManager):
    pass

ServerManager.register("GameServer", GameServer)

def new_server():
    manager = ServerManager()
    manager.start()
    server = manager.GameServer()
    return server


if __name__ == "__main__":
    import pprint

    server = GameServer(True)
    server.run()
    while True:
        print(server.gamestate.current_time, len([i for i in server.gamestate.scene]), repr(server.gamestate.simulation_clock))
        time.sleep(1)
