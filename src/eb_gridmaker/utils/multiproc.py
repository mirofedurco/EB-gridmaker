from multiprocessing import Pool
import numpy as np

from .. import config


def multiprocess_eval(items, fn, args):
    """
    Function for multiprocess evaluation of curves.

    :param items: numpy.array; IDs of curves
    :param fn: callabe; curve evaluation function
    :param args: tuple; arguments of curve evaluation function
    :return:
    """
    chunksize = 1000
    n_chunks = int(len(items) / chunksize + 1)
    for jj in range(n_chunks):
        print(f'Chunk {jj+1}/{n_chunks}.')

        idxs = np.arange(jj*chunksize, (jj+1)*chunksize)
        idxs = idxs[idxs < len(items)]
        chunk_items = items[idxs]
        pool = Pool(processes=config.NUMBER_OF_PROCESSES)
        [pool.apply_async(fn, (iden, ii+jj*chunksize)+args) for ii, iden in enumerate(chunk_items)]

        pool.close()
        pool.join()
