__author__ = 'chijun'

import json


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        try:
            return json.dumps(dict_data)
        except:
            return {}

    @staticmethod
    def unpack(json_data):
        try:
            return json.loads(json_data)
        except:
            pass

