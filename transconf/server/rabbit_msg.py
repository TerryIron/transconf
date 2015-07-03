__author__ = 'chijun'

import os
import uuid
import pika

from transconf.server.utils import JsonSerializionPacker
from transconf.server.utils import from_config


class RabbitAMQP(object):
    CONNECTION_CLASS = pika.BlockingConnection
    CONNECTION_ATTEMPTS = 3
    DEFAULT_CONF = os.path.join(os.path.dirname(__file__), 'rabbit_default.ini')
    CONF_FILE = None

    def __init__(self, amqp_url=None, timeout=5):
        self.connection_class = self.CONNECTION_CLASS
        self.packer = JsonSerializionPacker()
        if self.CONF_FILE:
            self.conf = self.CONF_FILE
        else:
            self.conf = self.DEFAULT_CONF
        if not amqp_url:
            amqp_url = self.conf_amqp_url
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
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
    @from_config('rabbit_url', 'amqp://guest:guest@localhost:5672')
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


# It is a static method for sync-call, don's use it outside.
def hold_on(func):
    def __do_hold_on(self, *args, **kwargs):
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)
        self.res = None
        # Send message
        func(self, *args, **kwargs)
        while self.res is None:
            self.connection.process_data_events()
        return self.res if not isinstance(self.res, NoneBody) else None
    return __do_hold_on


class NoneBody(object):
    pass


class BaseClient(RabbitAMQP):

    def _on_connect(self):
        self.connection = self.connection_class(self.parms)
        self.channel = self.connection.channel()

    def _ready(self, context, exchange, routing_key, reply_to, corr_id):
        self.corr_id = corr_id
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=reply_to,
                                       correlation_id=corr_id,
                                       delivery_mode=2,
                                   ),
                                   body=self.packer.pack(context))

    def config(self):
        raise NotImplementedError()

    def init(self):
        self.config()
        self._on_connect()
        result = self.channel.queue_declare(exclusive=True, auto_delete=True)
        self.callback_queue = result.method.queue

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            body = self.packer.unpack(body)
            if body:
                self.res = body
            else:
                self.res = NoneBody()


class RPCTranClient(BaseClient):

    def config(self, exchange=None, queue=None):
        self.bind_rpc_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        return self.conf

    def cast(self, context, routing_key=None):
        rpc_queue = self.bind_rpc_queue if not routing_key else routing_key
        self._ready(context, 
                    '', 
                    rpc_queue,
                    self.callback_queue, 
                    self.rand_corr_id)
        
    @hold_on
    def call(self, context, routing_key=None):
        self.cast(context, routing_key)


class TopicTranClient(BaseClient):

    """
    We use topic client to send tasks to worker's queue.
    """
    def config(self, exchange=None, queue=None):
        self.bind_topic_exchange = self.conf_topic_exchange if not exchange else exchange
        self.bind_topic_queue = self.conf_topic_queue if not queue else queue

    def init(self):
        super(TopicTranClient, self).init()
        self.channel.exchange_declare(exchange=self.bind_topic_exchange,
                                      type='topic')

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
        self._ready(context, 
                    self.bind_topic_exchange, 
                    '.'.join([self.bind_topic_queue, real_routing]),
                    self.callback_queue,
                    self.rand_corr_id)

    @hold_on
    def call(self, context, routing_key):
        self.cast(context, routing_key)

class FanoutTranClient(BaseClient):
    """
    We use fanout client to sync server's status by binding fanout queue as server topic.
    """
    def config(self, exchange=None, queue=None):
        self.bind_fanout_exchange = self.conf_fanout_exchange if not exchange else exchange
        self.bind_fanout_queue = self.conf_fanout_queue if not queue else queue

    def init(self):
        super(FanoutTranClient, self).init()
        self.channel.exchange_declare(exchange=self.bind_fanout_exchange,
                                      type='fanout')

    @property
    @from_config('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        return self.conf

    @property
    @from_config('fanout_binding_queue', 'default_fanout_queue')
    def conf_fanout_queue(self):
        return self.conf

    def cast(self, context, routing_key=None):
        fanout_exchange= self.bind_fanout_exchange if not routing_key else routing_key
        self._ready(context, 
                    fanout_exchange, 
                    '',
                    self.callback_queue, 
                    self.rand_corr_id)
        
    @hold_on
    def call(self, context, routing_key=None):
        self.cast(context, routing_key)


def get_rabbit_client(amqp_url=None, exchange=None, queue=None, type=''):
    client_list = [
        ('topic', TopicTranClient),
        ('fanout', FanoutTranClient),
        ('rpc', RPCTranClient), # Recommand local callback
    ]
    try:
        c = [cls(amqp_url) for t, cls in client_list if t == type].pop(0)
        c.config(exchange, queue)
        return c
    except e as IndexError:
        pass
