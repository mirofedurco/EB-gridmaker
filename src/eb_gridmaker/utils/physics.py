import numpy as np
from copy import copy
from elisa import const as c, BinarySystem
from elisa.binary_system.model import (
    potential_value_primary,
    potential_value_secondary,
    pre_calculate_for_potential_value_primary,
    pre_calculate_for_potential_value_secondary
)
from elisa.binary_system.radius import calculate_side_radius
from .. utils.default_binary_model import DEFAULT_SYSTEM


def side_radius_potential_primary(radius, mass_ratio):
    """
    Returns potential for given side radius.

    :param radius: float;
    :param mass_ratio: float;
    :return: float;
    """
    # (F, q, d, phi, theta)
    args = (1.0, mass_ratio, 1.0, c.HALF_PI, c.HALF_PI)
    pot_args = pre_calculate_for_potential_value_primary(*args, return_as_tuple=True)
    return potential_value_primary(radius, mass_ratio, *pot_args)


def side_radius_potential_secondary(radius, mass_ratio):
    """
    Returns potential for given side radius.

    :param radius: float; side radius of the secondary component
    :param mass_ratio: float;
    :return: float;
    """
    # (F, q, d, phi, theta)
    args = (1.0, mass_ratio, 1.0, c.HALF_PI, c.HALF_PI)
    pot_args = pre_calculate_for_potential_value_secondary(*args, return_as_tuple=True)
    return potential_value_secondary(radius, mass_ratio, *pot_args)


def secondary_side_radius(mass_ratio, surface_potential):
    """
    Side radius of secondary component
    :param mass_ratio: float;
    :param surface_potential: float;
    :return: float; side radius
    """
    return calculate_side_radius(1.0, mass_ratio, 1.0, surface_potential, 'secondary')


def critical_inclination(r1, r2):
    """
    Returns minimum inclination for occurence of eclipses.

    :param r1: float;
    :param r2: float;
    :return:
    """
    summ = r1+r2
    if np.isscalar(summ):
        return np.degrees(np.arccos(r1+r2))
    else:
        result = np.full(summ.shape, np.nan)
        mask = summ < 1
        result[mask] = np.degrees(np.arccos(summ[mask]))
        return result


def correct_sma(mass_ratio, r1, r2):
    mid_g = 10 ** 1.5
    m1 = 4e30
    m2 = mass_ratio * m1

    sma1 = np.sqrt(c.G * m1 / (r1**2 * mid_g))
    sma2 = np.sqrt(c.G * m2 / (r2**2 * mid_g))

    sma = 0.5 * (sma1 + sma2)
    period = np.sqrt(c.FULL_ARC**2 * sma**3 / (c.G * (m1 + m2)))

    return 1.4374e-9 * sma, period / 86400


def initialize_system(mass_ratio, r1, r2, t1, t2, inclination, omega1, omega2):

    sma, period = correct_sma(mass_ratio, r1, r2)
    params = copy(DEFAULT_SYSTEM)
    params["system"].update({
        'inclination': inclination, 'mass_ratio': mass_ratio,
        'semi_major_axis': sma, 'period': period,
    })
    params["primary"].update({
        'surface_potential': omega1, 't_eff': t1,
        'gravity_darkening': 1.0, 'albedo': 1.0,
    })
    params["secondary"].update({
        'surface_potential': omega2, 't_eff': t2,
        'gravity_darkening': 1.0, 'albedo': 1.0,
    })

    return BinarySystem.from_json(params)
