__author__ = 'chijun'

from common.reg import register_model                                                                                                                                                                     
from model import Model


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(object):
    FORM = [{'node': 'heart',
             'public': ['heartbeat', 'mod:heartbeat:heartbeat'],
            }
    ]

    def heartbeat(self, host, timeout=60):
        raise NotImplementedError()


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(object):
    FORM = [{'node': 'heartcond',
             'public': ['heartbeats', 'mod:heartbeat:heartbeats'],
             'public': ['register_heart', 'mod:heartbeat:register'],
             'public': ['unregister_heart', 'mod:heartbeat:unregister'],
            }
    ]

    def register(self, context):
        raise NotImplementedError()

    def unregister(self, context):
        raise NotImplementedError()

    def heartbeats(self):
        raise NotImplementedError()
