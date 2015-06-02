__author__ = 'chijun'

from common.struct import NodeStruct

__all__ = ['StructV1']

class NodeStructV1(NodeStruct): 
    def check_input(self, key, value):
        if (key not in self.keys()) or \
            (type(value) != self.get_type(key)):
            return False
        return True


StructV1 = NodeStructV1()
StructV1.set_default('node', str, None, 1)
StructV1.set_default('regex', list, None, 5)
StructV1.set_default('subs', list, {}, 50)
StructV1.set_nodename('node')
StructV1.set_branchname('subs')
