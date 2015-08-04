__author__ = 'chijun'

import json
import ConfigParser

from transconf.common.reg import get_model


def import_class(class_name):
    cls = __import__('.'.join(class_name[0:-1]), fromlist=[class_name[-1]])
    return getattr(cls, class_name[-1])


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        return json.loads(json_data)


def from_config_option(opt, default_val, sect=None):
    def _from_config_option(func):
        def __from_config_option(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser.ConfigParser)
            if not sect:
                default_sect = config._defaults
                if default_sect:
                    val = default_sect.get(opt, None)
                    return val if val else default_val
            else:
                if config.has_section(sect) and config.has_option(sect, opt):
                    return config.get(sect, opt)
                else:
                    return default_val
        return __from_config_option
    return _from_config_option


def from_model_option(opt, default_val, sect):
    def _from_model_option(func):
        def __from_model_option(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser.ConfigParser)
            target = get_model(sect)
            if not target:
                return default_val
            if config.has_section(sect) and config.has_option(sect, opt):
                return config.get(sect, opt)
            else:
                return default_val
        return __from_model_option
    return _from_model_option


class Model(object):
    pass


def as_model_action(opt, sect='model_action'):
    def _from_model_action(func):
        def __from_model_action(self, *args, **kwargs):
            config = func(self, *args, **kwargs)
            assert isinstance(config, ConfigParser.ConfigParser)
            if not hasattr(self, 'commands'):
                setattr(self, 'commands', {})
            if config.has_section(sect) and config.has_option(sect, opt):
                ret = config.get(sect, opt).split('.')
                self.commands[opt] = Model()
                self.commands[opt].target = ret[0:-1]
                self.commands[opt].action = ret[-1]
                return True
            else:
                return False
        return __from_model_action
    return _from_model_action


def as_config(config_file):
    config = ConfigParser.ConfigParser()  
    config.read(config_file)
    return config


def from_config(sect=None):
    def _from_config(func):
        def __from_config(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser.ConfigParser)
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
