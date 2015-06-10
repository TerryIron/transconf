__author__ = 'chijun'

from common.basetype import BaseType
from common.reg import get_reg_target


__all__ = [
'IsString', 'IsList', 'IsDict', 'IsNodeInterface',
'IsPrivateInterface', 'IsPublicInterface', 'IsProperty',
]


# Use these BaseType class to define static value
class IsString(BaseType): 
    def check(self, data):
        if isinstance(data['value'], str):
            return data['key'], self, data['value']


class IsList(BaseType): 
    def check(self, data):
        if isinstance(data['value'], list):
            return data['key'], self, data['value']


class IsDict(BaseType): 
    def check(self, data):
        if isinstance(data['value'], dict):
            return data['key'], self, data['value']


# Use these BaseType class to define class members
class IsInterface(BaseType): 
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
    def check(self, data):
        return super(IsPrivateInterface, self).check(data)


class IsPublicInterface(IsInterface): 
    def check(self, data):
        return super(IsPublicInterface, self).check(data)


class IsNodeInterface(IsInterface): 
    def check(self, data):
        return super(IsNodeInterface, self).check(data)


class IsProperty(BaseType): 
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

