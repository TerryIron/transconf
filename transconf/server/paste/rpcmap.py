__author__ = 'chijun'

import cgi
import copy

try:
    import cpickle as pickle
except:
    import pickle

try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin

import transconf.server.paste.rpcexceptions as rpcexceptions
from transconf.utils import as_config, import_class
from transconf.server import twisted


def _load_factory(factory_line, global_conf, **local_conf):
    model, cls = factory_line.split(':')
    cls = cls.split('.')
    if len(cls) > 1: func = cls[1]
    else: func = 'factory'
    model = '.'.join([model, cls[0]])
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    middleware = import_class(model)
    func = getattr(middleware, func)
    if callable(func):
        return func(global_conf, **local_conf)


def shell_factory(loader, global_conf, **local_conf):
    assert 'paste.app_factory' in local_conf, 'please install model config as paste.app_factory=x'
    assert 'shell_class' in local_conf, 'please install model config as shell_class=x'
    assert 'shell' in local_conf, 'please install model config as shell=x'
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    shell_class = local_conf.pop('shell_class')
    sh = import_class(shell_class)()
    for model in local_conf['shell'].split():
        model = loader.get_app(model, global_conf=global_conf)
        mod = import_class(model)
        sh.load_model(mod, config=conf)
    app_factory = local_conf.pop('paste.app_factory')
    local_conf['shell'] = sh
    app = _load_factory(app_factory, global_conf, **local_conf)
    return app


def platform_factory(loader, global_conf, **local_conf):
    assert 'platform' in local_conf, 'please install platform config as platform=x'
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    platform = {}
    for pf in local_conf['platform'].split():
        app = loader.get_app(pf, global_conf=global_conf)
        platform[pf] = app
    return platform


def filter_factory(loader, global_conf, **local_conf):
    _filter_factory = local_conf.pop('paste.filter_factory')
    _filter = _load_factory(_filter_factory, global_conf, **local_conf)
    return _filter


def pipeline_factory(loader, global_conf, **local_conf):
    assert 'pipeline' in local_conf, 'please install pipeline config as pipeline=x'
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    pipe = []
    for p in local_conf['pipeline'].split():
        app = loader.get_app(p, global_conf=global_conf)
        pipe.append(app)
    return tuple(pipe)


def rpcmap_factory(loader, global_conf, **local_conf):
    if 'not_found_app' in local_conf:
        not_found_app = local_conf.pop('not_found_app')
    else:
        not_found_app = global_conf.get('not_found_app')
    if not_found_app:
        not_found_app = loader.get_app(not_found_app, global_conf=global_conf)
    rpcmap = RPCMap(not_found_app=not_found_app)
    for rpc_line, app_name in local_conf.items():
        rpc_line = parse_rpcline_expression(rpc_line)
        app = loader.get_app(app_name, global_conf=global_conf)
        rpcmap[rpc_line] = app
    return rpcmap


def parse_rpcline_expression(rpcline):
    try:
        return pickle.dumps(dict([item.split('|', 1) for item in rpcline.split(',')]))
    except:
        return rpcline
    

class RPCMap(DictMixin):
    def __init__(self, not_found_app=None):
        self.applications = []
        if not not_found_app:
            not_found_app = self.not_found_app
        self.not_found_application = not_found_app

    def not_found_app(self, environ, start_response=None):
        environ_is_dict = isinstance(environ, dict)
        mapper = environ.get('paste.rpcmap_object') if environ_is_dict else None
        if mapper:
            matches = [p for p, a in mapper.applications]
            extra = 'defined apps: %s' % (
                ',\n  '.join(map(repr, matches)))
        else:
            extra = ''
        excute = environ.get('execute') if environ_is_dict else None
        extra += '\nEXECUTE: %r' % excute
        app = rpcexceptions.RPCNotFound(
            excute, comment=cgi.escape(extra))
        return app.wsgi_application(app.message, start_response)

    def sort_apps(self):
        self.applications.sort()

    def __setitem__(self, rpc, app):
        if app is None:
            try:
                del self[rpc]
            except KeyError:
                pass
        dom_rpc = self.normalize_rpc(rpc)
        if dom_rpc in self:
            del self[dom_rpc]
        self.applications.append((dom_rpc, app))
        self.sort_apps()

    def __getitem__(self, rpc):
        dom_rpc = self.normalize_rpc(rpc)
        for app_rpc, app in self.applications:
            if app_rpc == dom_rpc:
                return app
        raise KeyError(
            "No application with the rpcline %r (existing: %s)"
            % (rpc, self.applications))

    def __delitem__(self, rpc):
        rpc = self.normalize_rpc(rpc)
        for app_rpc, app in self.applications:
            if app_rpc == rpc:
                self.applications.remove((app_rpc, app))
                break
            else:
                raise KeyError(
                    "No application with the rpcline %r" % (rpc,))

    def normalize_rpc(self, rpc):
        try:
            _rpc = pickle.loads(rpc)
            assert isinstance(_rpc, dict), 'RPC request format error.'
            return rpc
        except:
            return rpc

    def keys(self):
        return [app_rpc for app_rpc, app in self.applications if app_rpc != 'transport']

    def items(self):
        return [(pickle.loads(app_rpc), app) for app_rpc, app in self.applications if app_rpc != 'transport']

    def transports(self):
        return [app for app_rpc, app in self.applications if app_rpc == 'transport']

    @staticmethod
    def _check_rpc_exist(rpc, environ):
        app_is_found = True
        for k, v in rpc.items():
            if (k not in environ) or environ[k] != v:
                app_is_found = False
                break
        return app_is_found

    @staticmethod
    def _is_environ_dict(environ):
        return isinstance(environ, dict)

    def __call__(self, environ, start_response=None):
        is_environ_dict = self._is_environ_dict(environ)
        _environ = None
        while not is_environ_dict:
            copy_environ = copy.copy(environ)
            for _app in self.transports():
                _environ = _app(copy_environ, start_response)
                is_environ_dict = self._is_environ_dict(_environ)
            break
        if not _environ:
            _environ = environ
        for app_rpc_dict, app in self.items():
            if is_environ_dict and self._check_rpc_exist(app_rpc_dict, _environ):
                for _app in app:
                    _environ = _app(_environ, start_response)
                return _environ
        if is_environ_dict:
            _environ['paste.rpcmap_object'] = self
        return self.not_found_application(_environ, start_response)
