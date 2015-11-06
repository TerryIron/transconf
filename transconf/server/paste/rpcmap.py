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

from transconf.utils import as_config
import transconf.server.paste.rpcexceptions as rpcexceptions



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
        extra += '\nSHELL_COMMAND: %r' % environ.get('shell_command')
        app = rpcexceptions.RPCNotFound(
            environ['shell_command'],
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
	    return
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
        if not environ.get('shell_command', None):
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