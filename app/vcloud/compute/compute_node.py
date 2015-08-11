__author__ = 'chijun'

INSTALL_PATH = './etc'

import os

from transconf.server import twisted
from transconf.server.utils import as_config

serve_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/compute_node.ini'.format(INSTALL_PATH)))
model_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                    '{0}/compute_node_models.ini'.format(INSTALL_PATH)))
cmd_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                  '{0}/compute_node_cmds.ini'.format(INSTALL_PATH)))
twisted.CONF = serve_conf

from transconf.server.twisted.internet import TranServer
from transconf.server.twisted.utils import TranMiddleware
from transconf.server.twisted.models import model_configure
from transconf.driver import command_configure


class ServerMiddleware(TranMiddleware):
    def process_request(self, context):
        return super(ServerMiddleware, self).process_request(context)


if __name__ == '__main__':
    command_configure(cmd_conf)
    m = ServerMiddleware(model_configure(model_conf))
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
