#coding=utf-8

__author__ = 'chijun'

import os
import functools

from transconf.utils import from_config, from_config_option, as_config, import_class
from transconf.common.reg import get_local_cmd
from transconf.utils import Exception


class Command(object):
    """
        基础命令对象

        使用示例:
        cmd = Command('regular_file')
        cmd.setup()
        cmd['forced_remove'](name='kkk')
    """
    DEFAULT_CONF = as_config(os.path.join(os.path.dirname(__file__), 'cmd/default.ini'))
    CONF = None

    def __init__(self, name):
        self.conf = self.DEFAULT_CONF if not self.CONF else self.CONF
        self.name = name #Section Name
        self.enabled_method = []
        self.exp = {}
        self.init()

    def init(self):
        """
        基础命令初始化

        Returns:
            None

        """
        pass

    @staticmethod
    def translate(expression, **kwargs):
        """
        命令行表达式

        Args:
            expression: 表达式
            **kwargs: 表达式参数

        Returns:
            str: 命令表达式

        """
        return str(expression).format(**kwargs)

    def setup(self):
        """
        安装命令行

        Returns:
            None

        """
        if self.enabled_method:
            self._default_setup()
        else:
            self._conf_setup()

    def _default_setup(self):
        for em in self.enabled_method:
            if isinstance(em, list):
                self._setup(*em)
            else:
                self._setup(em)

    def _conf_setup(self):
        @from_config(sect=self.name)
        def get_conf_methods():
            return self.conf
        for method_name, exp in get_conf_methods():
            self.exp[method_name] = exp

    def _setup(self, method_name, exp=None):
        @from_config_option(method_name, None, sect=self.name)
        def get_enabled_method():
            return self.conf
        if not exp:
            exp = get_enabled_method()
        if exp:
            self.exp[method_name] = exp

    def __getitem__(self, name):
        exp = self.exp.get(name, None)
        if exp:
            func = functools.partial(Command.translate, exp)
            return func


def command_configure(conf):
    """
    自动配置命令行对象

    Args:
        conf: 配置对象

    Returns:
        None

    """
    Command.DEFAULT_CONF = conf
    for sect in conf.sections():
        @from_config_option('factory', None, sect=sect)
        def conf_command_factory():
            return conf
        factory = conf_command_factory()
        if factory:
            mod = import_class(factory)
            if callable(mod):
                mod(sect).setup()


class CommandNotRegister(Exception):
    """Raised when command name cat not be found in registry"""


class CommandNotFound(Exception):
    """Raised when method cat not be found in command target"""


def command(target_name, method_name, **kwargs):
    """
    调用命令行

    Args:
        target_name: 命令对象名
        method_name: 方法名
        **kwargs: 参数

    Returns:
        命令结果

    """
    target = get_local_cmd(target_name)
    if not target:
        raise CommandNotRegister(target_name)
    meth = target[method_name]
    if callable(meth):
        return meth(**kwargs)
    else:
        raise CommandNotFound(method_name)
