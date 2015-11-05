__author__ = 'chijun'

try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    from twisted.internet import selectreactor
    selectreactor.install()

import pika
import functools

from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.msg.rabbit.core import RabbitAMQP
from transconf.utils import from_config_option
from transconf.server.response import Response
from transconf.server.twisted.log import getLogger


LOG  = getLogger(__name__)


SERVER = []


def serve_register(func, *args, **kwargs):
    SERVER.append(functools.partial(func, *args, **kwargs))


def serve_forever(pool_size=1000):
    for func in SERVER:
        func()
    reactor.suggestThreadPoolSize(pool_size)
    reactor.run()


def serve_stop():
    reactor.stop()


class Middleware(object):
    def __init__(self, handler):
        self.handler = handler

    def process_request(self, context):
        from twisted.internet.defer import succeed
        return succeed({})


class RPCTranServer(RabbitAMQP):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection
    TIMEOUT = 30

    def init(self):
        self.bind_exchange = ''
        self.bind_queue = None
        self.bind_routing_key = None

    """
        Setup Middleware
    """
    def setup(self, middleware):
        self.middleware = middleware

    """
        Process request by Customer Middleware 
    """
    def process_request(self, body):
        return self.middleware.process_request(body)
            

    def _connect(self):
        cc = protocol.ClientCreator(reactor, 
                                    self.connection_class,
                                    self.parms)
        return cc.connectTCP(self.parms.host, 
                             self.parms.port,
                             timeout=self.TIMEOUT)

    def connect(self, callback):
        d = self._connect()
        d.addCallback(lambda procotol: procotol.ready)
        d.addCallback(callback)

    @defer.inlineCallbacks
    def _result_back(self, ch, properties, result):
        yield ch.basic_publish(exchange=self.bind_exchange,
                               routing_key=properties.reply_to,
                               properties=pika.BasicProperties(
                                   correlation_id=properties.correlation_id
                               ),
                               body=self.packer.pack(result))
        
    @defer.inlineCallbacks
    def success(self, result):
        yield defer.returnValue(Response.success(result))

    @defer.inlineCallbacks
    def failed(self, err):
        yield defer.returnValue(Response.failed(err))

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        ch, method, properties, body = yield queue_object.get()
        body = yield self.packer.unpack(body)
        if body:
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
            body = self.process_request(body)
            if body:
                body.addCallbacks(lambda result: self.success(result),
                                  errback=lambda err: self.failed(err))
                body.addBoth(lambda ret: self._result_back(ch, properties, ret))
        yield queue_object.close(None)

    @defer.inlineCallbacks
    def on_channel(self, channel):
        queue_object, consumer_tag = yield channel.basic_consume(queue=self.bind_queue, no_ack=False)
        l = yield task.LoopingCall(lambda: self.on_request(queue_object))
        l.start(0.001)

    @defer.inlineCallbacks
    def on_connect(self):
        raise NotImplementedError()

    def register(self):
        serve_register(self.connect, self.on_connect)

