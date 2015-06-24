__author__ = 'chijun'

import pika
import uuid 

from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task


COMMON_QUEUE_NAME = 'trans_queue'


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        import json
        return json.dumps(dict_data)
        
    @staticmethod
    def unpack(json_data):
        import json
        return json.loads(json_data)


class RPCMiddleware(object):
    def __init__(self, handler):
        self.handler = handler

    def run(self, context):
        raise NotImplementedError()


class RPC(object):
    CONNECTION_ATTEMPTS = 3
    QUEUE_NAME = COMMON_QUEUE_NAME

    def __init__(self, amqp_url, timeout=5):
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
        )
        self.packer = JsonSerializionPacker()
        self.name = self.QUEUE_NAME


class RPCTranServer(RPC):

    def setup(self, middleware):
        assert isinstance(middleware, RPCMiddleware)
        self.middleware = middleware

    def process_request(self, body):
        return self.middleware.run(body)

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        ch, method, properties, body = yield queue_object.get()
        if body:
            res = self.process_request(self.packer.unpack(body))
            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id
                             ),
                             body=self.packer.pack(res))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        queue = yield channel.queue_declare(queue=self.name)
        yield channel.basic_qos(prefetch_count=1)
        queue_object, consumer_tag = yield channel.basic_consume(queue=self.name)
        l = task.LoopingCall(self.on_request, queue_object)
        l.start(0.01)

    def connect(self):
        cc = protocol.ClientCreator(reactor, 
                                    twisted_connection.TwistedProtocolConnection, 
                                    self.parms)
        d = cc.connectTCP(self.parms.host, self.parms.port)
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(self.on_connect)

    def serve_forever(self):
        self.connect()
        reactor.run()


class RPCTranClient(RPC):
    def __init__(self, amqp_url, timeout=5):
        super(RPCTranClient, self).__init__(amqp_url, timeout)
        self.connection = pika.BlockingConnection(self.parms)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

    def on_response(self, queue_object):
        ch, method, properties, body = queue_object.get()
        if self.corr_id == properties.correlation_id:
            self.res = body

    def call(self, context):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.name,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,                                
                                       correlation_id=self.corr_id,
                                   ),
                                   body=self.packer.pack(context))
        
    def call_ack(self, context):
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        self.res = None
        self.call(context)
        while self.res is None:
            self.connection.process_data_events()
        return self.res
