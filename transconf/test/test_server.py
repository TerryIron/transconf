__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/..')

from shell import ModelShell
from test_shell import Ifconfig
from server.twisted.service import RPCTranServer, RPCMiddleware
from twisted.internet import reactor

class ShellMiddleware(RPCMiddleware):
    def run(self, context):
        return self.handler.run('1234567.if_name.ip_addr.aaaaa:test', 'owner_ip_addr', 19)

if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    m = ShellMiddleware(sh)
    serve = RPCTranServer('amqp://guest:guest@localhost:5672')
    serve.setup(m)
    serve.serve_forever()
