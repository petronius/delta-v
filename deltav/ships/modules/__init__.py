from deltav.physics.body import Body

class BaseModule(Body):

    NAME = "<BaseModule>"

    def __init__(self):
        super(BaseModule, self).__init__()

        self.is_active = True

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
        self.is_active = True
        return self.is_active

    def deactivate(self):
        self.is_active = False
        return self.is_active

    def on_destruct(self):
        raise NotImplementedError()

    def explode(self, em_sig, duration, radius):
        pass


class EmptyModule(BaseModule):

    NAME = "(missing sys ctl)"

    def __init__(self):
        super(EmptyModule, self).__init__()
        self.is_active = False

    def activate(self):
        return False

    def deactivate(self):
        pass

    def on_destruct(self):
        pass
