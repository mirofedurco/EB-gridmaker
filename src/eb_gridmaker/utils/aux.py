import numpy as np
from math import modf

from ... import config


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
    return i_crit + step * (90 - i_crit)


def get_params_from_id(id):
    if id >= config.MAX_ID:
        raise ValueError('ID is above maximum')
    remainder = float(id)
    result, indices = [], []
    for ii, param in enumerate(config.PARAM_ORDER):
        denominator = np.prod([item.size for item in config.PARAM_ORDER[ii+1:]]) if ii < 5 else 1
        remainder /= denominator
        remainder, index = modf(remainder)
        remainder *= denominator

        index = int(index)
        result.append(param[index])
        indices.append(index)

    return result, indices


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
        if colname_split[0] not in ['primary', 'secondary']:
            raise ValueError('Only `primary` or `secondary` prefix can be in front of the `__` separator.')
        return getattr(getattr(system, colname_split[0]), colname_split[1])
    else:
        return getattr(system, colname_split[0]) \
            if colname_split[0] != 'critical_surface_potential' else getattr(system.primary, colname_split[0])


def typing(values, types):
    type_map = {'INTEGER': int, 'INTEGER NOT NULL': int, 'REAL': float, 'TEXT': str}
    for ii, val in enumerate(values):
        values[ii] = type_map[types[ii]](val)
    return values
