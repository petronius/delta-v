
class ConnectionError(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __repr__(self):
        return "<ConnectionError (%s): %s>" % (self.code, self.msg)


class GameClient(object):

    def __init__(self, server):
        self.uid = "" # Generate a unique ID, store it locally, but allow the player to regenerate it?
        self.ship = None
        self.server = server

    def connect(self, server):
        # Connect to server, get ship proxy for commands
        err, msg, ship = server.connect(self)
        if not err:
            self.ship = ship
            return True
        else:
            raise ConnectionError(err, msg)

    def get_scene_info(self):
        # For use by the ship nav and the UI
        return self.server.get_scene_info()

    def get_ship_info(self):
        # For use by the ship nav and the UI
        return self.ship.get_scene_info()