#coding=utf-8

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
from twisted.web.server import Site, Request
from twisted.web.http import unquote, datetimeToString, networkString
from twisted.python import failure

from transconf.msg.rabbit.core import RabbitAMQP
from transconf.server.response import Response
from transconf.server.crypto import Crypto
from transconf.server.twisted.log import getLogger
from transconf import __version__

LOG = getLogger(__name__)


SERVER = []


def serve_register(func, *args, **kwargs):
    SERVER.append(functools.partial(func, *args, **kwargs))


def serve_register_tcp(app, port):
    reactor.listenTCP(port, app)


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


class RPCTranServer(RabbitAMQP, Crypto):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection
    TIMEOUT = 30

    def init(self):
        self.bind_exchange = ''
        self.bind_queue = None
        self.bind_routing_key = None

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        self.middleware.process_request(request)

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
        LOG.debug('Result back to queue:{0}, result:{1}'.format(properties.reply_to, result))
        result = self.packer.pack(result)
        result = self.encode(result)
        # If not result, some unexpected errors happened
        yield ch.basic_publish(exchange='',
                               routing_key=properties.reply_to,
                               properties=pika.BasicProperties(
                                   correlation_id=properties.correlation_id
                               ),
                               body=result)

    @defer.inlineCallbacks
    def success(self, result):
        yield defer.returnValue(Response.success(result))

    @defer.inlineCallbacks
    def failed(self, err):
        yield defer.returnValue(Response.fail(err))

    def _process_request(self, ch, properties, body):
        LOG.debug('Ready to process request, body:{0}'.format(body))
        if isinstance(body, dict):
            body = self.process_request(body)
            if body:
                body.addCallbacks(lambda result: self.success(result),
                                  errback=lambda err: self.failed(err))
                body.addBoth(lambda ret: self._result_back(ch, properties, ret))

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        ch, method, properties, body = yield queue_object.get()
        yield ch.basic_ack(delivery_tag=method.delivery_tag)
        # LOG.debug('ch: {0}, method:{1}, properties:{2}, body length:{3}'.format(ch, method, properties, len(body)))
        body = self.decode(body)
        body = self.packer.unpack(body)
        yield self._process_request(ch, properties, body)
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


version = networkString("TransWeb {0}".format(__version__))


class URLRequest(Request):
    def getRequest(self):
        x = self.getStateToCopy()
        del x['transport']
        # XXX refactor this attribute out; it's from protocol
        # del x['server']
        del x['channel']
        del x['content']
        del x['site']
        if 'HTTPS' in x['clientproto']:
            x['wsgi.url_scheme'] = 'HTTPS'
        else:
            x['wsgi.url_scheme'] = 'HTTP'
        x['requestHeaders'] = self.getAllHeaders()

        return x

    def process(self):
        # get site from channel
        self.site = self.channel.site

        # set various default headers
        self.setHeader(b'server', version)
        self.setHeader(b'date', datetimeToString())

        # Resource Identification
        self.prepath = []
        self.postpath = list(map(unquote, self.path[1:].split(b'/')))

        LOG.debug('Site target:{0}'.format(self.site))
        LOG.debug('Site path:{0}'.format(self.path))
        LOG.debug('Site content:{0}'.format(self.content))
        LOG.debug('Server response header:{0}'.format(self.responseHeaders))
        LOG.debug('Get post path:{0}'.format(self.postpath))
        try:
            res = self.site.process_request(self.getRequest())
            self.render(res)
        except:
            self.processingFailed(failure.Failure())


class URLTranServer(Site):
    requestFactory = URLRequest

    def startFactory(self):
        pass

    def stopFactory(self):
        pass

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        return self.middleware.process_request(request)

    def register(self, port):
        serve_register_tcp(self, port)
