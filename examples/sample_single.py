from eb_gridmaker import evaluate_grid, config

config.NUMBER_OF_PROCESSES = 1
evaluate_grid('/home/cepheus/elisa_models/eb_grid/bla.db', desired_morphology='single_spotty', sampling='random')