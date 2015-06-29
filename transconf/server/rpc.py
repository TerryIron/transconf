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


class RPC(object):
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
        self.name = self.own_name
        self.topic = self.own_topic

    @property
    def own_name(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()  
        config.read(self.conf)
        default_sect = config._defaults
        name = default_sect.get('service_name', None)
        return name if name else 'trans_rpc'

    @property
    def own_topic(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()  
        config.read(self.conf)
        default_sect = config._defaults
        topic = default_sect.get('service_topic', None)
        return topic if topic else 'trans_topic'


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


class RPCTranClient(RPC):

    def __init__(self, amqp_url, timeout=5):
        super(RPCTranClient, self).__init__(amqp_url, timeout)
        self.init()

    def _on_connect(self):
        self.connection = pika.BlockingConnection(self.parms)
        self.channel = self.connection.channel()

    def init(self):
        self._on_connect()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

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
                          self.name, 
                          self.callback_queue, 
                          self.own_corr_id)
        
    @hold_on
    def call_ack(self, context):
        self.call(self, context)


class TopicTranClient(RPCTranClient):

    def init(self):
        super(TopicTranClient, self).init()
        self.name =  '_'.join([self.name, 'topic'])
        self.channel.exchange_declare(exchange=self.name,
                                      type='topic')

    def call(self, routing_key, context):
        real_routing = str(routing_key)
        uid = self.own_corr_id
        self._call(context, 
                   self.name, 
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
