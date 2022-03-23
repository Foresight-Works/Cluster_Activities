import pika
import json
import numpy as np
import random
message_id = 'message_{id}'.format(id=str(random.randint(0, 10000)))

credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
exchange_name = 'kc.ca.exchange'
queue_name = 'kc.ca.queue'
channel.exchange_declare(exchange=exchange_name,  durable=True, exchange_type='direct')
channel.queue_declare(queue=queue_name)
# message = 'Hello World!'
# f = open('response.json')
# message = f.read()
# message = json.load(f)
# print(type(message))
#print(message)
message = np.load('response.npy', allow_pickle=True)[()]
message = {message_id: message}
message = json.dumps(message)
channel.basic_publish(exchange='', routing_key=queue_name, body=message)
print("Sent %r:%r" % (queue_name, message))
print('message sent')
connection.close()