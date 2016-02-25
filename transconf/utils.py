# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'

import re
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from transconf.common.reg import get_model

__all__ = ['as_config', 'from_config', 'from_config_option',
           'as_model_action', 'from_model_option', 'Exception'
          ]


class myException(Exception):
    def __init__(self, string=''):
        self.string = string

    def __str__(self):
        return '<{0}> {1}'.format(self.__class__, self.string)


def import_class(class_name):
    if class_name:
        class_name = str(class_name).split('.')
        cls = __import__('.'.join(class_name[0:-1]), fromlist=[class_name[-1]])
        return getattr(cls, class_name[-1])


def _get_val(conf, sect, opt, default_val):
    if not sect:
        default_sect = conf._defaults
        if default_sect:
            val = default_sect.get(opt, None)
            return val if val else default_val
        else:
            return default_val
    else:
        try:
            return conf.get(sect, opt)
        except (NoOptionError, NoSectionError):
            return default_val
        

def from_model_option(opt, default_val, sect):
    def _from_model_option(func):
        def __from_model_option(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser)
            target = get_model(sect)
            if not target:
                return default_val
            return _get_val(config, sect, opt, default_val)
        return __from_model_option
    return _from_model_option


class SimpleModel(object):
    RE = re.compile('(\S+)\.(\S+)')

    def __init__(self, string):
        string = string.split(':', 1)
        if len(string) > 1:
            self.version = string[1]
        else:
            self.version = '0.1.0'
        ret = self.RE.match(string[0]).groups()
        if ret:
            self.target = ret[0]
            self.action = ret[1]
        else:
            self.target = None
            self.action = None


def as_model_action(command_name, opt, sect='model_action'):
    def _from_model_action(func):
        def __from_model_action(self, *args, **kwargs):
            config = func(self, *args, **kwargs)
            assert isinstance(config, ConfigParser)
            if not hasattr(self, command_name):
                setattr(self, command_name, {})
            if config.has_section(sect) and config.has_option(sect, opt):
                d = getattr(self, command_name)
                d[opt] = SimpleModel(config.get(sect, opt))
                return True
            else:
                return False
        return __from_model_action
    return _from_model_action


def as_config(config_file):
    if isinstance(config_file, ConfigParser):
        return config_file
    config = ConfigParser()  
    config.read(config_file)
    return config


def from_config(sect=None):
    def _from_config(func):
        def __from_config(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser)
            if not sect:
                default_sect = config._defaults
                if default_sect:
                    return default_sect.items()
            else:
                if config.has_section(sect):
                    d = [(k, v) for k, v in config.items(sect) if k not in config.defaults()]
                    return d
        return __from_config
    return _from_config


def from_config_option(opt, default_val, sect=None):
    def _from_config_option(func):
        def __from_config_option(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser)
            return _get_val(config, sect, opt, default_val)
        return __from_config_option
    return _from_config_option
