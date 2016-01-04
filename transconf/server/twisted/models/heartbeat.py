# coding=utf-8

__author__ = 'chijun'

import time

from transconf.server.twisted.log import getLogger
from transconf.common.reg import get_model
from transconf.model import Model
from transconf.configration import Configuration
from transconf.server.twisted.client import RSAClient
from transconf.server.twisted.internet import new_public_client
from transconf.server.twisted.event import Task, EventDispatcher
from transconf.server.twisted import CONF as global_conf
from transconf.server.twisted import get_sql_engine 
from transconf.server.twisted.netshell import ActionRequest
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend
from transconf.utils import Exception as _Exception


LOG = getLogger(__name__)

SERVER_CONF = global_conf

sql_engine = get_sql_engine()

BACKEND = HeartBeatCollectionBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(_Exception):
    def __init__(self, group_name, group_type):
        self.group_name = group_name
        self.group_type = group_type

    def __str__(self):
        return 'Group name:{0}, Group type:{1} can not found.'.format(self.group_name, self.group_type)


class HeartRateErr(HeartBeatNotFound):
    def __str__(self):
        return 'Group name:{0}, Group type:{1} got a invalid heartrate.'.format(self.group_name, self.group_type)


CONFIG = Configuration(SERVER_CONF)
CONFIG.add_members('heartbeats', sect='controller:heartbeat:listen', avoid_options='heartrate')
CONFIG.add_members('heartbeartcenters', sect='controller:heartbeat:fanout', avoid_options='heartrate')
master_group = CONFIG.add_group('master', sect='controller:heartbeat:listen')
master_group.add_property('heartrate', option='heartrate', default_val='60')
slaver_group = CONFIG.add_group('slaver', sect='controller:heartbeat:fanout')
slaver_group.add_property('heartrate', option='heartrate', default_val='60')
manage_group = CONFIG.add_group('manage')
manage_group.add_property('group_name', option='local_group_name')
manage_group.add_property('group_type', option='local_group_type')
manage_group.add_property('group_uuid', option='local_group_uuid')


# @register_model
class HeartBeat(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'alive', 'dead'
    # Ver: (0, 1, 1) by chijun
    # 1 add get_fanout_members
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heart',
             'public': ['alive', 'mod:self:heartbeat'],
            }
    ]

    __version__ = (0, 1, 1)

    def _get_fanout_members(self):
        for g_option, is_enabled in CONFIG.heartbeartcenters:
            g = g_option.split('.')
            if (len(g) > 1) and ((is_enabled and g_option) not in self.UNEXPECTED_OPTIONS):
                yield (g[0], g[1], is_enabled)  

    def start(self, config=None):
        self.heartbeat(int(CONFIG.slaver.heartrate))

    def _build_heartbeat_event(self, client, local_name, local_uuid, local_type):
        req = ActionRequest('heartcond.checkin',
                             **dict(group_name=local_name,
                                    uuid=local_uuid,
                                    group_type=local_type))
        return EventDispatcher(client, req, need_close=False)

    def _heartbeat(self, timeout):
        local_name = CONFIG.manage.group_name
        local_type = CONFIG.manage.group_type
        local_uuid = CONFIG.manage.group_uuid
        if local_name and local_type and local_uuid:
            for g_name, typ, is_enabled in self._get_fanout_members():
                client = new_public_client(g_name, typ, local_uuid, type='fanout')
                # TODO by chijun
                # Action Request version can not be supported by server.
                event = self._build_heartbeat_event(client, local_name, local_uuid, local_type)
                t = Task(lambda: event.startWithoutResult())
                t.LoopingCall(timeout)

    def heartbeat(self, timeout):
        # Check if has call heartbeat event-loop, don't call it again.
        if getattr(self, 'is_start', None):
            return True
        self._heartbeat(timeout)
        setattr(self, 'is_start', True)


class RSAHeartBeat(HeartBeat):
    def _build_heartbeat_event(self, client, local_name, local_uuid, local_type):
        client = RSAClient(client)
        return super(RSAHeartBeat, self)._build_heartbeat_event(client, local_name, local_uuid, local_type)


