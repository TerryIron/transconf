__author__  = 'chijun'

import re
import json

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
        if name in self.__help__:
            del self.__help__[name]

    def add_property(self, name, option=None, default_val=None, help=None):
        @from_config_option(option or '', default_val, sect=self.sect)
        def add():
            return self.config
        self.__setattr__(name, json.loads(add()))
        self.__setitem__(name, str(help))

    def del_property(self, name):
        self.__delattr__(name)
        self.__delitem__(name)


class Configure(BaseConfigure):
    def add_group(self, name, sect=None):
        self.__setattr__(name, ConfigureGroup(config, sect))
        return self.__getattr__(name)

    def del_group(self, name):
        self.__delattr__(name)

    def _process_options(self, output, option_regex=None, avoid_options=None, avoid_option_regex=None):
        option_re, avoid_re, avoid_options, new  = re.compile('.*') if not option_regex else re.compile(option_regex), \
                                                   re.compile('^$') if not avoid_regex else re.compile(avoid_option_regex), \
                                                   tuple() if not avoid_options else avoid_options, \
                                                   set()
        for out in output:
            if not isinstance(out, list or tuple):
                continue
            if out[0] in avoid_options or out[0].search(avoid_re):
                continue
            if out[0].search(option_re):
                new.add(tuple(out[0], out[1]))
            
    def add_members(self, name, sect=None, default_val=None, option_regex=None, 
                    avoid_options=None, avoid_option_regex=None, help=None):
        @from_config(sect)
        def add():
            return self.config
        val = add() or default_val
        val = self._process_options(val, option_regex, avoid_options, avoid_option_regex)
        self.__setattr__(name, val)

    def del_members(self, name):
        self.__delattr__(name)
