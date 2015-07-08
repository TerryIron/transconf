__author__ = 'chijun'

"""
TransConf
---------

TransConf is a framework based on Twisted, AMQP, SqlAlChemy.

Save in a shell.py:

.. code:: python

    from transconf.common.reg import register_model
    from transconf.model import Model
    from transconf.shell import ModelShell
    from transconf.server.twisted.client import RPCTranClient

    @register_model('ifdev')
    class Ifconfig(Model):
        FORM = [{'node': 'if_name',
                'subs': [
                         {'node': 'ip_addr',
                          'public': ['ip_addr', 'mod:ifdev:ip_addr'],
                          'subs': [
                                   {'node': 'test_name',
                                    'name': ['owner_found_ip_addr', 'mod:ifdev:owner_found_ip_addr'],
                                    'private': ['owner_ip_addr', 'mod:ifdev:ip_addr'],
                                   },
                          ],
                         },
                         {'node': 'hw_addr',
                          'public': ['hw_addr', 'mod:ifdev:hw_addr'],
                         },
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
            data = dict(kwargs={'value': ifname,
                                'target': 'network.if_name.hw_addr',
                                'method': 'hw_addr',
                               }
                        )
            c = RPCTranClient()
            v = c.call(data)
            return '1.1.1.1'

        def hw_addr(self, ifname):
            return 'xx.xx.xx.xx.xx.xx'

    if __name__ == '__main__':
        sh = ModelShell()
        sh.load_model('network', Ifconfig)
        sh.run('network.if_name.ip_addr.test_name:test', 'owner_ip_addr', 'eth0')

Save in a server.py:

.. code:: python

        import functools
        from shell import Ifconfig

        from transconf.server.twisted.service import RPCTranServer, Middleware
        from transconf.server.twisted.netshell import NetShell

        class ShellMiddleware(Middleware):
            def process_request(self, context):
                value = context['kwargs']['value']
                target = context['kwargs']['target']
                method = context['kwargs']['method']
                cb = functools.partial(self.handler.run, target, method, value)
                return cb()

        if __name__ == '__main__':
            sh = NetShell()
            sh.load_model('network', Ifconfig)
            m = ShellMiddleware(sh)
            serve = RPCTranServer()
            serve.setup(m)
            serve.serve_forever()
"""

from setuptools import setup
from transconf.__init__ import __version__

version = '.'.join(map(str, __version__))

setup(
      name="TransConf",
      version=version,
      description="A framework based on Twisted, AMQP, SqlAlChemy",
      long_description=__doc__,
      author="Chi Jun",
      packages=[
        'transconf',
        'transconf.test',
        'transconf.common',
        'transconf.server',
        'transconf.server.twisted',
        'transconf.msg',
        'transconf.msg.rabbit',
        'transconf.models',
      ]
)
