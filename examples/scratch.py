from elisa import BinarySystem, Star


community_params = {
    "system": {
        "inclination": 86.0,
        "period": 10.1,
        "argument_of_periastron": 90.0,
        "gamma": 0.0,
        "eccentricity": 0.0,
        "primary_minimum_time": 0.0,
        "phase_shift": 0.0,
        "semi_major_axis": 10.5,  # default unit is solRad
        "mass_ratio": 0.5
    },
    "primary": {
        "surface_potential": 7.1,
        "synchronicity": 1.0,
        "t_eff": "6900.0 K",  # parameters can be provided in string representation consistent with astropy unit format
        # "gravity_darkening": 1.0,
        # "albedo": 1.0,
        # "metallicity": 0.0
    },
    "secondary": {
        "surface_potential": 7.1,
        "synchronicity": 1.0,
        "t_eff": 5000.0,
        "gravity_darkening": 1.0,
        "albedo": 1.0,
        # "metallicity": 0.0
    }
}

bs = BinarySystem.from_json(community_params)

params = {
    "system": {
        "inclination": 86.0,
        "period": 10.1,
        "argument_of_periastron": 90.0,
        "gamma": 0.0,
        "eccentricity": 0.0,
        "primary_minimum_time": 0.0,
        "phase_shift": 0.0
    },
    "primary": {
        "mass": 2.0,
        "surface_potential": 7.1,
        "synchronicity": 1.0,
        "t_eff": "5500 K",  # parameters can be provided in string representation consistent with astropy unit format
        # "gravity_darkening": 1.0,
        "albedo": 1.0,
        # "metallicity": 0.0
    },
    "secondary": {
        "mass": 1.0,
        "surface_potential": 7.1,
        "synchronicity": 1.0,
        "t_eff": 5000.0,
        "gravity_darkening": 1.0,
        "albedo": 1.0,
        # "metallicity": 0.0
    }
}

# primary = Star(**params['primary'])
# secondary = Star(**params['secondary'])
# bs = BinarySystem(primary=primary, secondary=secondary, **params['system'])

print(bs.primary.gravity_darkening, bs.secondary.gravity_darkening)
print(bs.primary.albedo, bs.secondary.albedo)
