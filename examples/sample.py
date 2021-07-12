from eb_gridmaker import evaluate_grid, config

config.NUMBER_OF_PROCESSES = 1
evaluate_grid('bla.db', bottom_boundary=0.0, top_boundary=0.0001)