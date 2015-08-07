__author__ = 'chijun'

import functools
import twisted
from twisted.internet import task

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
    def __init__(self, cleint, shell_request, callback_request=None, errback_request=None, timeout=60):
        d = dict(timeout=timeout,
                 client=client,
                 shell_request=shell_request,
                 callback_request=callback_request,
                 errback_request=errback_request)
        return super(EventRequest, self).__init__(**d)       

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}
        self.shell_request.to_dict(context)
        if 'eventloop' not in context:
            context['eventloop'] = []
        d = {}
        if self['callback_request']:
            d['if_success'] = self['callback_request'].to_dict()
        if self['errback_request']:
            d['if_failed'] = self['errback_request'].to_dict()
        if len(d) > 0:
            d['timeout'] = self['timeout']
            d['client'] = dict(self['client'].__simple__)
            context['eventloop'].append(d)
        return context


class EventQueueRequest(Request):
    def to_dict(self, event_requests, context=None):
        pass


class EventQueueDispatcher(object):
    def __init__(self):
        self.queue = []

    def addNext(self, client, shell_request, callback_request=None, errback_request=None, timeout=60)
        self.queue.append(EventDispatcher(client, shell_request, callback_request, errback_request, timeout))

    def start(self):
        if self.pool:
            cur = self.queue.pop()
            cur_request = cur.request
            cur.request = EventQueueRequest(self.queue)
            cur.send()


class EventDispatcher(object):
    def __init__(self, client, shell_request, callback_request=None, errback_request=None, timeout=60, delivery_mode=1):
        self.client = client
        self.delivery_mode = delivery_mode
        self.request = EventRequest(client, shell_request, callback_request, errback_request, timeout)

    def send(self):
        self.client.cast(self.request, delivery_mode=self.delivery_mode)
    

class EventMiddleware(ShellMiddleware):
    def process_request(self, context)
        if 'eventloop' in context:
            eventloop = context.pop('eventloop')
            def callback_if_success():
                pass
            def callback_if_failed():
                pass
            try:
                defer = super(EventMiddleware, self).process_request(context)
                callback_if_success()
                return defer
            except e as Exception:
                callback_if_failed()
                raise e
        else:
            defer = super(EventMiddleware, self).process_request(context)
            return defer
