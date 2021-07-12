import os
import numpy as np

DATABASE_NAME = 'ceb_atlas.db'
# NUMBER_OF_PROCESSES = 1
NUMBER_OF_PROCESSES = os.cpu_count()
N_POINTS = 400  # number of points in LC

# ELISA names of used photometric filters
PASSBANDS = [
    'Generic.Bessell.U',
    'Generic.Bessell.B',
    'Generic.Bessell.V',
    'Generic.Bessell.R',
    'Generic.Bessell.I',
    'SLOAN.SDSS.u',
    'SLOAN.SDSS.g',
    'SLOAN.SDSS.r',
    'SLOAN.SDSS.i',
    'SLOAN.SDSS.z',
    'Kepler',
    'GaiaDR2',
    'TESS',
]

T_MAX_OVERCONTACT = 8000  # maximum allowed temperature of the overcontact system components
MAX_DIFF_T_OVERCONTACT = 500  # maximum temperature difference between overcontact components

# if you want to extend the table once the table is generated, do it only by appending the desired values to the end of
# existing arrays, DO NOT INSERT additional values between original values once the table is (partially) generated
Q_ARRAY = np.round(np.arange(0.1, 1.01, 0.1), 3)  # grid mass ratios
R_ARRAY = np.round(np.arange(0.01, 1.0, 0.04), 6)  # grid of component's radii
I_ARRAY = np.round(np.arange(0.0, 1.01, 0.1), 6)  # ranges of inclinations (i_min + I_ARRAY*(90-i_min))
T_ARRAY = np.concatenate((np.arange(4000, 10001, 1000), np.arange(12000, 20001, 2000), np.arange(25000, 50000, 5000)))  # t_eff of components
# T_ARRAY = np.concatenate((np.arange(4000, 10001, 1000), np.arange(12000, 20001, 2000)))  # t_eff of components/

PARAMETER_COLUMNS = (
    'id', 'mass_ratio',
    'primary__surface_potential', 'secondary__surface_potential',
    'primary__t_eff', 'secondary__t_eff',
    'inclination', 'critical_surface_potential', 'morphology',
    'primary__equivalent_radius', 'secondary__equivalent_radius',
    'primary__filling_factor', 'secondary__filling_factor',
)

PARAMETER_TYPES = (
    'INTEGER NOT NULL', 'REAL',
    'REAL', 'REAL',
    'INTEGER', 'INTEGER',
    'REAL', 'REAL', 'TEXT',
    'REAL', 'REAL',
    'REAL', 'REAL',
)

# mappping of elisa passbands with db column names
PASSBAND_COLLUMN_MAP = {
    'Generic.Bessell.U': 'Bessell_U',
    'Generic.Bessell.B': 'Bessell_B',
    'Generic.Bessell.V': 'Bessell_V',
    'Generic.Bessell.R': 'Bessell_R',
    'Generic.Bessell.I': 'Bessell_I',
    'SLOAN.SDSS.u': 'SLOAN_u',
    'SLOAN.SDSS.g': 'SLOAN_g',
    'SLOAN.SDSS.r': 'SLOAN_r',
    'SLOAN.SDSS.i': 'SLOAN_i',
    'SLOAN.SDSS.z': 'SLOAN_z',
    'Kepler': 'Kepler',
    'GaiaDR2': 'GaiaDR2',
    'TESS': 'TESS',
}

PASSBAND_COLLUMNS = tuple(PASSBAND_COLLUMN_MAP[p] for p in PASSBANDS)

# ______________________AUXILIARY_VARIABLES____________________________________
COUNTER = 0
OVERCONTACT_T_ARRAY = T_ARRAY[T_ARRAY <= T_MAX_OVERCONTACT]
MAX_G_RATIO = 1e5
MAX_ID = np.prod([Q_ARRAY.size, R_ARRAY.size ** 2, I_ARRAY.size, T_ARRAY.size ** 2])
PARAM_ORDER = [Q_ARRAY, R_ARRAY, R_ARRAY, T_ARRAY, T_ARRAY, I_ARRAY]
