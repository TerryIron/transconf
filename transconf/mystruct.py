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

from transconf.common.struct import *
from transconf.mystructtypes import *


class NodeStructV1(NodeStruct):
    """
    节点结构类型检查器
    """
    SUPPORTED_TYPES = [
                       IsString, 
                       IsDict, 
                       IsList, 
                       IsPublicInterface, 
                       IsPrivateInterface, 
                       IsProperty
                      ]

    def __init__(self, model):
        super(NodeStructV1, self).__init__()
        self.set_default('node', IsString, 1, None)
        self.set_default('name', IsNodeInterface, 1, None)
        self.set_default('private', IsPrivateInterface, 1, None)
        self.set_default('public', IsPublicInterface, 1, None)
        self.set_default('property', IsProperty, 1, None)
        self.set_default('subs', IsList, 50, {})
        self.set_nodename('node')
        self.set_branchname('subs')
        self.model = model

    def check_input(self, key, value):
        """
        检查输入数据

        Args:
            key: 键值
            value: 数据

        Returns:
            处理后的数据

        """
        if key not in self.keys():
            raise NodeItemNotFound('Can not found variable:{0}'.format(key))
        try:
            typ = self.get_type(key)
            if key in ('private', 'public', 'property', 'name'):
                key = self.model
            return typ().check(key, value)
        except Exception as e:
            raise NodeItemTypeNotSupport('Key:{0}, value:{1}, caused:{2}.'.format(key, value, e))

