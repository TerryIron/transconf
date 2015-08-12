__author__ = 'chijun'

import os
import uuid
import pika

from transconf.server.utils import JsonSerializionPacker
from transconf.server.utils import from_config_option, as_config


class RabbitAMQP(object):
    CONNECTION_CLASS = pika.BlockingConnection
    CONNECTION_ATTEMPTS = 3
    DEFAULT_CONF = as_config(os.path.join(os.path.dirname(__file__), 'default.ini'))
    CONF = None

    def __init__(self, amqp_url=None, con_timeout=5, con_attempts=3):
        self.connection_class = self.CONNECTION_CLASS
        self.packer = JsonSerializionPacker()
        self.conf = self.DEFAULT_CONF if not self.CONF else self.CONF
        self.parms = None
        if not amqp_url:
            amqp_url = self.conf_amqp_url
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(con_timeout,
                                             con_attempts or self.CONNECTION_ATTEMPTS)
        )
        self.bind_rpc_queue = None
        self.bind_topic_exchange = None
        self.bind_topic_queue = None
        self.bind_topic_routing_key = None
        self.bind_fanout_exchange = None
        self.bind_fanout_queue = None
        self.init()

    def init(self):
        pass

    @property
    def rand_corr_id(self):
        return str(uuid.uuid4())

    @property
    @from_config_option('amqp_url', 'amqp://guest:guest@localhost:5672')
    def conf_amqp_url(self):
        return self.conf

    @property
    def conf_rpc_queue(self):
        raise NotImplementedError()

    @property
    def conf_topic_exchange(self):
        raise NotImplementedError()

    @property
    def conf_topic_queue(self):
        raise NotImplementedError()

    @property
    def conf_topic_routing_key(self):
        raise NotImplementedError()

    @property
    def conf_fanout_exchange(self):
        raise NotImplementedError()

    @property
    def conf_fanout_queue(self):
        raise NotImplementedError()

