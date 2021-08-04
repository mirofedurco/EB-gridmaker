from eb_gridmaker.dtb import merge_databases

# db_files = ['ceb_atlas1.db', 'ceb_atlas2.db']

home_dir = '/home/miro/elisa_models/ceb_atlas/'
db_files = [home_dir + 'ceb_atlas1.db', home_dir + 'ceb_atlas2.db']
res_file = home_dir + 'ceb_atlas.db'

merge_databases(db_files, res_file)