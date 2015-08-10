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
    def __init__(self, client, shell_request, callback_request=None, callback_client=None, 
                 errback_request=None, errback_client=None, timeout=60):
        d = dict(timeout=timeout,
                 cli=client,
                 shell_cli=shell_client,
                 cb_rq=callback_request,
                 cb_cli=callback_cient,
                 eb_rq=errback_request,
                 eb_cli=errback_client)
        return super(EventRequest, self).__init__(**d)       

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}
        # Call ShellReqeust's to_dict()
        self['shell_rq'].to_dict(context)
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
            d['cli'] = dict(self['cli'].__simple__)
            context['eventloop'].append(d)
        return context


class EventDispatcher(object):
    def __init__(self, client, shell_request, callback_request=None, callback_client=None, 
                 errback_request=None, errback_client=None, timeout=60, delivery_mode=1):
        self.client = client
        self.delivery_mode = delivery_mode
        self.request = EventRequest(self.client, 
                                    shell_request, 
                                    callback_request, 
                                    callback_client, 
                                    errback_request, 
                                    errback_client, 
                                    timeout)

    def start(self):
        self.client.cast(self.request, delivery_mode=self.delivery_mode)

    def send(self):
        return self.client.call(self.request, delivery_mode=self.delivery_mode)
    

class EventsRequest(Request):
    def __init__(self, event_requests):
        d = dict(requests=event_requests)
        return super(EventsRequest, self).__init__(**d)       

    def to_dict(self, context=None):
        for event_rq in self['requests']:
            context = event_rq.to_dict(context)
        return context


class EventDeferDispatcher(object):
    def __init__(self, client, delivery_mode=1):
        self.queue = []
        self.client = client
        self.delivery_mode=delivery_mode

    def addNext(self, client, shell_request, callback_request=None, callback_client=None,
                errback_client=None, errback_request=None, timeout=60)
        self.queue.append(EventDispatcher(client, shell_request, callback_request, callback_client or self.client,
                                          errback_request, errback_client or self.client, timeout))

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
        return client
        
    def start(self):
        if self.queue:
            requests = EventsRequest(self.queue)
            client = EventDeferDispatcher.get_first_client(requests)
            if not client:
                return
            client.cast(requests, delivery_mode=self.delivery_mode)


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
    def process_request(self, context)
        if 'eventloop' in context:
            eventloop = context.pop('eventloop')
            if (isinstance(eventloop, list)) and \ 
               (len(eventloop) > 0):
                event_context = eventloop[0]
                def if_success():
                    cli = event_context.get('success_cli', None)
                    text = event_context.get('success', None)
                    if cli and text:
                        client = get_client(cli['group'], cli['type'],
                                            group_uuid=cli['uuid'],
                                            type=cli['cls'])
                        client.castBase(text)
                def if_failed():
                    cli = event_context.get('failed_cli', None)
                    text = event_context.get('failed', None)
                    if cli and text:
                        client = get_client(cli['group'], cli['type'],
                                            group_uuid=cli['uuid'],
                                            type=cli['cls'])
                        client.castBase(text)
                def if_next():
                    eventloop.pop(0)
                    if eventloop:
                        event_context = eventloop[0]
                        cli = event_context.get('cli', None)
                        if cli:
                            event_context['cli'] = None
                            client = get_client(cli['group'], cli['type'],
                                                group_uuid=cli['uuid'],
                                                type=cli['cls'])
                            client.castBase(text)
                try:
                    defer = super(EventMiddleware, self).process_request(context)
                    if_success()
                    return defer
                except e as Exception:
                    if_failed()
                    raise e
                finally:
                    if_next()
            else:
                defer = super(EventMiddleware, self).process_request(context)
                return defer
        else:
            defer = super(EventMiddleware, self).process_request(context)
            return defer
