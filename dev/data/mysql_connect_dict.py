import mysql.connector as mysql
db_name = 'toyDB'
conn_params = {'host': 'localhost', 'user': 'rony', 'password': 'exp8546$fs'}
## Create Database ##
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute('CREATE DATABASE IF NOT EXISTS {db}'.format(db=db_name))

## Create Table##
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'db': db_name}
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (name VARCHAR(255), user_name VARCHAR(255))')
c.execute('SHOW TABLES')
print(c.fetchall())

## Insert values to table ##
query = 'INSERT INTO users (name, user_name) VALUES (%s, %s)'
values = ('Hafeez', 'hafeez')
c.execute(query, values)
conn.commit()
query = "INSERT INTO users (name, user_name) VALUES ('Uma', 'uma')"
c.execute(query)
c.execute('SELECT * FROM users')
print(c.fetchall())

#c.execute('DROP DATABASE IF EXISTS {db}'.format(db=db))