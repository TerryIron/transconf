#coding=utf-8

__author__ = 'chijun'

from transconf.common.basetype import BaseType
from transconf.common.reg import get_reg_target


__all__ = [
    'IsString', 'IsList', 'IsDict', 'IsNodeInterface',
    'IsPrivateInterface', 'IsPublicInterface', 'IsProperty',
]


class BaseTypeError(Exception):
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return "Item:{0} should be mod:NAME:METHOD".format(self.string)


# Use these BaseType class to define static value
class IsString(BaseType):
    """
    字符串类型检查器

    """
    def check(self, key, value):
        if isinstance(value, str):
            return key, self, value


class IsList(BaseType):
    """
    列表类型检查器

    """
    def check(self, key, value):
        if isinstance(value, list):
            return key, self, value


class IsDict(BaseType):
    """
    字典类型检查器

    """
    def check(self, key, value):
        if isinstance(value, dict):
            return key, self, value


# Use these BaseType class to define class members
class IsInterface(BaseType):
    """
    接口类型检查器

    """
    def check(self, key, value):
        _key, _val = value
        try:
            typ, name, val = _val.split(':')
            obj = get_reg_target(typ, name) if name != 'self' else key
            if not obj:
                return
            if hasattr(obj, val):
                _method = getattr(obj, val)
                if callable(_method):
                    return _key, self, _method
        except:
            raise BaseTypeError(value[1])


class IsPrivateInterface(IsInterface):
    """
    私有接口类型检查器

    """
    def check(self, key, value):
        return super(IsPrivateInterface, self).check(key ,value)


class IsPublicInterface(IsInterface):
    """
    公有接口类型检查器

    """
    def check(self, key, value):
        return super(IsPublicInterface, self).check(key, value)


class IsNodeInterface(IsInterface):
    """
    节点接口类型检查器

    """
    def check(self, key, value):
        return super(IsNodeInterface, self).check(key, value)


class IsProperty(BaseType):
    """
    节点属性类型检测器

    """
    def check(self, key, value):
        _key, _val = value
        try:
            typ, name, val = _val.split(':')
            obj = get_reg_target(typ, name) if name != 'self' else key
            if not obj:
                return
            if hasattr(obj, val):
                _property = getattr(obj, val)
                if not callable(_property):
                    return _key, self, _property
        except:
            raise BaseTypeError(value[1])
