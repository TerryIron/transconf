__author__ = 'chijun'


from transconf.server.twisted import get_service_conf
from transconf.server.twisted.service import RPCTranServer as AsyncServer
from transconf.server.twisted.client import RPCTranClient as RPCClient
from transconf.server.twisted.client import TopicTranClient as TopicClient
from transconf.server.twisted.client import FanoutTranClient as FanoutClient
from transconf.server.utils import from_config_option
from transconf.msg.rabbit.client import _get_client


class TranServer(AsyncServer):
    DEFAULT_CONF = get_service_conf()

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

    @property
    def conf_topic_exchange(self):
        return self._conf_get_name + 'topic'

    @property
    def conf_topic_queue(self):
        return self._conf_get_name

    @property
    def conf_topic_routing_key(self):
        return self._conf_get_type

    @property
    def conf_rpc_queue(self):
        return self._conf_get_name + 'rpc'

    @property
    def conf_fanout_queue(self):
        uuid = self._conf_get_uuid
        if not uuid:
            uuid = self.rand_corr_id
        return self._conf_get_name + uuid

    @property
    def conf_fanout_exchange(self):
        return self._conf_get_name + 'fanout'

    def init(self):
        self.bind_rpc_queue = self.conf_rpc_queue
        self.bind_topic_exchange = self.conf_topic_exchange
        self.bind_topic_queue = self.conf_topic_queue
        self.bind_topic_routing_key = self.conf_topic_routing_key
        self.bind_fanout_exchange = self.conf_fanout_exchange
        self.bind_fanout_queue = self.conf_fanout_queue


class RPCTranClient(RPCClient):
    DEFAULT_CONF = get_service_conf()

    def config(self, group='', type=''):
        self.bind_rpc_queue = group + 'rpc'


class TopicTranClient(TopicClient):
    DEFAULT_CONF = get_service_conf()

    def init(self):
        super(TopicTranClient, self).init()
        self.routing_key = None

    def config(self, group='', type=''):
        self.bind_topic_exchange = group + 'topic'
        self.bind_topic_queue = group
        self.routing_key = type

    def _ready(self, context, routing_key):
        if not routing_key:
            routing_key = self.routing_key
        super(TopicTranClient, self)._ready(context, routing_key)


class FanoutTranClient(FanoutClient):
    DEFAULT_CONF = get_service_conf()

    def config(self, group='', type=''):
        self.bind_fanout_exchange = group + 'fanout'


client_list = [
    ('topic', TopicTranClient),
    ('fanout', FanoutTranClient),
    ('rpc', RPCTranClient),
]


def get_client(group_name, group_type, type='topic', amqp_url=None):
    c = _get_client(client_list, type, amqp_url)
    if not c: 
        return 
    c.config(group_name, group_type)
    return c
