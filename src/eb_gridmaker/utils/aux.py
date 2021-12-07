import numpy as np
from math import modf
from copy import copy

from . default_single_model import DEFAULT_SYSTEM as S_DEFAULT_SINGLE_SYSTEM
from . default_binary_model import DEFAULT_SYSTEM as DEFAULT_BINARY_SYSTEM
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


def get_params_from_id(id, maxid):
    order = [config.Q_ARRAY, config.R_ARRAY, config.R_ARRAY, config.T_ARRAY, config.T_ARRAY, config.I_ARRAY]
    if id >= maxid:
        raise ValueError('ID is above maximum')
    remainder = float(id)
    result, indices = [], []
    for ii, param in enumerate(order):
        denominator = np.prod([item.size for item in order[ii+1:]]) if ii < 5 else 1
        remainder /= denominator
        remainder, index = modf(remainder)
        remainder *= denominator

        index = int(index)
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
    params = copy(DEFAULT_BINARY_SYSTEM)
    params["system"]["period"] = np.random.uniform(config.M_RANGE[0], config.M_RANGE[1])


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
    return values
