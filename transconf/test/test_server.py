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
    def run(self, context):
        if not hasattr(self, '_itm'):
            setattr(self, '_itm', datetime.now())
        else:
            print 'used:{0}'.format((datetime.now() - self._itm).seconds)
        value = context['kwargs']['value']
        d = self.handler.run('1234567.if_name.ip_addr.aaaaa:test', 'owner_ip_addr', value)
        print context
        return d

if __name__ == '__main__':
    sh = TxShell()
    sh.load_model('1234567', Ifconfig)
    m = ShellMiddleware(sh)
    serve = RPCTranServer('amqp://guest:guest@localhost:5672')
    serve.setup(m)
    serve.serve_forever()
