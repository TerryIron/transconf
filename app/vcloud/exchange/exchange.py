__author__ = 'chijun'

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
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


class ServerMiddleware(ShellMiddleware):
    def process_request(self, context):
        print context
        return super(ServerMiddleware, self).process_request(context)


if __name__ == '__main__':
    m = ServerMiddleware(model_configure(model_conf))
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
