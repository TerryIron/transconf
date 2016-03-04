# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'

import time
import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol

from transconf.msg.rabbit.client import BaseClient as BaseSyncClient, ExchangeType
from transconf.utils import from_config_option, myException
from transconf.server.response import Response
from transconf.server.crypto import Crypto
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class SendFailed(myException):
    pass


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

    @staticmethod
    def _ready(context, exchange, routing_key):
        return context, exchange, routing_key

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
                result = yield Response.from_dict(body)
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
        # TODO by xichijun
        # Use Rabiitmq build-in timestamp
        if not self.reply_to:
            result = yield self.channel.queue_declare(exclusive=True, auto_delete=True)
            setattr(self, 'reply_to', result.method.queue)
        properties = yield pika.BasicProperties(reply_to=self.reply_to,
                                                correlation_id=self.corr_id,
                                                delivery_mode=self.delivery_mode,
                                                timestamp=time.time())
        try:
            exchange, routing_key, body = context[1], context[2], context[0]
            yield self.publish_context(self.channel,
                                       exchange,
                                       routing_key,
                                       body,
                                       properties=properties)
        except TypeError as e:
            raise SendFailed("Failed to send request:{0}, {1}".format(context[0], e))

    @staticmethod
    def publish_context(channel, exchange, routing_key, body, properties=None):
        LOG.debug('Ready to publish channel:{0}, exchange:{1}, '
                  'routing_key:{2}, body:{3}|type:{4}, properties:{5}'.format(channel,
                                                                              exchange,
                                                                              routing_key,
                                                                              body,
                                                                              type(body),
                                                                              properties))
        return channel.basic_publish(exchange=exchange,
                                     routing_key=routing_key,
                                     properties=properties,
                                     body=body)

    @defer.inlineCallbacks
    def close(self):
        if self.connection:
            yield self.connection.close()
            setattr(self, 'connection', None)

    """
        Publish an async message, return None
        @request: request object
        @routing_key: routing key
    """
    def castBase(self, context, routing_key=None, delivery_mode=2):
        LOG.debug('Ready to send context:{0} without result'.format(context))
        self._on_connect(self._ready(context, routing_key), None, delivery_mode)

    def cast(self, request, routing_key=None, delivery_mode=2):
        self.castBase(request.to_dict(), routing_key, delivery_mode)

    """
        Publish an async message, return a defer, do not support concurrency
        @request: request object
        @routing_key: routing key
    """
    def callBase(self, context, routing_key=None, delivery_mode=2):
        LOG.debug('Ready to send context:{0} with result'.format(context))
        d = self._on_connect(self._ready(context, routing_key), self.on_response, delivery_mode)
        return d

    def call(self, request, routing_key=None, delivery_mode=2):
        return self.callBase(request.to_dict(), routing_key, delivery_mode)


class RPCTranClient(BaseClient):
    def config(self, exchange=None, queue=None):
        self.bind_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config_option('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf

    def _ready(self, context, routing_key):
        rpc_queue = self.bind_queue if not routing_key else routing_key
        return super(RPCTranClient, self)._ready(context, 
                                                 '', 
                                                 rpc_queue)


class TopicTranClient(BaseClient):
    def init(self):
        super(TopicTranClient, self).init()
        self.exchange_type = ExchangeType.TYPE_TOPIC

    def config(self, exchange=None, queue=None):
        self.bind_exchange = self.conf_topic_exchange if not exchange else exchange
        self.bind_queue = self.conf_topic_queue if not queue else queue

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
                                                   self.bind_exchange,
                                                   '.'.join([self.bind_queue, real_routing]))


class FanoutTranClient(BaseClient):
    def init(self):
        super(FanoutTranClient, self).init()
        self.exchange_type = ExchangeType.TYPE_FANOUT

    def config(self, exchange=None, queue=None):
        self.bind_exchange = self.conf_fanout_exchange if not exchange else exchange

    @property
    @from_config_option('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    def _ready(self, context, routing_key):
        fanout_exchange = self.bind_exchange if not routing_key else routing_key
        return super(FanoutTranClient, self)._ready(context,
                                                    fanout_exchange,
                                                    '')


def RSAClient(client):
    crypto = Crypto()

    def publish_context(channel, exchange, routing_key, body, properties=None):
        body = crypto.encode(body)
        return channel.basic_publish(exchange=exchange,
                                     routing_key=routing_key,
                                     properties=properties,
                                     body=body)
    setattr(client, 'publish_context', publish_context)
    return client