class HeartCondition(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'has', 'register'
    # Ver: (0, 1, 1) by chijun
    # 1 add '_update_target', '_check_target', '_check_target_is_init'
    # 2 add '_check_heart_still_alive', '_check_has_available_targets'
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heartcond',
             'public': [
                        ['has', 'mod:self:has_heartbeat'],
                        ['add', 'mod:self:add_heartbeat'],
                        ['remove', 'mod:self:remove_heartbeat'],
                        ['checkin', 'mod:self:checkin'],
                       ]
            }
    ]

    __version__ = (0, 1, 1)

    def start(self, config=None):
        # Re-initialize sql table
        self._target_init()
        self._timestamp_init()
        configure_heartcondition()

    @property
    def buf_available_uuid(self):
        if not hasattr(self, '_buf_available_uuid'):
            self._set_buf_available_uuid()
        return self._buf_available_uuid

    def _set_buf_available_uuid(self):
        setattr(self, '_buf_available_uuid', CONF_BACKEND.uuids())

    def _check_heart_still_alive(self, group_name, group_type, uuid):
        heartrate = CONFIG.master.heartrate
        cur_time = time.time()
        # Check this heartbeat was timeout?
        if int(cur_time - self._timestamp[uuid]) > int(heartrate):
            # Maybe heartbeat is lost?
            self._update_target(group_name, group_type, uuid, False, False)
            self._check_has_available_targets(group_name, group_type)

    def _check_heart_health(self, group_name, group_type, uuid):
        heartrate = CONFIG.master.heartrate
        # TODO by chijun
        # Use MQ timestamp as better
        cur_time = time.time()
        if uuid not in self._timestamp:
            self._timestamp[uuid] = cur_time
            return cur_time
        else:
            if int(cur_time - self._timestamp[uuid] + 1) >= (int(heartrate)):
                return cur_time
        raise HeartRateErr(group_name, group_type)

    def _target_init(self):
        if not hasattr(self, 'buf_group_target'):
            setattr(self, 'buf_group_target', {})

    def _timestamp_init(self):
        if not hasattr(self, '_timestamp'):
            setattr(self, '_timestamp', {})

    def _check_target(self, group_name, group_type):
        if not self.buf_group_target.get(group_name + '_' + group_type, None):
            return False
        return True

    def _update_target(self, group_name, group_type, uuid, need_count=True):
        LOG.debug('Update a heartbeat for group:{0}, type:{1}, uuid:{2}'.format(group_name,
                                                                                group_type,
                                                                                uuid))
        BACKEND.update(dict(group_name=group_name,
                            group_type=group_type,
                            uuid=uuid),
                       need_count)

    def _check_has_available_targets(self, group_name, group_type):
        # Check if it has available uuid of group target?
        if BACKEND.has(group_name, group_type):
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
                    # Heartbeat is not in enabled range.
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
        else:
            LOG.warn('Got a bad heartbeat, context:{0}'.format(context))

    def has_heartbeat(self, context):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        if not (group_name or group_type) or \
                not self._check_target(group_name, group_type):
            return False
        return True

    def add_heartbeat(self, context):
        uuid = context.get('uuid', None)
        if uuid not in CONF_BACKEND.uuids():
            CONF_BACKEND.update(dict(uuid=uuid))
            self._set_buf_available_uuid()

    def remove_heartbeat(self, context):
        uuid = context.get('uuid', None)
        if uuid in CONF_BACKEND.uuids():
            CONF_BACKEND.delete(dict(uuid=uuid))
            self._set_buf_available_uuid()


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


def configure_heartcondition():
    CONF_BACKEND.create()
    CONF_BACKEND.clear()
    BACKEND.create()
    BACKEND.clear()
    for uuid, is_enabled in CONFIG.heartbeats:
        if str(is_enabled).lower() == 'true':
            CONF_BACKEND.update(dict(uuid=uuid))
