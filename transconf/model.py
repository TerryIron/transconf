__author__ = 'chijun'

from common.model import BaseModel
from common.namebus import NameBus
from struct import NodeStructV1


class Model(BaseModel):
    STRUCT = NodeStructV1()
    SPLIT_DOT = '.'

    def init(self, config):
        self.split = self.SPLIT_DOT

    def _build_nodename(self, lst):
        return self.split.join(lst)

    def run(self, target_name, method_name, *args, **kwargs):
        raise NotImplementedError()

    def getattr(self, target_name, property_name):
        raise NotImplementedError()

    def setattr(self, target_name, property_name, value):
        raise NotImplementedError()

    def set_node_member(self, name_lst, key, value):
        real_name = self._build_nodename(name_lst)
        if real_name in self.namebus:
            self.namebus[real_name][key] = value
            return True
        return False

    def set_nodeobj(self, name_lst):
        real_name = self._build_nodename(name_lst)
        self.namebus[real_name] = {}

