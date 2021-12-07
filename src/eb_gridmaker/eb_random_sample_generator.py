import numpy as np

from eb_gridmaker import dtb, config
from eb_gridmaker.utils import aux, multiproc
from elisa import SingleSystem, Observer
from elisa.base.error import LimbDarkeningError, AtmosphereError


def eval_single_grid_node(iden, counter, phases, maxiter, start_index):
    """
    Evaluating randomly generated spotty single system model.

    :param iden: str; node ID
    :param counter: int; current number of already calculeted nodes
    :param phases: numpy.array; desired phases of observations
    :param maxiter: int; total number of nodes in this batch
    :param start_index: int; number of iterations already calculated before interruption
    :return: None
    """
    aug_counter = counter + start_index
    print(f'Processing node: {aug_counter}/{maxiter}, {100.0 * aug_counter / maxiter:.2f}%')
    while True:
        params = aux.draw_single_star_params()

        try:
            s = SingleSystem.from_json(params)
        except ValueError as e:
            continue

        o = Observer(passband=config.PASSBANDS, system=s)

        try:
            o.lc(phases=phases, normalize=True)
            # o.plot.lc()
        except (LimbDarkeningError, AtmosphereError) as e:
            # print(f'Parameters: {params} produced system outside grid coverage.')
            continue

        dtb.insert_observation(
            config.DATABASE_NAME, o, iden, config.PARAMETER_COLUMNS_SINGLE, config.PARAMETER_TYPES_SINGLE
        )
        break


def spotty_single_system_random_sampling(db_name=None, number_of_samples=1e4):
    """
    Producing sample of spotty single system models generated randomly in given parameter space.

    :param db_name: str;
    :param number_of_samples: int;
    :return: None;
    """
    if db_name is not None:
        config.DATABASE_NAME = db_name
    phases = np.linspace(0, 1.0, num=config.N_POINTS, endpoint=False)

    # generating IDs of each possible combination
    ids = np.arange(0, number_of_samples, dtype=np.int)

    dtb.create_ceb_db(config.DATABASE_NAME, config.PARAMETER_COLUMNS_SINGLE, config.PARAMETER_TYPES_SINGLE)
    brkpoint = dtb.search_for_breakpoint(config.DATABASE_NAME, ids)
    print(f'Breakpoint found {100.0 * brkpoint / number_of_samples:.2f}%: {brkpoint}/{number_of_samples}')
    ids = ids[brkpoint:]

    args = (phases, number_of_samples, brkpoint, )
    multiproc.multiprocess_eval(ids, eval_single_grid_node, args)


def eval_eccentric_random_sample(iden, counter, phases, maxiter, start_index):
    aug_counter = counter + start_index
    print(f'Processing node: {aug_counter}/{maxiter}, {100.0 * aug_counter / maxiter:.2f}%')
    while True:
        params = aux.draw_eccentric_system_params()


def eccentric_system_random_sampling(db_name=None, number_of_samples=1e4):
    if db_name is not None:
        config.DATABASE_NAME = db_name
    phases = np.linspace(0, 1.0, num=config.N_POINTS, endpoint=False)

    # generating IDs of each possible combination
    ids = np.arange(0, number_of_samples, dtype=np.int)

    dtb.create_ceb_db(config.DATABASE_NAME, config.PARAMETER_COLUMNS_ECCENTRIC, config.PARAMETER_TYPES_ECCENTRIC)
    brkpoint = dtb.search_for_breakpoint(config.DATABASE_NAME, ids)
    print(f'Breakpoint found {100.0 * brkpoint / number_of_samples:.2f}%: {brkpoint}/{number_of_samples}')
    ids = ids[brkpoint:]

    args = (phases, number_of_samples, brkpoint,)
    multiproc.multiprocess_eval(ids, eval_eccentric_random_sample, args)


def random_sampling(db_name=None, desired_morphology='all', number_of_samples=1e4):
    """

    :param db_name: str; path to the database
    :param desired_morphology: string; `all`, `detached` - detached binaries on circular orbit, `overcontact`,
                                       `single_spotty`, `eccentric`
    :param number_of_samples: int; number of samples for random sampling
    :return:
    """
    if desired_morphology in ['detached', 'overcontact', 'circular']:
        raise NotImplementedError('Random sampling on circular binaries is not yet implemented. '
                                  'Try grid sampling method.')
    elif desired_morphology in ['single_spotty']:
        spotty_single_system_random_sampling(db_name, number_of_samples=number_of_samples)
    elif desired_morphology in ['eccentric']:
        eccentric_system_random_sampling()
    else:
        raise ValueError(f'Unknown morphology: {desired_morphology}. '
                         f'List of available morphologies: `all`, `detached` - detached binaries on circular orbit, '
                         f'`overcontact`, `single_spotty`, `eccentric`')


if __name__ == "__main__":
    config.NUMBER_OF_PROCESSES = 1
    random_sampling('../../random.db', desired_morphology='single_spotty', number_of_samples=10)
