import pika
import sys
credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
parameters = pika.ConnectionParameters('172.31.34.107',5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
message = 'Hello World!'
exchange_name = 'kc.ca.exchange'
queue_name = 'kc.ca.queue'
channel.exchange_declare(exchange=exchange_name,  durable=True, exchange_type='direct')
channel.queue_declare(queue=queue_name)
channel.basic_publish( exchange='', routing_key=queue_name, body=message)
print(" [x] Sent %r:%r" % (queue_name, message))
connection.close()