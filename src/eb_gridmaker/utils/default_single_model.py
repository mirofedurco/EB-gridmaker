DEFAULT_SYSTEM = {
    "system": {
        "inclination": None,
        "rotation_period": None,
        "gamma": 0.0,
        "reference_time": 0.0,
        "phase_shift": 0.0
    },
    "star": {
        "mass": None,
        "t_eff": None,
        "metallicity": 0.0,
        "polar_log_g": None,   # you can also use logarithmic units using json/dict input
        "spots": [
            {
                "longitude": None,
                "latitude": None,
                "angular_radius": None,
                "temperature_factor": None
            }
        ]
    }
}