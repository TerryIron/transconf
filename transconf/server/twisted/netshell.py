# coding=utf-8

__author__ = 'chijun'

import functools
from twisted.internet import defer

from transconf.shell import ModelShell
from transconf.server.twisted.service import Middleware
from transconf.server.request import Request
from transconf.utils import SimpleModel, Exception as _Exception
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class BadRequest(_Exception):
    """Raised when request comming with invalid data """


class NoHandlerFound(_Exception):
    """Raised when no handler to process request"""


class ShellRequest(Request):

    def __init__(self, target_name, method_name, version, **kwargs):
        d = dict(target=target_name,
                 method=method_name,
                 version=version,
                 kwargs=kwargs)
        super(ShellRequest, self).__init__(**d)

    def to_dict(self, context=None, timeout=60):
        if not context:
            context = {}

        context['execute'] = dict(
            target=self['target'],
            method=self['method'],
            version=self['version'],
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
        try:
            if not hasattr(self.handler, 'run'):
                raise NoHandlerFound()
            shell_req = context.get('execute', None)
            if shell_req:
                target_name = shell_req.get('target', None)
                method_name = shell_req.get('method', None)
                if target_name and method_name:
                    kwargs = shell_req.get('kwargs', None)
                    cb = functools.partial(self.handler.run,
                                           target_name,
                                           method_name, **kwargs)
                    return cb()
                else:
                    raise BadRequest(context)
        except Exception as e:
            LOG.error(e)


class NetShell(ModelShell):
    def __init__(self):
        super(NetShell, self).__init__(LOG)

    def preload_model(self, model_class, config=None):
        model = super(NetShell, self).preload_model(model_class, config)
        return model

    def run(self, _target_name, _method_name, **kwargs):
        try:
            ret = super(NetShell, self).run(_target_name, _method_name, **kwargs)
            return ret
        except Exception, e:
            LOG.error(e)

    def _run(self, _model, _name, _method, **kwargs):
        def process_error(err):
            LOG.error(err)
            raise Exception(err.value)
        print 1111, _name, _method, kwargs
        d = defer.succeed({})
        d.addCallback(lambda r: _model.run(_name, _method, **kwargs))
        d.addErrback(lambda e: process_error(e))
        return d
