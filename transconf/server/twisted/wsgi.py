# coding=utf-8

__author__ = 'chijun'



from transconf.utils import as_config
from transconf.server.twisted.service import serve_forever, serve_stop
from transconf.server.twisted.internet import RPCTranServer as _RPCTranServer
from transconf.server.twisted.internet import TopicTranServer as _TopicTranServer 
from transconf.server.twisted.internet import FanoutTranServer as _FanoutTranServer
from transconf.server.twisted.service import URLTranServer as _URLTranServer
from transconf.server.twisted.event import EventMiddleware
from transconf.server.twisted.url import URLMiddleware as _URLMiddleware
from transconf.server import twisted
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class WSGIMiddleware(object):
    @classmethod
    def factory(cls, global_config, **local_config):
        twisted.CONF = as_config(global_config['__file__'])
        sh = local_config.pop('shell') if 'shell' in local_config else None

        def _factory(app, start_response=None):
            c = cls(app, **local_config)
            if sh:
                c.handler = sh
            if hasattr(c, 'process_request'):
                return c.process_request(app)
            else:
                return c
        return _factory


class URLMiddleware(_URLMiddleware, WSGIMiddleware):
    pass


class TranMiddleware(EventMiddleware, WSGIMiddleware):
    pass


class TranWSGIServer(object):

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        try:
            d = self.middleware(request)
            if hasattr(d, 'process_request'):
                return d.process_request(request)
            else:
                return d
        except Exception as e:
            LOG.error(e)


class RPCTranServer(TranWSGIServer, _RPCTranServer):
    pass


class TopicTranServer(TranWSGIServer, _TopicTranServer):
    pass


class FanoutTranServer(TranWSGIServer, _FanoutTranServer):
    pass


class URLTranServer(TranWSGIServer, _URLTranServer):
    pass


class TranServer(object):
    def __init__(self, pool_size=1000):
        self.pool_size = pool_size

    def setup_mq(self, app):
        for s in (RPCTranServer, TopicTranServer, FanoutTranServer):
            serve = s()
            serve.setup(app)
            serve.register()

    def setup_url(self, app, port=9889):
        serve = URLTranServer(app)
        serve.register(port)

    def start(self):
        serve_forever(pool_size=self.pool_size)

    def stop(self):
        serve_stop()

    def wait(self):
        raise NotImplementedError()
