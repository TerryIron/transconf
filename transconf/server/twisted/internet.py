__author__ = 'chijun'

import functools
from twisted.internet import defer

from transconf.server.twisted import get_service_conf
from transconf.server.twisted.service import serve_forever, RPCTranServer as AsyncServer
from transconf.server.twisted.client import RPCTranClient as RPCClient
from transconf.server.twisted.client import TopicTranClient as TopicClient
from transconf.server.twisted.client import FanoutTranClient as FanoutClient
from transconf.utils import from_config_option
from transconf.msg.rabbit.client import _get_client
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


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
    @from_config_option('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf

    def init(self):
        self.bind_queue = self.conf_queue if not 'default_rpc_queue' else self._conf_get_name + self._get_uuid() + 'rpc'
        LOG.info('''' Message Service is starting, Mode:RPC;
                      Listen PRC queue:{0};'''.format(self.bind_queue))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.queue_declare(queue=self.bind_queue)
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel)


class TopicTranServer(TranServer):
    @property
    @from_config_option('topic_binding_exchange', 'default_topic_exchange')
    def conf_topic_exchange(self):
        return self.conf

    @property
    @from_config_option('topic_binding_queue', 'default_topic_queue')
    def conf_topic_queue(self):
        return self.conf

    @property
    @from_config_option('topic_routing_key', 'default_topic_routing_key')
    def conf_topic_routing_key(self):
        return self.conf

    def init(self):
        self.bind_exchange = self.conf_topic_exchange if not 'default_topic_exchange' else self._conf_get_name + 'topic'
        self.bind_queue = self.conf_topic_queue if not 'default_topic_queue' else self._conf_get_name
        self.bind_routing_key = self.conf_topic_routing_key if not 'default_topic_routing_key' else self._conf_get_type
        LOG.info('''' Message Service is starting, Mode:TOPIC;
                      Listen TOPIC exchange:{0};
                      Listen TOPIC queue:{1};
                      Listen TOPIC routing_key:{2};'''.format(self.bind_exchange,
                                                              self.bind_queue,
                                                              self.bind_routing_key))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_exchange, type='topic')
        yield channel.queue_declare(queue=self.bind_queue, auto_delete=False, exclusive=False)
        yield channel.queue_bind(exchange=self.bind_exchange,
                                 queue=self.bind_queue,
                                 routing_key='.'.join([self.bind_queue, self.bind_routing_key]))
        yield channel.basic_qos(prefetch_count=1)
        yield self.on_channel(channel)


class FanoutTranServer(TranServer):
    @property
    @from_config_option('fanout_binding_queue', 'default_fanout_queue')
    def conf_fanout_queue(self):
        return self.conf

    @property
    @from_config_option('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    def init(self):
        self.bind_exchange = self.conf_fanout_exchange if not 'default_fanout_exchange' else self._conf_get_name + 'fanout'
        self.bind_queue = self.conf_fanout_queue if not 'default_fanout_exchange' else self._conf_get_name + self._get_uuid()
        LOG.info('''' Message Service is starting, Mode:FANOUT;
                      Listen FANOUT exchange:{0};
                      Listen FANOUT queue:{1};'''.format(self.bind_exchange,
                                                        self.bind_queue))

    @defer.inlineCallbacks
    def on_connect(self, connection):
        channel = yield connection.channel()
        yield channel.exchange_declare(exchange=self.bind_exchange, type='fanout')
        yield channel.queue_declare(queue=self.bind_queue, auto_delete=True)
        yield channel.queue_bind(exchange=self.bind_exchange, queue=self.bind_queue)
        yield self.on_channel(channel)


class RPCTranClient(RPCClient):
    DEFAULT_CONF = get_service_conf()

    def config(self, group='', type='', uuid=None):
        if uuid:
            self.bind_rpc_queue = group + uuid + 'rpc'
        else:
            self.bind_rpc_queue = group + 'rpc'
        self.__simple__ = dict(cls='rpc',
                               group=group,
                               type=type,
                               uuid=uuid)


class TopicTranClient(TopicClient):
    DEFAULT_CONF = get_service_conf()

    def init(self):
        super(TopicTranClient, self).init()
        self.routing_key = None

    def config(self, group='', type='', uuid=None):
        self.bind_topic_exchange = group + 'topic'
        self.bind_topic_queue = group
        self.bind_routing_key = type
        self.__simple__ = dict(cls='topic',
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
        self.bind_fanout_exchange = group + 'fanout'
        self.__simple__ = dict(cls='fanout',
                               group=group,
                               type=type,
                               uuid=uuid)


CLIENT_POOL = {}


def get_client_list():
    client_list = [
        ('topic', TopicTranClient),
        ('fanout', FanoutTranClient),
        ('rpc', RPCTranClient), #Point-to-point remote procedure call
    ]
    return client_list


def get_public_client(group_name, group_type, group_uuid=None, type='topic', amqp_url=None):
    name = group_name + group_type + str(group_uuid) + type
    if name not in CLIENT_POOL:
        c = _get_client(get_client_list(), type, amqp_url)
        if not c: 
            return 
        c.config(group_name, group_type, group_uuid)
        CLIENT_POOL[name] = c
    LOG.debug('Get client:{0}, groupname:{1}, grouptype:{2}, groupuuid:{3}'.format(CLIENT_POOL[name],
                                                                                   group_name,
                                                                                   group_type,
                                                                                   group_uuid))
    return CLIENT_POOL[name]


def get_private_client(group_name, group_type, group_uuid=None, type='topic', amqp_url=None):
    c = _get_client(get_client_list(), type, amqp_url)
    if not c: 
        return 
    c.config(group_name, group_type, group_uuid)
    LOG.debug('Get client:{0}, groupname:{1}, grouptype:{2}, groupuuid:{3}'.format(c,
                                                                                   group_name,
                                                                                   group_type,
                                                                                   group_uuid))
    return c
