#coding=utf-8

__author__  = 'chijun'

import re
import json

from transconf.utils import *


class BaseConf(object):
    """
    配置对象
    """
    def __init__(self, config):
        self.config = as_config(config)


class ConfGroup(BaseConf):
    """
    配置对象组
    """
    def __init__(self, config, sect=None):
        super(ConfGroup, self).__init__(config)
        self.__help__ = {}
        self.sect = sect

    def __setitem__(self, key, value):
        if key not in self.__help__:
            self.__help__[key] = value

    def __getitem__(self, key):
        if key not in self.__help__:
            return None
        return self.__help__[key]

    def __delitem__(self, key):
        if key in self.__help__:
            del self.__help__[key]

    def add_property(self, name, option=None, default_val=None, help=None):
        """
        添加配置组成员

        Args:
            name: 成员名
            option: 配置文件选项
            default_val: 默认值
            help: 帮助信息

        Returns:
            None

        """
        @from_config_option(option or '', default_val, sect=self.sect)
        def add():
            return self.config
        val = add()
        if val:
            try:
                val = json.loads(val)
            except:
                val = str(val)
            setattr(self, name, val)
        else:
            setattr(self, name, val)
        self.__setitem__(name, str(help))

    def del_property(self, name):
        """
        删除配置组成员

        Args:
            name: 成员名

        Returns:
            None

        """
        delattr(self, name)
        self.__delitem__(name)


class Configuration(BaseConf):
    """
    配置文件对象化

    """
    def add_group(self, name, sect=None):
        """
        添加配置组对象

        Args:
            name: 对象名
            sect: 配置文件段落名

        Returns:
            None

        """
        setattr(self, name, ConfGroup(self.config, sect))
        return getattr(self, name)

    def del_group(self, name):
        """
        删除配置组对象

        Args:
            name: 对象名

        Returns:
            None

        """
        delattr(self, name)

    @staticmethod
    def _process_options(output, option_regex=None, avoid_options=None, avoid_option_regex=None):
        option_re, avoid_re, avoid_options, new  = re.compile('.*') if not option_regex else re.compile(option_regex), \
                                                   re.compile('^$') if not avoid_option_regex else re.compile(avoid_option_regex), \
                                                   tuple() if not avoid_options else avoid_options, \
                                                   set()
        if not output:
            return new
        for out in output:
            if not isinstance(out, tuple):
                continue
            if out[0] in avoid_options or avoid_re.search(out[0]):
                continue
            if option_re.search(out[0]):
                new.add((out[0], out[1]))
        return new

    def add_members(self, name, sect=None, default_val=None, option_regex=None,
                    avoid_options=None, avoid_option_regex=None, help=None):
        """
        添加配置组成员

        Args:
            name: 对象名
            sect: 配置文件段落名
            default_val: 默认值
            option_regex: 可匹配配置选项
            avoid_options: 可避免配置选项
            avoid_option_regex: 可避免匹配配置选项
            help: 帮助信息

        Returns:
            None

        """
        @from_config(sect)
        def add():
            return self.config
        val = add() or default_val
        val = self._process_options(val, option_regex, avoid_options, avoid_option_regex)
        setattr(self, name, val)

    def del_members(self, name):
        """
        删除配置组成员

        Args:
            name: 对象名

        Returns:
            None

        """
        delattr(self, name)
