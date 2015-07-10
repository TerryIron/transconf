__author__ = 'chijun'

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.backend.heartbeat import HeartBeatBackend
from transconf.server.twisted.internet import SQL_ENGINE, _get_conf_members

sql_engine = SQL_ENGINE

BACKEND = HeartBeatBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type))


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    FORM = [{'node': 'heart',
             'public': ['push', 'mod:heartbeat:heartbeat'],
            }
    ]

    def heartbeat(self, host, timeout=60):
        raise NotImplementedError()


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    FORM = [{'node': 'heartcond',
             'public': ['has', 'mod:heartcondition:heartbeats'],
             'public': ['register', 'mod:heartcondition:register'],
             'public': ['unregister', 'mod:heartcondition:unregister'],
            }
    ]

    def start(self):
        BACKEND.create()

    def stop(self):
        BACKEND.drop()

    def register(self, context):
        raise NotImplementedError()

    def unregister(self, context):
        raise NotImplementedError()

    def heartbeats(self, group_name, group_type):
        return BACKEND.has(group_name, group_type)


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
