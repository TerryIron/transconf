__author__ = 'chijun'

from common.model import BaseModel
from common.namebus import NameBus
from common.basetype import BaseType
from struct import NodeStructV1
from structtypes import *


class ModelInternalStuctErr(Exception):
    """Raised when pointed node object's struct or its env struct being bad"""


class Model(BaseModel):
    STRUCT = NodeStructV1()
    SPLIT_DOT = '&'

    def init(self, config):
        self.split = self.SPLIT_DOT

    def _build_class_nodename(self, lst):
        return self.split.join(lst)

    def _build_nodename(self, lst):
        for n_unit in lst:
            if self._is_model_owner(n_unit):
                pass

    def _is_private_model(self, name):
        pass

    def _is_private_method(self, name):
        pass

    def run(self, target_name, method_name, *args, **kwargs):
        real_name = self._build_nodename(target_name)
        m_inst = self.get_namebus(real_name)
        if isinstance(m_inst, dict):
            meth = m_inst.get(method_name)
            if callable(meth):
                return meth(*arg, **kwargs)
            else:
                return meth
        else:
            raise ModelInternalStuctErr('Can not loading method name:{0} of {1}'.format(method_name, real_name))

    def set_node_member(self, name_lst, key, value):
        real_name = self._build_class_nodename(name_lst)
        if real_name in self.namebus:
            n = self.get_namebus(real_name)
            if isinstance(n, dict):
                n[key] = value
                return True
        return False

    def set_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        self.set_namebus(real_name, {})

    def get_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        return self.get_namebus(real_name)
