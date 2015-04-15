
from celestials import BaseOrbitalObject
from utils import random_ship_name



class BaseShip(BaseOrbitalObject):

    _type = "BaseShip"

    def __init__(self, ship_name = None, radius = 1):
        super(BaseShip, self).__init__()
        self._name = ship_name or random_ship_name()
        self._radius = radius


class PlayerShip(BaseShip):
    _type = "PlayerShip"

class MobShip(BaseShip):
    _type = "MobShip"