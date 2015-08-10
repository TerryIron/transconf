__author__ = 'chijun'

import pickle
import functools
import twisted
from twisted.internet import task

from transconf.server.twisted.internet import get_client
from transconf.server.twisted.netshell import ShellMiddleware
from transconf.server.request import Request, Response, RequestTimeout, InvalidRequest


class Task(object):
    def __init__(self, f, *args, **kwargs):
        self.f = functools.partial(f, *args, **kwargs)

    def CallLater(self, seconds):
        reactor.callLater(self.seconds, self.f())

    def LoopingCall(self, seconds):
        d = task.LoopingCall(self.f())
        d.start(seconds)


class EventRequest(Request):
    def __init__(self, client, shell_request, is_cast=False, callback_request=None, errback_request=None, timeout=60):
        d = dict(timeout=timeout,
                 cli=client,
                 cli_is_cast=is_cast,
                 shell_rq=shell_request,
                 cb_rq=callback_request,
                 eb_rq=errback_request)
        return super(EventRequest, self).__init__(**d)       

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}
        # Call ShellReqeust's to_dict()
        self['shell_rq'].to_dict(context)
        if 'eventloop' not in context:
            context['eventloop'] = []
        d = {}
        if self['cb_rq']:
            d['success'] = self['cb_rq'].to_dict()
        if self['errback_request']:
            d['failed'] = self['eb_rq'].to_dict()
        if len(d) > 0:
            d['timeout'] = self['timeout']
            d['cli'] = dict(self['cli'].__simple__)
            d['cli_is_cast'] = dict(self['cli'].__simple__)
            context['eventloop'].append(d)
        return context


class EventDispatcher(object):
    def __init__(self, client, shell_request, is_cast=False, callback_request=None, errback_request=None, timeout=60, delivery_mode=1):
        self.client = client
        self.is_cast = is_cast
        self.delivery_mode = delivery_mode
        self.request = EventRequest(self.client, 
                                    shell_request, 
                                    self.is_cast, 
                                    callback_request, 
                                    errback_request, 
                                    timeout)

    def start(self):
        if not self.is_cast:
            return self.client.call(self.request, delivery_mode=self.delivery_mode)
        else:
            self.client.cast(self.request, delivery_mode=self.delivery_mode)
    

class EventsRequest(Request):
    def __init__(self, event_requests):
        d = dict(requests=event_requests)
        return super(EventsRequest, self).__init__(**d)       

    def to_dict(self, context=None):
        for event_rq in self['requests']:
            context = event_rq.to_dict(context)
        return context


class EventDeferDispatcher(object):
    def __init__(self, delivery_mode=1):
        self.queue = []
        self.delivery_mode=delivery_mode

    def addNext(self, client, shell_request, callback_request=None, errback_request=None, timeout=60)
        self.queue.append(EventDispatcher(client, shell_request, callback_request, errback_request, timeout))

    @staticmethod
    def get_first_client(requests):
        if (not isinstance(requests['requests'], list)) or \ 
           (len(requests['requests']) <= 0):
            return
        part = requests['requests'][0]
        if not isinstance(part, EventRequest):
            return
        cli = part['cli']
        client = get_client(cli['group'], cli['type'],
                            group_uuid=cli['uuid'],
                            type=cli['cls'])
        part['cli'] = None
        is_cast = bool(part['cli_is_cast'])
        part['cli_is_cast'] = None
        return client, is_cast
        
    def start(self):
        if self.queue:
            requests = EventsRequest(self.queue)
            client, is_cast = EventDeferDispatcher.get_first_client(requests)
            if not client:
                return
            if not is_cast:
                return client.call(requests, delivery_mode=self.delivery_mode)
            else:
                client.cast(requests, delivery_mode=self.delivery_mode)


"""
            context
    ------------------    ----------------------
    | shell_env      | -> | timestamp | timeout|
    ------------------    ----------------------
    ------------------    ---------------------------------------------
    | shell_command  | -> | target_name | method_name | args | kwargs |
    ------------------    ---------------------------------------------
    ------------------    --------------------------------------------------
    | event_request  | -> | success | failed | timeout | cli | cli_is_cast |
    ------------------    --------------------------------------------------
    ------------------    --------------------------------      ------------------------------   -------------------------------------------------------
    | eventloop      | -> | EVENT_REQ1 | EVENT_REQ2 |        -> | success | failed | timeout | + | success | failed | timeout | cli | cli_is_cast |
    ------------------    --------------------------------      ------------------------------   -------------------------------------------------------
"""

class EventMiddleware(ShellMiddleware):
    def process_request(self, context)
        if 'eventloop' in context:
            eventloop = context.pop('eventloop')
            def if_success():
                pass
            def if_failed():
                pass
            try:
                defer = super(EventMiddleware, self).process_request(context)
                if_success()
                return defer
            except e as Exception:
                if_failed()
                raise e
        else:
            defer = super(EventMiddleware, self).process_request(context)
            return defer
