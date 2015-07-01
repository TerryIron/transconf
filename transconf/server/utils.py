__author__ = 'chijun'


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        import json
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        import json
        return json.loads(json_data)


def from_config(opt, default_val, sect=None):
    def _from_config(func):
        def __from_config(*args, **kwargs):
            conf = func(*args, **kwargs)
            import ConfigParser
            config = ConfigParser.ConfigParser()  
            config.read(conf)
            if not sect:
                default_sect = config._defaults
                val = default_sect.get(opt, None)
                return val if val else default_val
            else:
                if config.has_section(sect) and config.has_option(sect, opt):
                    return config.get(sect, opt)
        return __from_config
    return _from_config


