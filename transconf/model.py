__author__ = 'chijun'

from transconf.common.model import BaseModel
from transconf.common.namebus import NameBus
from transconf.common.basetype import BaseType
from transconf.mystruct import NodeStructV1
from transconf.mystructtypes import *
from transconf.server.utils import as_config


class ModelInternalStuctErr(Exception):
    """Raised when pointed node object's struct or its env struct being bad"""


class Model(BaseModel):
    STRUCT = NodeStructV1()
    SPLIT_DOT = '&'
    IS_NODE_METHOD = IsNodeInterface
    IS_PRIVATE_METHOD = IsPrivateInterface
    IS_PUBLIC_METHOD = IsPublicInterface
    __version__ = (0, 1, 0)

    def __init__(self):
        super(Model, self).__init__()
        self.is_pri_rule = self.IS_PRIVATE_METHOD
        self.is_pub_rule = self.IS_PUBLIC_METHOD 
        self.is_node_rule = self.IS_NODE_METHOD
        self.node_rules = {}

    def _build_nodename(self, lst):
        def name(self, n, sub_name):
            if 'name' not in n:
                n['name'] = sub_name
            else:
                n['name'] = n['name'] + self.split + sub_name
            return n['name'] 
        try:
            ln = {}
            new_lst = [self._found_nodename(name(self, ln, n)) for n in lst]
            return new_lst[-1]
        except TypeError:
            return None, None

    def _found_nodename(self, name):
        p, s = self._is_private_mode(name)
        if p and s:
            name_meth = self.node_rules.get(p, None)
            if callable(name_meth):
                if name_meth(s):
                    return p, self.is_pri_rule
        else:
            return name, self.is_pub_rule

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
                    self.node_rules[real_name] = value[1]
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
                    return meth(*args, **kwargs)
                else:
                    return meth
            else:
                return False
        else:
            raise ModelInternalStuctErr('Can not loading method name:{0} of {1}'.format(method_name, real_name))
