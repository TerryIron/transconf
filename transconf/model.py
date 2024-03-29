# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'

from transconf.common.model import BaseModel, BaseResource
from transconf.mystruct import NodeStructV1
from transconf.mystructtypes import *
from transconf.utils import myException


class ModelInternalStuctErr(myException):
    """Raised when pointed node object's struct or its env struct being bad"""


class Resource(BaseResource):
    @staticmethod
    def build_rule(target, method, func, **kwargs):
        """
        添加基本路由规则

        Args:
            target: 路由对象名
            method: 路由方法名
            func: 函数入口
            **kwargs: 字典参数

        """

        _object = kwargs.get('from_obj', None)
        if not _object:
            _object = 'self'

        _validate = kwargs.get('validate_method', None)
        _public = kwargs.get('is_public', False)
        if _validate and not _public:
            _validate_obj = kwargs.get('validate_obj', 'self')
            return dict(node=target,
                        name=(_validate, ('mod',
                                          '{0}'.format(_validate_obj),
                                          '{1}'.format(_validate),
                                          )),
                        private=(method, ('mod', _object, func)))
        else:
            return dict(node=target,
                        public=(method, ('mod', _object, func)))


class Model(BaseModel):
    """
    模型解释器

    """
    STRUCT_CLASS = NodeStructV1
    STRUCT = None
    SPLIT_DOT = '&'
    IS_NODE_METHOD = IsNodeInterface
    IS_PRIVATE_METHOD = IsPrivateInterface
    IS_PUBLIC_METHOD = IsPublicInterface
    __version__ = (0, 1, 0)

    def __init__(self):
        self.is_pri_rule = self.IS_PRIVATE_METHOD
        self.is_pub_rule = self.IS_PUBLIC_METHOD 
        self.is_node_rule = self.IS_NODE_METHOD
        self.node_rules = dict()
        self.__items__ = dict()
        if self.STRUCT_CLASS:
            self.STRUCT = self.STRUCT_CLASS(self)
        super(Model, self).__init__()

    def __getitem__(self, item):
        return self.__items__.get(item, None)

    def __setitem__(self, key, value):
        self.__items__[key] = value

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
                    return p, s, self.is_pri_rule
        else:
            return name, None, self.is_pub_rule

    def _is_private_mode(self, name):
        l = name.split(self.member_split)        
        if len(l) == 2:
            return l[0], l[1]
        return None, None

    def set_node_member(self, name_lst, key, value):
        """
        设置节点成员

        Args:
            name_lst(lis): 节点名
            key: 节点属性名
            value: 节点属性值

        Returns:
            None

        """
        real_name = self._build_real_nodename(name_lst)
        n = self.get(real_name)
        if isinstance(n, dict):
            if isinstance(value[0], self.is_node_rule):
                self.node_rules[real_name] = value[1]
            n[key] = value
            return True
        return False

    def run(self, _target_name, _method_name, **kwargs):
        """
        运行内置方法

        Args:
            _target_name: 内置对象名
            _method_name: 内置方法名
            **kwargs: 字典参数

        Returns:
            运行结果

        """
        # Check node instance is available ?
        real_name, inst_name, typ = self._build_nodename(_target_name)
        m_inst = self.get(real_name) or None
        if not m_inst:
            return
        _type, _meth = m_inst.get(_method_name, (None, None))
        if _meth and isinstance(_type, typ):
            if callable(_meth):
                if not inst_name:
                    return _meth(**kwargs)
                else:
                    return _meth(inst_name, **kwargs)
            else:
                return _meth
        else:
            raise ModelInternalStuctErr('Can not loading method name:{0} of {1}'.format(_method_name, _target_name))

    def build_rule(self, target, method, func, **kwargs):
        return Resource.build_rule(target, method, func, **kwargs)

    def add_resource(self, resource):
        """
        添加资源规则

        Args:
            resource: 资源实例

        """
        if isinstance(resource, Resource):
            self._form += resource.form
