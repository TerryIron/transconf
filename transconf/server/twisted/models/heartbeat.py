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

import time
import os.path
import commands
from uuid import uuid3, UUID

from transconf.utils import myException
from transconf.model import Model
from transconf.common.reg import get_model
from transconf.server.twisted.client import RSAClient
from transconf.server.twisted.internet import ExchangeType, IGroup, get_client_from_pool
from transconf.server.twisted.event import Task, EventDispatcher
from transconf.server.twisted.netshell import ActionRequest
from transconf.server.twisted.models.heartbeat_conf import manage_group, master_group, slaver_group
from transconf.server.twisted.models.heartbeat_conf import CONFIG, get_available_heartbeats
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend
from transconf.server.twisted.log import getLogger


LOG = getLogger(__name__)


class UnsupportedItem(myException):
    pass


def channel_id2token(channel_id, token, uuid='6ba7b810-9dad-11d1-80b4-00c04fd430c8'):
    print uuid, token, channel_id
    _token = uuid3(UUID(uuid), "%s%s" % (token, channel_id))
    return _token


def setup_cluster_channel(token, install_path="/var/lib/rabbitmq"):
    target = os.path.join(install_path, '.erlang.cookie')
    with open(target, 'w') as f:
        f.write(str(token))


CLUSTER_MODE_METH = {
   'memory': 'rabbitmqctl stop_app && rabbitmqctl join_cluster {hostname} --ram',
   'disk': 'rabbitmqctl stop_app && rabbitmqctl join_cluster {hostname}',
}


def setup_cluster_node(hostname, mode):
    global CLUSTER_MODE_METH
    if mode not in CLUSTER_MODE_METH:
        raise UnsupportedItem('Please select disk/memory mode for cluster:{0}'.format(hostname))
    code, out = commands.getstatusoutput(CLUSTER_MODE_METH[mode](hostname))
    if int(code) != 0:
        LOG.debug('Failed to add cluster host:{0}, mode:{1}, '
                  'please check hostname has added into /etc/hosts '
                  'or setup channel by the same token'.format(hostname, mode))
        return False
    else:
        LOG.debug('Added cluster host:{0}, mode:{1}'.format(hostname, mode))
    commands.getstatusoutput('rabbitmqctl start_app')
    return True


class HeartBeatNotFound(myException):
    def __init__(self, group_name, group_type):
        self.group_name = group_name
        self.group_type = group_type

    def __str__(self):
        return 'Group name:{0}, Group type:{1} can not found.'.format(self.group_name,
                                                                      self.group_type)


class HeartRateErr(HeartBeatNotFound):
    def __str__(self):
        return 'Group name:{0}, Group type:{1} got a invalid heartrate.'.format(self.group_name,
                                                                                self.group_type)


class HeartbeatNotAvailable(myException):
    pass


