__author__ = 'chijun'

import functools

from twisted.internet import defer

from transconf.shell import ModelShell, ShellTargetNotFound
from transconf.model import Model
from transconf.server.twisted.service import Middleware
from transconf.server.request import Request


class ShellRequest(Request):
    def __init__(self, target_name, method_name, *args, **kwargs):
        d = dict(target_name=target_name,
                 method_name=method_name,
                 args=args,
                 kwargs=kwargs)
        return super(ShellRequest, self).__init__(**d)

    def to_dict(self):
        d = dict(target_name=self['target_name'],
                 method_name=self['method_name'],
                 args=self['args'],
                 kwargs=self['kwargs'])
        return d


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


class NetShell(ModelShell):

    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            d = defer.succeed({})
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:])
                cb = functools.partial(model.run, other_names, method_name, *args, **kwargs)
                d.addCallback(lambda r: cb())
            return d
        else:
            raise ShellTargetNotFound(target_name)
