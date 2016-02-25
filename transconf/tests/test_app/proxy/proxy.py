__author__ = 'chijun'

import os

CONF_PATH = './etc'

here = os.path.dirname(os.path.abspath(__file__))
here_etc = os.path.join(here, CONF_PATH)

from transconf.utils import as_config

cmd_conf = as_config(os.path.join(os.path.dirname(__file__), 
                                  '{0}/proxy_cmds.ini'.format(CONF_PATH)))

from transconf.server.twisted.wsgi import TranMiddleware, TranServer, URLMiddleware
from transconf.command_driver import command_configure
from transconf.server.paste.deploy import loadapp


class ProxyMiddleware(TranMiddleware):
    def process_request(self, context):
        return super(ProxyMiddleware, self).process_request(context)


if __name__ == '__main__':
    command_configure(cmd_conf)
    app = loadapp('config:proxy.ini',
                  'main',
                  relative_to=here_etc)
    server = TranServer()
    server.setup_mq(app['mainrpc'])
    server.start()
