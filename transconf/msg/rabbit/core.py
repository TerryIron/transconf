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

import os
import uuid
import pika

from transconf.packer import JsonSerializionPacker
from transconf.utils import from_config_option, as_config


class RabbitAMQP(object):
    """
        RabbitMQ 基础类

    """
    CONNECTION_CLASS = pika.BlockingConnection
    CONNECTION_ATTEMPTS = 3
    DEFAULT_CONF = as_config(os.path.join(os.path.dirname(__file__), 'default.ini'))
    PACKER = JsonSerializionPacker()
    CONF = None

    def __init__(self, amqp_url=None, con_timeout=5, con_attempts=3, packer=None):
        self.connection_class = self.CONNECTION_CLASS
        self.packer = self.PACKER if not packer else packer
        self.conf = self.DEFAULT_CONF if not self.CONF else self.CONF
        if callable(self.conf):
            self.conf = self.conf()
        self.parms = None
        if not amqp_url:
            amqp_url = self.conf_amqp_url
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(con_timeout,
                                             con_attempts or self.CONNECTION_ATTEMPTS)
        )
        self.bind_queue = None
        self.bind_exchange = None
        self.init()

    def init(self):
        """
        初始化

        Returns:
            未实现

        """
        pass

    @property
    def rand_corr_id(self):
        """
        Returns:
            str: 随机UUID值

        """
        return str(uuid.uuid4())

    @property
    @from_config_option('amqp_url', 'amqp://guest:guest@localhost:5672')
    def conf_amqp_url(self):
        """
        Returns:
            str: AMQP地址

        """
        return self.conf

    @property
    def conf_rpc_queue(self):
        """
        Returns:
            str: RPC模式队列

        """
        raise NotImplementedError()

    @property
    def conf_topic_exchange(self):
        """
        Returns:
            str: TOPIC模式交换机

        """
        raise NotImplementedError()

    @property
    def conf_topic_queue(self):
        """
        Returns:
            str: TOPIC模式队列

        """
        raise NotImplementedError()

    @property
    def conf_fanout_exchange(self):
        """
        Returns:
            str: FANOUT模式交换机

        """
        raise NotImplementedError()

    @property
    def conf_fanout_queue(self):
        """
        Returns:
            str: FANOUT模式队列

        """
        raise NotImplementedError()

