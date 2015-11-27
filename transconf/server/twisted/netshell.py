#coding=utf-8

__author__ = 'chijun'

import functools

from twisted.internet import defer

from transconf.shell import ModelShell
from transconf.server.twisted.service import Middleware
from transconf.server.request import Request
from transconf.utils import SimpleModel
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class BadShellRequest(Exception):
    """Raised when request comming with invalid data """


class ShellRequest(Request):

    def __init__(self, target_name, method_name, version, *args, **kwargs):
        d = dict(target_name=target_name,
                 method_name=method_name,
                 version=version,
                 args=args,
                 kwargs=kwargs)
        super(ShellRequest, self).__init__(**d)

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}

        context['shell_command'] = dict(
            target_name=self['target_name'],
            method_name=self['method_name'],
            version=self['version'],
            args=self['args'],
            kwargs=self['kwargs'],
        )
        return context


class ActionRequest(ShellRequest):
    __version__ = (0, 1, 0)

    def __init__(self, target, *args, **kwargs):
        if not isinstance(target, SimpleModel):
            target = SimpleModel(target)
        LOG.debug('Action req, target:{0}, action:{1}, args:{2}, kwargs:{3}'.format(target.target,
                                                                                    target.action,
                                                                                    args,
                                                                                    kwargs))
        super(ActionRequest, self).__init__(target.target,
                                            target.action,
                                            target.version,
                                            *args,
                                            **kwargs)

    def to_dict(self, context=None, timeout=60):
        context = super(ActionRequest, self).to_dict(context, timeout)
        context['ver'] = 'v' + str(int(''.join([str(i) for i in self.__version__ if i != 0])))
        return context


class ShellMiddleware(Middleware):
    def process_request(self, context):
        shell_req = context.get('shell_command', None)
        if shell_req:
            target_name = shell_req.get('target_name', None)
            method_name = shell_req.get('method_name', None)
            if target_name and method_name:
                args = shell_req.get('args', None)
                kwargs = shell_req.get('kwargs', None)
                cb = functools.partial(self.handler.run,
                                       target_name, 
                                       method_name, *args, **kwargs)
                return cb()
            else:
                raise BadShellRequest()


class NetShell(ModelShell):
    def __init__(self):
        super(NetShell, self).__init__(LOG)

    def preload_model(self, model_class, config=None):
        model = super(NetShell, self).preload_model(model_class, config)
        return model

    def _run(self, model, name, method, *args, **kwargs):
        d = defer.succeed({})
        d.addCallback(lambda r: model.run(name, method, *args, **kwargs))
        return d
