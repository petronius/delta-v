# FIXME: make this into tests, and do more from Horizons ephemerides

earth = Body(5.972e24, 6371000) # kg, m

iss = PlayerShip("ISS")
iss.mass = 419600 # kg

# Horizons ephemerides, in km and km/s, multiplied out to meters
# 2457380.183935185 = A.D. 2015-Dec-23 16:24:52.0000 (TDB)

# pyglet.clock.schedule_interval(update, 1/24.0)

v_position = numpy.array([
    -9.389136074764635E+02 * 1000,
    -5.116319908091118E+03 * 1000,
    4.342059664304661E+03 * 1000,
], dtype="float128")

v_velocity = numpy.array([
    6.628784989010491E+00 * 1000,
    1.718224103100249E+00 * 1000,
    3.457710395445335E+00 * 1000,
], dtype="float128")

# Test
test_values = {
    "eccentricity": 3.743276399381678E-04,
    "argument_of_periapsis": radians(5.857936559219403E+01),
    "inclination": radians(5.157910786454486E+01),
    "mean_anomaly": radians(3.563009472454253E+02),
    "true_anomaly": radians(3.562981785606661E+02),
    "semi_major_axis": 6.778354516341115E+03 * 1000,
    "long_of_asc_node": radians(2.181413903120838E+02),
}


iss.orbit(earth, v_position, v_velocity)

print(iss._orbit)

args = copy.deepcopy(test_values)
args.pop("true_anomaly", "")
args["gravitational_parameter"] = iss._orbit.gravitational_parameter
reversed = iss._orbit.reverse(**args)

for k, v in test_values.items():
    rv = getattr(iss._orbit, k)
    if rv != v:
        print(k, ":")
        print(" ", v)
        print(" ", rv)
print("reversed:")
print(" ",v_position)
print(" ", reversed[0])
print("--")
print(" ",v_velocity)
print(" ", reversed[1])