import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/../..')

from twisted.internet import defer

from transconf.common.reg import register_model
from transconf.model import Model
from transconf.shell import ModelShell
from transconf.server.twisted.client import FanoutTranClient

"""
    Simple unit test, or a sample code for developers.
"""

@register_model('ifdev')
class Ifconfig(Model):
    METHOD_TABLE = {'owner_ip_addr': 'private'}
    FORM = [{'node': 'if_name',
            'subs': [
                     {'node': 'ip_addr',
                      'public': ['ip_addr', 'mod:ifdev:ip_addr'],
                      'subs': [
                               {'node': 'aaaaa',
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
        print 0

    def ip_addr(self, ifname):
        c = FanoutTranClient()
        data = dict(expression='client.fanout',
                    args=[1,2,3,4],
                    kwargs={'value': ifname}
                   )
        #from time import sleep
        #d = defer.Deferred()
        #d.addCallback(lambda: sleep(5))
        c.cast(data, 'default_fanout_exchange')
        v = c.call(data, 'default_fanout_exchange')
        print 'ip_addr:{0}'.format(v)
        return ifname

    def hw_addr(self, ifname):
        print 'hw_addr'

    def mask(self, ifname):
        print 3

    def boardcast(self, ifname):
        print 4

if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    for i in range(10000):
        sh.run('1234567.if_name.ip_addr.aaaaa:test', 'owner_ip_addr', i)