class HeartBeat(Model):
    FORM = [{'node': 'heart',
             'public': [
                        ['alive', ('mod', 'self', 'heartbeat')],
                        ['set_channel', ('mod', 'self', 'setChannel')],
                       ]
            }
    ]

    __version__ = (0, 1, 1)

    def _ready_cluster(self):
        if slaver_group.joined_cluster:
            channel = slaver_group.cluster_channel_id
            self.setChannel(channel)

    def init(self):
        self.local_name = manage_group.group_name
        self.local_type = manage_group.group_type
        self.local_uuid = manage_group.group_uuid
        self.heartrate = int(slaver_group.heartrate)
        self.mode = slaver_group.cluster_mode
        self.hostname = slaver_group.cluster_hostname

    def start(self):
        if self.local_name and self.local_type and self.local_uuid:
            self.heartbeat(self.heartrate)
            self._ready_cluster()

    @staticmethod
    def _get_fanout_members():
        for g_option, is_enabled in CONFIG.heartbeartcenters:
            g = g_option.split('.', 1)
            if len(g) > 1:
                yield (g[0], g[1], is_enabled)  

    def _build_heartbeat_event(self, client, group):
        # TODO by chijun
        # Action Request version can not be supported by server.
        req = ActionRequest('heartcond.checkin',
                            **dict(group_name=group.local_name,
                                   uuid=group.local_uuid,
                                   group_type=group.local_type))
        return Task(lambda: EventDispatcher(client, req, need_close=False).startWithoutResult())

    def _build_cluster_event(self, client, hostname, mode):
        # TODO by chijun
        # Action Request version can not be supported by server.
        req = ActionRequest('heartcond.setup_cluster',
                            **dict(mode=mode,
                                   hostname=hostname))
        return Task(lambda: EventDispatcher(client, req).startWithoutResult())

    def heartbeat(self, timeout):
        # Check if has call heartbeat event-loop, don't call it again.
        if getattr(self, 'is_start', None):
            return True
        for g_name, typ, is_enabled in self._get_fanout_members():
            g = IGroup(g_name, typ, self.local_uuid)
            client_1 = get_client_from_pool(g, ExchangeType.TYPE_FANOUT)
            task_1 = self._build_heartbeat_event(client_1, g)
            task_1.LoopingCall(timeout)
            client_2 = get_client_from_pool(g, ExchangeType.TYPE_FANOUT)
            task_2 = self._build_cluster_event(client_2, self.hostname, self.mode)
            task_2.CallLater(timeout * 1.5)
        setattr(self, 'is_start', True)

    def setChannel(self, channel):
        uuid = slaver_group.cluster_uuid
        token = slaver_group.cluster_token
        if uuid:
            channel_token = channel_id2token(channel, token, uuid)
        else:
            channel_token = channel_id2token(channel, token)
        setup_cluster_channel(token=channel_token)


class RSAHeartBeat(HeartBeat):
    def _build_heartbeat_event(self, client, group):
        client = RSAClient(client)
        return super(RSAHeartBeat, self)._build_heartbeat_event(client, group)

    def _build_cluster_event(self, client, hostname, mode):
        client = RSAClient(client)
        return super(RSAHeartBeat, self)._build_cluster_event(client,
                                                              hostname,
                                                              mode)


