__author__ = 'chijun'

import os
import uuid
import pika

class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        import json
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        import json
        return json.loads(json_data)


def get_conf(opt, default_val, sect=None):
    def _get_conf(func):
        def __get_conf(*args, **kwargs):
            conf = func(*args, **kwargs)
            import ConfigParser
            config = ConfigParser.ConfigParser()  
            config.read(conf)
            if not sect:
                default_sect = config._defaults
                val = default_sect.get(opt, None)
                return val if val else default_val
        return __get_conf
    return _get_conf


class RabbitAMQP(object):
    CONNECTION_ATTEMPTS = 3
    DEFAULT_CONF = os.path.join(os.path.dirname(__file__), 'default.ini')
    CONF_FILE = None

    def __init__(self, amqp_url, timeout=5):
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
        )
        self.packer = JsonSerializionPacker()
        if self.CONF_FILE:
            self.conf = self.CONF_FILE
        else:
            self.conf = self.DEFAULT_CONF
        self.bind_rpc_queue = None
        self.bind_topic_exchange = None
        self.bind_topic_queue = None
        self.bind_topic_routing_key = None
        self.init()

    def init(self):
        pass

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


def hold_on(func):
    def __do_hold_on(self, *args, **kwargs):
        def on_response(self, ch, method, properties, body):
            if self.corr_id == properties.correlation_id:
               self.res = body
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)
        self.res = None
        # Send message
        func(self, *args, **kwargs)
        while self.res is None:
            self.connection.process_data_events()
        return self.res
    return __do_hold_on


class RPCTranClient(RabbitAMQP):

    def _on_connect(self):
        self.connection = pika.BlockingConnection(self.parms)
        self.channel = self.connection.channel()

    def config(self):
        self.bind_rpc_queue = self.conf_rpc_queue

    def init(self):
        self.config()
        self._on_connect()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

    @get_conf('rpc_binding_queue', 'default_rpc_queue')
    @property
    def default_rpc_queue(self):
        return self.conf

    @property
    def own_corr_id(self):
        return str(uuid.uuid4())

    def _call(self, context, exchange, routing_key, reply_to, corr_id):
        self.corr_id = corr_id
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=reply_to,
                                       correlation_id=corr_id,
                                       delivery_mode=2,
                                   ),
                                   body=self.packer.pack(context))

    def call(self, context):
        return self._call(context, 
                          '', 
                          self.bind_rpc_queue, 
                          self.callback_queue, 
                          self.own_corr_id)
        
    @hold_on
    def call_ack(self, context):
        self.call(self, context)


class TopicTranClient(RPCTranClient):

    def config(self):
        self.bind_topic_exchange = self.conf_topic_exchange()

    def init(self):
        super(TopicTranClient, self).init()
        self.channel.exchange_declare(exchange=self.bind_topic_exchange,
                                      type='topic')

    @get_conf('topic_binding_exchange', 'default_topic_exchange')
    @property
    def conf_topic_exchange(self):
        return self.conf

    def call(self, routing_key, context):
        real_routing = str(routing_key)
        uid = self.own_corr_id
        self._call(context, 
                   self.bind_topic_exchange, 
                   real_routing,
                   real_routing + uid,
                   uid
                   )

    @hold_on
    def call_ack(self, routing_key, context):
        self.call(routing_key, context)


def get_rpc_client(amqp_url, typ):
    if typ == 'rpc':
        return RPCTranClient(amqp_url)
    elif typ == 'topic':
        return TopicTranClient(amqp_url)
