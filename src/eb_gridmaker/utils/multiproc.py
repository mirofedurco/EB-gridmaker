from multiprocessing import Pool

from ... import config


def multiprocess_eval(items, fn, args):
    """
    Function for multiprocess evaluation of curves.

    :param items: numpy.array; IDs of curves
    :param fn: callabe; curve evaluation function
    :param args: tuple; arguments of curve evaluation function
    :return:
    """
    pool = Pool(processes=config.NUMBER_OF_PROCESSES)
    [pool.apply_async(fn, (iden, ii)+args) for ii, iden in enumerate(items)]
    pool.close()
    pool.join()
