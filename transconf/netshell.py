__author__ = 'chijun'

from shell import ModelShell
from models.heartbeat import HeartBeat, HeartCondition


class CenterShell(ModelShell):
    def __init__(self, host):
        super(NetShell, self).__init__(self)
        self.load_model('__heartbeat__', HeartCondition)


class NetShell(ModelShell):
    def __init__(self, host):
        super(NetShell, self).__init__(self)
        self.load_model('__heartbeat__', HeartBeat)
        self.run('__heartbeat__.heart', 'heartbeat', host)
