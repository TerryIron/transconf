__author__ = 'chijun'

import json


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        return json.dumps(dict_data)

    @staticmethod
    def unpack(json_data):
        return json.loads(json_data)

