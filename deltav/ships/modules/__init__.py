

class BaseModule(object):

    mass = 0

    def __init__(self):
        self.hp = 0

        self.power_draw = 0
        # adds to overall ship size
        self.external_size = 0
        # Ship has to have enough of this
        self.internal_size = 0

        # (magnitude, (elevation, declination, ang_size)). None in the second term
        # means it is omnidirectional
        self.em_output = {
            "infrared": (0, None),
            "visible": (0, None),
            "radio": (0, None),
            "microwave": (0, None),
            "vlf": (0, None),
            # ionizing radiation
            "xray": (0, None),
            "ultraviolet": (0, None),
            "neutron": (0, None),
            "alpha": (0, None),
            "beta": (0, None),
            "gamma": (0, None),
        }

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def on_destruct(self):
        raise NotImplementedError()

    def explode(self, em_sig, duration, radius):
        pass


class EmptyModule(BaseModule):

    def activate(self):
        pass

    def deactivate(self):
        pass

    def on_destruct(self):
        pass
