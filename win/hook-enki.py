from hookutils import collect_submodules, collect_data_files

hiddenimports = (
    # The plugins are dynamically loaded, making them a hidden import.
    collect_submodules('enki.plugins') +
    # The preview plugin's .ui file needs QtWebKit, making it hidden as well.
    ['PyQt4.QtWebKit'])

datas = (
# Enki relies on a number of .ui files and some .json files. Gather all these.
    collect_data_files('enki') +
# Enki's dynamic plug system needs the plugin available for os.listdir-type operations to be found. Gather than.
    collect_data_files('enki.plugins', True))
