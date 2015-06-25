__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from transconf.shell import ModelShell
from transconf.server.rpc import get_rpc_client


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    client = get_rpc_client('amqp://guest:guest@localhost:5672', 'rpc')
    for i in range(1):
        data = dict(expression='hello.world',
                args=[1,2,3,4],
                kwargs={'value': i}
                )
        client.call(data)
