__author__ = 'chijun'

import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/../../..')

INSTALL_PATH = './etc'

import os

from transconf.server.twisted import internet
from transconf.server.utils import as_config

serve_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/compute.ini'.format(INSTALL_PATH)))
model_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/compute_models.ini'.format(INSTALL_PATH)))
internet.CONF = serve_conf

from transconf.server.twisted.internet import TranServer
TranServer.CONF = serve_conf
from transconf.server.twisted.netshell import ShellMiddleware
from transconf.server.twisted.models import model_configure


class ServerMiddleware(ShellMiddleware):
    def process_request(self, context):
        return super(ServerMiddleware, self).process_request(context)


if __name__ == '__main__':
    m = ServerMiddleware(model_configure(model_conf))
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
