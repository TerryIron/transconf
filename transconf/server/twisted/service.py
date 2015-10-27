__author__ = 'chijun'

import pika
import functools

from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

from transconf.msg.rabbit.core import RabbitAMQP
from transconf.server.utils import from_config_option
from transconf.server.request import Response
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


SERVER = []


def serve_register(func, *args, **kwargs):
    SERVER.append(functools.partial(func, *args, **kwargs))


def serve_forever():
    for func in SERVER:
        func()
    reactor.run()


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
        assert isinstance(middleware, Middleware)
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
                               body=self.packer.pack(result.as_dict()))
        
    @defer.inlineCallbacks
    def success(self, result):
        yield defer.returnValue(Response.success(result))

    @defer.inlineCallbacks
    def failed(self, err):
        yield defer.returnValue(Response.failed(err))

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        ch, method, properties, body = yield queue_object.get()
        LOG.debug('CH:{0}, METHOD:{1}, PROPERITES:{2}'.format(ch, method, properties))
        body = yield self.packer.unpack(body)
        if body:
            yield ch.basic_ack(delivery_tag=method.delivery_tag)
            body = yield self.process_request(body)
            if body:
                body.addCallbacks(lambda result: self.success(result),
                                  errback=lambda err: self.failed(err))
                body.addBoth(lambda ret: self._result_back(ch, properties, ret))
        #LOG.debug('CH:{0},{1}'.format(ch, dir(ch)))
        #LOG.debug('CH connection:{0}, {1}'.format(ch.connection, dir(ch.connection)))
        #LOG.debug('CH Properties:{0}, {1}'.format(properties, dir(properties)))
        #LOG.debug('CH queue_object:{0}, {1}'.format(queue_object, dir(queue_object)))
        yield queue_object.close(None)
        yield ch.queue_delete()

    @defer.inlineCallbacks
    def on_channel(self, channel):
        queue_object, consumer_tag = yield channel.basic_consume(queue=self.bind_queue, no_ack=False)
        l = yield task.LoopingCall(lambda: self.on_request(queue_object))
        l.start(0.001)

    @defer.inlineCallbacks
    def on_connect(self):
        raise NotImplementedError()

    def register(self):
        #self.connect(self.on_connect)
        serve_register(self.connect, self.on_connect)

