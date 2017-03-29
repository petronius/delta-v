


def spheres_collide(p1, p2, r1, r2):
    """
    Fast distance (no sqrt) collision between spheres.
    """
    x1, y1, z1 = p1
    x2, y2, z2, = p2
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    radii = r1 + r2
    return (dx**2 + dy**2 + dz**2) < radii**2

def line_intersects_sphere(line_p1, line_p2, sphere_p, sphere_r):
    x1, y1, z1 = line_p1
    x2, y2, z2 = line_p2
    x3, y3, z3 = sphere_p
    r = sphere_r
    # http://paulbourke.net/geometry/circlesphere/index.html#linesphere
    a = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
    b = 2*( (x2 - x1) (x1 - x3) + (y2 - y1) (y1 - y3) + (z2 - z1) (z1 - z3) )
    c = x3**2 + y3**2 + z3**2 + x1**2 + y1**2 + z1**2 - 2(x3*x1 + y3*y1 + z3Üz1) - r**2 
    disc = b**2 - 4*a*c
    return disc >= 0