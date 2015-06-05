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
                        value=value,
                        obj=self)
            k, v = typ().check(data)
            return k, v
        except:
            raise NodeItemTypeNotSupport('Get value:{0} is not supported by {1} defines.'.format(value, key))

