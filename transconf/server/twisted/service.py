__author__ = 'chijun'

import pika

from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.server.rpc import RPC
from transconf.server.rpc import RPCTranClient as RPCTranSyncClient

class RPCMiddleware(object):
    def __init__(self, handler):
        self.handler = handler

    def run(self, context):
        raise NotImplementedError()


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
            body = yield self.process_request(self.packer.unpack(body))
            yield ch.basic_publish(exchange='',
                                   routing_key=properties.reply_to,
                                   properties=pika.BasicProperties(
                                       correlation_id=properties.correlation_id
                                   ),
                                   body=self.packer.pack(body))
            yield ch.basic_ack(delivery_tag=method.delivery_tag)

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.queue_declare(queue=self.name)
        yield channel.basic_qos(prefetch_count=1)
        queue_object, consumer_tag = yield channel.basic_consume(queue=self.name,
                                                                 no_ack=False)
        l = task.LoopingCall(self.on_request, queue_object)
        l.start(0.001)

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


class RPCTranClient(RPCTranSyncClient):

    def init(self):
        self.connection = pika.TwistedConnection(self.parms)
        self.channel = yield self.connection.channel()
        result = yield self.channel.queue_declare(exclusive=True)
        self.queue_name = yield result.method.queue

    def call(self, context):
        self.corr_id = yield str(uuid.uuid4())
        yield self.channel.basic_publish(exchange='',
                                         routing_key=self.name,
                                         properties=pika.BasicProperties(
                                             reply_to=self.queue_name,                                
                                             correlation_id=self.corr_id,
                                             delivery_mode=2,
                                         ),
                                         body=self.packer.pack(context))



