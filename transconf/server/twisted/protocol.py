__author__ = 'chijun'

import logging

import pika
from twisted.internet.protocol import ServerFactory, ClientFactory
from pika.adapters import twisted_connection

from ..request import MessageResponse


_Logger = logging.getLogger(__name__)

class MessageProtocol(twisted_connection.TwistedProtocolConnection):
    _id = 0

    def __init__(self, parameters=pika.ConnectionParameters(host='localhost', port=5672)):
        super(MessageProtocol, self).__init__(parameters)
        self._recv = ''
        self._id = MessageProtocol._id
        MessageProtocol._id += 1

    def dataReceived(self, data):
        super(MessageProtocol, self).dataReceived(data)
        print 'Get new message: {0}'.format(data)
        self._recv += data
        print 'Recv message: {0}'.format(self._recv)
        #_Logger.info('Get new message: {0}'.format(data))
        #self.request_received(data)

    def request_received(self, request_info):
        defer = self.factory.process_request(request_info)
        defer.addCallbacks(self.success_result, self.error_result)
        defer.addBoth(lambda r: self.transport.loseConnection())

    def success_result(self, result):
        r = MessageResponse.success(result)
        _Logger.info('[{0}]success: {1}'.format(self._id, r))
        self.transport.write(r)

    def error_result(self, err):
        r = MessageResponse.fail('<{0}> {1}'.format(err.type.__name__, err.value))
        _Logger.error('[{0}]fail: {1}'.format(self._id, r))
        self.transport.write(r)


class MessageShell(object):
    def __init__(self, shell):
        assert callable(getattr(shell, 'run', None))
        self._shell = shell

    def process_request(self, request):
        isinstance(request, dict)
        from twisted.internet.defer import succeed
        return succeed({})


class MessageFactory(ServerFactory):
    protocol = MessageProtocol

    def __init__(self, shell):
        assert isinstance(shell, MessageShell)
        self._shell = shell

    def process_request(self, request):
        return self._shell.process_request(request)

