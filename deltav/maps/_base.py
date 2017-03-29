
from rtree import index

from deltav.geometry import spheres_collide
from deltav.worldbuilding import random_ship_name

class BaseScene(object):
    """
    Wrapper for getting information about the current scene.

    Uses an RTree implementation internally that works on bounding boxes, rather
    than points (we may find this more useful in the long run), and has the additional
    advantage of not being of limited size.

    Further notes:

    - Lots of deleting from the index is expensive, but we don't want it to grow too
      large. So we add a flush() method that just dumps the index and builds a new one
      every simulation iteration.
    
    """

    def __init__(self):
        self.objects = {}
        self.bodies = set() # Treated differently because square boxes aren't good enough
        self._ip = index.Property()
        self._ip.dimension = 3
        self._ip.leaf_capacity = 100
        self._new_index()

    def __iter__(self):
        for j in list(self.objects.values()):
            yield j


    def load_player(self, client):
        name = random_ship_name()

    #
    # Scene tracking
    #

    def visible_objects(self, obj):
        # For each other object in the scene, draw a ray, and make sure that
        # planets/asteroids/etc. don't intersect. For now, we are only checking
        # a) non-ship bodies, and
        # b) sphere approximations
        #
        # This isn't a permanent solution, though.
        for obj2 in self.objects.values():
            if obj2.tracking_id != obj.tracking_id:
                for body in self.bodies:
                    if line_intersects_sphere(
                        obj1.get_position(),
                        obj2.get_position(),
                        body.get_position(),
                        body.radius
                    ):
                        break
                else:
                    yield obj2

    def get_collisions(self, obj):
        id_ = hash(obj.tracking_id)
        box = self._get_box(obj)
        for nearby in self.index.intersection(box):
            if nearby != id_: # Don't collide with self
                yield self.objects.get(nearby)
        # Check collision with any bodies
        for body in self.bodies:
            if spheres_collide(obj.get_position(), body.get_position(), obj.radius, body.radius):
                yield body

    def tick(self, gt):
        del self.index
        self._new_index()
        collisions = []
        marked = []

        for obj in self.objects.values():
            obj.game_tick(gt)               # Update epoch of orbit
            box = self._get_box(obj)        # Get the new bounding box
            id_ = hash(obj.tracking_id)
            self.index.insert(id_, box)     # Add to index

            #
            # FIXME: one issue with this is that if gt is large, or objects are
            #        moving very fast, we run the risk of missing collisions 
            #        that happened between ticks. The solution is to draw the
            #        bounding box to include intermediate points. The downside
            #        of this is that it can create collisions in the "wake" of
            #        objects, or in what should properly be near-misses. It may
            #        also fail if the path of an object is very fast around a
            #        perigee or apogee.
            #
            for obj2 in self.get_collisions(obj):
                # Only moved objects have been added back to the index at this
                # point, so we have no risk of colliding with an object in a
                # stale position.
                collisions.append((obj, obj2))

        # Perform collisions, remove old objects, add new ones
        for obj1, obj2 in collisions:
            new_debris = self.collide(obj1, obj2)
            self.add_all(*new_debris)


    def collide(self, obj1, obj2):
        # FIXME: not all collisions should result in total obliteration
        debris = []
        if obj1.destructable:
            impact_vector1 = obj2.get_velocity()
            debris += obj1.explode(impact_vector1)
            self.remove(obj1)
        if obj2.destructable:
            impact_vector2 = obj1.get_velocity()
            debris += obj2.explode(impact_vector2)
            self.remove(obj2)
        return debris

    def _new_index(self):
        self.index = index.Index(interleaved=False, properties=self._ip)

    def _get_box(self, obj):
        px, py, pz = obj.get_position()
        r = obj.radius/2
        box = (px-r, px+r, py-r, py+r, pz-r, pz+r)
        return box

    def add(self, obj):
        id_ = hash(obj.tracking_id)
        self.objects[id_] = obj

    def remove(self, obj):
        id_ = hash(obj.tracking_id)
        self.objects.pop(id_, "")

    def remove_all(self, *objs):
        for obj in objs:
            self.remove(obj)

    def add_all(self, *objs):
        for obj in objs:
            self.add(obj)

    def add_body(self, obj):
        self.bodies.add(obj)

    #
    # "Map" functions.
    #

    def setup(self):
        # Add ships, planets, etc. here.
        raise NotImplementedError()
