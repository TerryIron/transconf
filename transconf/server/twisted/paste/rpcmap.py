__author__ = 'chijun'

try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin


def rpcmap_factory(loader, global_conf, **local_conf):
    if 'not_found_app' in local_conf:
        not_found_app = local_conf.pop('not_found_app')
    else:
        not_found_app = global_conf.get('not_found_app')
    if not_found_app:
        not_found_app = loader.get_app(not_found_app, global_conf=global_conf)
    rpcmap = RPCMap(not_found_app=not_found_app)
    for rpc_line, app_name in local_conf.items():
        app = loader.get_app(app_name, global_conf=global_conf)
        rpcmap[rpc_line] = app
    return rpcmap


class RPCMap(DictMixin):
    def __init__(self, not_found_app=None):
	self.applications = []
	if not not_found_app:
	    not_found_app = self.not_found_app
	self.not_found_application = not_found_app

    def not_found_app(self, environ, start_response):
	pass

    def sort_apps(self):
	pass

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

    def normalize_rpc(self, rpc, trim=True):
	pass

    def keys(self):
	return [app_rpc for app_rpc, app in self.applications]

    def __call__(self, environ, start_response):
	pass
