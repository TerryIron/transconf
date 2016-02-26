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

from transconf.model import Model
from transconf.common.reg import get_model
from transconf.server.twisted.client import RSAClient
from transconf.server.twisted.internet import new_public_client
from transconf.server.twisted.event import Task, EventDispatcher
from transconf.server.twisted.netshell import ActionRequest
from transconf.server.twisted.models.heartbeat_conf import get_available_heartbeats
from transconf.server.twisted.models.heartbeat_conf import CONFIG, master_group
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend
from transconf.server.twisted.log import getLogger


LOG = getLogger(__name__)


class HeartBeatNotFound(Exception):
    def __init__(self, group_name, group_type):
        self.group_name = group_name
        self.group_type = group_type

    def __str__(self):
        return 'Group name:{0}, Group type:{1} can not found.'.format(self.group_name, self.group_type)


class HeartRateErr(HeartBeatNotFound):
    def __str__(self):
        return 'Group name:{0}, Group type:{1} got a invalid heartrate.'.format(self.group_name, self.group_type)


class HeartBeat(Model):
    UNEXPECTED_OPTIONS = ['heartrate', 'interval_times']
    FORM = [{'node': 'heart',
             'public': ['alive', ('mod', 'self', 'heartbeat')],
            }
    ]

    __version__ = (0, 1, 1)

    def init(self, config=None):
        self.local_name = CONFIG.manage.group_name
        self.local_type = CONFIG.manage.group_type
        self.local_uuid = CONFIG.manage.group_uuid

    def start(self, config=None):
        if self.local_name and self.local_type and self.local_uuid:
            self.heartbeat(int(CONFIG.slaver.heartrate))

    def _get_fanout_members(self):
        for g_option, is_enabled in CONFIG.heartbeartcenters:
            g = g_option.split('.')
            if (len(g) > 1) and ((is_enabled and g_option) not in self.UNEXPECTED_OPTIONS):
                yield (g[0], g[1], is_enabled)  

    def _build_heartbeat_event(self, client, local_name, local_uuid, local_type):
        req = ActionRequest('heartcond.checkin',
                            **dict(group_name=local_name,
                                   uuid=local_uuid,
                                   group_type=local_type))
        return EventDispatcher(client, req, need_close=False)

    def heartbeat(self, timeout):
        # Check if has call heartbeat event-loop, don't call it again.
        if getattr(self, 'is_start', None):
            return True
        for g_name, typ, is_enabled in self._get_fanout_members():
            client = new_public_client(g_name, typ, self.local_uuid, type='fanout')
            # TODO by chijun
            # Action Request version can not be supported by server.
            event = self._build_heartbeat_event(client, self.local_name, self.local_uuid, self.local_type)
            t = Task(lambda: event.startWithoutResult())
            t.LoopingCall(timeout)
        setattr(self, 'is_start', True)


class RSAHeartBeat(HeartBeat):
    def _build_heartbeat_event(self, client, local_name, local_uuid, local_type):
        client = RSAClient(client)
        return super(RSAHeartBeat, self)._build_heartbeat_event(client, local_name, local_uuid, local_type)


class HeartCondition(Model):
    UNEXPECTED_OPTIONS = ['heartrate', 'interval_times', 'connection']
    FORM = [{'node': 'heartcond',
             'public': [
                        ['has', ('mod', 'self', 'has_heartbeat')],
                        ['checkin', ('mod', 'self', 'checkin')],
                       ]
            }
    ]

    __version__ = (0, 1, 1)

    def init(self, config=None):
        self.heartrate, self.interval = CONFIG.master.heartrate, CONFIG.master.interval_times
        self.timeout = int(self.heartrate * self. interval)
        self.health_range = (int(self.heartrate),
                             int(self.interval + (self.interval + 1) * self.heartrate))
        self._ready()

    def _ready(self):
        # Re-initialize sql table
        self.BACKEND = HeartBeatCollectionBackend(master_group.sql_engine)
        self.BACKEND.clear()
        self.CONF_BACKEND = HeartBeatIsEnabledBackend(master_group.sql_engine)
        self.CONF_BACKEND.clear()
        for a in get_available_heartbeats():
            self.add_heartbeat(a)
        self._buf_available_uuid, self._timestamp, self.buf_group_target = self.CONF_BACKEND.uuids(), {}, {}

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

    def _check_heart_health(self, group_name, group_type, uuid):
        # TODO by chijun
        # Use MQ timestamp as better
        cur_time = time.time()
        if uuid not in self._timestamp:
            self._timestamp[uuid] = cur_time
            return cur_time
        else:
            used_time = int(cur_time - self._timestamp[uuid] + 1)
            if int(self.health_range[0]) <= used_time < int(self.health_range[1]):
                return cur_time
        raise HeartRateErr(group_name, group_type)

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
        if self.BACKEND.has(group_name, group_type):
            self.buf_group_target[group_name + '_' + group_type] = True
        else:
            self.buf_group_target[group_name + '_' + group_type] = False

    def checkin(self, group_name, group_type, uuid, heartrate=60):
        LOG.debug('Got a heartbeat from group:{0}, type:{1}, uuid:{2}'.format(group_name,
                                                                              group_type,
                                                                              uuid))
        if group_name and group_type and uuid:
            try:
                cur_time = self._check_heart_health(group_name, group_type, uuid)
                if uuid not in self.buf_available_uuid:
                    # Heartbeat is not in available range.
                    return 
                self._timestamp[uuid] = cur_time
            except HeartRateErr:
                return 
            except Exception:
                return
            self._update_target(group_name, group_type, uuid)
            self._check_has_available_targets(group_name, group_type)
            t = Task(lambda:  self._check_heart_still_alive(group_name, group_type, uuid))
            t.CallLater(heartrate + heartrate / 2)

    def has_heartbeat(self, group_name, group_type):
        if not (group_name or group_type) or \
                not self._check_target(group_name, group_type):
            return False
        return True

    def add_heartbeat(self, uuid):
        if uuid not in self.CONF_BACKEND.uuids():
            self.CONF_BACKEND.update(dict(uuid=uuid))

    def remove_heartbeat(self, uuid):
        if uuid in self.CONF_BACKEND.uuids():
            self.CONF_BACKEND.delete(dict(uuid=uuid))


def if_available(group_name, group_type):
    def _if_available(func):
        def __if_available(*args, **kwargs):
            m = get_model('heartcond')
            if hasattr(m, 'has_heartbeat') and m.has_heartbeat(dict(group_name=group_name,
                                                                    group_type=group_type)):
                return func(*args, **kwargs)
            else:
                raise HeartBeatNotFound(group_name, group_type)
        return __if_available
    return _if_available
