#coding=utf-8

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

try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin

"""
    Target name's structure is like below:
                ---->  NAMEBUS.NAMEBUS[MODEL_TYPE]
                |
    ns.run('bus.driver[MODEL_A]', 'stop_bus') == True
    ns.getattr('bus.driver[MODEL_B]', 'stop_bus') == None
    ns.getattr('bus[MODEL_B]', 'stop_times') == 0
    ns.setattr('bus.driver[MODEL_A]' == False
          ||
          \/
     {
       'bus': {
           'MODEL_A': {'is_started': A_DRV_API, 'is_stop': A_DRV_API},
           'MODEL_B': {'is_started': B_DRV_API, 'stop_times': B_DRV_API},
       },
       'bus.driver': {
           'MODEL_A': {'start_bus': A_API, 'stop_bus': A_API},
           'MODEL_B': {'start_bus': B_API, 'stop_bus': B_API},
       }
     }

                ---->  $NAMEBUS.NAMEBUS[MODEL_TYPE]
                |
    ns.run('$bus.database[MODEL_A]', 'name') == False
    ns.getattr('bus.database[MODEL_A]', 'name') == 'ABC'
    ns.setattr('bus.database[MODEL_A]', 'name', 'ABC') == True
     {
       'bus': {
           'MODEL_A': {'is_started': A_API, 'is_stop': A_API},
           'MODEL_B': {'is_started': B_API, 'is_stop': B_API},
       },
       'bus.driver': {
           'MODEL_A': {'start_bus': A_API, 'stop_bus': A_API},
           'MODEL_B': {'start_bus': B_API, 'stop_bus': B_API},
       },
       'bus.database': {
           'MODEL_A': {'name': A_API)
           'MODEL_B': {'name': B_API)
       }
     }

"""


class Bus(DictMixin):
    def __init__(self):
        self.bus = []

    def keys(self):
        return [k for k, v in self.bus]

    def __getitem__(self, item):
        """
        获取总线对象

        Args:
            item(str): 对象名称

        Returns:
            object: 总线对象

        """
        for it, obj in self.bus:
            if it == item:
                return obj

    def __setitem__(self, key, value):
        """
        设置总线对象

        Args:
            key(str): 对象名称
            value(object): 总线对象
            force(bool): 是否强制，默认为False

        Returns:
            None
        """
        if key in self:
            del self[key]
        self.bus.append((key, value))

    def __delitem__(self, key):
        """
        删除总线对象

        Args:
            key: 对象名称

        Returns:
            None

        """
        for it, obj in self.bus:
            if it == key:
                self.bus.remove((it, obj))


class NameBus(object):
    """
    空间总线
    作为模型类和模型命令解释器的内置空间

    """
    
    def __init__(self, safe=True):
        self.__namebus__ = Bus()
        self.safe = safe

    def get(self, item):
        return self.__namebus__[item]

    def all(self):
        return self.__namebus__

    def set(self, key, value):
        if key in self.__namebus__.keys():
            if not self.safe:
                self.__namebus__[key] = value
        else:
            self.__namebus__[key] = value

    def remove(self, key):
        del self.__namebus__[key]