class HeartCondition(Model):
    FORM = [{'node': 'heartcond',
             'public': [
                        ['has', ('mod', 'self', 'hasHeartbeat')],
                        ['checkin', ('mod', 'self', 'checkin')],
                        ['setup_cluster', ('mod', 'self', 'setupCluster')],
                        ['set_channel', ('mod', 'self', 'setChannel')],
                       ]
            }
    ]

    __version__ = (0, 1, 1)

    def _ready_cluster(self):
        if master_group.joined_cluster:
            channel = slaver_group.cluster_channel_id if slaver_group.cluster_channel_id \
                else master_group.cluster_channel_id
            self.setChannel(channel)
            mode = slaver_group.cluster_mode if slaver_group.cluster_mode \
                else master_group.cluster_mode
            hostname = master_group.cluster_hostname
            self.setupCluster(hostname, mode)

    def _ready_backend(self):
        # Re-initialize sql table
        self.BACKEND = HeartBeatCollectionBackend(master_group.sql_engine)
        self.BACKEND.clear()
        self.CONF_BACKEND = HeartBeatIsEnabledBackend(master_group.sql_engine)
        self.CONF_BACKEND.clear()
        for a in get_available_heartbeats():
            self.addHeartbeat(a)
        self._buf_available_uuid, self._timestamp, self.buf_group_target = self.CONF_BACKEND.uuids(), {}, {}

    def init(self):
        self.heartrate, self.interval = master_group.heartrate, master_group.interval_times
        self.timeout = int(self.heartrate * self. interval)
        self.health_range = (int(self.heartrate),
                             int(self.interval + (self.interval + 1) * self.heartrate))

    def start(self):
        self._ready_backend()
        self._ready_cluster()

    def setupCluster(self, hostname, mode):
        LOG.debug('setup cluster mode:{0}'.format(mode))

    def setChannel(self, channel):
        uuid = master_group.cluster_uuid
        token = master_group.cluster_token
        if uuid:
            channel_token = channel_id2token(channel, token, uuid)
        else:
            channel_token = channel_id2token(channel, token)
        setup_cluster_channel(token=channel_token)

    @property
    def buf_available_uuid(self):
        return self._buf_available_uuid

    def _check_heart_still_alive(self, group_name, group_type, uuid):
        cur_time = time.time()
        # Check this heartbeat was timeout?
        if int(cur_time - self._timestamp[uuid]) > int(self.timeout):
            # Maybe heartbeat is lost?
            self._update_target(group_name, group_type, uuid, False)
            self._check_has_available_targets(group_name, group_type)

    def _check_heart_health(self, group):
        uuid = group.uuid
        if uuid not in self.buf_available_uuid:
            # Heartbeat is not in available range.
            raise HeartRateErr(group.group_name, group.group_type)
        # TODO by chijun
        # Use MQ timestamp as better
        cur_time = time.time()
        if uuid not in self._timestamp:
            self._timestamp[uuid] = cur_time
            self._timestamp[uuid] = cur_time
        else:
            used_time = int(cur_time - self._timestamp[uuid] + 1)
            if int(self.health_range[0]) <= used_time < int(self.health_range[1]):
                self._timestamp[uuid] = cur_time
        raise HeartRateErr(group.group_name, group.group_type)

    def _check_target(self, group_name, group_type):
        if not self.buf_group_target.get(group_name + '_' + group_type, None):
            return False
        return True

    def _update_target(self, group_name, group_type, uuid, need_count=True):
        LOG.debug('Update a heartbeat for group:{0}, type:{1}, uuid:{2}'.format(group_name,
                                                                                group_type,
                                                                                uuid))
        self.BACKEND.update(dict(group_name=group_name,
                                 group_type=group_type,
                                 uuid=uuid),
                            need_count)

    def _check_has_available_targets(self, group_name, group_type):
        # Check if it has available uuid of group target?
        _name = group_name + '_' + group_type
        if self.BACKEND.has(group_name, group_type):
            self.buf_group_target[_name] = True
        else:
            self.buf_group_target[_name] = False

    def checkin(self, group, heartrate=60):
        if isinstance(group, IGroup):
            LOG.debug('Got a heartbeat from group:{0}, type:{1}, uuid:{2}'.format(group.group_name,
                                                                                  group.group_type,
                                                                                  group.uuid))
            try:
                self._check_heart_health(group)
            except HeartRateErr:
                return 
            except Exception:
                return
            self._update_target(group_name, group_type, uuid)
            self._check_has_available_targets(group_name, group_type)
            t = Task(lambda:  self._check_heart_still_alive(group_name, group_type, uuid))
            t.CallLater(heartrate + heartrate / 2)

    def hasHeartbeat(self, group_name, group_type):
        if not (group_name or group_type) or \
                not self._check_target(group_name, group_type):
            return False
        return True

    def addHeartbeat(self, uuid):
        if uuid not in self.CONF_BACKEND.uuids():
            self.CONF_BACKEND.update(dict(uuid=uuid))

    def rmHeartbeat(self, uuid):
        if uuid in self.CONF_BACKEND.uuids():
            self.CONF_BACKEND.delete(dict(uuid=uuid))


def if_available(group_name, group_type):
    def _if_available(func):
        def __if_available(*args, **kwargs):
            m = get_model('heartcond')
            if hasattr(m, 'hasHeartbeat') and m.hasHeartbeat(dict(group_name=group_name,
                                                                  group_type=group_type)):
                return func(*args, **kwargs)
            else:
                raise HeartBeatNotFound(group_name, group_type)
        return __if_available
    return _if_available
