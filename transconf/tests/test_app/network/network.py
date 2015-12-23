__author__ = 'chijun'

INSTALL_PATH = './etc'

import os

from transconf.server import twisted
from transconf.utils import as_config

serve_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/network.ini'.format(INSTALL_PATH)))
model_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/network_models.ini'.format(INSTALL_PATH)))
twisted.CONF = serve_conf

from transconf.server.twisted.internet import RPCTranServer, TopicTranServer, FanoutTranServer
from transconf.server.twisted.service import serve_forever
from transconf.server.twisted.models import model_configure
from transconf.server.twisted.wsgi import TranMiddleware


class ServerMiddleware(TranMiddleware):
    def process_request(self, context):
        return super(ServerMiddleware, self).process_request(context)


if __name__ == '__main__':
    m = ServerMiddleware(model_configure(model_conf))
    for s in (RPCTranServer, TopicTranServer, FanoutTranServer):
        serve = s()
        serve.setup(m)
        serve.register()
    serve_forever()