from deltav.physics.helpers import _float

# The gravitational constant
G = _float("6.67408e-11")
# Unit vector
K = array([0, 0, 1])

# Used for comparisons, because of floating point rounding error
ACCURACY = _float("1e-12")