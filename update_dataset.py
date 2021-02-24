import kaggle

kaggle.api.authenticate()
dataset = 'gpreda/covid-world-vaccination-progress'
path = '/Users/GDRomaine/ds/covid-19_vax'
kaggle.api.dataset_download_files(dataset, path, unzip=True)