__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/..')

from shell import ModelShell
from test_shell import Ifconfig
from server.twisted.service import RPCTranClient
from twisted.internet import reactor


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    client = RPCTranClient('amqp://guest:guest@localhost:5672')
    data = dict(expression='hello.world',
                args=[1,2,3,4],
                kwargs={'kkk': 10}
                )
    for i in range(10000):
        client.call(data)
