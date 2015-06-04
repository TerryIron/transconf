__author__ = 'chijun'

from basetype import BaseType

__all__ = [
 'NodeItemNotFound', 'NodeItemTypeNotSupport', 'NodeItemStructError',
 'IsString', 'IsList', 'IsDict', 'IsInterface', 'NodeStruct',
]

class NodeItemNotFound(Exception):
    """ Raised when value name not found"""

class NodeItemTypeNotSupport(Exception):
    """ Raised when value's type not support"""

class NodeItemStructError(Exception):
    """ Raised when struct is bad"""


class IsString(BaseType): 
    def check(self, data):
        if isinstance(data['value'], str):
            return data['key'], data['value']

class IsList(BaseType): 
    def check(self, data):
        if isinstance(data['value'], list):
            return data['key'], data['value']

class IsDict(BaseType): 
    def check(self, data):
        if isinstance(data['value'], dict):
            return data['key'], data['value']

class IsInterface(BaseType): 
    def check(self, data):
        if hasattr(data['obj'], data['value']):
            _mehtod = getattr(data['obj'], data['value'])
            if callable(_method):
                return data['key'], _method


class NodeStruct(object):

    SUPPORT_TYPES = [IsString, IsList, IsDict, IsInterface]

    def __init__(self):
        self.support_types = self.SUPPORT_TYPES
        self.dic = dict()
        self.branch = set()
        self.name = None

    def set_nodename(self, name):
        self.name = name

    def get_nodename(self):
        return self.name

    def set_branchname(self, name):
        self.branch.add(name)

    def get_branchname(self):
        return self.branch

    def is_branch(self, name):
        if name not in self.branch:
            return False
        else:
            return True
        
    def keys(self):
        return self.dic.keys()

    def items(self):
        return self.dic.items()

    def set_default(self, var_name, var_type, len=10, default_value=None):
        self.dic[var_name] = [[], (default_value), var_type, len]
        return True

    def _check_struct_base(self, struct):
        if not (len(struct) == 4 and type(struct) == list):
            raise NodeItemStructError()

    def _get(self, var_name):
        if var_name in self.dic:
            self._check_struct_base(self.dic[var_name])
            return self.dic[var_name]
        raise NodeItemNotFound('Can not found variable:{0}'.format(var_name))

    def _get_len(self, item):
        return item[3]

    def _get_type(self, item):
        return item[2]

    def _check_type(self, item, data):
        try:
            _type = self._get_type(item)
            return _type.check(data)
        except:
            pass

    def _get_default(self, item):
        return item[1]

    def _get_value(self, item):
        return item[0]

    def get_value(self, var_name):
        item = self._get(var_name)
        v = self._get_value(item)
        if len(v) > 0:
            return v
        else:
            return self._get_default(item)

    def get_default(self, var_name):
        item = self._get(var_name)
        return self._get_default(item)

    def get_type(self, var_name):
        item = self._get(var_name)
        return self._get_type(item)

    def get_len(self, item):
        item = self._get(var_name)
        return self._get_len(item)

    def set(self, var_name, value):
        _v = self._get(var_name)
        if self._check_type(_v, value):
            _v[0].append(value)
            if len(_v[0]) > self._get_len(_v):
                _v.pop(0)
            return True
        else:
            raise NodeItemTypeNotSupport('Type: {0} not in {1}'.format(var_type, self.support_types))

    def check_input(self, key, value):
        raise NotImplementedError()
