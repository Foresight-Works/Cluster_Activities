import pika, os, time
import json
import ast
import numpy as np

import json
import pika
import time
import threading


RABBIT_URL = 'amqp://nuvihermoth:D0nn1eDarkoisRabbitFrank@rabbit-cluster-external-stage-1443209739.us-east-1.elb.amazonaws.com'
ROUTING_KEY = 'throttle.compact_social_activity.throttled'
QUEUE_NAME = 'kc.ca.queue'
EXCHANGE = 'kc.ca.exchange'
THREADS = 1

class ThreadedConsumer(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
    parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    self.channel = connection.channel()
    self.channel.queue_declare(queue=QUEUE_NAME, auto_delete=False)
    #self.channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE)#, routing_key=ROUTING_KEY)
    self.channel.exchange_declare(exchange=EXCHANGE, durable=True, exchange_type='direct')
    self.channel.basic_qos(prefetch_count=THREADS * 10)
    self.channel.basic_consume(QUEUE_NAME, on_message_callback=self.callback)
    threading.Thread(target=self.channel.basic_consume(QUEUE_NAME, on_message_callback=self.callback))

  def callback(self, channel, method, properties, body):
    message = json.loads(body)
    time.sleep(5)
    print(message)
    channel.basic_ack(delivery_tag=method.delivery_tag)

  def run(self):
    print('starting thread to consume from rabbit...')
    self.channel.start_consuming()


def main():
  for i in range(THREADS):
    print('launch thread', i)
    td = ThreadedConsumer()
    td.start()
    #td.join()

main()

