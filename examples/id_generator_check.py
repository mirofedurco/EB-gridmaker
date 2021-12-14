import numpy as np
from time import time

from eb_gridmaker import config
from eb_gridmaker.utils.aux import get_params_from_id

np.set_printoptions(precision=2, suppress=True)


if __name__ == '__main__':
    n_id = 10000000
    indices = np.empty((n_id, 6), dtype=int)
    vals = np.empty((n_id, 6), dtype=float)
    config.CUMULATIVE_PRODUCT = np.cumprod([o.size for o in reversed(config.sampling_order())])
    start = time()
    for n in range(n_id):
        vals[n, :], indices[n, :] = get_params_from_id(n)
        # print(vals[n, :], indices[n, :])

    print(f'Elapsed time: {time() - start:.2f}')

    print('generator has finished')

    if indices.shape == np.unique(indices, axis=0).shape and vals.shape == np.unique(vals, axis=0).shape:
        print("sucess")
    else:
        print("fail")
