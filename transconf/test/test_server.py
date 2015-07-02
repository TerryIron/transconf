__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from datetime import datetime
from twisted.internet import reactor

from transconf.server.twisted.service import RPCTranServer, RPCMiddleware
from transconf.server.twisted.netshell import TxShell
from transconf.shell import ModelShell

class ShellMiddleware(RPCMiddleware):
    def process_request(self, context):
        if not hasattr(self, '_itm'):
            setattr(self, '_itm', datetime.now())
            self.off = True
        else:
            print 'used:{0}'.format((datetime.now() - self._itm).seconds)
        value = context['kwargs']['value']
        if self.off:
            d = self.handler.run('1234567.if_name.ip_addr.aaaaa:test', 'owner_ip_addr', value)
            self.off = False
        else:
            d = self.handler.run('1234567.if_name.hw_addr', 'hw_addr', value)
            self.off = True
        print d
        print context
        return d

if __name__ == '__main__':
    sh = TxShell()
    sh.load_model('1234567', Ifconfig)
    m = ShellMiddleware(sh)
    serve = RPCTranServer()
    serve.setup(m)
    serve.serve_forever()
