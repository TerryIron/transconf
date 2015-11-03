__author__ = 'chijun'

from transconf.utils import as_config

from transconf.server.twisted.event import EventMiddleware
from transconf.server.twisted.models import model_configure


class TranMiddleware(EventMiddleware):
    def __init__(self, application):
        print application
        app = as_config(application)
        super(TranMiddleware, self).__init__(model_configure(app))

    @classmethod                                                                                                                                               
    def factory(cls, global_config, **local_config):
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
