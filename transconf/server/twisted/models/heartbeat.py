__author__ = 'chijun'

from twisted.internet import tast

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.backend.heartbeat import HeartBeatBackend, HeartBeatIsEnabledBackend
from transconf.server.twisted.internet import SQL_ENGINE, get_client
from transconf.server.twisted.internet import CONF as global_conf
from transconf.server.utils import from_config, from_config_option, as_config
from transconf.server.twisted.netshell import ShellRequest

SERVER_CONF = global_conf

sql_engine = SQL_ENGINE

BACKEND = HeartBeatBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type)


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    FORM = [{'node': 'heart',
             'public': ['beat', 'mod:heartbeat:heartbeat'],
             'public': ['dead', 'mod:heartbeat:stop'],
            }
    ]

    def start(self, config=None):
        global SERVER_CONF
        @from_model_option('name', None, sect='heartcondition')
        def get_target_name(conf):
            return conf
        name = get_target_name(config)
        if name:
            self.heart = self.heartbeat(name)
            @from_config_option('timeout', 60, sect='controller:heartbeat:fanout')
            def get_timeout(conf):
                return conf
            if self.heart:
                timeout = float(get_timeout(SERVER_CONF))
                for h in self.heart:
                    h.start(timeout)

    def stop(self, config=None):
        if self.is_start and self.heart:
            for h in self.heart:
                h.stop()
            self.is_start = False

    def heartbeat(self, target_name):
        global SERVER_CONF
        if self.is_start:
            return True
        self.is_start = True
        @from_config(sect='controller:heartbeat:fanout')
        def get_group_names(conf):
            return conf
        @from_config_option('local_group_name', None)
        def local_group_name(conf):
            return conf
        @from_config_option('local_group_type', None)
        def local_group_type(conf):
            return conf
        local_name = local_group_name(SERVER_CONF)
        local_type = local_group_type(SERVER_CONF)
        if local_name and local_type:
            d = [task.LoopingCall(get_client(g_name, '', type='fanout').cast(
                 dict(shell_command=ShellRequest('{0}.heartcond'.format(target_name), 
                                                 'register', 
                 dict(group_name=local_name, group_type=local_type))))) for g_name, is_enabled in get_group_names(SERVER_CONF) if is_enabled]
            return d


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    FORM = [{'node': 'heartcond',
             'public': ['has', 'mod:heartcondition:heartbeats'],
             'public': ['register', 'mod:heartcondition:register'],
            }
    ]

    def start(self, config=None):
        # Re-initialize sql table
        configuare_heartbeats()

    def register(self, context):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        uuid = context.get('group_uuid', None)
        available = context.get('available', None) or False
        if group_name and group_type and uuid:
            d = dict(group_name=group_name,
                     group_type=group_type,
                     uuid=uuid,
                     available=available)
            BACKEND.update(**d)

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


def configuare_heartcondition():
    global CONF_BACKEND
    CONF_BACKEND.drop()
    CONF_BACKEND.create()
    global SERVER_CONF
    @from_config(sect='controller:heartbeat:listen')
    def get_heartbeat_members(conf):
        return conf
    for uuid, is_enabled in get_heartbeat_members(SERVER_CONF):
        if is_enabled:
            d = dict(group_uuid=uuid)
            CONF_BACKEND.update(**d)
    global BACKEND
    BACKEND.drop()
    BACKEND.create()
