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

from transconf.common.basetype import BaseType
from transconf.common.reg import get_reg_target
from transconf.utils import Exception


__all__ = [
    'IsString', 'IsList', 'IsDict', 'IsNodeInterface',
    'IsPrivateInterface', 'IsPublicInterface', 'IsProperty',
]


class BaseTypeError(Exception):
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return "Item:{0} should be (mod, NAME, METHOD)".format(self.string)


# Use these BaseType class to define static value
class IsString(BaseType):
    """
    字符串类型检查器

    """
    def check(self, key, value):
        if isinstance(value, str):
            return key, self, value


class IsList(BaseType):
    """
    列表类型检查器

    """
    def check(self, key, value):
        if isinstance(value, list):
            return key, self, value


class IsDict(BaseType):
    """
    字典类型检查器

    """
    def check(self, key, value):
        if isinstance(value, dict):
            return key, self, value


# Use these BaseType class to define class members
class IsInterface(BaseType):
    """
    接口类型检查器

    """
    def check(self, key, value):
        _key, _val = value
        try:
            typ, name, val = _val
            obj = get_reg_target(typ, name) if name != 'self' else key
            if not obj:
                return
            if callable(val):
                return _key, self, val
            if hasattr(obj, val):
                _method = getattr(obj, val)
                if callable(_method):
                    return _key, self, _method
        except:
            raise BaseTypeError(value[1])


class IsPrivateInterface(IsInterface):
    """
    私有接口类型检查器

    """
    def check(self, key, value):
        return super(IsPrivateInterface, self).check(key ,value)


class IsPublicInterface(IsInterface):
    """
    公有接口类型检查器

    """
    def check(self, key, value):
        return super(IsPublicInterface, self).check(key, value)


class IsNodeInterface(IsInterface):
    """
    节点接口类型检查器

    """
    def check(self, key, value):
        return super(IsNodeInterface, self).check(key, value)


class IsProperty(BaseType):
    """
    节点属性类型检测器

    """
    def check(self, key, value):
        _key, _val = value
        try:
            typ, name, val = _val
            obj = get_reg_target(typ, name) if name != 'self' else key
            if not obj:
                return
            if callable(val):
                return _key, self, val
            if hasattr(obj, val):
                _property = getattr(obj, val)
                if not callable(_property):
                    return _key, self, _property
        except:
            raise BaseTypeError(value[1])
