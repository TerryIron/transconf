__author__ = 'chijun'

import sys
import functools

sys.path.insert(0, sys.path[0] + '/../..')

from test_internet_shell import Ifconfig

from datetime import datetime

from transconf.server.twisted.service import Middleware
from transconf.server.twisted.internet import TranServer
from transconf.server.twisted.netshell import NetShell, ShellMiddleware
from transconf.shell import ModelShell

class ServerMiddleware(ShellMiddleware):
    def process_request(self, context):
        if not hasattr(self, '_itm'):
            setattr(self, '_itm', datetime.now())
        else:
            print '[SERVER] used:{0}'.format((datetime.now() - self._itm).seconds)
        return super(ServerMiddleware, self).process_request(context)

if __name__ == '__main__':
    sh = NetShell()
    sh.load_model('network', Ifconfig)
    m = ServerMiddleware(sh)
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
