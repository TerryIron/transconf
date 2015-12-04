__author__ = 'chijun'

import cgi

try:
    import cpickle as pickle
except:
    import pickle

try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin

import transconf.server.paste.rpcexceptions as rpcexceptions
from transconf.server.twisted.netshell import NetShell
from transconf.utils import as_config, import_class
from transconf.server import twisted


SHELL_CLASS = NetShell


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
    assert 'shell' in local_conf, 'please install model config as shell=x'
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    sh = SHELL_CLASS()
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
    return pickle.dumps(dict([item.split('|', 1) for item in rpcline.split(',')]))
    

class RPCMap(DictMixin):
    def __init__(self, not_found_app=None):
        self.applications = []
        if not not_found_app:
            not_found_app = self.not_found_app
        self.not_found_application = not_found_app

    def not_found_app(self, environ, start_response=None):
        mapper = environ.get('paste.rpcmap_object')
        if mapper:
            matches = [p for p, a in mapper.applications]
            extra = 'defined apps: %s' % (
                ',\n  '.join(map(repr, matches)))
        else:
            extra = ''
        extra += '\nEXECUTE: %r' % environ.get('execute')
        app = rpcexceptions.RPCNotFound(
            environ['execute'],
            comment=cgi.escape(extra)).wsgi_application
        return app(environ, start_response) 

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
        _rpc = pickle.loads(rpc)
        assert isinstance(_rpc, dict), 'RPC request format error.'
        return rpc

    def keys(self):
        return [app_rpcline for app_rpcline, app in self.applications]

    def __call__(self, environ, start_response=None):
        if not environ.get('execute', None):
            return 
        for app_rpc, app in self.applications:
            app_rpc_dict = pickle.loads(app_rpc)
            app_is_found = True
            for k, v in app_rpc_dict.items():
                if (k not in environ) or environ[k] != v:
                    app_is_found = False
                    break
            if app_is_found:
                return app(environ, start_response)
        environ['paste.rpcmap_object'] = self
        return self.not_found_application(environ, start_response)
