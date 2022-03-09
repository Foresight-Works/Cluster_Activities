import pika, os, time
import json
import ast
import numpy as np
def process_function(msg):
  print(" Message processing")
  msg = ast.literal_eval(msg.decode('utf-8'))
  print('msg')
  print(msg)
  print('type(msg)', type(msg))
  np.save('msg.npy', msg)
  return;

credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
exchange_name = 'kc.ca.exchange'
queue_name = 'kc.ca.queue'
channel.exchange_declare(exchange=exchange_name,  durable=True, exchange_type='direct')
channel.queue_declare(queue=queue_name)

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  process_function(body)

# set up subscription on the queue
channel.basic_consume(queue_name, callback, auto_ack=True)

# start consuming (blocks)
channel.start_consuming()
connection.close()