# coding=utf-8

__author__ = 'chijun'

import time
import functools
from twisted.internet import task, reactor, defer

from transconf.server.twisted.internet import new_public_client
from transconf.server.twisted.netshell import ShellMiddleware
from transconf.server.request import Request, RequestTimeout, InvalidRequest
from transconf.server.twisted.log import getLogger
from transconf.utils import Exception

LOG = getLogger(__name__)


class Task(object):
    """
        Task Object

        @f: input function 
        @args: input args
        @kwargs: input kwargs
    """
    def __init__(self, f, *args, **kwargs):
        self.f = functools.partial(f, *args, **kwargs)

    def CallLater(self, seconds):
        reactor.callLater(seconds, self.f)

    def LoopingCall(self, seconds):
        d = task.LoopingCall(self.f)
        d.start(seconds)


class EventRequestTimeout(Exception):
    """ Raised when request comming out of time"""


class EventRequest(Request):
    """
        Event Request

        @client: local client target
        @shell_request: local request target
        @callback_request: request target for callback
        @callback_client: client target for callback
        @errback_request: request target for errback
        @errback_client: client target for errback
        @timeout: timeout
    """
    def __init__(self, client, shell_request, callback_request=None, callback_client=None, 
                 errback_request=None, errback_client=None, timeout=60):
        d = dict(timeout=timeout,
                 cli=client,
                 shell_rq=shell_request,
                 cb_rq=callback_request,
                 cb_cli=callback_client,
                 eb_rq=errback_request,
                 eb_cli=errback_client)
        super(EventRequest, self).__init__(**d)

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}
        # Call ShellReqeust's to_dict()
        context = self['shell_rq'].to_dict(context)
        if 'eventloop' not in context:
            context['eventloop'] = []
        d = {}
        if self['cb_rq'] and self['cb_cli']:
            d['success'] = self['cb_rq'].to_dict()
            d['success_cli'] = dict(self['cb_cli'].__simple__)
        if self['eb_rq'] and self['eb_cli']:
            d['failed'] = self['eb_rq'].to_dict()
            d['failed_cli'] = dict(self['eb_cli'].__simple__)
        if len(d) > 0:
            d['timeout'] = self['timeout']
            # TODO by chijun
            # use MQ timestamp as better
            d['timestamp'] = time.time()
            context['eventloop'].append(d)
        return context


class EventDispatcher(object):
    """
        Event Dispatcher

        @client: local client target
        @request: local request target
        @callback_request: request target for callback
        @callback_client: client target for callback
        @errback_request: request target for errback
        @errback_client: client target for errback
        @timeout: timeout
        @delivery_mode: 2 to set queue message been persistence, 
                        1 to set queue message been short-lived.
        @need_result: if True return result defer
        @need_close: if True close client after sending message(Only for Method Cast)
    """
    def __init__(self, client, request, callback_request=None, callback_client=None, 
                 errback_request=None, errback_client=None, timeout=60, delivery_mode=2, 
                 need_result=True, need_close=True):
        self.client = client
        self.need_close = need_close
        self.need_result = need_result
        self.delivery_mode = delivery_mode
        self.request = EventRequest(self.client, 
                                    request, 
                                    callback_request, 
                                    callback_client, 
                                    errback_request, 
                                    errback_client, 
                                    timeout)

    def startWithoutResult(self):
        self.client.cast(self.request, delivery_mode=self.delivery_mode)
        if self.need_close:
            self.client.close()

    def startWithResult(self):
        return self.client.call(self.request, delivery_mode=self.delivery_mode)

    def start(self):
        if self.need_result: 
            return self.startWithResult()
        else:
            self.startWithoutResult()
    

class EventDeferDispatcher(object):
    # Make sure that client is one of pointed sub-services not a worker.
    """
        Event Dispatcher Defer Queue

        @delivery_mode: 2 to set queue message been persistence, 
                        1 to set queue message been short-lived.
    """
    def __init__(self, delivery_mode=2):
        self.queue = []
        self.delivery_mode=delivery_mode

    """
        Add a new event dispatcher inited by input arguments

        @client: local client target
        @request: local request target
        @callback_request: request target for callback
        @callback_client: client target for callback
        @errback_request: request target for errback
        @errback_client: client target for errback
        @timeout: timeout
        @delivery_mode: 2 to set queue message been persistence, 
                        1 to set queue message been short-lived.
        @need_result: if True return result defer
        @need_close: if True close client after sending message(Only for Method Cast)
    """
    def addNextReq(self, client, shell_request, callback_request=None, callback_client=None,
                   errback_client=None, errback_request=None, timeout=60, need_result=True, need_close=True):
        self.queue.append(EventDispatcher(client, shell_request, callback_request, callback_client or self.client,
                                          errback_request, errback_client or self.client, 
                                          timeout, self.delivery_mode, need_result))

    """
        Add a new event dispatcher
    """
    def addNext(self, dispatcher):
        assert isinstance(dispatcher, EventDispatcher)
        self.queue.append(dispatcher)

    def start(self):
        d = defer.Deferred({})
        for disp in self.queue:
            d.addBoth(lambda: disp.start())
        return d


"""
            context
    ------------------    -----------------------
    | shell_env      | -> | timestamp | timeout |
    ------------------    -----------------------
    ------------------    ---------------------------------------------
    | shell_command  | -> | target_name | method_name | args | kwargs |
    ------------------    ---------------------------------------------
    ------------------    ---------------------------------------------------------------
    | event_request  | -> | success | success_cli | failed | failed_cli | timeout | cli | 
    ------------------    ---------------------------------------------------------------
    ------------------    --------------------------------  
    | eventloop      | -> | EVENT_REQ1 | EVENT_REQ2 |       
    ------------------    -------------------------------- 
"""


class EventMiddleware(ShellMiddleware):
    """
        Process Event Request
    """
    def process_request(self, context):
        defer = super(EventMiddleware, self).process_request(context)
        if 'eventloop' in context:
            eventloop = context.pop('eventloop')
            if (isinstance(eventloop, list)) and (len(eventloop) > 0):
                event_context = eventloop[0]
                timeout = event_context.get('timeout', None)
                timestamp = event_context.get('timestamp', None)
                if not (timestamp and timeout):
                    raise InvalidRequest('Invalid request for {0}.'.format(eventloop))
                cost_time = float(time.time()) - float(timestamp)
                if cost_time > float(timeout):
                    raise RequestTimeout('Call {0} timeout.'.format(eventloop))

                def call(cli, text, ret):
                    client = new_public_client(cli['group'], cli['type'],
                                               group_uuid=cli['uuid'],
                                               type=cli['cls'])
                    text['result'] = ret
                    client.callBase(text)
                    client.close()

                def if_success(ret):
                    cli = event_context.get('success_cli', None)
                    text = event_context.get('success', None)
                    if cli and text:
                        return call(cli, text, ret)

                def if_failed(ret):
                    cli = event_context.get('failed_cli', None)
                    text = event_context.get('failed', None)
                    if cli and text:
                        return call(cli, text, ret)
                defer.addCallbacks(lambda ret: if_success(ret),  
                                   errback=lambda ret: if_failed(ret))
        return defer
