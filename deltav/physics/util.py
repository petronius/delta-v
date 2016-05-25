
import datetime

from deltav.physics.helpers import _float

#
# FIXME: I guess dates should be Julian
#

RAD = _float("0.0174533")

def load_tle_file(file_path, max = 0):
    with open(file_path) as fp:
        data = fp.readlines()
        # Group into three-line sets
        sets = [data[r:r+3] for r in range(0, len(data), 3)]
        for s in sets:
            tle = parse_tle(s)
            yield tle
            max -= 1
            if max == 0:
                break


def parse_tle(lines):
    """
    All units converted to meters, radians, and seconds
    """
    name = lines[0].strip()
    # field description: https://en.wikipedia.org/wiki/Two-line_element_set
    epoch_year = int(lines[1][19:20])
    if epoch_year < 20:
        epoch_year = 2000 + epoch_year
    else:
        epoch_year = 1900 + epoch_year
    epoch_day = _float(lines[1][21:32])
    epoch = datetime.datetime(epoch_year, 1, 1) + datetime.timedelta(days=float(epoch_day-1))
    return {
        # line 0
        "name":                                 name,
        # line 1
        "satellite_number":                     lines[1][2:6],
        "classification":                       lines[1][7],
        "international_designator":             lines[1][9:16],
        "epoch":                                epoch,
        "first_time_derivative":                _float(lines[1][33:42]),
        "second_time_derivative":               _float(lines[1][44:49]+"e"+lines[1][50:52]),
        "bstar_drag_term":                      _float(lines[1][53:58]+"e"+lines[1][68:70]),
        # ephemeris type is skipped, since it is always 0
        "element_set_number":                   lines[1][64:67],
        # line 2
        "inclination":                          _float(lines[2][8:15])  * RAD,
        "long_of_ascending_node":               _float(lines[2][17:24]) * RAD,
        "eccentricity":                         _float("0."+lines[2][26:33]),
        "argument_of_periapsis":                _float(lines[2][34:41]) * RAD,
        "mean_anomaly":                         _float(lines[2][43:50]) * RAD,
        "mean_motion":                          86400 / _float(lines[2][52:62]),
        "revolution_number_at_epoch":           _float(lines[2][63:67]),
    }


if __name__ == "__main__":

    from deltav.physics.orbit import Orbit
    from deltav.physics.body import Body
    from deltav.ships import MobShip
    earth = Body(5.972e24, 6371000)
    for tle in load_tle_file("stations.txt"):
        o = Orbit.from_tle(tle, earth, MobShip(tle["name"]))
        print(o, o.v_position, o.v_velocity)

