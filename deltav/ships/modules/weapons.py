
from . import BaseModule


class BaseWeapon(BaseModule):

    def fire(self):
        raise NotImplementedError()



class Laser(BaseModule):

    def fire(self):
        pass