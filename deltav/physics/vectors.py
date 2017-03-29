
    @classmethod
    def _rotate(cls, r, Ω, ι, ω):
        r = r[:, newaxis]
        r = (Rz(-Ω)*Rx(-ι)*Rz(-ω)).dot(r)
        return squeeze(asarray(r))


    @classmethod
    def _reverse(cls,
        true_anomaly,
        eccentric_anomaly,
        eccentricity,
        gravitational_parameter,
        semi_major_axis,
        long_of_ascending_node,
        inclination,
        argument_of_periapsis,
    ):

        r_distance = semi_major_axis * (1 - eccentricity * cos(eccentric_anomaly))

        pos_orbital = r_distance * array([
            cos(true_anomaly),
            sin(true_anomaly),
            0,
        ])

        vel_orbital = sqrt(gravitational_parameter*semi_major_axis)/r_distance * array([
            -sin(eccentric_anomaly),
            sqrt(1 - eccentricity**2) * cos(eccentric_anomaly),
            0,
        ])

        v_position = cls._rotate(pos_orbital, long_of_ascending_node, inclination, argument_of_periapsis)
        v_velocity = cls._rotate(vel_orbital, long_of_ascending_node, inclination, argument_of_periapsis)

        return v_position, v_velocity


        

def vecs_from_tle(tle, parent, satellite, epoch = None):
    """
    Only works for kepler (elliptical) orbits.
    """
    # https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
    # FIXME: make dates Julian
    delta_t = 0
    if epoch:
        interval = tle["epoch"] - epoch
        delta_t = interval.seconds + interval.days * 86400

    gravitational_parameter = G * parent.mass
    semi_major_axis = cbrt((tle["mean_motion"]/(2*pi))**2*gravitational_parameter)

    mean_anomaly = tle["mean_anomaly"] + delta_t * sqrt(gravitational_parameter/semi_major_axis**3)
    mean_anomaly %= 2*pi

    eccentricity = tle["eccentricity"]

    eccentric_anomaly = kepler(mean_anomaly, eccentricity, ACCURACY)

    arg1 = sqrt(1 + eccentricity) * sin(eccentric_anomaly/2)
    arg2 = sqrt(1 - eccentricity) * cos(eccentric_anomaly/2)
    true_anomaly = 2 * arctan2(arg1, arg2)

    return vecs_from_elements(
        true_anomaly,
        eccentric_anomaly, 
        eccentricity, 
        gravitational_parameter, 
        semi_major_axis, 
        tle["long_of_ascending_node"], 
        tle["inclination"], 
        tle["argument_of_periapsis"]
    )