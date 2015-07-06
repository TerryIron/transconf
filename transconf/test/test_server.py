__author__ = 'chijun'

import sys
import functools

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from datetime import datetime
from twisted.internet import reactor, defer

from transconf.server.twisted.service import RPCTranServer, RPCMiddleware
from transconf.server.twisted.netshell import TxShell
from transconf.shell import ModelShell

class ShellMiddleware(RPCMiddleware):
    def process_request(self, context):
        if not hasattr(self, '_itm'):
            setattr(self, '_itm', datetime.now())
        else:
            print 'used:{0}'.format((datetime.now() - self._itm).seconds)
        value = context['kwargs']['value']
        target = context['kwargs']['target']
        method = context['kwargs']['method']
        print context
        def get_result(result):
            return result
        cb = functools.partial(self.handler.run, target, method, value)
        return cb()

if __name__ == '__main__':
    sh = TxShell()
    sh.load_model('1234567', Ifconfig)
    m = ShellMiddleware(sh)
    serve = RPCTranServer()
    serve.setup(m)
    serve.serve_forever()
