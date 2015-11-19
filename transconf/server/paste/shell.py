__author__ = 'chijun'

from transconf.server.twisted.netshell import NetShell
from transconf.utils import as_config, import_class
from transconf.server import twisted


def shell_factory(loader, global_conf, **local_conf):
    assert 'models' in local_conf, 'please install model config as models=x'
    sh = NetShell()
    conf = as_config(global_conf['__file__'])
    twisted.CONF = conf
    for model in local_conf['models'].split():
        mod = import_class(loader.get_app(model, global_conf=global_conf))
        sh.load_model(mod, config=conf)
        print 1111111111, sh
    return sh
