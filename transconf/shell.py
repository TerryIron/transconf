__author__ = 'chijun'


from common.namebus import NameBus


class ModelShell(NameBus):
    """
        Sample code:
    """
    def __init__(self, name):
        super(ModelShell, self).__init__(name)
        self.parser = None
        self.init_drivers()
        self.init_models()

    def _is_readonly_mode(self, target_name):
        if target_name.startswith('$'):
            return False
        return True

    def run(self, target_name, method_name, *args, **kwargs):
        if not self._is_readonly_mode(target_name):
            return None
        pass

    def getattr(self, target_name, property_name):
        pass

    def setattr(self, target_name, property_name, value):
        if self._is_readonly_mode(target_name):
            return False
        pass

    def init_drivers(self):
        raise NotImplementedError()

    def init_models(self):
        raise NotImplementedError()

    def load_driver(self, name, driver):
        raise NotImplementedError()

    def remove_driver(self, name):
        raise NotImplementedError()

    def update_model(self, name, model):
        raise NotImplementedError()

    def remove_model(self, name):
        raise NotImplementedError()
