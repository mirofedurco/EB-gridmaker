import numpy as np

from eb_gridmaker.utils import aux, physics, multiproc
from eb_gridmaker import dtb, config
from elisa import BinarySystem, SingleSystem, settings, Observer
from elisa.base.error import LimbDarkeningError, AtmosphereError


def basic_param_eval(params, crit_potentials=None, omega1=None, omega2=None):
    """
    Function makes sure that the parameters met basic criteria for validity for surface potentials and effective
    temperatures:

    - overflow through L2,
    - duplicity of models caused by the  inability to vary secondary component in case of overcontacts,
    - not allowing overcontacts with too high surface temperature
    - not allowing for too different temperatures ov overcontact components
    - making sure that both components of detached system are within Roche lobe

    :param params: list; [q, r1, r2, t1, t2, i]
    :param crit_potentials: list; critical potentials [L3, L1, L2]
    :param omega1: float;
    :param omega2: float;
    :return: tuple; (bool, bool) test for validity of the system and test for overcontact system
    """
    r2 = params[2]
    t1, t2 = params[3], params[4]
    if omega1 <= crit_potentials[2]:  # check for system overflow through L2
        return False, None

    if omega1 < crit_potentials[1]:  # treating overcontact
        if r2 != config.R_ARRAY[0]:  # this removes duplicity of overcontacts due to fixed radius of secondary
            return False, None
        elif t2 > config.T_MAX_OVERCONTACT or t1 > config.T_MAX_OVERCONTACT:
            return False, None  # do not sample too hot overcontacts

        elif np.abs(t2-t1) > config.MAX_DIFF_T_OVERCONTACT:
            idx_t1 = np.where(t1 == config.T_ARRAY)[0]
            idx_t2 = np.where(t2 == config.T_ARRAY)[0]
            if np.abs(idx_t1-idx_t2) > 1:  # not allowing too different temperatures in overcontacts
                return False, None

        overcontact = True
    else:  # treating detached
        if omega2 < crit_potentials[1]:
            return False, None
        overcontact = False

    return True, overcontact


def eval_binary_grid_node(iden, counter, crit_potentials, omega1_grid, omega2_grid, i_crits, phases, maxiter,
                          start_index, desired_morphology, maxid):
    """
    Evaluating binary system located on grid node defined by its unique ID.

    :param desired_morphology: string; `all`, `detached`, `overcontact`
    :param iden: str; node ID
    :param counter: int; current number of already calculeted nodes
    :param crit_potentials: float; critical potential of the system
    :param omega1_grid: numpy.array; pre-calculated grid of primary surface potentials
    :param omega2_grid: numpy.array; pre-calculated grid of secondary surface potentials
    :param i_crits: numpy.array; pre-calculated grid of critical inclinations
    :param phases: numpy.array; desired phases of observations
    :param maxiter: int; total number of nodes in this batch
    :param start_index: int; number of iterations already calculated before interruption
    :return: None
    """
    params, idxs = aux.get_params_from_id(iden, maxid)
    valid, overcontact = basic_param_eval(params,
                                          crit_potentials=crit_potentials[idxs[0]],
                                          omega1=omega1_grid[idxs[0], idxs[1]],
                                          omega2=omega2_grid[idxs[0], idxs[2]])

    if not valid:
        return
    if desired_morphology == 'detached' and overcontact:
        return
    elif desired_morphology == 'overcontact' and not overcontact:
        return

    aug_counter = counter + start_index
    print(f'Processing node: {aug_counter}/{maxiter}, {100.0*aug_counter/maxiter:.2f}%')
    omega1 = omega1_grid[idxs[0], idxs[1]]
    omega2 = omega1 if overcontact else omega2_grid[idxs[0], idxs[2]]

    # if secondary component t_eff is bigger, switch primary and secondary components
    params, omega1, omega2 = physics.switch_components(*params, omega1=omega1, omega2=omega2)

    params[-1] = aux.generate_i(i_crits[idxs[1], idxs[2]], params[-1])

    bs = physics.initialize_system(*params, omega1=omega1, omega2=omega2, overcontact=overcontact)
    o = Observer(passband=config.PASSBANDS, system=bs)

    try:
        o.lc(phases=phases, normalize=True)
        # o.plot.lc()
    except (LimbDarkeningError, AtmosphereError) as e:
        # print(f'Parameters: {params} produced system outside grid coverage.')
        return

    dtb.insert_observation(
        config.DATABASE_NAME, o, iden, config.PARAMETER_COLUMNS_BINARY, config.PARAMETER_TYPES_BINARY
    )


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


