__author__ = 'chijun'

import json


class JsonSerializionPacker(object):
    @staticmethod
    def pack(dict_data):
        try:
            return json.dumps(dict(json_data=dict_data))
        except:
            return {}

    @staticmethod
    def unpack(json_data):
        try:
            d = json.loads(json_data)
            return d.get('json_data')
        except:
            pass

