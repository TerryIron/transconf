__author__ = 'chijun'


from transconf.common.utils import NameSpace


@NameSpace
class Registry(object):
    def __init__(self, name):
        self.name = name
        self.reg = {}

    def register(self, name, obj, is_forced=False):
        if is_forced:
            self.reg[name] = obj
        else:
            if name not in self.reg:
                self.reg[name] = obj

    def get(self, name):
        return self.reg.get(name, None)

    def unregister(self, name):
        if name in self.reg:
            self.reg.pop(name)


def get_reg_target(reg_type, name):
    if reg_type.startswith('lib'): return get_local_driver(name)
    elif reg_type.startswith('mod'): return get_model(name)
    elif reg_type.startswith('cmd'): return get_local_cmd(name)


"""
LibReg = Registry('lib')


def register_local_lib(name):
    def _register_local_lib(cls):
        def __register_local_lib(*_args, **_kwargs):
            obj = cls(*_args, **_kwargs)
            LibReg.register('__is_lib__' + str(name), obj)
            return obj
        return __register_local_lib
    return _register_local_lib


def get_local_lib(name=None):
    return LibReg.get('__is_lib__' + str(name))
"""


ModelReg = Registry('model')


def register_model(cls):
    def __register_model(*_args, **_kwargs):
        obj = cls(*_args, **_kwargs)
        for single in obj.FORM:
            ModelReg.register('__is_model__' + str(single['node']), obj)
        return obj
    return __register_model


def get_model(name):
    return ModelReg.get('__is_model__' + str(name)) 


CmdReg = Registry('cmd')


def register_local_cmd(cls):
    def __register_local_cmd(*_args, **_kwargs):
        obj = cls(*_args, **_kwargs)
        CmdReg.register('__is_cmd__' + str(obj.name), obj)
        return obj
    return __register_local_cmd


def get_local_cmd(name):
    return CmdReg.get('__is_cmd__' + str(name))


