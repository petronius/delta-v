
from . import BaseModule



class FusionCore(BaseModule):

    NAME = "Fusion core (I)"

    DETAILS = """
    IPP HEAVY INDUSTRIES - Helios(TM) Stellarator

    MODEL NUMBER: W/24-C
    MASS:         1000 KG
    FUEL:         DEUTERIUM-3
    UNIT COUNT:   1
    POWER OUTPUT: 2133 MWe

    A deuterium-powered fusion reactor, based on the designs of Lyman Spitzer
    and developed in the early 2120s. The Helios model line is a compact
    variation of the Wendelstein series, meant for fitting in sub-frigate class
    ships and smaller extra-planetary stations.

    Although quite safe even in cases of catastrophic failure, due to the
    fragile nature of fusion reactions, the Helios power system is not as rugged
    as certain alternatives.
    """

    mass = 1000

    def __init__(self):
        super(FusionCore, self).__init__()
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

    NAME = "Antimatter core (I)"

    DETAILS = """
    IPP HEAVY INDUSTRIES - Janus(TM) Matter/antimatter jetstream generator

    MODEL NUMBER: S/01-N
    MASS:         2500 KG
    FUEL:         PX-90
    UNIT COUNT:   1
    POWER OUTPUT: 6432 MWe

    
    """

    mass = 2500

    def __init__(self):
        super(FusionCore, self).__init__()
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