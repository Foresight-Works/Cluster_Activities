from dev.pipeline.service.cluster_service5.setup import *
# Database tables
db_name = 'cluster_activities'
table_name = 'experiments'
conn = psycopg2.connect(database="{db}".format(db=db_name), \
                        user='rony', password='1234', host='localhost', port='5432')
create_db(db_name, conn)
create_table(table_name, results_columns, data_types, conn)
