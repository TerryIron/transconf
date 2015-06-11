__author__ = 'chijun'

from common.model import BaseModel
from common.namebus import NameBus
from common.basetype import BaseType
from mystruct import NodeStructV1
from mystructtypes import *


class ModelInternalStuctErr(Exception):
    """Raised when pointed node object's struct or its env struct being bad"""


class Model(BaseModel):
    STRUCT = NodeStructV1()
    SPLIT_DOT = '&'
    IS_NODE_METHOD = IsNodeInterface
    IS_PRIVATE_METHOD = IsPrivateInterface
    IS_PUBLIC_METHOD = IsPublicInterface

    def __init__(self, db_engine=None):
	super(Model, self).__init__(db_engine)
        self.is_pri_rule = self.IS_PRIVATE_METHOD 
        self.is_pub_rule = self.IS_PUBLIC_METHOD 
        self.is_node_rule = self.IS_NODE_METHOD
	self.node_rules = {}

    def _build_nodename(self, lst):
        def name(self, n, sub_name):
            if not n:
                n = sub_name
                print 000, n
            else:
                n = n + self.split + sub_name
                print 001, n
            return n 
        try:
            ln = None
            new_lst = [self._found_nodename(name(self, ln, n)) for n in lst]
            return self._build_class_nodename(new_lst)
        except TypeError:
            return None, None

    def _found_nodename(self, name):
        p, s = self._is_private_mode(name)
        if p and s:
            print 111, name
        else:
            print 222, name

    def _is_private_mode(self, name):
        l = name.split(self.member_split)        
        if len(l) == 2:
            return l[0], l[1]
        return None, None

    def set_node_member(self, name_lst, key, value):
        real_name = self._build_class_nodename(name_lst)
        if real_name in self.namebus:
            n = self.get_namebus(real_name)
            if isinstance(n, dict):
		if isinstance(value[0], self.is_node_rule):
		    self.node_rules[key] = value
                n[key] = value
                return True
        return False

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

   
