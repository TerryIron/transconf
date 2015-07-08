__author__ = 'chijun'

import os

from transconf.server.twisted.service import RPCTranServer as AsyncServer
from transconf.server.twisted.client import RPCTranClient as RPCClient
from transconf.server.twisted.client import TopicTranClient as TopicClient
from transconf.server.twisted.client import FanoutTranClient as FanoutClient
from transconf.server.utils import from_config
from transconf.msg.rabbit.client import _get_client

CONF = os.path.join(os.path.dirname(__file__), 'default.ini')


class TranServer(AsyncServer):
    DEFAULT_CONF = CONF

    @property
    @from_config('local_group_uid', None)
    def _conf_get_uuid(self):
        return self.conf

    @property
    @from_config('local_group_name', 'default_group_name')
    def _conf_get_name(self):
        return self.conf

    @property
    @from_config('local_group_type', 'default_group_type')
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


class TopicTranClient(TopicClient):
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


client_list = [
    ('topic', TopicTranClient),
    ('fanout', FanoutClient),
    ('rpc', RPCClient),
]

client_conf_file = CONF 

def get_client(section_name, type='topic', amqp_url=None, conf=client_conf_file):
    @from_config('group_name', None, sect=section_name)
    def get_group_name(conf):
        return conf
    @from_config('group_type', None, sect=section_name)
    def get_group_type(conf):
        return conf
    group_name = get_group_name(conf)
    group_type = get_group_type(conf)
    global client_list
    c = _get_client(client_list, type, amqp_url)
    if not c: 
        return 
    if type == 'topic':
        if group_name and group_type:
            c.config(group_name, group_type)
            return c
    elif type == 'rpc':
        if group_name:
            c.config(queue=group_name+'rpc')
            return c
    elif type == 'fanout':
        if group_name:
            c.config(exchange=group_name+'fanout')
            return c
     