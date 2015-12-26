
from pyglet.gl import *
from pyglet.window import key

class Camera:
    """ A camera.
    """
    mode = 1
    x, y, z = 0, 0, -1000
    rx, ry, rz = 30, -45, 0
    w, h = 640, 480
    far = 100192
    fov = 60

    def view(self, width, height):
        """ Adjust window size.
        """
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        print("Viewport " + str(width) + "x" + str(height))
        if self.mode == 2:
            self.isometric()
        elif self.mode == 3:
            self.perspective()
        else:
            self.default()

    def default(self):
        """ Default pyglet projection.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def isometric(self):
        """ Isometric projection.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.w/2., self.w/2., -self.h/2., self.h/2., 0, self.far)
        glMatrixMode(GL_MODELVIEW)

    def perspective(self):
        """ Perspective projection.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.w)/self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)

    def key(self, symbol, modifiers):
        """ Key pressed event handler.
        """
        if symbol == key.F1:
            self.mode = 1
            self.default()
            print("Projection: Pyglet default")
        elif symbol == key.F2:
            print("Projection: 3D Isometric")
            self.mode = 2
            self.isometric()
        elif symbol == key.F3:
            print("Projection: 3D Perspective")
            self.mode = 3
            self.perspective()
        elif self.mode == 3 and symbol == key.NUM_SUBTRACT:
            self.fov -= 1
            self.perspective()
        elif self.mode == 3 and symbol == key.NUM_ADD:
            self.fov += 1
            self.perspective()
        else: 
            print("KEY " + key.symbol_string(symbol))

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
        if self.mode == 1: return
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)