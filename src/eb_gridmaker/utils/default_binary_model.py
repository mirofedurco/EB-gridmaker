DEFAULT_SYSTEM = {
    "system": {
        "inclination": None,
        "period": None,
        "argument_of_periastron": 0.0,
        "gamma": 0.0,
        "eccentricity": 0.0,
        "primary_minimum_time": 0.0,
        "phase_shift": 0.0,
        "semi_major_axis": None,  # default unit is solRad
        "mass_ratio": None
    },
    "primary": {
        "surface_potential": None,
        "synchronicity": 1.0,
        "t_eff": None,  # parameters can be provided in string representation consistent with astropy unit format
        "metallicity": 0.0
    },
    "secondary": {
        "surface_potential": None,
        "synchronicity": 1.0,
        "t_eff": None,
        "metallicity": 0.0
    }
}