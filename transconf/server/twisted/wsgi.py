#coding=utf-8

__author__ = 'chijun'



from transconf.utils import as_config
from transconf.server.twisted.service import serve_forever, serve_stop
from transconf.server.twisted.internet import RPCTranServer as _RPCTranServer
from transconf.server.twisted.internet import TopicTranServer as _TopicTranServer 
from transconf.server.twisted.internet import FanoutTranServer as _FanoutTranServer
from transconf.server.twisted.service import URLTranServer as _URLTranServer
from transconf.server.twisted.event import EventMiddleware
from transconf.server import twisted


class TranMiddleware(EventMiddleware):
    @classmethod                                                                                                                                               
    def factory(cls, global_config, **local_config):
        assert 'shell' in local_config, 'please install model shell as shell=x'
        twisted.CONF = as_config(global_config['__file__'])
        sh = local_config.pop('shell')

        def _factory(app, start_response=None):
            c = cls(app, **local_config)
            c.handler = sh
            return c
        return _factory

    def process_request(self, request):
        d = super(TranMiddleware, self).process_request(request)
        return d

    def process_response(self, response):
        """Do whatever you'd like to the response."""
        return response

    def __call__(self, req):
        response = self.process_request(req)
        return self.process_response(response)


class TranWSGIServer(object):

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        d = self.middleware(request)
        if d:
            d = d.process_request(request)
            return d

    def process_response(self, response):
        return response


class RPCTranServer(TranWSGIServer, _RPCTranServer):
    pass


class TopicTranServer(TranWSGIServer, _TopicTranServer):
    pass


class FanoutTranServer(TranWSGIServer, _FanoutTranServer):
    pass


class URLTranServer(TranWSGIServer, _URLTranServer):
    def setup(self, middleware):
        self.resource = middleware


class TranServer(object):
    def __init__(self, pool_size=1000):
        self.pool_size = pool_size

    def setup_rpc(self, app):
        for s in (RPCTranServer, TopicTranServer, FanoutTranServer):
            serve = s()
            serve.setup(app)
            serve.register()

    def setup_url(self, app, port=9889):
        serve = URLTranServer()
        serve.setup(app)
        serve.register(port)

    def start(self):
        serve_forever(pool_size=self.pool_size)

    def stop(self):
        serve_stop()

    def wait(self):
        raise NotImplementedError()
