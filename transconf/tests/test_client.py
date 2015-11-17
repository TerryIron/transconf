__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from transconf.shell import ModelShell
from transconf.msg.rabbit.client import get_client


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model(Ifconfig)
    client = get_client(type='rpc')
    for i in range(1):
        data = dict(kwargs={'value': i,
                            'target': 'if_name.ip_addr.test_name:test',
                            'method': 'owner_ip_addr',
                    }
                )
        client.cast(data)
    client = get_client(type='topic')
    for i in range(1):
        data = dict(kwargs={'value': i,
                            'target': 'if_name.hw_addr',
                            'method': 'hw_addr',
                    }
                )
        client.cast(data, 'default_worker')
    client = get_client(type='fanout')
    for i in range(1):
        data = dict(kwargs={'value': i,
                            'target': 'if_name.ip_addr.test_name:test',
                            'method': 'owner_ip_addr',
                    }
                )
        client.cast(data, 'default_fanout_exchange')
