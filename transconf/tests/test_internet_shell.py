import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/../..')

from twisted.internet.threads import deferToThread

from transconf.common.reg import register_model
from transconf.model import Model
from transconf.shell import ModelShell
from transconf.server.twisted.internet import get_client
from transconf.server.twisted.netshell import ShellRequest

"""
    Simple unit test, or a sample code for developers.
"""

def sleeping(timeout):
    from time import sleep
    sleep(timeout)

@register_model('ifdev')
class Ifconfig(Model):
    FORM = [{'node': 'if_name',
            'subs': [
                     {'node': 'ip_addr',
                      'public': ['ip_addr', 'mod:ifdev:ip_addr'],
                      'subs': [
                               {'node': 'test_name',
                                'private': ['owner_ip_addr', 'mod:ifdev:ip_addr'],
                                'name': ['owner_found_ip_addr', 'mod:ifdev:owner_found_ip_addr'],
                               },
                      ],
                     },
                     {'node': 'hw_addr',
                      'public': ['hw_addr', 'mod:ifdev:hw_addr'],
                     },
                     {'node': 'mask',
                      'public': ['mask', 'mod:ifdev:mask'],
                     },
                     {'node': 'boardcast',
                      'public': ['boardcast', 'mod:ifdev:boardcast'],
                     }
            ]}
         ]

    def owner_found_ip_addr(self, ifname):
        k = ['test']
        if ifname in k:
            return True
        return False

    def owner_ip_addr(self, ifname):
        pass

    def ip_addr(self, ifname):
        def do_things_later():
            print '[SHELL] get ip addr'
            def get_result(t):
                print '[SHELL] get result:{0}'.format(t)
            data = ShellRequest('network.if_name.hw_addr', 'hw_addr', ifname).to_dict()
            c = get_client('default_local_worker_group', 'default_type', type='topic')
            v = c.call(data)
            print '[SHELL] rpc call hw addr, client:{0}'.format(c)
            v.addCallback(get_result)
        d = deferToThread(lambda: sleeping(5))
        d.addCallback(lambda r: do_things_later())
        return '1.1.1.1'

    def hw_addr(self, ifname):
        def foo(r):
            print '[SHELL] get hw addr'
            return 'xx:xx:xx:xx:xx:xx'
        d = deferToThread(lambda: sleeping(1))
        d.addCallback(foo)
        return d

    def mask(self, ifname):
        pass

    def boardcast(self, ifname):
        pass

if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('network', Ifconfig)
    for i in range(10000):
        sh.run('network.if_name.ip_addr.test_name:test', 'owner_ip_addr', i)
