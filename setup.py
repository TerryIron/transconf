__author__ = 'chijun'

from setuptools import setup, find_packages

from transconf.__init__ import __version__

version = '.'.join(map(str, __version__))

"""
    TransConf
    ---------

    TransConf is a framework based on Twisted, AMQP, SqlAlChemy.

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

            from transconf.server.twisted.service import Middleware, serve_forever
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
"""


def find_datafiles(where='.', include_endswith=()):
    data = []
    import glob, os.path
    where = os.path.abspath(where)
    stack = glob.glob(os.path.join(where, '*'))
    while stack:
        p = stack.pop(0)
        item = []
        for d in glob.glob(os.path.join(p, '*')):
            if os.path.isdir(d):
                stack.append(d)
                continue
            if not include_endswith or any(d.endswith(end) for end in include_endswith):
                d = d[len(where) + 1:]
                item.append(d)
        if item:
            data.append((p[len(where) + 1:], tuple(item)))
    return data


setup(
    name="TransConf",
    version=version,
    description="A framework based on AMQP, Twisted, SqlAlChemy etc",
    long_description=__doc__,
    author="Chi Jun",
    author_email="greenhoop777@gmail.com",
    packages=find_packages(),
    data_files=find_datafiles(include_endswith=['_tmpl']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'twisted>=14.0',
        'pika>=0.9.14',
        'SQLAlchemy>=0.7.8,!=0.9.5,<=0.9.99',
        'PasteDeploy>=1.5.2',
        'PasteScript>=1.7.5',
        'Mako>=0.5.0',
        'Tempita>=0.5.1',
    ],
    extras_require={
        'genshi': ['Genshi>=0.6'],
        'jinja2': ['Jinja2'],
    },
    entry_points="""
        [paste.paster_command]
        controller = transconf.commands:ControllerCommand
        restcontroller = transconf.commands:RestControllerCommand
        routes = transconf.commands:RoutesCommand
        shell = transconf.commands:ShellCommand

        [paste.paster_create_template]
        transconf = transconf.installer:TransconfTemplate
    """
)
