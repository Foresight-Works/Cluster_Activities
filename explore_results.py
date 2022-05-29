import ast
import pandas as pd
import mysql.connector as mysql
service_location = 'Local'
db_name = 'CAdb'
location_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': db_name},\
                      'Remote': {'host': '172.31.36.11', 'user':'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
conn_params = location_db_params[service_location]
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
experiment_id = 311
def result_from_table(experiment_id, result_key='clusters'):
    result_df = pd.read_sql_query("SELECT * FROM results \
    WHERE experiment_id={eid}".format(eid=experiment_id), conn)
    result = result_df['result'].values[0]
    result = ast.literal_eval(result)
    return result[result_key]
clusters = result_from_table(experiment_id)
for key, names in clusters.items():
	print(30 * '-')
	print('key:', key)
	for name in names: print(name)

