__author__  = 'chijun'

import re

from transconf.utils import *


class BaseConfigure(object):
    def __init__(self, config):
        self.config = as_config(config)
        self.__attrs__ = {}

    def __setattr__(self, key, value):
        if key not in self.__attrs__:
            self.__attrs__[key] = value

    def __getattr__(self, key):
        if key not in self.__attrs__:
            return None
        return self.__attrs__[key]

    def __delattr__(self, key):
        if name in self.__attrs__:
            del self.__attrs__[name]


class ConfigureGroup(BaseConfigure):
    def __init__(self, config, sect=None):
        super(ConfigureGroup, self).__init__(config)
        self.sect = sect

    def add_property(self, name, default_val=None, key=None, default_type=str, help=None):
        pass

    def del_property(self, name):
        self.__delattr__(name):


class Configure(BaseConfigure):
    def add_group(self, name, sect=None):
        self.__setattr__(name, ConfigureGroup(config, sect)
        return __getattr__(name)

    def del_group(self, name):
        self.__delattr__(name):

    def _process_options(self, output, option_regex=None, avoid_options=None, avoid_option_regex=None):
        option_re = None
        avoid_re = None
        new = set()
        for out in output:
            if not isinstance(out, list or tuple):
                continue
            if out[0] in avoid_options:
                continue
            new.add(tuple(out[0], out[1]))
            
    def add_members(self, name, sect=None, default_val=None, option_regex=None, 
                    avoid_options=None, avoid_option_regex=None, help=None):
        if sect and self.config.has_section(sect):
            d = [(k, v) for k, v in self.config.items(sect) if k not in self.config.defaults()]
            val = self._process_options(d, option_regex, avoid_options, avoid_option_regex)
            self.__setattr__(name, val)
        else:
            if default_val:
                val = self._process_options(default_val, option_regex, avoid_options, avoid_option_regex)
                self.__setattr__(name, val)

    def del_members(self, name):
        self.__delattr__(name):
