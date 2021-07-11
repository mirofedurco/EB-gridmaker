# EB-gridmaker

This package enables to create sqlite databases containing light curves of large number of eclipsing binary (EB) 
models on pre-determined grid of EB parameters. This package currently supports following parameters: mass ratio, 
components radii, inclinations and effective temperatures. For now, this package is designed to generate grids of EBs 
with circular orbits. This package requires to have ELISa 0.4 or higher already installed 
(https://github.com/mikecokina/elisa).

Parameters of the EB database are specified in config.py file. Custom grid nodes can be specified with configuration 
parameters::

    import numpy as np
    from eb_gridmaker import config
    
    
    config.Q_ARRAY = np.round(np.arange(0.1, 1.01, 0.1), 3)  # grid mass ratios
    config.R_ARRAY = np.round(np.arange(0.01, 1.0, 0.04), 6)  # grid of component's radii
    config.I_ARRAY = np.round(np.arange(0.0, 1.01, 0.1), 6)  # ranges of inclinations (i_min + I_ARRAY*(90-i_min))
    config.T_ARRAY = np.concatenate((np.arange(4000, 10001, 1000), np.arange(12000, 20001, 2000)))  # t_eff of components
    
Additionally, maximum effective temperatures and maximum differences between effective temperatures can be set for
overcontact EB systems::

    config.T_MAX_OVERCONTACT = 8000  # maximum allowed temperature of the overcontact system components
    config.MAX_DIFF_T_OVERCONTACT = 1000  # maximum temperature difference between overcontact components

List of passbands in which we want to calculate the light curves can be also specified::

    config.PASSBANDS = [
        'Generic.Bessell.U',
        'Generic.Bessell.B',
        'Generic.Bessell.V',
        'Generic.Bessell.R',
        'Generic.Bessell.I',
        'Kepler',
        'GaiaDR2',
        'TESS',
    ]

where the names of the passbands corresponds to the names of the ELISa passbands (see `elisa.settings.PASSBANDS`). 
Number of LC points on (0, 1) phase interval is specified with `config.N_POINTS` parameter and finally, a number of 
CPUs used  for calculations can be manually specified in `config.NUMBER_OF_PROCESSES` which uses `os.cpu_count()` by 
default.
    
Generating a grid can be performed by the command::

    from eb_gridmaker import evaluate_grid
    
    
    evaluate_grid(db_name='path/to/grid.db')
    
This will create the whole grid at once. However, calculation can be split to multiple machines where each machine will 
calculate a portion of the grid::

    evaluate_grid(db_name='path/to/grid_part1.db', bottom_boundary=0.0, top_boundary=0.5)
    
This command in particular will create one half of the grid. In order to merge databases from each machine you can use 
following command::

    db_files = ['path/to/grid_part1.db', 'path/to/grid_part2.db']
    res_file = 'path/to/grid.db'

    merge_databases(db_files, res_file)

which will create a single database containing a desired grid.
    