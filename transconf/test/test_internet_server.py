__author__ = 'chijun'

import sys
import functools

sys.path.insert(0, sys.path[0] + '/../..')

from test_internet_shell import Ifconfig

from datetime import datetime

from transconf.server.twisted.service import Middleware
from transconf.server.twisted.internet import TranServer
from transconf.server.twisted.netshell import NetShell
from transconf.shell import ModelShell

class ShellMiddleware(Middleware):
    def process_request(self, context):
        if not hasattr(self, '_itm'):
            setattr(self, '_itm', datetime.now())
        else:
            print '[SERVER] used:{0}'.format((datetime.now() - self._itm).seconds)
        value = context['kwargs']['value']
        target = context['kwargs']['target']
        method = context['kwargs']['method']
        cb = functools.partial(self.handler.run, target, method, value)
        return cb()

if __name__ == '__main__':
    sh = NetShell()
    sh.load_model('network', Ifconfig)
    m = ShellMiddleware(sh)
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