def evaluate_binary_on_grid(db_name=None, bottom_boundary=0.0, top_boundary=1.0, desired_morphology='all'):
    """
    Producing sample of binary system models generated on grid of model parameter.

    :param db_name: str;
    :param bottom_boundary: float;
    :param top_boundary: float;
    :param desired_morphology: str;
    :return: None;
    """
    maxid = np.prod(
        [config.Q_ARRAY.size, config.R_ARRAY.size ** 2, config.I_ARRAY.size, config.T_ARRAY.size ** 2])

    if db_name is not None:
        config.DATABASE_NAME = db_name
    phases = np.linspace(0, 1.0, num=config.N_POINTS, endpoint=False)

    # generating IDs of each possible combination
    ids = np.arange(0, maxid, dtype=np.int)
    # randomizing calculation to fill the grid homogenously
    np.random.seed(42)
    np.random.shuffle(ids)

    # selecting subset to calculate (if you use multiple machines to spread the task
    ids = ids[int(bottom_boundary * maxid): int(top_boundary * maxid)]
    maxiter = len(ids)

    dtb.create_ceb_db(config.DATABASE_NAME, config.PARAMETER_COLUMNS_BINARY, config.PARAMETER_TYPES_BINARY)
    brkpoint = dtb.search_for_breakpoint(config.DATABASE_NAME, ids) + 1
    print(f'Breakpoint found {100.0 * brkpoint / maxiter:.2f}%: {brkpoint}/{maxiter}')
    ids = ids[brkpoint:]

    crit_potentials = [BinarySystem.libration_potentials_static(1.0, q) for q in config.Q_ARRAY]

    # pre-calculating potentials in grid
    omega1_grid = aux.precalc_grid(config.Q_ARRAY, config.R_ARRAY, physics.back_radius_potential_primary)
    omega2_grid = aux.precalc_grid(config.Q_ARRAY, config.R_ARRAY, physics.back_radius_potential_secondary)
    # grid of critical inclinations
    i_crits = aux.precalc_grid(config.R_ARRAY, config.R_ARRAY, physics.critical_inclination)

    args = (crit_potentials, omega1_grid, omega2_grid, i_crits, phases, maxiter, brkpoint, desired_morphology, maxid)
    multiproc.multiprocess_eval(ids, eval_binary_grid_node, args)


def evaluate_single_random_grid(db_name=None, number_of_samples=1e4):
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
    maxiter = len(ids)

    dtb.create_ceb_db(config.DATABASE_NAME, config.PARAMETER_COLUMNS_SINGLE, config.PARAMETER_TYPES_SINGLE)
    brkpoint = dtb.search_for_breakpoint(config.DATABASE_NAME, ids) + 1
    print(f'Breakpoint found {100.0 * brkpoint / maxiter:.2f}%: {brkpoint}/{maxiter}')
    ids = ids[brkpoint:]

    args = (phases, maxiter, brkpoint, )
    multiproc.multiprocess_eval(ids, eval_single_grid_node, args)


def evaluate_grid(db_name=None, bottom_boundary=0.0, top_boundary=1.0, desired_morphology='all', sampling='grid',
                  number_of_samples=1e4):
    """
    This loop will evaluate the part/whole grid using Pool of workers. Calculation can be split to bathes by defining a
    sub-interval of (0, 1) to downsize the grid calculated in this loop which is helpful if you want to split the
    calculations on multiple machines. Use then utils.dtb.merge_databases to join databases to a single one.

    :param db_name: str; path to the database
    :param desired_morphology: string; `all`, `detached`, `overcontact`
    :param bottom_boundary: float; defines lower boundary of given batch, select 0 for calculation of the whole grid at
                                   once
    :param top_boundary: float; defines upper boundary of given batch, select 1 for calculation of the whole grid at
                                once
    :param sampling: str; `grid` or `random`, `grid` samples models on pre-determined grid, `random` sampling will
                          sample defined parameter region randomly
    :param number_of_samples: int; number of samples for random sampling
    :return: None;
    """

    if desired_morphology not in ['detached', 'overcontact', 'single_spotty', 'all']:
        raise ValueError(f'Invalid value of `desired_morphology`: {desired_morphology} argument. Use `detached`, '
                         f'`overcontact` or `all`.')

    settings.configure(LOG_CONFIG='fit', MAX_DISCRETIZATION_FACTOR=8)

    if desired_morphology in ['detached', 'overcontact', 'all']:
        if sampling == 'grid':
            evaluate_binary_on_grid(db_name, bottom_boundary, top_boundary, desired_morphology)
        else:
            raise NotImplementedError('Random sampling is not implemented for binary systems.')
    elif desired_morphology in ['single_spotty']:
        if sampling == 'random':
            evaluate_single_random_grid(db_name, number_of_samples=number_of_samples)
        else:
            raise NotImplementedError('Grid sampling is not implemented for single systems.')


if __name__ == "__main__":
    evaluate_grid('../../ceb_atlas1.db', 0.0, 0.5, desired_morphology='detached')

    # sz = aux.estimate_size(config.COUNTER)
    # print(f'Number of of expected nodes: {config.COUNTER*10} with size: {10*sz} Gb. \n')
