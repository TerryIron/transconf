__author__ = 'chijun'

import json
import ConfigParser

from transconf.common.reg import get_model

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
