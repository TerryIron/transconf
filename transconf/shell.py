__author__ = 'chijun'


from common.namebus import NameBus
from form_parser import FormParser
from model import Model


class ShellTargetNameFormatErr(Exception):
    """Raised when target's name got by a wrong format"""

class ModelShell(NameBus):
    SPLIT_DOT = '.'
    """
        Sample code:
    """
    def __init__(self, name):
        super(ModelShell, self).__init__(name)
        self.split = self.SPLIT_DOT
        self.parser = FormParser()
        self.init_drivers()
        self.init_models()

    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:-1])
                return model.run(other_names, method_name, *args, **kwargs)
            return False
        else:
            raise ShellTargetNameFormatErr(target_name)

    def set_env(self, key, value):
        pass

    def get_env(self, key, value):
        pass

    def init_drivers(self):
        raise NotImplementedError()

    def init_models(self):
        raise NotImplementedError()

    def load_driver(self, name, driver):
        raise NotImplementedError()

    def remove_driver(self, name):
        raise NotImplementedError()

    def load_model(self, name, model):
        raise NotImplementedError()

    def remove_model(self, name):
        raise NotImplementedError()
