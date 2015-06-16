__author__ = 'chijun'


from common.namebus import NameBus
from parse_form import FormParser
from model import Model


class ShellTargetNotFound(Exception):
    """Raised when target can not found"""


class ModelShell(NameBus):
    SPLIT_DOT = '.'

    def __init__(self):
        super(ModelShell, self).__init__()
        self.split = self.SPLIT_DOT
        self.environ = {}
        self.parser = FormParser()

    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:])
                return model.run(other_names, method_name, *args, **kwargs)
            # What is it ? I don't care.
            return False
        else:
            raise ShellTargetNotFound(target_name)

    def init_models(self, config=None):
        raise NotImplementedError()

    def set_env(self, key, value):
        raise NotImplementedError()

    def get_env(self, key, value):
        raise NotImplementedError()

    def load_model(self, name, model_class, config=None):
        model = model_class()
        model.init(config)
        self.parser.translate(model)
        self.set_namebus(name, model, False)
        model.start(config)

    def remove_model(self, name):
        self.remove_namebus(name)
        model.stop(config)

    def list_models(self):
        return self.list_namebus()
