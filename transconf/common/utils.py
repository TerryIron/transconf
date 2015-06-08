__author__ = 'chijun'

__all__ = ['NameSpace']


def NameSpace(cls, *args, **kwargs):
    """
       Internal interface for base object, 
       forbidden '@' any succeessor
    """
    space = {}
    def _namespace(name, *_args, **_kwargs):
        _name = cls.__name__ + '_' + name
        if _name not in space:
            space[_name] = cls(name, *_args, **_kwargs)
        return space[_name]
    return _namespace




