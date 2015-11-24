__author__ = 'chijun'

from transconf.common.basetype import BaseType
from transconf.common.reg import get_reg_target


__all__ = [
'IsString', 'IsList', 'IsDict', 'IsNodeInterface',
'IsPrivateInterface', 'IsPublicInterface', 'IsProperty',
]


# Use these BaseType class to define static value
class IsString(BaseType):
    """
    字符串类型检查器

    """
    def check(self, data):
        if isinstance(data['value'], str):
            return data['key'], self, data['value']


class IsList(BaseType):
    """
    列表类型检查器

    """
    def check(self, data):
        if isinstance(data['value'], list):
            return data['key'], self, data['value']


class IsDict(BaseType):
    """
    字典类型检查器

    """
    def check(self, data):
        if isinstance(data['value'], dict):
            return data['key'], self, data['value']


# Use these BaseType class to define class members
class IsInterface(BaseType):
    """
    接口类型检查器

    """
    def check(self, data):
        key = data['value'][0]
        typ, name, val = data['value'][1].split(':')
        obj = get_reg_target(typ, name)
        if not obj:
            return
        if hasattr(obj, val):
            _method = getattr(obj, val)
            if callable(_method):
                return key, self, _method


class IsPrivateInterface(IsInterface):
    """
    私有接口类型检查器

    """
    def check(self, data):
        return super(IsPrivateInterface, self).check(data)


class IsPublicInterface(IsInterface):
    """
    公有接口类型检查器

    """
    def check(self, data):
        return super(IsPublicInterface, self).check(data)


class IsNodeInterface(IsInterface):
    """
    节点接口类型检查器

    """
    def check(self, data):
        return super(IsNodeInterface, self).check(data)


class IsProperty(BaseType):
    """
    节点属性类型检测器

    """
    def check(self, data):
        key = data['value'][0]
        typ, name, val = data['value'][1].split(':')
        obj = get_reg_target(typ, name)
        if not obj:
            return
        if hasattr(obj, val):
            _property = getattr(obj, val)
            if not callable(_property):
                return key, self, _property

