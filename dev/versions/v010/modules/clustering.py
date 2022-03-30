from setup import *

def similar(a, b):
    #return SequenceMatcher(None, a, b).ratio()
    #Treat blanks as "junk"
    return SequenceMatcher(lambda x: x == " ", a, b).ratio()


def cluster_names(name, names, checked, lower_sim, upper_sim):
    '''Calculate name similarity for input name compared to all cluster_key
    from a list of cluster_key and cluster cluster_key that are more similar than the
    specified threshold.
    '''
    cluster = [name]
    for name2 in names:
        if name2 not in checked:
            if (similar(name, name2) > lower_sim) \
                    & (similar(name, name2) < upper_sim):
                cluster.append(name2)
    return cluster


def cluster_names_df(name, names, lower_sim, upper_sim):
    '''Calculate name similarity for input name compared to all cluster_key
    from a list of cluster_key and cluster cluster_key that are more similar than the
    specified threshold.

    test:
    name = 'aaaa'
    namel = [name]
    cluster_key = ['eeaa', 'aaaa', 'aaab', 'aaac']
    cluster_names (name, cluster_key, 0.5 ,0.95)

    '''
    namel = [name]
    names_df = pd.DataFrame()
    names_df['query'] = [len(names) * namel][0]
    names_df['name'] = names
    names_df['distance'] = names_df.apply(lambda x: \
                                              similar(str(x['query']), str(x['name'])), axis=1)
    names_df = names_df[(names_df['distance'] > lower_sim) & (names_df['distance'] < upper_sim)]
    # print(names_df)
    cluster = list(names_df['name'])
    return cluster


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


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


def plot_dendrogram(model, **kwargs):
    plt.title("Hierarchical Clustering Dendrogram")
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")

    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

    fig1 = plt.gcf()
    return fig1