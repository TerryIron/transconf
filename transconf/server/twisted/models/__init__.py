__version__ = (0, 1, 0)

from transconf.server.twisted.netshell import NetShell
from transconf.server.utils import from_model_option


class LostModel(Exception):
    def __str__(self, name, by_name):
        return "We need model:{0}'s name and model class for {1}".format(name, by_name)

class LostModelConfig(Exception):
    def __str__(self, name, by_name):
        return "We need model:{0}'s name for {1}".format(name, by_name)


def check_depends(conf, model_name, deps):
    deps = deps.split(',')
    for dep in deps:
        @from_model_option('name', None, sect=dep)
        def get_depend_name():
            return conf
        @from_model_option('model', None, sect=dep)
        def get_depend_model():
            return conf
        if not (get_depend_name() and get_depend_model):
            raise LostModel(dep, model_name)


def check_needs(conf, model_name, needs):
    needs = needs.split(',')
    for nd in needs:
        @from_model_option('name', None, sect=nd)
        def get_need_name():
            return conf
        if not get_need_name():
            raise LostModelConfig(nd, model_name)


def model_configure(conf):
    sh = NetShell()
    for sect in conf.sections():
        @from_model_option('model', None, sect=sect)
        def get_model_class():
            return conf
        @from_model_option('name', None, sect=sect)
        def get_model_name():
            return conf
        @from_model_option('depend', None, sect=sect)
        def get_model_depend():
            return conf
        @from_model_option('need', None, sect=sect)
        def get_model_need():
            return conf
        class_name = get_model_class()
        name = get_model_name()
        if class_name and name:
            depends = get_model_depend()
            if depends:
                check_depends(conf, sect, depends)
            else:
                need = get_model_need()
                if need:
                    check_needs(conf, sect, need)
            cls = __import__(class_name)
            sh.load_model(name, cls, conf)
    return sh
