__author__ = 'chijun'

from common.struct import NodeStruct

__all__ = ['StructV1']

class NodeStructV1(NodeStruct):
    pass


StructV1 = NodeStructV1()
StructV1.set_default('node', str, None, 1)
StructV1.set_default('regex', str, None, 5)
StructV1.set_default('subs', dict, {}, 50)
