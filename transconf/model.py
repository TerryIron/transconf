__author__ = 'chijun'

from common.model import BaseModel
from common.namebus import NameBus
from common.basetype import BaseType
from mystruct import NodeStructV1
from mystructtypes import *


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
        self.is_node_rule = self.IS_NODE_METHOD 
        self.is_pri_rule = self.IS_PRIVATE_METHOD 
        self.is_pub_rule = self.IS_PUBLIC_METHOD 

    def _build_nodename(self, lst):
        try:
            ln = None
            def name(self, n, sub_name):
                if not n:
                    n = sub_name
                else:
                    n = n + self.split + sub_name
                return n 
            print lst
            new_lst = [self._found_nodename(name(self, ln, n)) for n in lst]
            print new_lst
            return self._build_class_nodename(new_lst)
        except ModelNodeFoundFail:
            return None, None

    def _found_nodename(self, name):
        print name

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

   
