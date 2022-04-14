import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
print('sys.path:', sys.path)
from modules.libraries import *
from modules.config import *

from modules.build_references import *
from modules.utils import *
from modules.clustering import *
from modules.db_tables import *
from modules.evaluate import *
from modules.tokenizers import *
from modules.tokens_distances import *
from modules.aws.s3 import *

def run_pipeline(projects, experiment_id, client, experiment_dir, runs_dir, num_files, file_names_str,\
                 runs_cols, results_cols, metrics_cols, metrics_optimize, conn_params,\
                 min_cluster_size, n_clusters_posted, duplicates_count, ids_files):
    print('matrices_dir:', matrices_dir)
    conn = mysql.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

    print('experiment_id sent to pipeline=', experiment_id)
    pipeline_start = time.time()
    duration = []
    print('{n} tasks'.format(n=len(projects)))
    print('task_type:', task_type)

    # Calculate Planned and Actual Duration
    id_planned_duration = activities_duration(projects, 'planned')
    id_actual_duration = activities_duration(projects, 'actual')
    
    names, ids = list(projects[names_col]), list(projects[ids_col])
    print('cluster_key sample:', names[:10])

    names = list(projects[names_col])
    tokens = tokenize_texts(names, exclude_stopwords=False, \
                      exclude_numbers=True, exclude_digit_tokens=True)
    with open(tokens_path, 'w') as f:
        for token in tokens: f.write('{t}\n'.format(t=token))

    ####################################################################################################
    # Token distance matrices
    subprocess.call('python modules/tokens_distances.py', shell=True)
    distance_matrices = []
    paths = get_s3_paths(ds_bucket_obj, matrices_dir)
    for path in paths:
        file = load_pickle_file(path, s3, ds_bucket, matrices_dir)
        distance_matrices.append(file)

    # Encode cluster_key
    print('Encode activity cluster_key')

    # Sentences transformer
    print('Loading language model')
    start = datetime.now()
    print('sentences_model:', sentences_model)
    model_path = os.path.join(models_dir, sentences_model)
    import psutil
    process = psutil.Process(os.getpid())
    print('memory_info:', process.memory_info().rss)

    if sentences_model in os.listdir(models_dir):
        transformer_model = SentenceTransformer(model_path)
        print('memory_info:', process.memory_info().rss)

    else:
        transformer_model = SentenceTransformer(sentences_model)
        transformer_model.save(model_path)
        print('memory_info:', process.memory_info().rss)

    duration.append(['model_upload', round((datetime.now() - start).total_seconds(), 2)])

    names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
    X = np.array(names_embeddings)
    ids_embeddings = dict(zip(ids, X))
    duration.append(['encode_names', round((datetime.now() - start).total_seconds(), 2)])

    runs_rows = []

    # Number of cluster per run
    print('n_clusters_posted:', n_clusters_posted)
    if n_clusters_posted > 1:
        n_clusters_runs = [n_clusters_posted]
    else:
        n_clusters_runs = [int(len(names) * n_clusters_perc/100) for n_clusters_perc in n_clusters_percs]
        n_clusters_runs = [n for n in n_clusters_runs if n>1]
    print('n_clusters runs:', n_clusters_runs)
    tasks_count = X.shape[0]
    print('(tasks_count / 2):', (tasks_count / 2))
    if n_clusters_posted > (tasks_count / 2):
        print('n_clusters_posted > (tasks_count / 2)')
        clustering_result = {'clustering_result': 'The number of clusters posted ({nc}) is in the range of the tasks count ({tc}).\n \
                   Re-run the application with a smaller number of clusters.'\
            .format(nc=n_clusters_posted, tc=tasks_count)}
        print(clustering_result)
    else:
        for run_id, n_clusters in enumerate(n_clusters_runs):
            run_id += 1
            print('*** run id={r} | {n} clusters ***'.format(r=run_id, n=n_clusters))
            run_dir = os.path.join(runs_dir, str(run_id))
            if str(run_id) not in os.listdir(runs_dir):
                os.mkdir(run_dir)
            run_start = datetime.now()
            # Cluster activities
            start = datetime.now()
            model_params = {}
            model_params['affinity'] = affinity
            clustering_params_write = '_'.join(['{param}|{val}'.format(param=k, val=v) for k, v in model_params.items()])
            model_params['n_clusters'] = n_clusters
            model_conf = model_conf_instance(clustering_model_name, model_params)
            clustering = model_conf.fit(X)
            clusters_labels = list(clustering.labels_)
            projects['cluster'] = clusters_labels
            clusters = list(projects['cluster'].unique())
            clustering_result, clusters_namesIDs = build_result(projects, clusters, names_col, ids_col)
            np.save(os.path.join(run_dir, 'clusters_namesIDs.npy'), clusters_namesIDs)
            duration.append(['cluster_names', round((datetime.now() - start).total_seconds(), 2)])

            # Evaluation
            clusters_dict = {}
            for cluster in clusters: clusters_dict[cluster] = list(projects[ids_col][projects['cluster'] == cluster])

            # SOS, Calinski-Harabasz index
            bcss, wcss, ch_index, scores = ch_index_sklearn(clusters_dict, ids_embeddings)
            print('distances scores: wcss={w} | bcss={b} |ch_index={ch}'.format(w=wcss, b=bcss, ch=ch_index))

            # Davies-Bouldin Index
            db_index = davies_bouldin_score(X, clusters_labels)
            db_index = round(db_index, 2)

            # Silhouette Index
            silhouette = silhouette_score(X, clusters_labels, metric='euclidean')
            silhouette = round(silhouette, 2)

            # Duration STD
            std_scores = clusters_duration_std(clusters_dict, id_planned_duration)
            scores = pd.merge(scores, std_scores, on='key')
            ave_std = round(sum(scores['duration_std'])/n_clusters, 2)
            print('average clusters standard deviation:', ave_std)

            # Words-Pairs
            references_dir = os.path.join(run_dir, 'references')
            if 'references' not in os.listdir(run_dir):
                os.mkdir(references_dir)

            # Run Reference Dictionaries
            print('run references directory:', references_dir)
            reference_dictionaries(clustering_result, references_dir, distance_matrices)
            subprocess.call('python words_pairs.py {path}'.format(path=references_dir), shell=True)
            words_pairs_score = open(os.path.join(results_dir, 'words_pairs_score.txt')).read().split('\n')[0]
            print('words_pairs_score:', words_pairs_score)

            run_end = datetime.now()
            run_duration = round((run_end - run_start).total_seconds(), 2)
            run_start = run_start.strftime("%d/%m/%Y %H:%M:%S")
            run_end = run_end.strftime("%d/%m/%Y %H:%M:%S")
            print("end time =", run_end, type(run_end))

            # Clusters stats
            tasks_per_cluster = [len(v) for k, v in clusters_dict.items()]
            mean_tpc = round(np.mean(tasks_per_cluster), 2)
            median_tpc = round(np.median(tasks_per_cluster), 2)
            min_tpc, max_tpc = np.min(tasks_per_cluster), np.max(tasks_per_cluster)
            min_max_tpc = max_tpc-min_tpc

            ## Results
            best = '0' # To be changed to 1 for the best run following scoring and voting
            print('file_names_str written:', file_names_str)
            runs_row = [experiment_id, run_id, file_names_str, \
                           num_files, run_start, run_end, run_duration,\
                           tasks_count, sentences_model, clustering_model_name, clustering_params_write, \
                           n_clusters, ave_std,\
                           mean_tpc, median_tpc, min_tpc, max_tpc,\
                           min_max_tpc, wcss, bcss, ch_index, db_index, silhouette,\
                           words_pairs_score]
            runs_row = [str(i) for i in runs_row]
            statement = insert_into_table_statement('{db}.runs'.format(db=db_name), runs_cols, runs_row)
            print('insert into statement:', statement)
            cur.execute(statement)
            conn.commit()

            # Keep the clustering score if the smallest cluster is larger than the minimal cluster size
            min_tpc = int(min_tpc)
            print('minimal cluster size=', min_tpc)
            if min_tpc >= min_cluster_size:
                runs_rows.append(runs_row)

        scores = pd.DataFrame(runs_rows, columns=runs_cols)
        print('** Scores **')
        print(scores)
        # Vote on results
        if len(scores) == 0:
            message = {'clustering_result': 'No clustering result produced the desired minimal clusters level'}
            clustering_result = message['clustering_result']
            print(clustering_result)
        else:
            scaled_scores = scale_df(scores[metrics_cols])
            scaled_scores.to_excel(os.path.join(experiment_dir, 'scaled_scores.xlsx'), index=False)
            print('scaled_scores')
            print(scaled_scores)
            # If the user did not specify a desired run to provide as a response, deliver the run with the highest score
            best_run_id = vote(scaled_scores, metrics_cols, metrics_optimize)
            # Check point: Selected_run_id in run ids
            print('best_run_id:', best_run_id)
            write_duration('Clusters calculation', pipeline_start)

            ## Name clusters and build results
            subprocess.call('python build_response.py {eid} {rid} {fn}'.\
                            format(eid=experiment_id, rid=best_run_id,\
                                   fn=file_names_str), shell=True)
            if client == 'ui':
                dict_file_name = 'named_clusters.npy'
            else: dict_file_name = 'named_clusters_ids.npy'
            response_dict = np.load(os.path.join(results_dir, dict_file_name), allow_pickle=True)[()]
            message = json.dumps(response_dict)

            # Write best clustering result
            if list(clustering_result.keys())[0] == 'clustering_result':
                clustering_result = list(clustering_result.values())[0]
            else:
                response_dict['planned_duration_vals'], response_dict['actual_duration_vals'] \
                    = id_planned_duration, id_actual_duration
                response_dict['duplicates_count'] = duplicates_count
                response_dict['ids_files'] = ids_files
                clustering_result = json.dumps(response_dict)
                clustering_result = clustering_result.replace("'", "''")

            result_row_query = "SELECT * FROM {db}.runs WHERE experiment_id={eid} AND run_id={rid}"\
                                   .format(db=db_name, eid=experiment_id, rid=best_run_id)
            cur.execute(result_row_query)
            results_row = [i for i in cur.fetchall()[0]]
            results_row.append(clustering_result)
            statement = insert_into_table_statement('{db}.results'.format(db=db_name), results_cols, results_row)
            cur.execute(statement)
            conn.commit()
            # print('** Results table **')
            # results_df = pd.read_sql_query("SELECT * FROM {db}.results".format(db=db_name), conn)
            # print(results_df)

        ## Publish results
        QUEUE_NAME = 'experiment_{id}'.format(id=experiment_id)
        EXCHANGE = 'kc.ca.exchange'
        credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
        parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, durable=True, exchange_type='direct')
        channel.queue_declare(queue=QUEUE_NAME)
        #message_id = 'experiment_{id}'.format(id=experiment_id)
        #channel.basic_publish(exchange='', routing_key=QUEUE_NAME,\
        #                      body=message, properties=pika.BasicProperties(message_id=message_id))
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
        print('Integration result published')
        write_duration('Pipeline', pipeline_start)
        conn.commit()
        conn.close()