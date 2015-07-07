__author__ = 'chijun'

import functools

from twisted.internet import defer

from transconf.shell import ModelShell, ShellTargetNotFound
from transconf.model import Model

from twisted.internet import defer

class TxShell(ModelShell):

    def run(self, target_name, method_name, *args, **kwargs):
        name_lst = str(target_name).split(self.split)
        if len(name_lst) > 1:
            model_name = name_lst[0]
            model = self.get_namebus(model_name)
            d = defer.succeed({})
            if isinstance(model, Model):
                other_names = tuple(name_lst[1:])
                cb = functools.partial(model.run, other_names, method_name, *args, **kwargs)
                d.addCallback(lambda r: cb())
            return d
        else:
            raise ShellTargetNotFound(target_name)
