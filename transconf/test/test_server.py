__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/..')

from shell import ModelShell
from test_shell import Ifconfig
from server.twisted.protocol import MessageShell, MessageFactory
from twisted.internet import reactor


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    ms = MessageShell(sh)
    mf = MessageFactory(ms)
    reactor.listenTCP(8888,
                      mf)
    reactor.run()
