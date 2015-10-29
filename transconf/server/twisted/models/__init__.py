__version__ = (0, 1, 0)

from transconf.server.twisted.netshell import NetShell
from transconf.utils import from_config_option, import_class
from transconf.common.reg import get_model
from transconf.server.twisted.log import getLogger

LOG  = getLogger(__name__)


class LostModel(Exception):
    def __str__(self, name, by_name):
        return "Model:{0} is depend on model:{1}.".format(by_name, name)

class LostModelConfig(Exception):
    def __str__(self, name, by_name):
        return "Model:{0} is depend on model:{1}'s defined name.".format(by_name, name)

class ModelSectNameErr(Exception):
    def __str__(self, name):
        return "Can not found model in registry by section name:{0}.".format(name)

class ModelVersionErr(Exception):
    def __str__(self, name):
        return "Can not found model:{0} 's version.".format(name)

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
        sh = NetShell(LOG)
    for sect in conf.sections():
        @from_config_option('model', None, sect=sect)
        def get_model_class():
            return conf
        @from_config_option('name', None, sect=sect)
        def get_model_name():
            return conf
        @from_config_option('ver', '0.1.0', sect=sect)
        def get_model_ver():
            return conf
        def load_model(self, name, model_class, config=None):
            if self.preload_model(name, model_class, config):
                if not get_model(sect):
                    raise ModelSectNameErr(sect)
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
                model = self.get_namebus(name)
                if '.'.join([str(i) for i in model.__version__]) != get_model_ver():
                    raise ModelVersionErr(name)
                model.start(config)
        class_name = get_model_class()
        name = get_model_name()
        if class_name and name:
            mod = import_class(class_name)
            load_model(sh, name, mod, conf)
    return sh
