__author__ = 'chijun'

import pika

from transconf.msg.rabbit.core import RabbitAMQP
from transconf.utils import from_config_option


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
    """
        RabbitMQ客户端封装

    """

    def _on_connect(self):
        self.connection = self.connection_class(self.parms)
        self.channel = self.connection.channel()

    def _ready(self, context, exchange, routing_key, reply_to, corr_id, delivery_mode=2):
        self.corr_id = corr_id
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=reply_to,
                                       correlation_id=corr_id,
                                       delivery_mode=delivery_mode,
                                   ),
                                   body=self.packer.pack(context))

    def config(self):
        """
        初始化配置

        Returns:
            未实现

        """
        raise NotImplementedError()

    def init(self):
        """
        初始化客户端

        Returns:
            None

        """
        self.config()
        self._on_connect()
        result = self.channel.queue_declare(exclusive=True, auto_delete=True)
        self.callback_queue = result.method.queue

    def on_response(self, ch, method, properties, body):
        """
        响应结果

        Args:
            ch: 频道
            method: 方法
            properties: 属性
            body: 结果

        Returns:
            None

        """
        if self.corr_id == properties.correlation_id:
            body = self.packer.unpack(body)
            if body:
                self.res = body['result']
            else:
                self.res = NoneBody()


class RPCTranClient(BaseClient):

    def config(self, exchange=None, queue=None):
        """
        初始化RPC模式配置

        Returns:
            None

        """
        self.bind_queue = self.conf_rpc_queue if not queue else queue

    @property
    @from_config_option('rpc_binding_queue', 'default_rpc_queue')
    def conf_rpc_queue(self):
        """
        Returns:
            str: RPC队列名

        """
        return self.conf

    def cast(self, context, routing_key=None, delivery_mode=2):
        """
        发送数据，不返回结果


        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            None

        """
        rpc_queue = self.bind_queue if not routing_key else routing_key
        self._ready(context, 
                    '', 
                    rpc_queue,
                    self.callback_queue, 
                    self.rand_corr_id,
                    delivery_mode)
        
    @hold_on
    def call(self, context, routing_key=None, delivery_mode=2):
        """
        发送数据，返回结果 (等待结果)

        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            结果

        """
        self.cast(context, routing_key, delivery_mode)


class TopicTranClient(BaseClient):

    """
    We use topic client to send tasks to worker's queue.
    """
    def config(self, exchange=None, queue=None):
        """
        初始化TOPIC模式配置

        Returns:
            None

        """
        self.bind_exchange = self.conf_topic_exchange if not exchange else exchange
        self.bind_queue = self.conf_topic_queue if not queue else queue

    def init(self):
        """
        初始化TOPIC客户端

        Returns:
            None

        """
        super(TopicTranClient, self).init()
        self.channel.exchange_declare(exchange=self.bind_exchange,
                                      type='topic')

    @property
    @from_config_option('topic_binding_exchange', 'default_topic_exchange')
    def conf_topic_exchange(self):
        """
        Returns:
            str: TOPIC交换机名称

        """
        return self.conf

    @property
    @from_config_option('topic_binding_queue', 'default_topic_queue')
    def conf_topic_queue(self):
        """
        Returns:
            str: TOPIC队列名称

        """
        return self.conf

    def cast(self, context, routing_key):
        """
        发送数据，不返回结果


        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            None

        """
        real_routing = str(routing_key)
        self._ready(context, 
                    self.bind_exchange,
                    '.'.join([self.bind_queue, real_routing]),
                    self.callback_queue,
                    self.rand_corr_id)

    @hold_on
    def call(self, context, routing_key):
        """
        发送数据，返回结果 (等待结果)

        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            结果

        """
        self.cast(context, routing_key)


class FanoutTranClient(BaseClient):
    """
    We use fanout client to sync server's status.
    """
    def config(self, exchange=None, queue=None):
        """
        初始化FANOUT模式配置

        Returns:
            None

        """
        self.bind_exchange = self.conf_fanout_exchange if not exchange else exchange
        self.bind_queue = self.conf_fanout_queue if not queue else queue

    def init(self):
        """
        初始化FANOUT客户端

        Returns:
            None

        """
        super(FanoutTranClient, self).init()
        self.channel.exchange_declare(exchange=self.bind_exchange,
                                      type='fanout')

    @property
    @from_config_option('fanout_binding_exchange', 'default_fanout_exchange')
    def conf_fanout_exchange(self):
        """
        Returns:
            str: FANOUT交换机名称

        """
        return self.conf

    @property
    @from_config_option('fanout_binding_queue', 'default_fanout_queue')
    def conf_fanout_queue(self):
        """
        Returns:
            str: FANOUT队列名称

        """
        return self.conf

    def cast(self, context, routing_key=None):
        """
        发送数据，不返回结果


        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            None

        """
        fanout_exchange= self.bind_exchange if not routing_key else routing_key
        self._ready(context, 
                    fanout_exchange, 
                    '',
                    self.callback_queue, 
                    self.rand_corr_id)
        
    @hold_on
    def call(self, context, routing_key=None):
        """
        发送数据，返回结果 (等待结果)

        Args:
            context: 发送数据
            routing_key: 路由关键字
            delivery_mode: 投递模式

        Returns:
            结果

        """
        self.cast(context, routing_key)


client_list = [
    ('topic', TopicTranClient),
    ('fanout', FanoutTranClient),
    ('rpc', RPCTranClient),
]


def _get_client(client_list, type, amqp_url=None, exchange=None, queue=None):
    for t, cls in client_list:
        if t == type:
            c = cls(amqp_url)
            return c


def get_client(amqp_url=None, exchange=None, queue=None, type='topic'):
    """
    获取客户端

    Args:
        amqp_url: AMQP地址
        exchange: 交换机名
        queue: 队列名
        type: 类型

    Returns:

    """
    c = _get_client(client_list, type, amqp_url, exchange, queue)
    if not c: 
        return 
    c.config(exchange, queue)
    return c
