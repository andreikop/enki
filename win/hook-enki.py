from hookutils import collect_submodules, collect_data_files

hiddenimports = collect_submodules('enki.plugins')
print("\n\n\n\n\n\n\n\n" +str(hiddenimports))
datas = collect_data_files('enki')
