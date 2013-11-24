from hookutils import collect_submodules, collect_data_files

hiddenimports = collect_submodules('enki.plugins')
datas = collect_data_files('enki')
