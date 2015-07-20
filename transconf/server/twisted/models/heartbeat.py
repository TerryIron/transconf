__author__ = 'chijun'

import time
import functools
from twisted.internet import task, reactor

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.server.twisted.internet import get_client
from transconf.server.twisted import CONF as global_conf
from transconf.server.twisted import get_sql_engine 
from transconf.server.utils import from_config, from_config_option, from_model_option, as_config
from transconf.server.twisted.netshell import ShellRequest
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend

SERVER_CONF = global_conf

sql_engine = get_sql_engine()

BACKEND = HeartBeatCollectionBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type)

class HeartRateErr(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} got a invalid heartrate.'.format(group_name, group_type)


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'alive', 'dead'
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heart',
             'public': ['alive', 'mod:heartbeat:heartbeat'],
             'public': ['dead', 'mod:heartbeat:stop'],
            }
    ]

    @from_model_option('name', None, sect='heartcondition')
    def _conf_target_name(self, config):
        return config

    @property
    @from_config(sect='controller:heartbeat:fanout')
    def _conf_group_names(self):
        return SERVER_CONF

    @property
    @from_config_option('local_group_name', None)
    def _conf_group_name(self):
        return SERVER_CONF

    @property
    @from_config_option('local_group_type', None)
    def _conf_group_type(self):
        return SERVER_CONF

    @property
    @from_config_option('local_group_uuid', None)
    def _conf_group_uuid(self):
        return SERVER_CONF

    @property
    @from_config_option('heartrate', 60, sect='controller:heartbeat:fanout')
    def _conf_heartrate(self):
        return SERVER_CONF

    def start(self, config=None):
        self.is_start = None
        name = self._conf_target_name(config)
        if name:
            self.heart = self.heartbeat(name)
            if self.heart:
                timeout = int(self._conf_heartrate)
                for h in self.heart:
                    h.start(timeout)

    def stop(self, config=None):
        # Stop all heartbeat event-loop.
        if self.heart:
            for h in self.heart:
                h.stop()
        if self.is_start:
            self.is_start = False
        name = self._conf_target_name(config)
        if name:
            local_name = self._conf_group_name
            local_type = self._conf_group_type
            local_uuid = self._conf_group_uuid
            if local_name and local_type and local_uuid:
                d = [reactor.callLater(0, lambda: get_client(g_name, '', type='fanout').cast(
                 dict(shell_command=ShellRequest('{0}.heartcond'.format(target_name), 
                                                 'register', 
                 dict(group_name=local_name, 
                      uuid=local_uuid,
                      available=str(False),
                      group_type=local_type)).to_dict()))) for g_name, 
                 is_enabled in self._conf_group_names if is_enabled and g_name not in self.UNEXPECTED_OPTIONS]

    def heartbeat(self, target_name):
        # Check if has call heartbeat event-loop, don't call it again.
        if self.is_start:
            return True
        self.is_start = True
        local_name = self._conf_group_name
        local_type = self._conf_group_type
        local_uuid = self._conf_group_uuid
        if local_name and local_type and local_uuid:
            d = [task.LoopingCall(lambda: get_client(g_name, '', type='fanout').cast(
                 dict(shell_command=ShellRequest('{0}.heartcond'.format(target_name), 
                                                 'register', 
                 dict(group_name=local_name, 
                      uuid=local_uuid,
                      available=str(True),
                      group_type=local_type)).to_dict()))) for g_name, 
                 is_enabled in self._conf_group_names if is_enabled and g_name not in self.UNEXPECTED_OPTIONS]
            return d


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'has', 'register'
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heartcond',
             'public': ['has', 'mod:heartcondition:has_heartbeat'],
             'public': ['register', 'mod:heartcondition:register'],
            }
    ]

    @property
    @from_config_option('heartrate', 60, sect='controller:heartbeat:listen')
    def _conf_heartrate(self):
        return SERVER_CONF

    def start(self, config=None):
        # Re-initialize sql table
        configure_heartcondition()
        self.buf_available_uuid = CONF_BACKEND.uuids()

    def _check_heart_alive(self, group_name, group_type, uuid):
        if (not (hasattr(self, 'buf_group_name') and hasattr(self, 'buf_group_type'))) \
            or (not (self.buf_group_name.get(group_name, None) and self.buf_group_type.get(group_type, None))) \
            or (not hasattr(self, '_timestamp')) \
            or (uuid not in self._timestamp):
            return False
        heartrate = self._conf_heartrate
        cur_time = time.time()
        if int(cur_time - self._timestamp[uuid]) > int(heartrate):
            # Maybe heartbeat is lost?
            d = dict(group_name=group_name,
                     group_type=group_type,
                     uuid=uuid,
                     available=str(False))
            BACKEND.update(d)
            return False
        return True

    def _check_heart_health(self, group_name, group_type, uuid):
        heartrate = self._conf_heartrate
        if not hasattr(self, '_timestamp'):
            setattr(self, '_timestamp', {})
        if uuid not in self._timestamp:
            self._timestamp[uuid] = time.time()
            return True
        else:
            cur_time = time.time()
            if int(cur_time - self._timestamp[uuid]) >= (int(heartrate) - 1):
                return cur_time
        raise HeartBeatTimeoutErr(group_name, group_type)

    def register(self, context, heartrate=60):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        uuid = context.get('uuid', None)
        available = context.get('available', None) or False
        if group_name and group_type and uuid:
            try:
                cur_time = self._check_heart_health(group_name, group_type, uuid)
                if uuid not in self.buf_available_uuid:
                    #Heartbeat is not in enabled range.
                    return 
                self._timestamp[uuid] = cur_time
            except HeartBeatTimeoutErr:
                return 
            except:
                return 
            d = dict(group_name=group_name,
                     group_type=group_type,
                     uuid=uuid,
                     available=str(available))
            BACKEND.update(d)
            if not (hasattr(self, 'buf_group_name') and hasattr(self, 'buf_group_type')):
                setattr(self, 'buf_group_name', {})
                setattr(self, 'buf_group_type', {})
            if BACKEND.has(group_name, group_type):
                self.buf_group_name[group_name] = True
                self.buf_group_type[group_type] = True

    def has_heartbeat(self, context):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        uuid = context.get('uuid', None)
        if not (group_name and group_type and uuid) \
            or not self._check_heart_alive(group_name, group_type, uuid):
            return False
        return True


def if_available(group_name, group_type):
    def _if_available(func):
        def __if_available(*args, **kwargs):
            m = get_model('heartcondition')
            if m and True in map(lambda uuid: m.has_heartbeat(dict(group_name=group_name, 
                                                                   group_type=group_type, 
                                                                   uuid=uuid)), 
                                 m.buf_available_uuid):
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
    @from_config(sect='controller:heartbeat:listen')
    def get_heartbeat_members():
        return SERVER_CONF
    for uuid, is_enabled in get_heartbeat_members():
        if str(is_enabled) == 'True' and uuid not in HeartCondition().UNEXPECTED_OPTIONS:
            CONF_BACKEND.update(dict(uuid=uuid))
