import sqlite3, os
from shutil import copyfile

import numpy as np

from .. utils.sqlite_data_adapters import adapt_array, convert_array
from .. utils import aux
from .. import config


sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("ARRAY", convert_array)


def create_ceb_db(db_name):
    """
    Function creates dataframe for holding synthetic light curves and parameters of systems.

    :param db_name: str; path to db location
    :return:
    """
    conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    db_args = (conn, cursor)

    # creating table of parameters
    create_table('parameters', config.PARAMETER_COLUMNS, config.PARAMETER_TYPES,
                 *db_args, **dict(additive='PRIMARY KEY (id)'))

    # creating table for each curve
    columns = config.PARAMETER_COLUMNS[:1] + config.PASSBAND_COLLUMNS
    types = config.PARAMETER_TYPES[:1] + tuple('ARRAY' for _ in config.PASSBAND_COLLUMNS)
    foreign_key = 'FOREIGN KEY (id) REFERENCES parameters (id)'
    create_table('curves', columns, types, *db_args, **dict(additive=foreign_key))

    # create index database
    create_table('auxiliary', ('last_index', ), ('INT', ), *db_args)

    conn.close()


def create_table(name, columns, types, *args, **kwargs):
    """
    Creates a new table if already does not exist.

    :param name: str; name of the table
    :param columns: tuple; name of columns
    :param types: tuple; types of columns
    :param args: tuple; (database connection, cursor)
    :param additive: str; additional string used to define primary or foreign key columns
    :return: None
    """
    conn, cursor = args

    tps = list(types)
    parameters = ','.join([f" {col} {tp}" for col, tp in zip(columns, tps)])
    additive = kwargs.get('additive')
    parameters = ', '.join([parameters, additive]) if additive is not None else parameters
    sql = f"CREATE TABLE IF NOT EXISTS {name} ({parameters})"
    cursor.execute(sql)

    conn.commit()


def insert_to_table(table, columns, values, *args):
    """
    Insert line to table defined by `columns` and `values`.

    :param table: str; name of the table
    :param columns: tuple; name of the columns
    :param values: tuple; values added to the table corresponding to `columns`
    :param args: tuple; (database connection, cursor)
    :return: None
    """
    conn, cursor = args

    val_holders = ', '.join(["?" for _ in values])
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({val_holders})"
    cursor.execute(sql, values)

    conn.commit()


def update_last_id(last_id, *args):
    """
    Updates a value of the last calculated node ID.

    :param last_id: int; node id
    :param args: tuple; (database connection, cursor)
    :return: None
    """
    conn, cursor = args

    sql = f"REPLACE INTO auxiliary (_rowid_, last_index) VALUES (?, ?)"
    cursor.execute(sql, (0, int(last_id)))

    conn.commit()


def insert_observation(db_name, observer, iden):
    """
    Create entry for the synthetic observation of given grid node with ID `iden` which will store system parameters in
    `parameters` table and normalized lightcurves in `curves` table.

    :param db_name: str;
    :param observer: elisa.Observer; observer instance with calculated light curves
    :param iden: str; node ID
    :return:
    """
    bs = getattr(observer, '_system')

    conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    db_args = (conn, cursor)

    # insert to parameters table
    values = [iden, ] + [aux.getattr_from_collumn_name(bs, item) for item in config.PARAMETER_COLUMNS[1:]]
    values = aux.typing(values, config.PARAMETER_TYPES)
    insert_to_table('parameters', config.PARAMETER_COLUMNS, values, *db_args)

    # insert to curves table
    columns = tuple(config.PARAMETER_COLUMNS[:1]) + config.PASSBAND_COLLUMNS
    values = [int(iden), ] + [observer.fluxes[p] for p in config.PASSBANDS]
    insert_to_table('curves', columns, values, *db_args)

    # alter last_index
    update_last_id(iden, *db_args)

    conn.close()


def search_for_breakpoint(db_name, ids):
    """
    Function will retrieve ID of last caluclated grid node to continue interrupted grid caclulation.

    :param db_name: str;
    :param ids: numpy.array; list of grid node ids to calculate in this batch
    :return: int; grid node from which start the calculation
    """
    conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()

    sql = f"SELECT last_index FROM auxiliary"
    last_idx = np.array(cursor.execute(sql).fetchall())

    if last_idx.size == 0:
        return 0
    elif last_idx[0] in ids:
        return np.where(last_idx[0] == ids)[0][0]
    else:
        raise ValueError('IDs of already calculated objects do not correspond to the generated ID. Breakpoint cannot '
                         'be generated.')

    conn.close()


def merge_databases(db_list, result_db):
    """
    Merges contents of databases calculated from different batches into a single database.

    :param db_list: list;
    :param result_db: str;
    :return: None
    """
    if type(db_list) not in [list, tuple]:
        raise ValueError('Function requires list of filenames of databases to merge')
    elif len(db_list) <= 1:
        raise ValueError('You need at least two databases to merge.')

    if os.path.isfile(result_db):
        raise IOError('Output file already exists.')

    copyfile(db_list[0], result_db)

    conn = sqlite3.connect(result_db, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE auxiliary')

    for fl in db_list[1:]:
        cursor.execute('ATTACH DATABASE ? AS db2', (fl, ))
        cursor.execute('INSERT INTO parameters SELECT * FROM db2.parameters')
        cursor.execute('INSERT INTO curves SELECT * FROM db2.curves')
        conn.commit()
        cursor.execute('DETACH DATABASE db2')

    conn.close()
