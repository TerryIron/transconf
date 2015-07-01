__author__ = 'chijun'

import pika

from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.server.rabbit_msg import RabbitAMQP
from transconf.server.utils import from_config
from transconf.server.rabbit_msg import RPCTranClient as RPCTranSyncClient

class RPCMiddleware(object):
    def __init__(self, handler):
        self.handler = handler

    def process_request(self, context):
        raise NotImplementedError()


class RPCTranServer(RabbitAMQP):
    @property
    @from_config('topic_binding_exchange', 'default_topic_exchange')
    def conf_topic_exchange(self):
        return self.conf

    @property
    @from_config('topic_binding_queue', 'default_topic_queue')
    def conf_topic_queue(self):
        return self.conf

    @property
    @from_config('topic_routing_key', 'default_topic_routing_key')
    def conf_topic_routing_key(self):
        return self.conf

    @property
    @from_config('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf

    @property
    @from_config('fanout_binding_queue', 'default_fanout_queue')
    def conf_fanout_queue(self):
        return self.conf

    @property
    @from_config('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    def init(self):
        self.bind_rpc_queue = self.conf_rpc_queue
        self.bind_topic_exchange = self.conf_topic_exchange
        self.bind_topic_queue = self.conf_topic_queue
        self.bind_topic_routing_key = self.conf_topic_routing_key
        self.bind_fanout_exchange = self.conf_fanout_exchange
        self.bind_fanout_queue = str(self.conf_fanout_queue) + self.rand_corr_id

    def setup(self, middleware):
        assert isinstance(middleware, RPCMiddleware)
        self.middleware = middleware

    def process_request(self, body):
        return self.middleware.process_request(body)

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
        queue_object, consumer_tag = yield channel.basic_consume(queue=queue, no_ack=False)
        l = task.LoopingCall(lambda: self.on_request(queue_object, exchange))
        l.start(0.001)

    """
    @defer.inlineCallbacks
    def on_rpc_mode(self, connection):
        channel = yield connection.channel()
        yield channel.queue_declare(queue=self.bind_rpc_queue)
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel, '', self.bind_rpc_queue)
    """

    @defer.inlineCallbacks
    def on_topic_mode(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_topic_exchange, type='topic')
        yield channel.queue_declare(queue=self.bind_topic_queue, auto_delete=False, exclusive=False)
        yield channel.queue_bind(exchange=self.bind_topic_exchange,
                                 queue=self.bind_topic_queue,
                                 routing_key='.'.join([self.bind_topic_queue, self.bind_topic_routing_key]))
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel, self.bind_topic_exchange, self.bind_topic_queue)

    @defer.inlineCallbacks
    def on_fanout_mode(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_fanout_exchange, type='fanout')
        yield channel.queue_declare(queue=self.bind_fanout_queue, auto_delete=True)
        yield channel.queue_bind(exchange=self.bind_fanout_exchange, queue=self.bind_fanout_queue)
        yield self.on_channel(channel, self.bind_fanout_exchange, self.bind_fanout_queue)

    def serve_forever(self):
        self.connect(self.on_fanout_mode)
        self.connect(self.on_topic_mode)
        #self.connect(self.on_rpc_mode)
        reactor.run()
