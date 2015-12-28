
from pyglet.gl import *
from pyglet.window import key


class Camera:
    """ A camera.
    """
    mode = 1
    rx, ry, rz = 30, -45, 0
    far = 100192
    fov = 60

    def __init__(self, w, h):

        self.w = w
        self.h = h

        self.x = 0.0
        self.y = 0.0
        self.z = 512

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

    def key(self, symbol, modifiers):
        """ Key pressed event handler.
        """

    def drag(self, x, y, dx, dy, button, modifiers):
        """ Mouse drag event handler.
        """
        if button == 1:
            self.x -= dx*2
            self.y -= dy*2
        elif button == 2:
            self.x -= dx*2
            self.z -= dy*2
        elif button == 4:
            self.ry += dx/4.
            self.rx -= dy/4.

    def apply(self):
        """ Apply camera transformation.
        """
        glLoadIdentity()
        #if self.mode == 1: return
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)
        # Set up for more rendering
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.w)/self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)
