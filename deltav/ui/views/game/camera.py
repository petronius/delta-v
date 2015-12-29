
import pyglet

from pyglet.gl import *
from pyglet.window import key

from numpy import *
from deltav.physics.helpers import Rx, Ry, Rz


class Camera:
    """ A camera.
    """
    mode = 1
    rx, ry, rz = 0, 0, 0
    near = 0.1
    far = 100192
    fov = 60

    FLAT="flat"
    NOFLAT="noflat"

    def __init__(self, w, h):

        self.w = w
        self.h = h

        self.x = 0.0
        self.y = 0.0
        self.z = 512

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

    # functions for setting up drawing
    def _perspective(self):
        self.mode = self.NOFLAT
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.w/self.h, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

        self.apply()

    def _flat(self):
        self.mode = self.FLAT

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, 0, self.far)
        glMatrixMode(GL_MODELVIEW)

        self.apply()

    def _rotate(self, x, y, _):
        """
        Rotate world coordinates x, y to screen coordinates
        """
        self._perspective() # reset before doing any maths
        # Ugh, C in Python...
        viewport = (GLint * 4)()
        pmat = (GLdouble * 16)()
        mmat = (GLdouble * 16)()

        nx = (GLdouble)()
        ny = (GLdouble)()
        nz = (GLdouble)()
        
        x, y, z = map(int, (x, y, _))
        
        glGetDoublev(GL_MODELVIEW_MATRIX, mmat)
        glGetDoublev(GL_PROJECTION_MATRIX, pmat)
        glGetIntegerv(GL_VIEWPORT, viewport)
        
        gluProject(x, y, _, mmat, pmat, viewport, nx, ny, nz)

        return nx.value, ny.value

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

    def scroll(self, delta):
        self.z += delta*20

    def apply(self):
        """ Apply camera transformation.
        """
        glLoadIdentity()
        if self.mode == self.FLAT:
            return
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)


    def text(self, s, coords):
        """
        Add text in the scene
        """

        x, y = self._rotate(*coords)

        self._flat()

        pyglet.text.Label(s,
            font_size=10,
            x = x + 10,
            y = y,
            anchor_x = "left",
            anchor_y = "top"
        ).draw()


    def draw_symbol(self, coords, color, offset=5):
        """
        Draw a flat symbol
        """
        x, y = self._rotate(*coords)

        a = (x, y+offset)
        b = (x+offset, y)
        c = (x-offset, y)

        self._flat()
        pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
            ('v2f', a + b + c),
            ('c3B', color*3),
        )


    def draw_loop(self, verticies, color):
        # Set up for more rendering
        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_LOOP)
        for vtx in verticies:
            glVertex3f(*vtx)
        glEnd()


    def draw_sphere(self, coords, radius, color):
        self._perspective()

        slices = (GLint)(30)
        stacks = (GLint)(30)

        glColor3f(*color)
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_NONE)
        gluQuadricDrawStyle(q, GLU_LINE)
        gluQuadricTexture(q, GL_TRUE)
        glTranslatef(0.0,0.0,0.0)
        glRotatef(90, 1, 0, 0)
        gluSphere(q, radius, slices, stacks)

        gluDeleteQuadric(q)
