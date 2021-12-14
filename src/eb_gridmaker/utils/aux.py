import numpy as np
from math import modf
from copy import copy

from . default_single_model import DEFAULT_SYSTEM as S_DEFAULT_SINGLE_SYSTEM
from . default_binary_model import DEFAULT_SYSTEM as DEFAULT_BINARY_SYSTEM
from . physics import (
    back_radius_potential_primary,
    back_radius_potential_secondary,
    correct_sma
)
from .. import config


def estimate_size(grid_size):
    """
    Estimation of the physical size of the database based on the grid size.

    :param grid_size: int;
    :return: float; size in Gb
    """
    return grid_size * len(config.PASSBAND_COLLUMNS) * (config.N_POINTS + 7 + 10) * 64 / (8 * 1024**3)


def generate_i(i_crit, step):
    """
    Generates inclination for table generator.

    :param i_crit: flaot; critical inclination in deg
    :param step: float; (0.0, 1.0) inclination iteration parameter
    :return: float; inclination
    """
    incl = i_crit + step * (90 - i_crit) if config.SAMPLE_OVER_CRITICAL_INCLINATION \
        else config.MINIMUM_INCLINATION + step * (i_crit - config.MINIMUM_INCLINATION)
    return incl


def get_params_from_id(id):
    if id >= config.CUMULATIVE_PRODUCT[-1]:
        raise ValueError('ID is above maximum')
    result, indices = [], []

    cumulative_product = config.CUMULATIVE_PRODUCT[:-1]
    n_hyper_cube = np.concatenate((cumulative_product[::-1], [1, ]))

    remainder = copy(id)
    for ii, param in enumerate(config.SAMPLING_ORDER):
        index, remainder = divmod(remainder, n_hyper_cube[ii])

        result.append(param[index])
        indices.append(index)

    return result, indices


def draw_single_star_params():
    """
    Drawing parameters for single star system with spots. In case of rotational period,
    only period/critical period was determined.

    :return: Dict; dictionary used to initialize a SingleSystem
    """
    params = copy(S_DEFAULT_SINGLE_SYSTEM)
    params["star"]["mass"] = np.random.uniform(config.M_RANGE[0], config.M_RANGE[1])
    params["star"]["polar_log_g"] = np.random.uniform(config.LOG_G_RANGE[0], config.LOG_G_RANGE[1])
    # params["star"]["t_eff"] = np.random.uniform(config.T_EFF_RANGE[0], config.T_EFF_RANGE[1])
    params["star"]["t_eff"] = np.random.choice(config.T_CHOICES)
    params["system"]["inclination"] = np.random.uniform(config.I_RANGE[0], config.I_RANGE[1])
    params["system"]["rotation_period"] = np.random.uniform(config.P_RANGE[0], config.P_RANGE[1])

    for spot in params["star"].get("spots", []):
        spot["longitude"] = np.random.uniform(config.LONGITUDE_RANGE[0], config.LONGITUDE_RANGE[1])
        spot["latitude"] = np.random.uniform(config.LATITUDE_RANGE[0], config.LATITUDE_RANGE[1])
        spot["angular_radius"] = np.random.uniform(config.SPOT_RADIUS_RANGE[0], config.SPOT_RADIUS_RANGE[1])
        t_diff = np.random.uniform(config.T_DIFF_SPOT_RANGE[0], config.T_DIFF_SPOT_RANGE[1])
        spot["temperature_factor"] = (params["star"]["t_eff"] + t_diff) / params["star"]["t_eff"]

    return params


def draw_eccentric_system_params():
    """
    Draw random parameters for sampling of eccentric EBs.

    :return: Tuple(dict, tuple); list of binary system parameters with random parameters included,
                                 tuple of equivalent radii.
    """
    params = copy(DEFAULT_BINARY_SYSTEM)
    params["system"]["inclination"] = 90     # placeholder
    params["system"]["argument_of_periastron"] = np.random.randint(config.ARG0_RANGE[0], config.ARG0_RANGE[1], dtype=int)
    params["system"]["eccentricity"] = np.random.uniform(config.E_RANGE[0], config.E_RANGE[1])
    params["system"]["mass_ratio"] = np.random.choice(config.Q_ARRAY)

    for component in ['primary', 'secondary']:
        params[component]['t_eff'] = np.random.choice(config.T_CHOICES)

    radii = draw_radii()

    return params, radii


def draw_radii():
    """
    Draw equivalent radii of the components
    :return:
    """
    while True:
        r1 = np.round(np.random.exponential(0.15), 2) + config.R_RANGE[0]
        r2 = np.round(np.random.exponential(0.15), 2) + config.R_RANGE[0]

        if r1 < 0.5 and r2 < 0.5:
            break

    return r1, r2


def assign_eccentric_system_params(params, radii):
    """
    Assign synchrinicities, surface potentials, semi-major axis and mass ratio.

    :param params: Dict; system parameters in JSON format
    :param radii: Tuple; back radii
    :return: Dict; parameters
    """
    eccentricity = params["system"]["eccentricity"]
    synchronicity = (1+eccentricity)**2 / (1-eccentricity**2)**1.5
    pot_fns = {"primary": back_radius_potential_primary, "secondary": back_radius_potential_secondary}
    for ii, component in enumerate(['primary', 'secondary']):
        params[component]['synchronicity'] = synchronicity
        args = (radii[ii], params["system"]["mass_ratio"], synchronicity, 1-eccentricity)
        params[component]['surface_potential'] = pot_fns[component](*args)

    params['system']['semi_major_axis'], params['system']['period'] = \
        correct_sma(params['system']['mass_ratio'], radii[0], radii[1])

    return params


def precalc_grid(arr1, arr2, fn):
    """
    Aux function to calculate various grids of parameters.

    :param arr1: numpy.array;
    :param arr2: numpy.array;
    :param fn: callable
    :return: numpy.array
    """
    ret_grid = np.empty((arr1.size, arr2.size))
    for ii, qq in enumerate(arr1):
        ret_grid[ii] = fn(arr2, qq)
    return ret_grid


def getattr_from_collumn_name(system, column_name):
    """
    Enables to return binary system attribute from column name.

    :param system: BinarySystem
    :param column_name: str;
    :return: requested attribute
    """
    colname_split = column_name.split('__')

    if len(colname_split) > 2:
        raise ValueError('Column name can contain only single `__` separator.')
    elif len(colname_split) > 1:
        if colname_split[0] not in ['primary', 'secondary', 'star']:
            raise ValueError('Only `primary` or `secondary` prefix can be in front of the `__` separator.')
        if colname_split[1][:4] == 'spot':
            star = getattr(system, colname_split[0])
            spot = star.spots[int(colname_split[1][4])-1]
            return getattr(spot, colname_split[1][6:])
        return getattr(getattr(system, colname_split[0]), colname_split[1])
    else:
        if colname_split[0] == 'critical_surface_potential':
            return getattr(system.primary, colname_split[0])
        elif colname_split[0] == 'overcontact':
            morph = getattr(system, 'morphology')
            return 1 if morph in ['over-contact', 'overcontact'] else 0
        else:
            return getattr(system, colname_split[0])


def typing(values, types):
    type_map = {'INTEGER': int, 'INTEGER NOT NULL': int, 'REAL': float, 'TEXT': str}
    for ii, val in enumerate(values):
        values[ii] = type_map[types[ii]](val)
        values[ii] = np.round(values[ii], 5) if types[ii] == 'REAL' else values[ii]

    return values
