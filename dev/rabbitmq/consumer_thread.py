import pika
import threading
import json

def consume(*args, **kwargs):
    def print_message(channel, method, properties, body):
        message = json.loads(body)
        print('recieved:', message)
    queue = kwargs["queue"]
    exchange = kwargs["exchange"]
    credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
    parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue, auto_delete=False)
    channel.exchange_declare(exchange=exchange, durable=True, exchange_type='direct')
    channel.basic_consume(queue, print_message, auto_ack=True)
    t1 = threading.Thread(target=channel.start_consuming)
    t1.start()
    t1.join(0)
    channel.queue_delete(queue=queue)

EXCHANGE = 'kc.ca.exchange'
QUEUE_NAME = 'kc.ca.queue'
consume(queue=QUEUE_NAME, exchange=EXCHANGE)
