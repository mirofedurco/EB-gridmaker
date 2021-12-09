import numpy as np

from eb_gridmaker.utils.aux import get_params_from_id


if __name__ == '__main__':
    n_id = 100000
    indices = np.empty((n_id, 6), dtype=int)
    for n in range(n_id):
        indices[n, :] = get_params_from_id(n, n_id)[1]

    if indices.shape == np.unique(indices, axis=0).shape:
        print("sucess")
    else:
        print("fail")
