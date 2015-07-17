__author__ = 'chijun'

import time
import functools
from twisted.internet import task, reactor

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend
from transconf.server.twisted.internet import get_client
from transconf.server.twisted import CONF as global_conf
from transconf.server.twisted import get_sql_engine 
from transconf.server.utils import from_config, from_config_option, from_model_option, as_config
from transconf.server.twisted.netshell import ShellRequest

SERVER_CONF = global_conf

sql_engine = get_sql_engine()

BACKEND = HeartBeatCollectionBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type)


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    UNEXPECTED_OPTIONS = ['timeout']
    FORM = [{'node': 'heart',
             'public': ['beat', 'mod:heartbeat:heartbeat'],
             'public': ['dead', 'mod:heartbeat:stop'],
            }
    ]

    @from_model_option('name', None, sect='heartcondition')
    def _conf_target_name(self, config):
        return config

    @from_config(sect='controller:heartbeat:fanout')
    def _conf_group_names(self):
        return SERVER_CONF

    @from_config_option('local_group_name', None)
    def _conf_group_name(self):
        return SERVER_CONF

    @from_config_option('local_group_type', None)
    def _conf_group_type(self):
        return SERVER_CONF

    @from_config_option('local_group_uuid', None)
    def _conf_group_uuid(self):
        return SERVER_CONF

    def start(self, config=None):
        self.is_start = None
        name = self._conf_target_name(config)
        if name:
            self.heart = self.heartbeat(name)
            @from_config_option('timeout', 60, sect='controller:heartbeat:fanout')
            def get_timeout():
                return SERVER_CONF
            if self.heart:
                timeout = float(get_timeout())
                for h in self.heart:
                    h.start(timeout)

    def stop(self, config=None):
        if self.heart:
            for h in self.heart:
                h.stop()
        if self.is_start:
            self.is_start = False
        name = self._get_target_name(config)
        if name:
            local_name = self._conf_group_name()
            local_type = self._conf_group_type()
            local_uuid = self._conf_group_uuid()
            if local_name and local_type and local_uuid:
                d = [reactor.callLater(0, lambda: get_client(g_name, '', type='fanout').cast(
                 dict(shell_command=ShellRequest('{0}.heartcond'.format(target_name), 
                                                 'register', 
                 dict(group_name=local_name, 
                      uuid=local_uuid,
                      available=str(False),
                      group_type=local_type)).to_dict()))) for g_name, 
                 is_enabled in self._conf_group_names() if is_enabled and g_name not in self.UNEXPECTED_OPTIONS]
            

    def heartbeat(self, target_name):
        if self.is_start:
            return True
        self.is_start = True
        local_name = self._conf_group_name()
        local_type = self._conf_group_type()
        local_uuid = self._conf_group_uuid()
        if local_name and local_type and local_uuid:
            d = [task.LoopingCall(lambda: get_client(g_name, '', type='fanout').cast(
                 dict(shell_command=ShellRequest('{0}.heartcond'.format(target_name), 
                                                 'register', 
                 dict(group_name=local_name, 
                      uuid=local_uuid,
                      available=str(True),
                      group_type=local_type)).to_dict()))) for g_name, 
                 is_enabled in self._conf_group_names() if is_enabled and g_name not in self.UNEXPECTED_OPTIONS]
            return d


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    UNEXPECTED_OPTIONS = ['timeout']
    FORM = [{'node': 'heartcond',
             'public': ['has', 'mod:heartcondition:heartbeats'],
             'public': ['register', 'mod:heartcondition:register'],
            }
    ]

    def start(self, config=None):
        # Re-initialize sql table
        configure_heartcondition()

    def _check_heart_health(self):
        @from_config_option('timeout', 60, sect='controller:heartbeat:listen')
        def get_timeout():
            return SERVER_CONF
        timeout = get_timeout()
        if not hasattr(self, '_timestamp'):
            setattr(self, '_timestamp', time.time())
            return True
        else:
            cur_time = time.time()
            if int(cur_time - self._timestamp) >= int(timeout):
                self._timestamp = cur_time
                return True
        return False

    def register(self, context, timeout=60):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        uuid = context.get('uuid', None)
        available = context.get('available', None) or False
        if uuid and CONF_BACKEND.has(uuid):
            if not self._check_heart_health():
                return
        if group_name and group_type:
            d = dict(group_name=group_name,
                     group_type=group_type,
                     uuid=uuid,
                     available=str(available))
            BACKEND.update(d)

    def heartbeats(self, context):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        if group_name and group_type:
            return BACKEND.has(group_name, group_type)
        return False


def if_available(group_name, group_type):
    def _if_available(func):
        def __if_available(*args, **kwargs):
            m = get_model(heartcondition)
            if m and m.heartbeats(group_name, group_type):
                return func(*args, **kwargs)
            else:
                raise HeartBeatNotFound(group_name, group_type)
        return __if_available
    return _if_available


def configure_heartcondition():
    BACKEND.create()
    BACKEND.clear()
    CONF_BACKEND.create()
    CONF_BACKEND.clear()
    @from_config(sect='controller:heartbeat:listen')
    def get_heartbeat_members():
        return SERVER_CONF
    for uuid, is_enabled in get_heartbeat_members():
        if str(is_enabled) == 'True' and uuid not in HeartCondition().UNEXPECTED_OPTIONS:
            d = dict(uuid=uuid)
            CONF_BACKEND.update(d)
