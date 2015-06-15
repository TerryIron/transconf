__author__ = 'chijun'

from common.reg import register_model                                                                                                                                                                     
from model import Model

@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(object):

    def heartbeat(self, host, timeout=60):
        raise NotImplementedError()

@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(object):

    def register(self, context):
        raise NotImplementedError()
