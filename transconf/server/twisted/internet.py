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

from twisted.internet import defer

from transconf.server.twisted import get_service_conf
from transconf.server.twisted.service import RPCTranServer as AsyncServer
from transconf.server.twisted.client import RPCTranClient as RPCClient
from transconf.server.twisted.client import TopicTranClient as TopicClient
from transconf.server.twisted.client import FanoutTranClient as FanoutClient
from transconf.utils import from_config_option
from transconf.msg.rabbit.client import _get_client, ExchangeType
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class TranServer(AsyncServer):
    DEFAULT_CONF = get_service_conf

    @property
    @from_config_option('local_group_uuid', None)
    def _conf_get_uuid(self):
        return self.conf

    @property
    @from_config_option('local_group_name', 'default_group_name')
    def _conf_get_name(self):
        return self.conf

    @property
    @from_config_option('local_group_type', 'default_group_type')
    def _conf_get_type(self):
        return self.conf

    def _get_uuid(self):
        uuid = self._conf_get_uuid
        if not uuid:
            uuid = self.rand_corr_id
        return uuid


class RPCTranServer(TranServer):
    def init(self):
        self.bind_queue = self._conf_get_name + self._get_uuid() + 'rpc'
        LOG.info('''' Message Service is starting, Mode:RPC;
                      Listen PRC queue:{0};'''.format(self.bind_queue))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.queue_declare(queue=self.bind_queue)
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel)


class TopicTranServer(TranServer):
    def init(self):
        self.bind_exchange = self._conf_get_name + 'topic'
        self.bind_queue = self._conf_get_name + self._get_uuid() + 'topic'
        self.bind_routing_key = self._conf_get_type
        LOG.info('''' Message Service is starting, Mode:TOPIC;
                      Listen TOPIC exchange:{0};
                      Listen TOPIC queue:{1};
                      Listen TOPIC routing_key:{2};'''.format(self.bind_exchange,
                                                              self.bind_queue,
                                                              self.bind_routing_key))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_exchange, type=ExchangeType.TYPE_TOPIC)
        yield channel.queue_declare(queue=self.bind_queue, auto_delete=False, exclusive=False)
        yield channel.queue_bind(exchange=self.bind_exchange,
                                 queue=self.bind_queue,
                                 routing_key='.'.join([self.bind_queue, self.bind_routing_key]))
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel)


class FanoutTranServer(TranServer):
    def init(self):
        self.bind_exchange = self._conf_get_name + 'fanout'
        self.bind_queue = self._conf_get_name + self._get_uuid() + 'fanout'
        LOG.info('''' Message Service is starting, Mode:FANOUT;
                      Listen FANOUT exchange:{0};
                      Listen FANOUT queue:{1};'''.format(self.bind_exchange,
                                                         self.bind_queue))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_exchange, type=ExchangeType.TYPE_FANOUT)
        yield channel.queue_declare(queue=self.bind_queue, auto_delete=True)
        yield channel.queue_bind(exchange=self.bind_exchange, queue=self.bind_queue)
        yield self.on_channel(channel)


class RPCTranClient(RPCClient):
    DEFAULT_CONF = get_service_conf()

    def config(self, group='', type='', uuid=None):
        if uuid:
            self.bind_queue = group + uuid + 'rpc'
        else:
            self.bind_queue = group + 'rpc'
        self.__simple__ = dict(cls=ExchangeType.TYPE_RPC,
                               group=group,
                               type=type,
                               uuid=uuid)


class TopicTranClient(TopicClient):
    DEFAULT_CONF = get_service_conf()

    def init(self):
        super(TopicTranClient, self).init()
        self.routing_key = None

    def config(self, group='', type='', uuid=None):
        self.bind_exchange = group + 'topic'
        self.bind_queue = group
        self.bind_routing_key = type
        self.__simple__ = dict(cls=ExchangeType.TYPE_TOPIC,
                               group=group,
                               type=type,
                               uuid=uuid)

    def _ready(self, context, routing_key=None):
        if not routing_key:
            routing_key = self.bind_routing_key
        return super(TopicTranClient, self)._ready(context, routing_key)


class FanoutTranClient(FanoutClient):
    DEFAULT_CONF = get_service_conf()

    def config(self, group='', type='', uuid=None):
        self.bind_exchange = group + 'fanout'
        self.__simple__ = dict(cls=ExchangeType.TYPE_FANOUT,
                               group=group,
                               type=type,
                               uuid=uuid)


CLIENT_POOL = {}


def get_client_list():
    client_list = [
        (ExchangeType.TYPE_TOPIC, TopicTranClient),
        (ExchangeType.TYPE_FANOUT, FanoutTranClient),
        (ExchangeType.TYPE_RPC, RPCTranClient),  # Point-to-point remote procedure call
    ]
    return client_list


def _client_name(group, _type):
    return '%s%s%s%s' % (group.group_name,
                         group.group_type,
                         group.uuid,
                         _type)


def _new_client(group, _type, amqp_url):
    c = _get_client(get_client_list(), _type, amqp_url)
    if not c:
        return
    c.config(group.group_name,
             group.group_type,
             group.uuid)
    return c


class IGroup(object):
    def __init__(self, group_name, group_type, uuid=None):
        self.group_name = group_name
        self.group_type = group_type
        self.uuid = uuid


def new_singleton_client(group, type=ExchangeType.TYPE_TOPIC, amqp_url=None):
    return _new_client(group,
                       type,
                       amqp_url)


def get_client_from_pool(group, _type=ExchangeType.TYPE_TOPIC, amqp_url=None):
    # Do not apply it.
    name = _client_name(group, _type)
    if name in CLIENT_POOL:
        return CLIENT_POOL[name]
    return _new_client(group, _type, amqp_url)
