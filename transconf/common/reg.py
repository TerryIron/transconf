__author__ = 'chijun'


from utils import NameSpace


@NameSpace
class Register(object):
    def __init__(self, name):
        self.name = name
        self.reg = {}

    def register(self, name, obj):
        self.reg[name] = obj


    def get(self, name):
        return self.reg.get(name, None)


def get_reg_target(reg_type, name):
    if reg_type.startswith('dri'): return get_local_driver(name)
    elif reg_type.startswith('mod'): return get_model(name)


LocalReg = Register('local')

def register_local_driver(name):
    def _register_local_driver(cls, *args, **kwargs):
        def __register_local_driver(*_args, **_kwargs):
            obj = cls(*_args, **_kwargs)
            LocalReg.register('__is_driver__' + str(name), obj)
            return obj
        return __register_local_driver
    return _register_local_driver
 
def get_local_driver(name):
    return LocalReg.get('__is_driver__' + str(name))
    

ModelReg = Register('model')

def register_model(name):
    def _register_model(cls, *args, **kwargs):
        def __register_model(*_args, **_kwargs):
            obj = cls(*_args, **_kwargs)
            ModelReg.register('__is_model__' + str(name), obj)
            return obj
        return __register_model
    return _register_model
    
def get_model(name):
    return ModelReg.get('__is_model__' + str(name)) 


