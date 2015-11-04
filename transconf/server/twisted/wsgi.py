__author__ = 'chijun'

from transconf.utils import as_config

from transconf.server.twisted.internet import serve_forever, RPCTranServer, TopicTranServer, FanoutTranServer
from transconf.server import twisted
from transconf.server.twisted.event import EventMiddleware
from transconf.server.twisted.models import model_configure


class TranMiddleware(EventMiddleware):
    def __init__(self, application):
        super(TranMiddleware, self).__init__(model_configure(app))

    @classmethod                                                                                                                                               
    def factory(cls, global_config, **local_config):
        twisted.CONF = as_config(global_config['__file__'])
        def _factory(app):
            return cls(app, **local_config)
        return _factory

    def process_request(self, request):
        return super(TranMiddleware, self).process_request(request)

    def process_response(self, response):
        """Do whatever you'd like to the response."""
        return response

    def __call__(self, req):
        response = self.process_request(req)
        return self.process_response(response)


class TranServer(object):
    def __init__(self, name, app, pool_size=1000):
        self.name = name
        self.app = app
        self._server = None
        self.pool_size = pool_size

    def start(self):
        for s in (RPCTranServer, TopicTranServer, FanoutTranServer):
            serve = s()
            serve.setup(self.app)
            serve.register()
        serve_forever(pool_size=self.pool_size)

    def stop(self):
        pass

    def wait(self):
        pass

