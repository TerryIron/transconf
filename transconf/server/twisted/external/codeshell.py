__author__ = 'chijun'

from transconf.shell import ModelShell, ShellTargetNotFound


class CodeShell(ModelShell):
    TARGET_NAME = 'vcloud.code' 

    def run(self, method_name, *args, **kwargs):
        model_name = self.TARGET_NAME
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:])
                d = defer.succeed({})
                cb = functools.partial(model.run, other_names, method_name, *args, **kwargs)
                d.addCallback(lambda r: cb())
            return d
        else:
            raise ShellTargetNotFound(method_name)

    def load_model(self, model_class, config=None):
        name = self.TARGET_NAME.split(self.split)[0]
        if self.preload_model(name, model_class, config):
            model = self.get_namebus(name)
            model.start(config)

    """
        Remove pointed model and finally call the stop-code.
    """
    def remove_model(self):
        name = self.TARGET_NAME.split(self.split)[0]
        model = self.get_namebus(name)
        model.stop()
        self.remove_namebus(name)


