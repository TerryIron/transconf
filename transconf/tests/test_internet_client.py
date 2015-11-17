__author__ = 'chijun'

import sys

sys.path.insert(0, sys.path[0] + '/../..')

from test_shell import Ifconfig

from transconf.shell import ModelShell
from transconf.msg.rabbit.client import get_client
from transconf.server.twisted.netshell import ShellRequest


if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('network', Ifconfig)
    client = get_client(type='rpc')
    for i in range(1):
        data = ShellRequest('if_name.ip_addr.test_name:test', 'owner_ip_addr', i).to_dict()
        client.cast(data, 'default_local_worker_grouprpc')
    client = get_client(exchange='default_local_worker_grouptopic', queue='default_local_worker_group', type='topic')
    for i in range(1):
        data = ShellRequest('if_name.hw_addr', 'hw_addr', i).to_dict()
        client.cast(data, 'default_type')
    client = get_client(type='fanout')
    for i in range(1):
        data = ShellRequest('if_name.ip_addr.test_name:test', 'owner_ip_addr', i).to_dict()
        client.cast(data, 'default_local_worker_groupfanout')
