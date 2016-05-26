"""
Handle all 3D drawing for the game view.

TODO:
- store ship/symbol/orbit colors on class
- solid planets?
- fix symbol jitter
- @perspective/@flat class method decorators
- Collaps draw_(ships|planets) into render()
"""
import pyglet
import numpy
import time

from numpy.linalg import norm

import deltav.ui

from deltav.gamestate.util import DebugClock

import OpenGL
# Has to be set before more imports
OpenGL.ERROR_CHECKING = deltav.configure.DEBUG
from OpenGL.GL import *
from OpenGL.GLU import *



class View3D:

    # Scale factor for the game view, in meters
    SCALE = 1e-5

    FLAT = "flat"
    NOFLAT = "noflat"

    LABEL_COLOR = (255, 255, 255, 255)
    ORBIT_COLOR = (0, 0, 255)

    SYMBOLS = {
        "ships":   ("triangle", (0, 255, 0)),    # passing in the night
        "bullets": ("diamond", (255, 0, 0)),     # a hail of
        "debris":  ("square", (100, 100, 100)),  # nothing but
        "bodies":  (None, (.5, 0, 0)),           # rising to the surface
    }

    FONT_FACE = "Droid Sans Mono"

    DEFAULT_CAMERA_POS = (0, 0, 312)
    DEFAULT_CAMERA_ROT = (-45, 0, -45)

    near = 2
    far = 10000000
    # whereeever you aaaaaaare
    fov = 60


    def __init__(self, game_view, bounds, center_on):

        self.bx, self.by, self.w, self.h = bounds

        self.rx, self.ry, self.rz = self.DEFAULT_CAMERA_ROT
        self.x, self.y, self.z = self.DEFAULT_CAMERA_POS

        self.mode = self.NOFLAT
        # GL initialization
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

        self.center_on(center_on)
        self.render_clock = DebugClock()


    def center_on(self, coords, reset = False):
        if reset:
            self.rx, self.ry, self.rz = self.DEFAULT_CAMERA_ROT
            self.x, self.y, self.z = self.DEFAULT_CAMERA_POS
        x, y, z = map(lambda x: x*self.SCALE, coords)
        self.center = numpy.array([x, y, z])


    def do_camera(self):
        """
        Apply camera transformation.
        """
        glLoadIdentity()
        if self.mode == self.FLAT:
            return
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)


    def render(self, game_view):

        self.v3d_batch = pyglet.graphics.Batch() # FIXME: don't make new batch and new labels on each render!

        scene = game_view.get_scene_data()
        # _debug_boxes = game_view.game_state.get_debug_boxes()
        tui_times = map(lambda x: str(int(x*1000)), (game_view.ui_clock.latest, game_view.ui_clock.avg, game_view.ui_clock.max))
        sim_times = map(lambda x: str(int(x*1000)), scene["timer"])
        ren_times = map(lambda x: str(int(x*1000)), (self.render_clock.latest, self.render_clock.avg, self.render_clock.max))

        self.text("sim time (recent): "+"/".join(sim_times)+" ms", (10,self.h - 10, -1), batch=self.v3d_batch)
        self.text("3d render time:    "+"/".join(ren_times)+" ms", (10,self.h - 30, -1), batch=self.v3d_batch)
        self.text("total draw time:   "+"/".join(tui_times)+" ms", (10,self.h - 50, -1), batch=self.v3d_batch)

        try: 
            self.render_clock.start_timer()

            self.do_camera()

            for k, list_ in scene["objects"].items():
                for uuid, obj in list_.items():

                    if obj.get("orbit") and obj["orbit"].get("plot"):

                        if game_view.get_option("tracking", "orbits"):
                            orbit = [self._world_to_scene(p) for p in obj["orbit"]["plot"]]
                            if obj["orbit"]["is_elliptical"]:
                                self.draw_loop(orbit, self.ORBIT_COLOR)
                            else:
                                self.draw_line(orbit, self.ORBIT_COLOR)

                    # Normalize from a numpy array
                    coords = self._world_to_scene(obj.get("position", (0,0,0)))

                    if k != "bodies":

                        coords = self._scene_to_screen(coords)

                        if game_view.get_option("tracking", "labels"):
                            self.text(obj["name"], coords, batch=self.v3d_batch)

                        if game_view.get_option("tracking", "symbols"):
                            sym, color = self.SYMBOLS[k]
                            self.draw_symbol(sym, coords, color)

                    elif game_view.get_option("tracking", "bodies"):
                        r = obj["radius"] * self.SCALE
                        self.draw_sphere(coords, r, self.SYMBOLS[k][1])

            # if _debug_boxes:
            #     for box in _debug_boxes:
            #         self.draw_cube(*box)

            self.v3d_batch.draw()

            self.draw_adi(*scene["player"]["attitude"])

            # Reset when we're done, for other rendering actions that need the
            # default pyglet behaviour
            width, height = deltav.ui.game_window.width, deltav.ui.game_window.height
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glViewport(0, 0, width, height)
            glOrtho(0, width, 0, height, -1, 2)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            self.render_clock.record_time()
        finally:
            self.render_clock.clear_timer()
    #
    # Rendering setup
    #
    
    def _perspective(self):
        if self.mode != self.NOFLAT:
            self.mode = self.NOFLAT

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glViewport(self.bx, self.by, self.w, self.h)
            gluPerspective(self.fov, self.w/self.h, self.near, self.far)
            glMatrixMode(GL_MODELVIEW)

            glEnable(GL_DEPTH_TEST)

            self.do_camera()

    def _flat(self):
        if self.mode != self.FLAT:
            self.mode = self.FLAT

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glViewport(self.bx, self.by, self.w, self.h)
            glOrtho(0, self.w, 0, self.h, -1, 2)
            glMatrixMode(GL_MODELVIEW)

            self.do_camera()

    #
    # Coordinate mapping
    #

    def _world_to_scene(self, coords):
        """
        Convert physics coordinates to render coordinates.
        """
        result = tuple(map(lambda x: x*self.SCALE, coords)) - self.center
        return tuple(result)

    def _scene_to_screen(self, coords):
        """
        Rotate world coordinates x, y to screen coordinates
        """
        x, y, z = coords
        self._perspective() # reset before doing any maths

        mmat = glGetDoublev(GL_MODELVIEW_MATRIX)
        pmat = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        x, y, z = gluProject(x, y, z, mmat, pmat, viewport)

        x -= self.bx
        y -= self.by

        return int(x), int(y), int(z)

    def drag(self, dx, dy, button):
        """
        Mouse drag event handler.
        """
        if button == 1:
            self.x -= dx*2
            self.y -= dy*2
        elif button == 2:
            self.z += dy*10
        elif button == 4:
            self.rz += dx/4.
            self.rx -= dy/4.

    def scroll(self, delta):
        """
        Scroll wheel
        """
        self.z += delta*10

    #
    # Drawing functions.
    #

    def text(self, s, coords, batch):
        """
        Add text in the scene

        FIXME: position labels optimally for location on screen (ie, don't draw
                offscreen).
        BONUS: don't let labels be drawn on each other
        """
        x, y, z = coords
        if z < 1:

            self._flat()

            s = '<font face="%s" size="1" color="#FFFFFF">%s</font>' % (self.FONT_FACE, s)

            pyglet.text.HTMLLabel(s,
                x = x + 10,
                y = y,
                anchor_x = "left",
                anchor_y = "top",
                batch = batch,
            )


    def _symbol_points(self, type_, coords, offset):
        x, y, z = coords
        if type_ == "square":
            return pyglet.gl.GL_QUADS, (
                (x-offset, y+offset, z),
                (x+offset, y+offset, z),
                (x+offset, y-offset, z),
                (x-offset, y-offset, z),
            )
        elif type_ == "diamond":
            return pyglet.gl.GL_QUADS, (
                (x, y+offset, z),
                (x+offset, y, z),
                (x, y-offset, z),
                (x-offset, y, z),
            )
        elif type_ == "triangle":
            return pyglet.gl.GL_TRIANGLES, (
                (x, y+offset, z),
                (x+offset, y, z),
                (x-offset, y, z),
            )
        else:
            raise ValueError("Invalid shape: %s" % type_)


    def draw_symbol(self, type_, coords, color, size = 5):
        """
        Draw a flat symbol
        """
        x, y, z = coords
        if z < 1:
            mode, points = self._symbol_points(type_, (x, y, z), size)
            ct = len(points)
            vec_list = ()
            for pt in points:
                vec_list += pt
            self._flat()
            pyglet.graphics.draw(ct, mode,
                ('v3f', vec_list),
                ('c3B', color*ct),
            )


    def draw_cube(self, p1, p2):
        p1 = self._world_to_scene(p1)
        p2 = self._world_to_scene(p2)

        color = (0.0, 0.0, 1) # the diagonal
        self.draw_line((p1, p2), color)

        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_STRIP)
        # top
        glVertex3f(p1[0], p1[1], p1[2])        
        glVertex3f(p1[0], p1[1], p2[2])

        glVertex3f(p2[0], p1[1], p2[2])

        glVertex3f(p2[0], p1[1], p1[2])
        
        glVertex3f(p1[0], p1[1], p1[2])
        # bottom
        glVertex3f(p1[0], p2[1], p1[2])        
        glVertex3f(p1[0], p2[1], p2[2])
        
        glVertex3f(p2[0], p2[1], p2[2])
        
        glVertex3f(p2[0], p2[1], p1[2])
        
        glVertex3f(p1[0], p2[1], p1[2])
        # sides
        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p1[0], p1[1], p2[2])
        glVertex3f(p1[0], p2[1], p2[2])

        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p2[0], p1[1], p2[2])
        glVertex3f(p2[0], p2[1], p2[2])

        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p2[0], p1[1], p1[2])
        glVertex3f(p2[0], p2[1], p1[2])

        glEnd()



    def draw_loop(self, verticies, color):
        # Set up for more rendering
        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_LOOP)
        for vtx in verticies:
            glVertex3f(*vtx)
        glEnd()


    def draw_line(self, verticies, color):
        self._perspective()
        glColor3f(*color)
        glBegin(GL_LINE_STRIP)
        for vtx in verticies:
            glVertex3f(*vtx)
        glEnd()


    def draw_sphere(self, coords, radius, color):
        self._perspective()

        stacks = slices = 20

        glColor3f(*color)
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_NONE)
        gluQuadricDrawStyle(q, GLU_LINE)
        gluQuadricTexture(q, GL_TRUE)
        glTranslatef(*coords)
        gluSphere(q, radius, slices, stacks)

        gluDeleteQuadric(q)

    def draw_adi(self, pitch, yaw, roll):

        # custom viewport

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(int(self.w/2), 0, 200, 200)
        gluPerspective(90, 1, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

        # custom camera

        glLoadIdentity()
        glTranslatef(0, 0, -20)
        # camera rot
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)

        # guides
        glColor3f(1, 0, 0)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)        
        glVertex3f(100, 0, 0)
        glEnd()
        glColor3f(0, 1, 0)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)        
        glVertex3f(0, 100, 0)
        glEnd()
        glColor3f(0, 0, 1)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)        
        glVertex3f(0, 0, 100)
        glEnd()



        # self._perspective()

        stacks = slices = 10
        r = 10

        c = (
            self.x + 10,
            self.y - 10,
            self.z -20
        )

        glColor3f(0, 1.0, 1.0)


        glEnable(GL_CLIP_PLANE0)

        rotations = (
            (90, 1, 0, 0),
            (pitch, 1, 0, 0),
            (yaw, 0, 1, 0),
            (roll, 0, 0, 1),
        )
        for rs in rotations:
            glRotatef(*rs)

        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_NONE)
        gluQuadricDrawStyle(q, GLU_LINE)
        gluQuadricTexture(q, GL_TRUE)

        glClipPlane(GL_CLIP_PLANE0, (0, 1, 0, 0))
        gluSphere(q, r, slices, stacks)

        glColor3f(1.0, 0, 1.0)
        glClipPlane(GL_CLIP_PLANE0, (0, -1, 0, 0))

        q1 = gluNewQuadric()
        gluQuadricNormals(q, GLU_NONE)
        gluQuadricDrawStyle(q, GLU_LINE)
        gluQuadricTexture(q, GL_TRUE)
        
        gluSphere(q, r, slices, stacks)

        gluDeleteQuadric(q1)
        gluDeleteQuadric(q)



        glDisable(GL_CLIP_PLANE0)


