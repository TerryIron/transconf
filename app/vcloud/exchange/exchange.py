__author__ = 'chijun'

import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/../../..')

INSTALL_PATH = './etc'

import os

from transconf.server import twisted
from transconf.server.utils import as_config

serve_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/exchange.ini'.format(INSTALL_PATH)))
model_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/exchange_models.ini'.format(INSTALL_PATH)))
twisted.CONF = serve_conf

from transconf.server.twisted.internet import TranServer
from transconf.server.twisted.netshell import ShellMiddleware
from transconf.server.twisted.models import model_configure


class ServerMiddleware(ShellMiddleware):
    def process_request(self, context):
        print context
        return super(ServerMiddleware, self).process_request(context)


if __name__ == '__main__':
    m = ServerMiddleware(model_configure(model_conf))
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()