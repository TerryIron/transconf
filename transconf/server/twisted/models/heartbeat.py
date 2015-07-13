__author__ = 'chijun'

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.backend.heartbeat import HeartBeatBackend, HeartBeatIsEnabledBackend
from transconf.server.twisted.internet import SQL_ENGINE
from transconf.server.twisted.internet import CONF as global_conf

CONF = global_conf

sql_engine = SQL_ENGINE

BACKEND = HeartBeatBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type))


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    FORM = [{'node': 'heart',
             'public': ['push', 'mod:heartbeat:heartbeat'],
            }
    ]

    def start(self):
        self.heart_is_start = True

    def stop(self):
        self.heart_is_start = False

    def heartbeat(self, eventer, timeout=60):
        raise NotImplementedError()


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    FORM = [{'node': 'heartcond',
             'public': ['has', 'mod:heartcondition:heartbeats'],
             'public': ['register', 'mod:heartcondition:register'],
            }
    ]

    def start(self):
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
            m = get_model(heartcondition):
            if m and m.heartbeats(group_name, group_type):
                return func(*args, **kwargs)
            else:
                raise HeartBeatNotFound(group_name, group_type)
        return __if_available
    return _if_available


def configuare_heartbeat():
    pass


def configuare_heartcondition():
    global CONF_BACKEND
    CONF_BACKEND.drop()
    CONF_BACKEND.create()
    global CONF
    @from_config(sect='controller:heartbeat:listen')
    def get_heartbeat_members(conf)
        return conf
    for uuid, is_enabled in get_heartbeat_members(CONF):
        if is_enabled:
            d = dict(group_uuid=uuid)
            CONF_BACKEND.update(**d)
    global BACKEND
    BACKEND.drop()
    BACKEND.create()
