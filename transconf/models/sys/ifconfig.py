__author__ = 'chijun'

from __init__ import Model
from __init__ import register_model


@register_model('ifdev')
class Ifconfig(Model):
    FORM = [{'node': 'if_name',
               'subs': [
                        {'node': 'ip_addr',
                         'method': 'mod:ifdev:ip_addr',
                        },
                        {'node': 'hw_addr',
                         'method': 'mod:ifdev:hw_addr',
                        },
                        {'node': 'mask',
                         'method': 'mod:ifdev:mask',
                        },
                        {'node': 'boardcast',
                         'method': 'mod:ifdev:boardcast',
                        }
               ]}
            ]
    def ip_addr(self, ifname):
        print 1

    def hw_addr(self, ifname):
        print 2

    def mask(self, ifname):
        print 3

    def boardcast(self, ifname):
        print 4

if __name__ == '__main__':
    import doctest
    doctest.testmod()
