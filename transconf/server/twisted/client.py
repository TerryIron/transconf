__author__ = 'chijun'

import time
import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol

from transconf.msg.rabbit.client import BaseClient as BaseSyncClient
from transconf.server.utils import from_config_option
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


class BaseClient(BaseSyncClient):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection

    def init(self):
        self.config()
        self.exchange_type = None
        self.connection = None
        self.channel = None
        self.reply_to = None

    def config(self):
        raise NotImplementedError()

    def _on_connect(self, context, result_back=None, delivery_mode=2):
        self.corr_id = self.rand_corr_id
        self.delivery_mode = delivery_mode
        if self.connection:
            d = defer.succeed({})
            d.addCallback(lambda result: self.on_channel(self.connection, context[1]))
        else:
            cc = protocol.ClientCreator(reactor,
                                        self.connection_class,
                                        self.parms)
            d = cc.connectTCP(self.parms.host, self.parms.port)
            d.addCallback(lambda procotol: procotol.ready)
            d.addCallback(lambda con: self.on_channel(con, context[1]))
        d.addCallback(lambda ret: self.publish(context))
        if result_back:
            d.addCallback(lambda ret: result_back())
        return d

    def _ready(self, context, exchange, routing_key):
        return [context, exchange, routing_key]

    @defer.inlineCallbacks
    def on_response(self):
        queue_object, consumer_tag = yield self.channel.basic_consume(queue=self.reply_to,
                                                                      no_ack=False)
        result = yield self.on_request(queue_object)
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
    def on_channel(self, connection, exchange):
        if not self.connection:
            self.connection = yield connection
            self.channel = yield self.connection.channel()
            if self.exchange_type:
                yield self.channel.exchange_declare(exchange=exchange,
                                           type=self.exchange_type)

    @defer.inlineCallbacks
    def publish(self, context):
        #LOG.debug('Publish channel:{0}'.format(self.channel))
        if not self.reply_to: 
            result = yield self.channel.queue_declare(exclusive=True, auto_delete=True)
            self.reply_to = result.method.queue
        yield self.channel.basic_publish(exchange=context[1],
                                    routing_key=context[2],
                                    properties=pika.BasicProperties(
                                        reply_to=self.reply_to,
                                        correlation_id=self.corr_id,
                                        delivery_mode=self.delivery_mode,
                                    ),
                                    body=self.packer.pack(context[0]))

    @defer.inlineCallbacks
    def close(self):
        if self.connection:
            yield self.connection.close()
            self.connection = None

    """
        Publish an async message, return None
        @request: request object
        @routing_key: routing key
    """
    def castBase(self, context, routing_key=None, delivery_mode=2):
        self._on_connect(self._ready(context, routing_key), None, delivery_mode)
        #LOG.debug('Context:{0}, routing_key:{1}, delivery:{2}'.format(context, 
        #                                                              routing_key,
        #                                                              delivery_mode))

    def cast(self, request, routing_key=None, delivery_mode=2):
        self.castBase(request.to_dict(), routing_key, delivery_mode)

        
    """
        Publish an async message, return a defer, do not support concurrency
        @request: request object
        @routing_key: routing key
    """
    def callBase(self, context, routing_key=None, delivery_mode=2):
        d = self._on_connect(self._ready(context, routing_key), self.on_response, delivery_mode)
        #LOG.debug('Context:{0}, routing_key:{1}, delivery:{2}, value:{3}'.format(context, 
        #                                                                         routing_key,
        #                                                                         delivery_mode,
        #                                                                         val))
        return d

    def call(self, request, routing_key=None, delivery_mode=2):
        return self.callBase(request.to_dict(), routing_key, delivery_mode)


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
                                                 rpc_queue)


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
                                                   '.'.join([self.bind_topic_queue, real_routing]))


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
                                                    '')

