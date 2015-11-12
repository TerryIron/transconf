__version__ = (0, 1, 0)

from transconf.server.twisted.netshell import NetShell
from transconf.utils import from_config_option, import_class
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class LostModel(Exception):
    def __str__(self, name, by_name):
        return "Model:{0} is depend on model:{1}.".format(by_name, name)


class LostModelConfig(Exception):
    def __str__(self, name, by_name):
        return "Model:{0} is depend on model:{1}'s defined name.".format(by_name, name)


def check_depends(conf, model_name, deps):
    deps = deps.split(',')
    for dep in deps:
        @from_config_option('name', None, sect=dep)
        def get_depend_name():
            return conf
        @from_config_option('model', None, sect=dep)
        def get_depend_model():
            return conf
        if not (get_depend_name() and get_depend_model):
            raise LostModel(dep, model_name)


def check_needs(conf, model_name, needs):
    needs = needs.split(',')
    for nd in needs:
        @from_config_option('name', None, sect=nd)
        def get_need_name():
            return conf
        if not get_need_name():
            raise LostModelConfig(nd, model_name)


def model_configure(conf, sh=None):
    if not sh:
        sh = NetShell()
    for sect in conf.sections():
        @from_config_option('model', None, sect=sect)
        def get_model_class():
            return conf

        def load_model(self, model_class, config=None):
            _model = self.preload_model(model_class, config)
            if _model:

                @from_config_option('depend', None, sect=sect)
                def get_model_depend():
                    return config

                @from_config_option('need', None, sect=sect)
                def get_model_need():
                    return config
                depends = get_model_depend()
                if depends:
                    check_depends(conf, sect, depends)
                else:
                    need = get_model_need()
                    if need:
                        check_needs(conf, sect, need)
            return _model
        class_name = get_model_class()
        if class_name:
            mod = import_class(class_name)
            model = load_model(sh, mod, conf)
            if model:
                model.start(conf)
    return sh
