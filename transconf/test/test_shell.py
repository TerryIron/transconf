import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/../..')

from transconf.common.reg import register_model
from transconf.model import Model
from transconf.shell import ModelShell

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
        return ifname

    def hw_addr(self, ifname):
        print 2

    def mask(self, ifname):
        print 3

    def boardcast(self, ifname):
        print 4

if __name__ == '__main__':
    sh = ModelShell()
    sh.load_model('1234567', Ifconfig)
    for i in range(10000):
        sh.run('1234567.if_name.ip_addr.aaaaa:test', 'owner_ip_addr', i)