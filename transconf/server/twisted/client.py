__author__ = 'chijun'

import time
import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol

from transconf.msg.rabbit.client import BaseClient as BaseSyncClient
from transconf.server.utils import from_config_option
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


class Content(object):
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

    def _on_connect(self, context, result_mode=None, delivery_mode=2):
        cc = protocol.ClientCreator(reactor,
                                    self.connection_class,
                                    self.parms)
        d = cc.connectTCP(self.parms.host, self.parms.port)
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(lambda con: self.on_channel(con, context, delivery_mode))
        if not result_mode:
            d.addCallback(lambda result: self.none_response(*result))
        else:
            d.addCallback(lambda result: self.on_response(*result))
        return d

    def _ready(self, context, exchange, routing_key, corr_id):
        self.corr_id = corr_id
        return Content(context, exchange, routing_key)

    @defer.inlineCallbacks
    def none_response(self, con, channel, reply_to):
        yield con.close()

    @defer.inlineCallbacks
    def on_response(self, con, channel, reply_to):
        queue_object, consumer_tag = yield channel.basic_consume(queue=reply_to,
                                                                 no_ack=False)
        result = yield self.on_request(queue_object)
        yield con.close()
        yield defer.returnValue(result)

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        if queue_object:
            ch, method, properties, body = yield queue_object.get()
            if self.corr_id == properties.correlation_id:
                body = yield self.packer.unpack(body)
                result = yield body['result'] if body else None
                yield defer.returnValue(result)

    @defer.inlineCallbacks
    def on_channel(self, connection, context, delivery_mode):
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
                                        delivery_mode=delivery_mode,
                                    ),
                                    body=self.packer.pack(context.context))
        yield defer.returnValue((connection, channel, reply_to))

    """
        Publish an async message, return None
        @request: request object
        @routing_key: routing key
    """
    def cast(self, request, routing_key=None):
        self._on_connect(self._ready(request.to_dict(), routing_key), False)
        
    """
        Publish an async message, return a defer, do not support concurrency
        @request: request object
        @routing_key: routing key
    """
    def call_wait(self, request, routing_key=None):
        return self._on_connect(self._ready(request.to_dict(), routing_key), True)

    """
        Publish an async message, return a defer, support concurrency
        @request: request object
        @routing_key: routing key
    """
    def call(self, request, routing_key=None):
        return 

class RPCTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.bind_rpc_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config_option('rpc_binding_queue', 'default_rpc_queue')
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
    @from_config_option('topic_binding_exchange', 'default_topic_exchange')
    def conf_topic_exchange(self):
        return self.conf

    @property
    @from_config_option('topic_binding_queue', 'default_topic_queue')
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

    @property
    @from_config_option('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    def _ready(self, context, routing_key):
        fanout_exchange = self.bind_fanout_exchange if not routing_key else routing_key
        return super(FanoutTranClient, self)._ready(context,
                                                    fanout_exchange,
                                                    '',
                                                    self.rand_corr_id)

