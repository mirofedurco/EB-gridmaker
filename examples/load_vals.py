import numpy as np
import sqlite3

import matplotlib.pyplot as plt

from eb_gridmaker.utils.sqlite_data_adapters import adapt_array, convert_array

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("ARRAY", convert_array)

db_name = '/home/miro/elisa_models/ceb_atlas/ceb_atlas.db'
conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = lambda cursor, row: row[0]
cursor = conn.cursor()
db_args = (conn, cursor)

# cursor. execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor. fetchall())

sql = 'SELECT Bessell_V from curves'
res = cursor.execute(sql).fetchall()[0]

plt.plot(res)
plt.show()