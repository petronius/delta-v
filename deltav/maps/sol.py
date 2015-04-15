
import ships
import celestials

MOBS = {
    "ISEA Boshin": {
        "radius": 100,
        "mean_distance": 150000,
        "orbital_period": 90,
        "primary": "Earth",
        "position": (0, 0),
        "type": ships.MobShip,
    },
    "SX 108-P": {
        "radius": 200,
        "mean_distance": 50000,
        "orbital_period": 60,
        "primary": "Luna",
        "position": (120, 0),
        "type": ships.MobShip,
    },
    "SX 789-P": {
        "radius": 200,
        "mean_distance": 60000,
        "orbital_period": 60,
        "primary": "Luna",
        "position": (110, 0),
        "type": ships.MobShip,
    },
    "MCA 2128-C Heavy": {
        "radius": 300,
        "mean_distance": 100000,
        "orbital_period": 200,
        "primary": "Mars",
        "position": (0, 0),
        "type": ships.MobShip,
    },
} #[ships.MobShip(), ships.MobShip()]

# http://en.wikipedia.org/wiki/List_of_gravitationally_rounded_objects_of_the_Solar_System#Planets
# but positions are random
BODIES = {
    "Sun": {
        "radius": 695800000,
        "type": celestials.Star,
        "orbits": {
            "Mercury": {
                # in meters
                "radius": 2439640,
                # in meters
                "mean_distance": 57909175000,
                # in minutes
                "orbital_period": 0.2408467 * 365 * 24 * 60,
                # arbitrarily chosen
                "position": (120, 0),
            },
            "Venus": {
                "radius": 6051590,
                "mean_distance": 108208930,
                "orbital_period": 0.61519726 * 365 * 24 * 60,
                "position": (350, 0),
            },
            "Earth": {
                "radius": 6378100,
                "mean_distance": 149597890000,
                "orbital_period": 1.0000174 * 365 * 24 * 60,
                "position": (70, 0),
                "orbits": {
                    "Luna": {
                        "radius": 1737000,
                        "mean_distance": 384399000,
                        "orbital_period": 27.32158 * 24 * 60,
                        "position": (20, 0),
                    },
                },
            },
            "Mars": {
                "radius": 3397000,
                "mean_distance": 227936640000,
                "orbital_period": 1.8808476 * 365 * 24 * 60,
                "position": (90, 0),
            },
            "Jupiter": {
                "radius": 71492680,
                "mean_distance": 778412010000,
                "orbital_period": 11.862615 * 365 * 24 * 60,
                "position": (110, 0),
                "orbits": {
                    "Io": {
                        "radius": 1815000,
                        "mean_distance": 421600000,
                        "orbital_period": 1.769138 * 24 * 60,
                        "position": (80, 0),
                    },
                    "Europa": {
                        "radius": 1569000,
                        "mean_distance": 670900000,
                        "orbital_period": 27.32158 * 24 * 60,
                        "position": (330, 0),
                    },
                    "Ganymede": {
                        "radius": 2634100,
                        "mean_distance": 1070400000,
                        "orbital_period": 27.32158 * 24 * 60,
                        "position": (250, 0),
                    },
                    "Callisto": {
                        "radius": 2410300,
                        "mean_distance": 1882700000,
                        "orbital_period": 27.32158 * 24 * 60,
                        "position": (100, 0),
                    },
                },
            },
            "Saturn": {
                "radius": 60267140,
                "mean_distance": 1426725400000,
                "orbital_period": 29.447498 * 365 * 24 * 60,
                "position": (310, 0),
                "orbits": {
                    "Mimas": {
                        "radius": 198300,
                        "mean_distance": 185520000,
                        "orbital_period": 0.942422 * 24 * 60,
                        "position": (80, 0),
                    },
                    "Enceladus": {
                        "radius": 533000,
                        "mean_distance": 237948000,
                        "orbital_period": 1.370218 * 24 * 60,
                        "position": (330, 0),
                    },
                    "Tethys": {
                        "radius": 533000,
                        "mean_distance": 294619000,
                        "orbital_period": 1.887802 * 24 * 60,
                        "position": (250, 0),
                    },
                    "Dione": {
                        "radius": 561700,
                        "mean_distance": 377396000,
                        "orbital_period": 2.736915 * 24 * 60,
                        "position": (100, 0),
                    },
                    "Rhea": {
                        "radius": 764300,
                        "mean_distance": 527108000,
                        "orbital_period": 4.518212 * 24 * 60,
                        "position": (100, 0),
                    },
                    "Titan": {
                        "radius": 2576000,
                        "mean_distance": 1221870000,
                        "orbital_period": 15.945 * 24 * 60,
                        "position": (250, 0),
                    },
                    "Iapetus": {
                        "radius": 735600,
                        "mean_distance": 3560820,
                        "orbital_period": 79.322 * 24 * 60,
                        "position": (100, 0),
                    },
                },
            },
            "Uranus": {
                "radius": 2557250,
                "mean_distance": 2870972200000,
                "orbital_period": 84.016846 * 365 * 24 * 60,
                "position": (60, 0),
                "orbits": {
                    "Miranda": {
                        "radius": 235800,
                        "mean_distance": 129390000,
                        "orbital_period": 1.4135 * 24 * 60,
                        "position": (80, 0),
                    },
                    "Ariel": {
                        "radius": 578900,
                        "mean_distance": 190900000,
                        "orbital_period": 2.520 * 24 * 60,
                        "position": (330, 0),
                    },
                    "Umbriel": {
                        "radius": 584700,
                        "mean_distance": 266000000,
                        "orbital_period": 4.144 * 24 * 60,
                        "position": (250, 0),
                    },
                    "Titania": {
                        "radius": 788900,
                        "mean_distance": 436300000,
                        "orbital_period": 8.706 * 24 * 60,
                        "position": (100, 0),
                    },
                    "Oberon": {
                        "radius": 761400,
                        "mean_distance": 583519000,
                        "orbital_period": 13.46 * 24 * 60,
                        "position": (100, 0),
                    },
                },
            },
            "Neptune": {
                "radius": 24766360,
                "mean_distance": 4498252900000,
                "orbital_period": 164.79132 * 365 * 24 * 60,
                "position": (80, 0),
                "orbits": {
                    "Triton": {
                        "radius": 1353400,
                        "mean_distance": 354759000,
                        "orbital_period": -5.877 * 24 * 60,
                        "position": (80, 0),
                    },
                },
            },
        },
    },
}

CELESTIALS  = {}

def build_orbits(data, parent = None):

    for k, v in data.items(): 

        cls = v.pop("type", None) or celestials.Planet
        obj = cls(k, v.pop("radius"))
        orbits = v.pop("orbits", None)
        CELESTIALS[k] = obj

        if parent:
            obj.set_orbit(parent, **v)

        if orbits:
            build_orbits(orbits, obj)

def build_mobs():

    for k, v in MOBS.items():

        cls = v.pop("type", None) or ships.MobShip
        obj = cls(k, v.pop("radius"))
        MOBS[k] = obj

        celestial = CELESTIALS[v.pop("primary")]

        obj.set_orbit(celestial, **v)



build_orbits(BODIES)
build_mobs()