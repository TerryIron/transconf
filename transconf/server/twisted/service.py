# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'

import json

try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    from twisted.internet import selectreactor
    selectreactor.install()

import pika
import functools
import os, signal

from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task
from twisted.web.server import Site
from twisted.web.wsgi import _WSGIResponse as WSGIResponse
from twisted.web.wsgi import WSGIResource, NOT_DONE_YET, INTERNAL_SERVER_ERROR, exc_info, err, Failure
from twisted.python.threadpool import ThreadPool

from transconf.msg.rabbit.core import RabbitAMQP
from transconf.server.response import Response
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


SERVER = []


def serve_register(func, *args, **kwargs):
    SERVER.append(functools.partial(func, *args, **kwargs))


def serve_register_tcp(app, port):
    reactor.listenTCP(port, app)


def serve_forever(pool_size=1000):
    def _stop():
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        os.kill(os.getpgid(os.getpid()), signal.SIGKILL)

    for func in SERVER:
        func()
    reactor.addSystemEventTrigger('before', 'shutdown', _stop)
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

    def process_response(self, response):
        """Do whatever you'd like to the response."""
        return response

    def __call__(self, req):
        d = self.process_request(req)
        d.addCallback(lambda res: self.process_response(res))
        return d


REQUEST_ID = 0


class RPCTranServer(RabbitAMQP):
    CONNECTION_CLASS = twisted_connection.TwistedProtocolConnection
    TIMEOUT = 30

    def init(self):
        self.bind_exchange = ''
        self.bind_queue = None
        self.bind_routing_key = None

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        LOG.debug('Middleware <{0}> ready to processing.'.format(self.middleware))
        return self.middleware.process_request(request)

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
    def _result_back(self, ch, properties, result, rid=0):
        LOG.debug('Request[{0}] get back to queue:{1}, result:{2}'.format(rid, properties.reply_to, result))
        # If not result, some unexpected errors happened
        result = self.packer.pack(result)
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
        global REQUEST_ID
        REQUEST_ID += 1
        LOG.debug('Ready to process request[{0}], body length:{1}'.format(REQUEST_ID, len(body)))
        body = self.process_request(body)
        if isinstance(body, defer.Deferred):
            body.addCallbacks(lambda result: self.success(result),
                              errback=lambda err: self.failed(err))
        else:
            body = self.failed(body)
        body.addBoth(lambda ret: self._result_back(ch, properties, ret, REQUEST_ID))

    @defer.inlineCallbacks
    def on_request(self, queue_object):
        ch, method, properties, body = yield queue_object.get()
        yield ch.basic_ack(delivery_tag=method.delivery_tag)
        yield self._process_request(ch, properties, body)
        yield queue_object.close(None)

    @defer.inlineCallbacks
    def on_channel(self, channel):
        queue_object, consumer_tag = yield channel.basic_consume(queue=self.bind_queue, no_ack=False)
        l = yield task.LoopingCall(lambda: self.on_request(queue_object))
        l.start(0.0001)

    @defer.inlineCallbacks
    def on_connect(self):
        raise NotImplementedError()

    def register(self):
        serve_register(self.connect, self.on_connect)


class _Site(Site):
    def doStart(self):
        pass

    def doStop(self):
        pass


class _WSGIResponse(WSGIResponse):
    def run(self):
        try:
            def _write_response(appIterator):
                if appIterator:
                    if isinstance(appIterator, dict):
                        elem = json.dumps(appIterator)
                        self.write(elem)
                    else:
                        for elem in appIterator:
                            if elem:
                                self.write(str(elem))
                            if self._requestFinished:
                                break
                    close = getattr(appIterator, 'close', None)
                    if close is not None:
                        close()

            def _wsgi_finish():
                def wsgiFinish(started):
                    if not self._requestFinished:
                        if not started:
                            self._sendResponseHeaders()
                        self.request.finish()
                self.reactor.callFromThread(wsgiFinish, self.started)

            d = self.application(self.environ, self.startResponse)
            if isinstance(d, defer.Deferred):
                d.addCallback(lambda _appIterator: _write_response(_appIterator))
                d.addCallback(lambda r: _wsgi_finish())
        except:
            def wsgiError(started, type, value, traceback):
                err(Failure(value, type, traceback), "WSGI application error")
                if started:
                    self.request.transport.loseConnection()
                else:
                    self.request.setResponseCode(INTERNAL_SERVER_ERROR)
                    self.request.finish()
            self.reactor.callFromThread(wsgiError, self.started, *exc_info())
        self.started = True


class _WSGIResource(WSGIResource):
    def render(self, request):
        response = _WSGIResponse(
            self._reactor, self._threadpool, self._application, request)
        response.start()
        return NOT_DONE_YET


class URLTranServer(object):
    def __init__(self, app):
        self.pool = ThreadPool()
        self.pool.start()
        self.resource = _WSGIResource(reactor, self.pool, app)
        self.site = _Site(self.resource)

    def register(self, port):
        serve_register_tcp(self.site, port)
