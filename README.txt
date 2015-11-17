TransConf
---------

TransConf is a framework based on AMQP, Twisted, SqlAlChemy.

Sample in a client.py:

.. code:: python

    from transconf.common.reg import register_model
    from transconf.model import Model
    from transconf.shell import ModelShell
    from transconf.server.twisted.internet import get_client

    @register_model
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
                                'target': 'if_name.hw_addr',
                                'method': 'hw_addr',
                               }
                        )
            c = get_client('default_worker', 'default_type', type='rpc')
            v = c.call(data)
            return '1.1.1.1'

        def hw_addr(self, ifname):
            return 'xx.xx.xx.xx.xx.xx'

Sample in a server.py:

.. code:: python

        import functools
        from shell import Ifconfig

        from transconf.server.twisted.service import Middleware, serve_forver
        from transconf.server.twisted.internet import TranServer
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
            sh.load_model(Ifconfig)
            m = ShellMiddleware(sh)
            serve = TranServer()
            serve.setup(m)
            serve_forever()
