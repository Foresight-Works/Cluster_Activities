def run_pipeline(projects, experiment_id, client, experiment_dir, runs_dir, num_files, file_names_str, \
                 runs_cols, results_cols, metrics_cols, metrics_optimize, service_location, conn_params, \
                 min_cluster_size, n_clusters_posted):

	'''
	A version of the pipeline which includes the code for validating the calculation of duration values,
	by producing the resulst in tables and histograms
	'''

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

	################################################################################
	print('Duration validation')
	c = list(zip(list(id_planned_duration.keys()), list(id_planned_duration.values())))
	planned_df = pd.DataFrame(c, columns=['id', 'planned_duration'])
	c = list(zip(list(id_actual_duration.keys()), list(id_actual_duration.values())))
	actual_df = pd.DataFrame(c, columns=['id', 'actual_duration'])
	actual_planned = pd.merge(planned_df, actual_df, on='id').dropna()
	actual_planned = actual_planned.loc[(actual_planned[['actual_duration', 'planned_duration']] > 0).all(axis=1)]
	actual_planned['ratio'] = actual_planned['actual_duration'] / actual_planned['planned_duration']
	actual_planned['overrun'] = actual_planned['actual_duration'] / actual_planned['planned_duration'] - 1
	actual_planned['perc overrun'] = 100 * actual_planned['overrun']
	print(actual_planned.info())
	print(actual_planned.head(20))
	actual_df.to_excel(os.path.join(experiment_dir, 'actual_df.xlsx'), index=False)
	planned_df.to_excel(os.path.join(experiment_dir, 'planned_df.xlsx'), index=False)
	actual_planned.to_excel(os.path.join(experiment_dir, 'actual_planned.xlsx'), index=False)
	print('duration stats')
	print(actual_planned[['actual_duration', 'planned_duration', 'ratio']].describe())

	from modules.plots import histogram_stats, save_fig
	histogram_stats(actual_planned['actual_duration'], 'Actual Duration', 'duration values', \
	                os.path.join(experiment_dir, 'actual_duration_histogram.png'))
	histogram_stats(actual_planned['planned_duration'], 'Planned Duration', 'duration values', \
	                os.path.join(experiment_dir, 'planned_duration_histogram.png'))
	histogram_stats(actual_planned['ratio'], 'Planned to Actual Duration', 'duration values', \
	                os.path.join(experiment_dir, 'planned_actual_ratio_histogram.png'))
	histogram_stats(actual_planned['perc overrun'], 'Percent Overrun', 'duration values', \
	                os.path.join(experiment_dir, 'percent_overrun_histogram.png'))
	################################################################################
