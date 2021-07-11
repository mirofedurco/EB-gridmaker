from eb_gridmaker.utils.dtb import merge_databases


db_files = ['ceb_atlas_part1.db', 'ceb_atlas_part2.db', 'ceb_atlas_part3.db']
res_file = 'ceb_atlas.db'

merge_databases(db_files, res_file)