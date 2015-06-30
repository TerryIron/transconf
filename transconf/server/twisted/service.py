__author__ = 'chijun'

import pika

from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.server.rpc import RabbitAMPQ
from transconf.server.rpc import RPCTranClient as RPCTranSyncClient

class RPCMiddleware(object):
    def __init__(self, handler):
        self.handler = handler

    def run(self, context):
        raise NotImplementedError()


class RPCTranServer(RabbitAMPQ):
    @property
    def conf_topic_exchange(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()  
        config.read(self.conf)
        default_sect = config._defaults
        val = default_sect.get('binding_topic_exchange', None)
        return val if val else 'default_topic_exchange'

    def init(self):

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
        yield channel.queue_declare(queue=self.name)
        yield self.on_channel(channel, '', self.name)

    @defer.inlineCallbacks
    def on_topic_mode(self, connection):
        channel = yield connection.channel()
        exchange_name = yield '_'.join([self.name, 'topic'])
        yield channel.exchange_declare(exchange=exchange_name,
                                       type='topic')
        yield channel.queue_declare(queue=self.topic, auto_delete=False, exclusive=False)
        yield channel.queue_bind(exchange=exchange_name,
                                 queue=self.topic,
                                 routing_key='.'.join([self.topic, '#']),
                                 )
        yield self.on_channel(channel, exchange_name, self.topic)

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
