__author__ = 'chijun'

import pika

from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.server.rpc import RabbitAMPQ, get_conf
from transconf.server.rpc import RPCTranClient as RPCTranSyncClient

class RPCMiddleware(object):
    def __init__(self, handler):
        self.handler = handler

    def run(self, context):
        raise NotImplementedError()


class RPCTranServer(RabbitAMPQ):
    @get_conf('topic_binding_exchange', 'default_topic_exchange')
    @property
    def conf_topic_exchange(self):
        return self.conf

    @get_conf('topic_binding_queue', 'default_topic_queue')
    @property
    def conf_topic_queue(self):
        return self.conf

    @get_conf('topic_routing_key', 'default_topic_routing_key')
    @property
    def conf_topic_routing_key(self):
        return self.conf

    @get_conf('rpc_binding_queue', 'default_rpc_queue')
    @property
    def conf_rpc_queue(self):
        return self.conf

    def init(self):
        self.bind_rpc_queue = self.conf_rpc_queue
        self.bind_topic_exchange = self.conf_topic_exchange
        self.bind_topic_queue = self.conf_topic_queue
        self.bind_topic_routing_key = self.conf_topic_routing_key

    def setup(self, middleware):
        assert isinstance(middleware, RPCMiddleware)
        self.middleware = middleware

    def process_request(self, body):
        return self.middleware.run(body)

    def _connect(self):
        cc = protocol.ClientCreator(reactor, 
                                    twisted_connection.TwistedProtocolConnection, 
                                    self.parms)
        return cc.connectTCP(self.parms.host, self.parms.port)

    def connect(self, callback):
        d = self._connect()
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(callback)

    @defer.inlineCallbacks
    def on_request(self, queue_object, exchange):
        ch, method, properties, body = yield queue_object.get()
        body = self.packer.unpack(body)
        if body:
            body = yield self.process_request(body)
            yield ch.basic_publish(exchange=exchange,
                                   routing_key=properties.reply_to,
                                   properties=pika.BasicProperties(
                                       correlation_id=properties.correlation_id
                                   ),
                                   body=self.packer.pack(body))
            yield ch.basic_ack(delivery_tag=method.delivery_tag)

    @defer.inlineCallbacks
    def on_channel(self, channel, exchange, queue):
        yield channel.basic_qos(prefetch_count=1)
        queue_object, consumer_tag = yield channel.basic_consume(queue=queue,
                                                                 no_ack=False)
        l = task.LoopingCall(lambda: self.on_request(queue_object, exchange))
        l.start(0.001)

    @defer.inlineCallbacks
    def on_rpc_mode(self, connection):
        channel = yield connection.channel()
        yield channel.queue_declare(queue=self.bind_rpc_queue)
        yield self.on_channel(channel, '', self.bind_rpc_queue)

    @defer.inlineCallbacks
    def on_topic_mode(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_topic_exchange,
                                       type='topic')
        yield channel.queue_declare(queue=self.topic, auto_delete=False, exclusive=False)
        yield channel.queue_bind(exchange=self.bind_topic_exchange,
                                 queue=self.bind_topic_queue,
                                 routing_key=self.bind_topic_routing_key,
                                 )
        yield self.on_channel(channel, self.bind_topic_exchange, self.bind_topic_queue)

    def serve_forever(self):
        self.connect(self.on_rpc_mode)
        self.connect(self.on_topic_mode)
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
