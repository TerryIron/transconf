#coding=utf-8

__author__ = 'chijun'

__all__ = ['NameSpace']


def NameSpace(cls, *args, **kwargs):
    """
    单例模式

    Args:
        cls: 类
        *args: 类列表参数
        **kwargs: 类字典参数

    Returns:
        object: 类对象

    """

    space = {}

    def _namespace(name, *_args, **_kwargs):
        _name = cls.__name__ + '_' + name
        if _name not in space:
            space[_name] = cls(name, *_args, **_kwargs)
        return space[_name]
    return _namespace




