
from . import BaseModule



class FusionCore(BaseModule):

    mass = 1000

    def __init__(self):
        super(self, FusionCore).__init__()
        self.hp = 10
        self.power_draw = -100
        self.internal_size = 10

        self.em_output.update({
            "infrared": (10, None),
            "neutron": (2, None),
        })

    def on_destruct(self):
        self.explode({
            "infrared": (6000, None),
            "visible": (10000, None),
            "radio": (2000, None),
            "microwave": (8000, None),
            "vlf": (100, None),
            # ionizing radiation
            "xray": (1000, None),
            "ultraviolet": (1000, None),
            "neutron": (10000, None),
            "alpha": (10000, None),
            "beta": (10000, None),
            "gamma": (10000, None),
        }, 4, 200)


class AMCore(BaseModule):

    mass = 2500

    def __init__(self):
        super(self, FusionCore).__init__()
        self.hp = 20
        self.power_draw = -200
        self.internal_size = 8

        self.em_output.update({
            "infrared": (10, None),
        })

    def on_destruct(self):
        self.explode({
            "infrared": (6000, None),
            "visible": (10000, None),
            "radio": (2000, None),
            "microwave": (8000, None),
            "vlf": (100, None),
            # ionizing radiation
            "xray": (1000, None),
            "ultraviolet": (1000, None),
            "neutron": (10000, None),
            "alpha": (10000, None),
            "beta": (10000, None),
            "gamma": (10000, None),
        }, 4, 200)