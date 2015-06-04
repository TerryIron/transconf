__author__ = 'chijun'

from common.struct import *


class NodeStructV1(NodeStruct): 
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


StructV1 = NodeStructV1()
StructV1.set_default('node', IsString, 1, None)
StructV1.set_default('regex', IsInterface, 1, None)
StructV1.set_default('subs', IsList, 50, {})
StructV1.set_nodename('node')
StructV1.set_branchname('subs')
