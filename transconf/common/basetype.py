# coding=utf-8

__author__ = 'chijun'


class BaseType(object):
    """
    基本变量类型检查器

    """

    def check(self, key, value):
        """
        检查数据类型相符

        Args:
            key: 数据键值
            data: 数据值

        Returns:
            未实现

        """
        raise NotImplementedError()

    def convert(self, data):
        """
        数据类型转换

        Args:
            data: 数据输入

        Returns:
            未实现

        """
        raise NotImplementedError()
