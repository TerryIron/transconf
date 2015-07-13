__author__ = 'chijun'

import json
import ConfigParser


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        return json.loads(json_data)


def from_config(opt, default_val, sect=None):
    def _from_config(func):
        def __from_config(*args, **kwargs):
            config = func(*args, **kwargs)
            assert isinstance(config, ConfigParser.ConfigParser)
            if not sect:
                default_sect = config._defaults
                val = default_sect.get(opt, None)
                return val if val else default_val
            else:
                if config.has_section(sect) and config.has_option(sect, opt):
                    return config.get(sect, opt)
        return __from_config
    return _from_config



def as_config(config_file):
    config = ConfigParser.ConfigParser()  
    config.read(config_file)
    return config
