__author__ = 'chijun'

from transconf.shell import ModelShell, ShellTargetNotFound
from transconf.model import Model

from twisted.internet import defer

class TxShell(ModelShell):

    @defer.inlineCallbacks
    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = yield str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = yield name_lst[0]
            model = yield self.get_namebus(model_name)
            if isinstance(model, Model):
                other_names = yield tuple(name_lst[1:])
                yield model.run(other_names, method_name, *args, **kwargs)
            yield False
        else:
            raise ShellTargetNotFound(target_name)
