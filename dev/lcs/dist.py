import time

from dev.data.data_to_table import *
task_names = task_names[:1000]
print('{} tasks to cluster'.format(len(task_names)))

clustered = []
def cluster_task(name):
    '''Calculate name similarity for input name compared to all names
    from a list of names and cluster names that are more similar than the
    specified threshold.
    '''
    lower_sim, upper_sim = 0.8, 1.0
    cluster = []
    #print('{} tasks clustered'.format(len(clustered)))
    #print('name:', name)
    if name not in clustered:
        #print('{n} not in clustered'.format(n=name))
        cluster = [name]
        clustered.append(name)
        for name2 in task_names:
            if name2 not in clustered:
                similarity = similar(name, name2)
                if ((similarity > lower_sim) & (similarity < upper_sim)):
                    cluster.append(name2)
                    clustered.append(name2)

    return name, cluster


results_path = os.path.join(results_dir, 'clusters.txt')
names_clusters = {}

num_executors = 6
if __name__ == '__main__':
    start = time.time()
    if num_executors <= 1:
        for task_name in task_names:
            #print('Task clustered:', task_name)
            task_name, cluster = cluster_task(task_name)
            if cluster:
                names_clusters[task_name] = cluster
                write_name_cluster(results_path, task_name, cluster)

    else:
        executor = ProcessPoolExecutor(6)
        for result in executor.map(cluster_task, task_names):
            task_name, cluster = result
            #print('Task clustered:', task_name)
            cluster = list(set(cluster))
            names_clusters[task_name] = cluster
            write_name_cluster(results_path, task_name, cluster)

    end = time.time()
    duration = end - start
    print('calculation duration:', duration)
