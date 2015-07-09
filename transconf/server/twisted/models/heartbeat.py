__author__ = 'chijun'

from transconf.common.reg import register_model                                                                                                                                                                     
from transconf.model import Model
from transconf.backend.heartbeat import HeartBeatBackend
from transconf.server.twisted.internet import SQL_ENGINE

BACKEND = HeartBeatBackend(SQL_ENGINE)

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
             'public': ['has', 'mod:heartbeat:heartbeats'],
             'public': ['register', 'mod:heartbeat:register'],
             'public': ['unregister', 'mod:heartbeat:unregister'],
            }
    ]

    def init(self):
        BACKEND.create()

    def register(self, context):
        raise NotImplementedError()

    def unregister(self, context):
        raise NotImplementedError()

    def heartbeats(self, group_name, group_type):
        return BACKEND.has(group_name, group_type)


def if_has_heartbeat(group_name, group_type):
    pass
