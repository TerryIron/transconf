#coding=utf-8

__author__ = 'chijun'

import re
import functools
from twisted.internet import defer

from transconf.shell import ModelShell
from transconf.server.twisted.service import Middleware
from transconf.server.twisted.log import getLogger
from transconf.shell import ShellTargetNotFound
from transconf.server.twisted.netshell import NoHandlerFound, BadRequest

LOG = getLogger(__name__)


class URLMiddleware(Middleware):
    def process_request(self, context):
        if not hasattr(self.handler, 'run'):
            raise NoHandlerFound()
        target_name = context.get('PATH_INFO', None)
        method_name = context.get('REQUEST_METHOD', 'GET')
        if target_name and method_name:
            cb = functools.partial(self.handler.run,
                                   target_name,
                                   method_name)
            return cb()
        else:
            raise BadRequest(context)


class NetShell(ModelShell):
    SPLIT_DOT = '/'
    RE = re.compile('<(.*)>')

    def _parse_url(self, pre, cur, length):
        kw = dict()
        for i in range(length):
            g = self.RE.match(cur[i])
            if g:
                item = str(g.groups()[0])
                kw[item.strip()] = pre
            elif pre[i] != cur[i]:
                return False, kw
        return True, kw

    def run(self, target_name, method_name, *args, **kwargs):
        try:
            path_info = [path for path in target_name.split(self.split) if path != ""]
            path_len = len(path_info)
            for key, model in self.all().items():
                key_info = key.split(self.split)
                if len(key_info) == path_len:
                    ret, kwargs = self._parse_url(path_info, key_info, path_len)
                    if ret:
                        return self._run(model, tuple(path_info), method_name, **kwargs)
            raise ShellTargetNotFound(target_name)
        except Exception as e:
            LOG.error(e)

    def _run(self, model, name, method, *args, **kwargs):
        def process_result(result):
            return [] if result is None else result

        d = defer.succeed({})
        d.addCallback(lambda r: model.run(name, method, *args, **kwargs))
        d.addCallback(lambda r: process_result(r))
        return d
