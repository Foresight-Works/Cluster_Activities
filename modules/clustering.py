import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *

def model_conf_instance(model_name, hyper_params_conf):
    '''
    Build an instance of the model with it's hyperparameters
    :params:
    model_name: The modelling method applied
    hyper_params_conf: A dictionary relating hyperparameters(key) to their values
    :return:
    A model-configuration object ready for training
    '''

    if model_name == 'SpectralClustering': model_conf = SpectralClustering(**hyper_params_conf)
    if model_name == 'AgglomerativeClustering': model_conf = AgglomerativeClustering(**hyper_params_conf)

    return model_conf


def get_clusters(X, names, model_name, hyper_params_conf):
    model_conf = model_conf_instance(model_name, hyper_params_conf)
    print('model_conf', model_conf)
    clustering = model_conf.fit(X)
    clusters_df = pd.DataFrame()
    clusters_df['name'] = names
    clusters_df['cluster'] = clustering.labels_
    clusters_df = clusters_df.sort_values(by=['cluster'], ascending=False)
    # print('distances:', clustering.distances_)
    # print('children:', clustering.children_)
    counts = np.zeros(clustering.children_.shape[0])
    return clustering, clusters_df


def results_file_name(model_name, hyper_params_conf):
    exclude = ['random_state', 'compute_distances']
    for k, v in hyper_params_conf.items():
        if k not in exclude: model_name += '_{k}{v}'.format(k=k, v=str(v).capitalize())
        # name = name[:-1]
    return model_name

