__author__ = 'chijun'

from common.model import BaseModel
from common.namebus import NameBus
from common.basetype import BaseType
from struct import NodeStructV1
from structtypes import *


class ModelInternalStuctErr(Exception):
    """Raised when pointed node object's struct or its env struct being bad"""


class ModelNodeFoundFail(Exception):
    """Raised when pointed node object cant not be found """


class Model(BaseModel):
    STRUCT = NodeStructV1()
    SPLIT_DOT = '&'
    IS_NODE_METHOD = IsNodeInterface
    IS_PRIVATE_METHOD = IsPrivateInterface
    IS_PUBLIC_METHOD = IsPublicInterface

    def init(self, config):
        self.split = self.SPLIT_DOT
        self.is_node_rule = self.IS_NODE_METHOD 
        self.is_pri_rule = self.IS_PRIVATE_METHOD 
        self.is_pub_rule = self.IS_PUBLIC_METHOD 

    def _build_class_nodename(self, lst):
        return self.split.join(lst)

    def _build_nodename(self, lst):
        try:
            new_lst = [self._found_nodename(n) for n in lst]
            return self._build_class_nodename(new_lst)
        except ModelNodeFoundFail:
            return None, None

    def _found_nodename(self, name):
        pass

    def _is_private_model(self, name):
        pass

    def run(self, target_name, method_name, *args, **kwargs):
        # Check node instance is available ?
        real_name, typ = self._build_nodename(target_name)
        if not (real_name and typ):
            return False
        m_inst = self.get_namebus(real_name)
        if isinstance(m_inst, dict):
            _type, meth = m_inst.get(method_name)
            if isinstance(_type, typ):
                if callable(meth):
                    return meth(*arg, **kwargs)
                else:
                    return meth
            else:
                return False
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
