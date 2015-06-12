__author__ = 'chijun'

from common.struct import *
from mystructtypes import *


class NodeStructV1(NodeStruct): 
    SUPPORTED_TYPES = [
                       IsString, 
                       IsDict, 
                       IsList, 
                       IsPublicInterface, 
                       IsPrivateInterface, 
                       IsProperty
                      ]

    def __init__(self):
        super(NodeStructV1, self).__init__()
        self.set_default('node', IsString, 1, None)
        self.set_default('name', IsNodeInterface, 1, None)
        self.set_default('private', IsPrivateInterface, 1, None)
        self.set_default('public', IsPublicInterface, 1, None)
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
            return typ().check(data)
        except Exception as e:
            raise NodeItemTypeNotSupport('Key:{0}, value:{1}, caused by {2}.'.format(key, value, e))

