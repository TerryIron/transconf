__author__ = 'chijun'

import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.server.rabbit_msg import RabbitAMQP
from transconf.server.utils import from_config


class BaseClient(RabbitAMQP):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection

    def init(self):
        self.config()

    def config(self):
        self.exchange_type = None

    def on_connect(self, channel_callback):
        cc = protocol.ClientCreator(reactor,
                                    self.connection_class,
                                    self.parms)
        d = cc.connectTCP(self.parms.host, self.parms.port)
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(channel_callback)

    def _call(self, context, exchange, routing_key, corr_id):
        self.context = context
        self.exchange = exchange
        self.routing_key = routing_key
        self.corr_id = corr_id

    @defer.inlineCallbacks
    def wait_on_channel(self, connection):
        yield self.on_channel(connection)
        queue_object, consumer_tag = yield self.channel.basic_consume(self.on_response,
                                                                      no_ack=True,
                                                                      queue=self.reply_to)

    @defer.inlineCallbacks
    def on_channel(self, connection):
        self.channel = yield connection.channel()
        result = yield self.channel.queue_declare(exclusive=True, auto_delete=True)
        self.reply_to = yield result.method.queue
        if self.exchange_type:
            yield self.channel.exchange_declare(exchange=self.exchange,
                                                type=self.exchange_type)
        yield self.channel.basic_publish(exchange=self.exchange,
                                         routing_key=self.routing_key,
                                         properties=pika.BasicProperties(
                                             reply_to=self.reply_to,
                                             correlation_id=self.corr_id,
                                             delivery_mode=2,
                                         ),
                                         body=self.packer.pack(self.context))

    @defer.inlineCallbacks
    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            yield body if not 'null' else None


class RPCTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.bind_rpc_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf

    def cast(self, context, routing_key=None):
        rpc_queue = self.bind_rpc_queue if not routing_key else routing_key
        self._call(context, 
                   '', 
                   rpc_queue,
                   self.rand_corr_id)
        self.on_connect(self.on_channel)
        
    def call(self, context, routing_key=None):
        rpc_queue = self.bind_rpc_queue if not routing_key else routing_key
        self._call(context, 
                   '', 
                   rpc_queue,
                   self.rand_corr_id)
        self.on_connect(self.wait_on_channel)


class TopicTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.exchange_type = 'topic'
        self.bind_topic_exchange = self.conf_topic_exchange if not exchange else exchange
        self.bind_topic_queue = self.conf_topic_queue if not queue else queue

    @property
    @from_config('topic_binding_exchange', 'default_topic_exchange')
    def conf_topic_exchange(self):
        return self.conf

    @property
    @from_config('topic_binding_queue', 'default_topic_queue')
    def conf_topic_queue(self):
        return self.conf

    def cast(self, context, routing_key):
        real_routing = str(routing_key)
        self._call(context, 
                   self.bind_topic_exchange, 
                   '.'.join([self.bind_topic_queue, real_routing]),
                   self.rand_corr_id)
        self.on_connect(self.on_channel)

    def call(self, context, routing_key):
        real_routing = str(routing_key)
        self._call(context, 
                   self.bind_topic_exchange, 
                   '.'.join([self.bind_topic_queue, real_routing]),
                   self.rand_corr_id)
        self.on_connect(self.wait_on_channel)


class FanoutTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.exchange_type = 'fanout'
        self.bind_fanout_exchange = self.conf_fanout_exchange if not exchange else exchange
        self.bind_fanout_queue = self.conf_fanout_queue if not queue else queue

    @property
    @from_config('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    @property
    @from_config('fanout_binding_queue', 'default_fanout_queue')
    def conf_fanout_queue(self):
        return self.conf


    def cast(self, context, routing_key=None):
        print 'i am cast'
        fanout_exchange = self.bind_fanout_exchange if not routing_key else routing_key
        self._call(context,
                   fanout_exchange,
                   '',
                   self.rand_corr_id)
        self.on_connect(self.on_channel)

    def call(self, context, routing_key=None):
        print 'i am call'
        fanout_exchange = self.bind_fanout_exchange if not routing_key else routing_key
        self._call(context,
                   fanout_exchange,
                   '',
                   self.rand_corr_id)
        self.on_connect(self.wait_on_channel)


