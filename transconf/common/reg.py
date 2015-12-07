#coding=utf-8

__author__ = 'chijun'


from transconf.common.utils import NameSpace


@NameSpace
class Registry(object):
    """
    内置注册表

    """
    def __init__(self, name):
        self.name = name
        self.reg = {}

    def register(self, name, obj, is_forced=False):
        """
        注册对象

        Args:
            name(str): 对象名
            obj(object): 对象
            is_forced(boo): 是否强制，默认为False

        Returns:
            None

        """
        if is_forced:
            self.reg[name] = obj
        else:
            if name not in self.reg:
                self.reg[name] = obj

    def get(self, name):
        """
        获取对象

        Args:
            name: 对象名

        Returns:
            object: 对象

        """
        return self.reg.get(name, None)

    def unregister(self, name):
        """
        注销对象

        Args:
            name: 对象名

        Returns:
            None

        """
        if name in self.reg:
            self.reg.pop(name)


def get_reg_target(reg_type, name):
    """
    获取注册表对象

    Args:
        reg_type: 注册类型
        name: 注册名

    Returns:
        object: 注册对象

    """
    if reg_type.startswith('lib'): return get_local_lib(name)
    elif reg_type.startswith('mod'): return get_model(name)
    elif reg_type.startswith('cmd'): return get_local_cmd(name)


LibReg = Registry('lib')


def register_lib_target(obj):
    CmdReg.register('__is_lib__' + str(obj.name), obj)


def register_lib(cls):
    """
    注册本地库(装饰器)

    Returns:
        object: 库对象

    """
    def __register_lib(*_args, **_kwargs):
        obj = cls(*_args, **_kwargs)
        register_lib_target(obj)
        return obj
    return __register_lib


def get_lib(name=None):
    """
    获取本地注册库对象

    Args:
        name: 对象名

    Returns:
        object: 库对象

    """
    return LibReg.get('__is_lib__' + str(name))


ModelReg = Registry('model')


def register_model_target(obj):
    for single in obj.FORM:
        ModelReg.register('__is_model__' + str(single['node']), obj)


def register_model(cls):
    """
    注册本地模型(装饰器)

    Returns:
        object: 库对象

    """
    def __register_model(*_args, **_kwargs):
        obj = cls(*_args, **_kwargs)
        register_model_target(obj)
        return obj
    return __register_model


def get_model(name):
    """
    获取本地注册模型对象

    Args:
        name: 对象名

    Returns:
        object: 模型对象

    """
    return ModelReg.get('__is_model__' + str(name)) 


CmdReg = Registry('cmd')


def register_cmd_target(obj):
    CmdReg.register('__is_cmd__' + str(obj.name), obj)


def register_cmd(cls):
    """
    注册本地命令对象(装饰器)

    Returns:
        object: 命令对象

    """
    def __register_cmd(*_args, **_kwargs):
        obj = cls(*_args, **_kwargs)
        register_cmd_target(obj)
        return obj
    return __register_cmd


def get_cmd(name):
    """
    获取本地注册命令对象

    Args:
        name: 对象名

    Returns:
        object: 命令对象

    """
    return CmdReg.get('__is_cmd__' + str(name))
