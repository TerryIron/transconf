__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from transconf.shell import ModelShell
from transconf.server.rabbit_msg import get_rabbit_client


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    #client = get_rabbit_client(type='rpc')
    #for i in range(10):
    #    data = dict(expression='hello.rpc',
    #            args=[1,2,3,4],
    #            kwargs={'value': i}
    #            )
    #    client.call(data)
    client = get_rabbit_client(type='topic')
    for i in range(10):
        data = dict(expression='hello.topic',
                args=[1,2,3,4],
                kwargs={'value': i}
                )
        client.call(data, 'default_worker')
    client = get_rabbit_client(type='fanout')
    for i in range(10):
        data = dict(expression='hello.fanout',
                args=[1,2,3,4],
                kwargs={'value': i}
                )
        client.call(data, 'default_fanout_exchange')
