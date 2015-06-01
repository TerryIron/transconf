__author__ = 'chijun'

import commands

try:
    from transconf.dev import ContentParser
    from transconf.dev.plugin.base import ExtensionNode
except:
    from ..dev import ContentParser
    from ..dev.plugin.base import ExtensionNode


__all__ = ['Ifconfig']


class Ifconfig(ContentParser):
    """
    Usage:
    >>> def scan():
    ...     return ''''
    ... lo      Link encap:Local Loopback
    ...         inet addr:127.0.0.1  Mask:255.0.0.0
    ...         inet6 addr: ::1/128 Scope:Host
    ...         UP LOOPBACK RUNNING  MTU:16436  Metric:1
    ...         RX packets:56389 errors:0 dropped:0 overruns:0 frame:0
    ...         TX packets:56389 errors:0 dropped:0 overruns:0 carrier:0
    ...         collisions:0 txqueuelen:0
    ...         RX bytes:3867686 (3.8 MB)  TX bytes:3867686 (3.8 MB)
    ... virbr0  Link encap:Ethernet  HWaddr 12:34:56:78:90:ff
    ...         inet addr:192.168.1.1  Bcast:192.168.1.255  Mask:255.255.255.0
    ...         UP BROADCAST MULTICAST  MTU:1500  Metric:1
    ...         RX packets:0 errors:0 dropped:0 overruns:0 frame:0
    ...         TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
    ...         collisions:0 txqueuelen:0
    ...         RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
    ... wlan0   Link encap:Ethernet  HWaddr 11:22:33:44:55:66
    ...         inet addr:192.168.2.1  Bcast:192.168.2.255  Mask:255.255.255.0
    ...         inet6 addr: fe80::5a94:6bff:fe73:81c4/64 Scope:Link
    ...         UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
    ...         RX packets:1437000 errors:0 dropped:0 overruns:0 frame:0
    ...         TX packets:761049 errors:0 dropped:0 overruns:0 carrier:0
    ...         collisions:0 txqueuelen:1000
    ... wlan1   Link encap:Ethernet  HWaddr 11:22:33:44:55:68
    ... '''
    >>> r = Ifconfig()
    >>> r.scan = scan
    >>> result = r.run()
    >>> result.has()
    ['if_name']
    >>> result.if_name['lo'].ip_addr
    ['127.0.0.1']
    >>> result.if_name['lo'].mask
    ['255.0.0.0']
    >>> result.if_name['virbr0'].ip_addr
    ['192.168.1.1']
    >>> result.if_name['virbr0'].hw_addr
    ['12:34:56:78:90:ff']
    >>> result.if_name['virbr0'].mask
    ['255.255.255.0']
    >>> result.if_name['virbr0'].boardcast
    ['192.168.1.255']
    >>> result.if_name['wlan0'].ip_addr
    ['192.168.2.1']
    >>> result.if_name['wlan0'].hw_addr
    ['11:22:33:44:55:66']
    >>> result.if_name['wlan0'].mask
    ['255.255.255.0']
    >>> result.if_name['wlan0'].boardcast
    ['192.168.2.255']
    >>> result.if_name['wlan1'].hw_addr
    ['11:22:33:44:55:68']
    >>> result.if_name['wlan1'].ip_addr.is_end
    True
    >>> result.if_name['wlan1'].hw_addr.is_end
    True
    >>> result.if_name['wlan1'].is_end
    False
    """

    NODE_CLASS = ExtensionNode
    FORMAT = [{'node': 'if_name',
               'regex': ['^([0-9a-z]+) .*'],
               'subs': [
                    {'node': 'ip_addr',
                     'regex': ['^.*inet addr:([0-9.]+)']
                    },
                    {'node': 'hw_addr',
                     'regex': ['^.*HWaddr ([0-9a-e:]+.*)']
                    },
                    {'node': 'mask',
                     'regex': ['^.*Mask:([0-9.]+)']
                    },
                    {'node': 'boardcast',
                     'regex': ['^.*Bcast:([0-9.]+)']
                    }
               ]
    }]

    def scan(self):
        return commands.getoutput('ifconfig')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
