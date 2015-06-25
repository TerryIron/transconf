__author__ = 'chijun'

import uuid
import pika

class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        import json
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        import json
        return json.loads(json_data)


class RPC(object):
    CONNECTION_ATTEMPTS = 3
    NAME = 'trans'

    def __init__(self, amqp_url, timeout=5):
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
        )
        self.packer = JsonSerializionPacker()
        self.name = self.NAME


class RPCTranClient(RPC):

    def __init__(self, amqp_url, timeout=5):
        super(RPCTranClient, self).__init__(amqp_url, timeout)
        self.init()

    def _on_connect(self):
        self.connection = pika.BlockingConnection(self.parms)
        self.channel = self.connection.channel()

    def init(self):
        self._on_connect()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.res = body

    def call(self, context):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.name,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                       delivery_mode=2,
                                   ),
                                   body=self.packer.pack(context))

    def call_ack(self, context):
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)
        self.res = None
        self.call(context)
        while self.res is None:
            self.connection.process_data_events()
        return self.res


class TopicTranClient(RPCTranClient):

    def init(self):
        self._on_connect()
        self.channel.exchange_declare(exchange=self.name,
                                      type='topic')
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

    def call(self, routing_key, context):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange=self.name,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=str(routing_key) + self.corr_id,
                                       correlation_id=self.corr_id,
                                       delivery_mode=2,
                                   ),
                                   body=self.packer.pack(context))


    def call_ack(self, routing_key, context):
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)
        self.res = None
        self.call(routing_key, context)
        while self.res is None:
            self.connection.process_data_events()
        return self.res


def get_rpc_client(amqp_url, typ):
    if typ == 'rpc':
        return RPCTranClient(amqp_url)
    elif typ == 'topic':
        return TopicTranClient(amqp_url)
