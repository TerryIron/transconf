# coding=utf-8

__author__ = 'chijun'

import json


class JsonSerializionPacker(object):
    """
    JSON序列化对象

    """

    @staticmethod
    def pack(dict_data):
        """
        导出序列化数据

        Args:
            dict_data: 输入对象

        Returns:
            str: 序列化数据

        """
        try:
            return json.dumps(dict(json_data=dict_data))
        except:
            return {}

    @staticmethod
    def unpack(json_data):
        """
        导入序列化数据

        Args:
            json_data: 输入对象

        Returns:
            str: 序列化对象

        """
        try:
            d = json.loads(json_data)
            return d.get('json_data')
        except:
            pass

