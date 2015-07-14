__author__ = 'chijun'

from transconf.server.twisted.service import Middleware
from transconf.server.twisted.internet import TranServer
from transconf.server.twisted.netshell import NetShell, ShellMiddleware
from transconf.shell import ModelShell

class ServerMiddleware(ShellMiddleware):
    def process_request(self, context):
        return super(ServerMiddleware, self).process_request(context)

if __name__ == '__main__':
    sh = NetShell()
    sh.load_model('network', Ifconfig)
    m = ServerMiddleware(sh)
    serve = TranServer()
    serve.setup(m)
    serve.serve_forever()
