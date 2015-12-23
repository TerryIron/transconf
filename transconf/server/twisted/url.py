# coding=utf-8

__author__ = 'chijun'

import copy
import os.path
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
        try:
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
        except Exception as e:
            LOG.error(e)


class NetShell(ModelShell):
    SPLIT_DOT = '/'
    RE = re.compile('{(.*)}')

    def __init__(self, document_path='/'):
        super(NetShell, self).__init__(LOG)
        self.document_path = document_path
        self.cache_mem = {}
        self.uri_list = []
        self.not_found = []
        LOG.debug('Setting document path:{0}'.format(self.document_path))

    def _update_cache(self, key, value):
        if key not in self.cache_mem:
            self.cache_mem[key] = value

    @staticmethod
    def _get_resource(path):
        def read_file(file_path):
            with open(file_path) as f:
                LOG.debug('Upload resource file:{0}'.format(file_path))
                return f.readlines()
        d = defer.succeed({})
        d.addCallback(lambda ret: read_file(path))
        return d

    def _parse_path(self, path, length):
        path_copy_list = [copy.copy(path)]
        relative_paths = ['.']
        relative_cache_path = []
        for _path in self.uri_list:
            _path_len = len(_path)
            maybe_in_path = _path_len < length
            if maybe_in_path:
                for i in range(_path_len):
                    g = self.RE.match(_path[i])
                    _p = _path[i]
                    _cp = path[i]
                    if not g and _p != _cp:
                        break
                    else:
                        path_copy_list.append(copy.copy(path_copy_list[-1]))
                        path_copy_list[-1].remove(path[i])
                        relative_paths.append('..')
        # If path cannot be found in URI list ?
        if len(relative_paths) == 1:
            def build_relative_path(_length):
                return self.split.join(['..' for i in range(_length) if i])
            for k in self.cache_mem.keys():
                _buf = build_relative_path(len(k.split(self.split)))
                if _buf not in relative_cache_path:
                    relative_cache_path.append(_buf)
                relative_cache_path.append('..')
                relative_cache_path = [r + '/' + self.split.join(path) for r in relative_cache_path]
        return set([self.split.join(relative_paths) + '/' + self.split.join(p)
                   for p in path_copy_list] + [self.split.join('.') + '/' + self.split.join(k)
                   for k in path_copy_list] + relative_cache_path)

    def _parse_url(self, pre, cur, length):
        kw = dict()
        _path = list()
        for i in range(length):
            g = self.RE.match(cur[i])
            if g:
                item = str(g.groups()[0]).strip()
                kw[item] = pre[i]
                _path.append('{' + item + '}')
            else:
                if pre[i] != cur[i]:
                    return False, kw, _path
                else:
                    _path.append(pre[i])
        return True, kw, _path

    def preload_model(self, model_class, config=None):
        model = super(NetShell, self).preload_model(model_class, config)
        model.split = self.split
        for key, model in self.all().items():
            key_info = tuple(key.split(self.split))
            self.uri_list.append(key_info)
            self.set(key_info, model)
            self.remove(key)
        self.uri_list.sort()
        return model

    def run(self, _target_name, _method_name, *args, **kwargs):
        try:
            LOG.debug('Lookup target:{0}, method:{1}'.format(_target_name, _method_name))
            path_info = [path for path in _target_name.split(self.split) if path != ""]
            path_len = len(path_info)
            # Check is API in model bus ?
            for key_info, model in self.all().items():
                if len(key_info) == path_len:
                    ret, kwargs, real_path = self._parse_url(path_info, key_info, path_len)
                    if ret:
                        self._update_cache(_target_name, model)
                        model['document_path'] = self.document_path
                        return self._run(model, tuple(real_path), _method_name, *args, **kwargs)
            # Check is URI ?
            real_target_paths = self._parse_path(path_info, path_len)
            for real_target_path in real_target_paths:
                if os.path.isfile(real_target_path):
                    return self._get_resource(real_target_path)
                path = os.path.join(os.path.abspath(self.document_path), real_target_path)
                if os.path.isfile(path):
                    return self._get_resource(path)
            raise ShellTargetNotFound(real_target_paths)

        except Exception as e:
            LOG.error(e)

            def _not_found():
                return self.not_found
            d = defer.fail(e)
            d.addErrback(lambda e: _not_found())
            return d

    def _run(self, _model, _name, _method, *args, **kwargs):
        def process_result(result):
            return [] if result is None else result

        d = defer.succeed({})
        d.addCallback(lambda r: _model.run(_name, _method, *args, **kwargs))
        d.addCallback(lambda r: process_result(r))
        return d
