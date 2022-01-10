import numpy as np
import sqlite3

import matplotlib.pyplot as plt
from elisa import BinarySystem
from eb_gridmaker.utils.physics import correct_sma

from eb_gridmaker.utils.sqlite_data_adapters import adapt_array, convert_array

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("ARRAY", convert_array)

db_name = '/home/cepheus/elisa_models/eb_grid/detached.db'
# db_name = '/home/cepheus/elisa_models/eb_grid/overcontact.db'
conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
# conn.row_factory = lambda cursor, row: row[0]
cursor = conn.cursor()
cursor2 = conn.cursor()

# cursor. execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor. fetchall())

step = 1000
sql = "SELECT Bessell_V, Bessell_R, id FROM curves"
sql2 = "SELECT * FROM parameters"
arr1, arr2 = [], []
cursor.execute(sql)
cursor2.execute(sql2)
phases = np.linspace(0, 1, 400, endpoint=False)
for ii, row in enumerate(zip(cursor, cursor2)):
    # print(ii)
    # arr1.append(row[0])
    # arr2.append(row[1])
    # print(row)

    if ii % step != 0:
        continue

    print(row[1])
    plt.figure(10)
    plt.plot(phases, row[0][0])
    plt.plot(phases, row[0][1])
    # plt.show()

    sma, period = correct_sma(row[1][1], row[1][9], row[1][10])

    community_params = {
        "system": {
            "inclination": np.degrees(row[1][6]),
            # "period": 0.5,
            "period": period,
            "argument_of_periastron": 90.0,
            "gamma": 0.0,
            "eccentricity": 0.0,
            "primary_minimum_time": 0.0,
            "phase_shift": 0.0,
            # "semi_major_axis": 0.5,  # default unit is solRad
            "semi_major_axis": sma,  # default unit is solRad
            "mass_ratio": row[1][1]
        },
        "primary": {
            "surface_potential": row[1][2],
            "synchronicity": 1.0,
            "t_eff": row[1][4]
        },
        "secondary": {
            "surface_potential": row[1][3],
            "synchronicity": 1.0,
            "t_eff": row[1][5]
        }
    }

    try:
        bs = BinarySystem.from_json(community_params)
        # plt.figure(2)
        figs = bs.plot.surface(return_figure_instance=True, phase=0.0)
    except Exception as e:
        print(f'exception occurred: {e}')
    plt.show()