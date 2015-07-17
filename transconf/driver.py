__author__ = 'chijun'

import os
import functools

from transconf.server.utils import from_config_option, as_config


class Command(object):
    DEFAULT_CONF = as_config(os.path.join(os.path.dirname(__file__), 'cmd/default.ini'))
    CONF = None 
    """
        Sample code:
        cmd = Command('regular_file')
        cmd.setup()
        cmd['forced_remove'](name='kkk')
    """
    def __init__(self, name):
        self.conf = self.DEFAULT_CONF if not self.CONF else self.CONF
        self.name = name #Section Name
        self.enabled_method = []
        self.exp = {}
        self.init()

    def init(self):
        pass

    @staticmethod
    def translate(expression, **kwargs):
        return str(expression).format(**kwargs)

    def setup(self):
        for em in self.enabled_method:
            if isinstance(em, list):
                self._setup(*em)
            else:
                self._setup(em)

    def _setup(self, method_name, exp=None):
        @from_config_option(method_name, None, sect=self.name)
        def get_enabled_method(conf):
            return conf
        if not exp:
            exp = get_enabled_method(self.conf)
        if exp:
            self.exp[method_name] = exp

    def __getitem__(self, name):
        exp = self.exp.get(name, None)
        if exp:
            func = functools.partial(Command.translate, exp)
            return func

def command_configure(conf):
    Command.DEFAULT_CONF = conf
    for sect in conf.sections():
        @from_config_option('factory', None, sect=sect)
        def conf_command_factory()
            return conf
        factory = conf_command_factory()
        if factory:
            factory = factory.split('.')
            cls = __import__('.'.join(factory[0:-1]), fromlist=[factory[-1]])
            mod = getattr(cls, factory[-1])
            if mod and callable(mod):
                mod(sect).setup()
