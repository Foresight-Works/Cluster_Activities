from modules.py_postgres import *
db_name, table_name = 'cluster_activities', 'experiments'
conn = psycopg2.connect(database="{db}".format(db=db_name), \
                            user='rony', password='1234', host='localhost', port='5432')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
print('Table values')
sql = "SELECT * FROM {tn}".format(tn=table_name)
dat = sqlio.read_sql_query(sql, conn)
dat.to_excel('experiments4.xlsx', index=False)
print(type(dat))
print(dat)