__author__ = 'chijun'

from common.struct import *


class NodeStructV1(NodeStruct): 
    def __init__(self):
        super(NodeStructV1, self).__init__()
        self.set_default('node', IsString, 1, None)
        self.set_default('method', IsInterface, 1, None)
        self.set_default('property', IsProperty, 1, None)
        self.set_default('subs', IsList, 50, {})
        self.set_nodename('node')
        self.set_branchname('subs')

    def check_input(self, key, value):
        if key not in self.keys():
            raise NodeItemNotFound('Can not found variable:{0}'.format(key))
        try:
            typ = self.get_type(key)
            data = dict(key=key,
                        value=value)
            k, v = typ().check(data)
            return k, v
        except Exception as e:
            raise NodeItemTypeNotSupport('Key:{0}, value:{1}, caused {2}.'.format(key, value, e))
