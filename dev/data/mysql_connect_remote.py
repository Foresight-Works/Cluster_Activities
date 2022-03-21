import mysql.connector as mysql
host = '172.31.36.11'
user = 'researchUIuser'
password = 'query1234'
db = 'toyDB'
## Create Database ##
conn = mysql.connect(host=host, user=user, passwd=password)
c = conn.cursor()
c.execute('CREATE DATABASE IF NOT EXISTS {db}'.format(db=db))
print('Connected to remote and created database {db}'.format(db=db))

## Create Table##
conn = mysql.connect(host=host, user=user, passwd=password, database=db)
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