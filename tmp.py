# def send_msg(self, message_id, body):
# 	"""
# 	Args:
# 		message_id: int
# 			ex) PUT_METRIC_DATA_MSG_ID (0x0001)
# 				PUT_METRIC_ALARM_MSG_ID (0x0002)
# 				...
# 		body: dict object (will be converted into json format)
#
# 	"""
#
# 	def publish(body, properties, use_metric_pool=True):
# 		msg = 'AMQP Connection is closed %d time(s)... retrying.'
# 		max_retries = 5
# 		mq_pool = self.metric_pool if use_metric_pool else self.alarm_pool
#
# 		with mq_pool.item() as conn:
# 			for i in range(max_retries + 1):
# 				try:
# 					return conn.channel.basic_publish(exchange='',
# 					                                  routing_key='metric_queue',
# 					                                  body=body, properties=properties)
# 				except ConnectionClosed:
# 					if i < max_retries:
# 						conn.connect()
# 						LOG.warn(_(msg) % i)
# 						time.sleep(2 * i)
# 					else:
# 						raise
#
# 	if type(message_id) is not int:
# 		raise RpcInvokeException()
#
# 	message_uuid = str(uuid.uuid4())
# 	body.setdefault('message_id', message_id)
# 	body.setdefault('message_uuid', message_uuid)
#
# 	properties = pika.BasicProperties(delivery_mode=2)
# 	use_metric_pool = (message_id == PUT_METRIC_DATA_MSG_ID)
# 	publish(json.dumps(body), properties, use_metric_pool)
#
# 	LOG.info(_("send_msg - id(%03d), %s"), message_id, message_uuid)
# 	LOG.debug(_("send_msg - body(%s)"), str(body))
response_dict = {'a':1, 'b':2}
message_id = 'b2'
response_dict.setdefault('message_id', message_id)
print(response_dict)