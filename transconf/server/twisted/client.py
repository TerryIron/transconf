__author__ = 'chijun'

import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task, threads

from transconf.server.rabbit_msg import BaseClient as BaseSyncClient
from transconf.server.utils import from_config


class Context(object):
    def __init__(self, context, exchange, routing_key):
        self.context = context
        self.exchange = exchange
        self.routing_key = routing_key


class BaseClient(BaseSyncClient):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection

    def init(self):
        self.config()
        self.exchange_type = None

    def config(self):
        raise NotImplementedError()

    def _on_connect(self, channel_callback, context, callback=None):
        cc = protocol.ClientCreator(reactor,
                                    self.connection_class,
                                    self.parms)
        d = cc.connectTCP(self.parms.host, self.parms.port)
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(lambda con: channel_callback(con, context))
        if callback:
            rd = defer.Deferred()
            rd.addCallback(lambda result: self.on_response(*result))
            od = defer.DeferredList([d, rd])
            return od

    def _ready(self, context, exchange, routing_key, corr_id):
        self.corr_id = corr_id
        return Context(context, exchange, routing_key)

    @defer.inlineCallbacks
    def on_response(self, channel, reply_to):
        def get_result(r):
            print '[CLIENT] get result:{0}'.format(r)
        queue_object, consumer_tag = yield channel.basic_consume(queue=reply_to,
                                                                 no_ack=False)
        d = threads.deferToThread(lambda: self.on_request(queue_object))
        d.addCallback(get_result)
        yield d

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        if queue_object:
            ch, method, properties, body = yield queue_object.get()
            if self.corr_id == properties.correlation_id:
                body = yield self.packer.unpack(body)
                result = yield body['result'] if body else None
                yield defer.returnValue(result)

    @defer.inlineCallbacks
    def on_channel(self, connection, context):
        channel = yield connection.channel()
        if self.exchange_type:
            yield channel.exchange_declare(exchange=context.exchange,
                                           type=self.exchange_type)
        result = yield channel.queue_declare(exclusive=True, auto_delete=True)
        reply_to = yield result.method.queue
        yield channel.basic_publish(exchange=context.exchange,
                                    routing_key=context.routing_key,
                                    properties=pika.BasicProperties(
                                        reply_to=reply_to,
                                        correlation_id=self.corr_id,
                                        delivery_mode=2,
                                    ),
                                    body=self.packer.pack(context.context))
        yield defer.returnValue((channel, reply_to))

    def cast(self, context, routing_key=None):
        self._on_connect(self.on_channel, self._ready(context, routing_key))
        
    def call(self, context, routing_key=None, callback=None):
        return self._on_connect(self.on_channel, self._ready(context, routing_key), callback)


class RPCTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.bind_rpc_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf


    def _ready(self, context, routing_key):
        rpc_queue = self.bind_rpc_queue if not routing_key else routing_key
        return super(RPCTranClient, self)._ready(context, 
                                                 '', 
                                                 rpc_queue, 
                                                 self.rand_corr_id)


class TopicTranClient(BaseClient):
    def init(self):
        super(TopicTranClient, self).init()
        self.exchange_type = 'topic'

    def config(self, exchange=None, queue=None):
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

    def _ready(self, context, routing_key):
        real_routing = str(routing_key)
        return super(TopicTranClient, self)._ready(context,
                                                   self.bind_topic_exchange, 
                                                   '.'.join([self.bind_topic_queue, real_routing]),
                                                   self.rand_corr_id)


class FanoutTranClient(BaseClient):
    def init(self):
        super(FanoutTranClient, self).init()
        self.exchange_type = 'fanout'

    def config(self, exchange=None, queue=None):
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

    def _ready(self, context, routing_key):
        fanout_exchange = self.bind_fanout_exchange if not routing_key else routing_key
        return super(FanoutTranClient, self)._ready(context,
                                                    fanout_exchange,
                                                    '',
                                                    self.rand_corr_id)

