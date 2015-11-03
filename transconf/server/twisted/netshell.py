__author__ = 'chijun'

import time
import functools

from twisted.internet import defer

from transconf.shell import ModelShell, ShellTargetNotFound
from transconf.model import Model
from transconf.server.twisted.service import Middleware
from transconf.server.request import Request, RequestTimeout, InvalidRequest
from transconf.server.response import Response
from transconf.utils import SimpleModel
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)

class BadShellRequest(Exception):
    """Raised when request comming with invalid data """


class ShellRequest(Request):
    def __init__(self, target_name, method_name, *args, **kwargs):
        d = dict(target_name=target_name,
                 method_name=method_name,
                 args=args,
                 kwargs=kwargs)
        return super(ShellRequest, self).__init__(**d)

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}
        context['shell_env'] = dict(
            timestamp=time.time(),
            timeout=timeout,
        )
        context['shell_command'] = dict(
            target_name=self['target_name'],
            method_name=self['method_name'],
            args=self['args'],
            kwargs=self['kwargs'],
        )
        return context


class ActionRequest(ShellRequest):
    def __init__(self, target, *args, **kwargs):
        if not isinstance(target, SimpleModel):
            print target
            target = SimpleModel(target)
        LOG.debug('Action req, target:{0}, action:{1}, args:{2}, kwargs:{3}'.format(target.target,
                                                                                    target.action,
                                                                                    args,
                                                                                    kwargs))
        return super(ActionRequest, self).__init__(target.target,
                                                   target.action,
                                                   *args,
                                                   **kwargs)


class ShellMiddleware(Middleware):
    def process_request(self, context):
        shell_req = context.get('shell_command', None)
        if shell_req:
            target_name = shell_req.get('target_name', None)
            method_name = shell_req.get('method_name', None)
            if target_name and method_name:
                def check_is_timeout(context):
                    shell_env = context.get('shell_env', None)
                    if not shell_env:
                        raise InvalidRequest('Invalid request for {0}.{1}.'.format(target_name, method_name))
                    else:
                        timestamp = shell_env.get('timestamp', None)
                        timeout = shell_env.get('timeout', None)
                        if not (timestamp and timeout):
                            raise InvalidRequest('Invalid request for {0}.{1}.'.format(target_name, method_name))
                    cost_time = float(time.time()) - float(timestamp)
                    LOG.debug('Get request [{0}.{1}] costs time {2} (s).'.format(target_name, method_name, cost_time))
                    if cost_time > float(timeout):
                        raise RequestTimeout('Call {0}.{1} timeout.'.format(target_name, method_name))
                try:
                    check_is_timeout(context)
                    args = shell_req.get('args', None)
                    kwargs = shell_req.get('kwargs', None)
                    cb = functools.partial(self.handler.run, 
                                           target_name, 
                                           method_name, *args, **kwargs)
                    return cb()
                except Exception as e:
                    def err_back(err):
                        return Response.fail(err)
                    d = defer.fail({})
                    d.addErrback(lambda result: err_back(e))
                    return d
            else:
                raise BadShellRequest()


class NetShell(ModelShell):
    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:])
                d = defer.succeed({})
                cb = functools.partial(model.run, other_names, method_name, *args, **kwargs)
                d.addCallback(lambda r: cb())
                return d
        else:
            raise ShellTargetNotFound(target_name)
