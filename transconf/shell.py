__author__ = 'chijun'


from transconf.common.namebus import NameBus
from transconf.parse_form import FormParser
from transconf.model import Model


class ShellTargetNotFound(Exception):
    """Raised when target can not found"""


class ModelShell(NameBus):
    SPLIT_DOT = '.'

    def __init__(self, log=None):
        super(ModelShell, self).__init__()
        self.split = self.SPLIT_DOT
        self.environ = {}
        self.log = log
        self.parser = FormParser(log)

    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) >= 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            if isinstance(model, Model):
                return model.run(tuple(name_lst), method_name, *args, **kwargs)
            return False
        else:
            raise ShellTargetNotFound(target_name)

    def set_env(self, key, value):
        raise NotImplementedError()

    def get_env(self, key):
        raise NotImplementedError()

    def preload_model(self, model_class, config=None):
        def translate():
            model = model_class()
            model.init(config)
            self.parser.translate(model)
            self.log.debug('Load model:{0} successfully'.format(model))
            return model
        model = translate()
        if model:
            for single in model.FORM:
                self.set_namebus(single['node'], model, False)
        return model

    """
        Load model class and finally call the start-code.
    """
    def load_model(self, name, model_class, config=None):
        model = self.preload_model(model_class, config)
        if model:
            model.start(config)

    """
        Remove pointed model and finally call the stop-code.
    """
    def remove_model(self, name):
        model = self.get_namebus(name)
        model.stop()
        self.remove_namebus(name)

    def list_models(self):
        return self.list_namebus()
