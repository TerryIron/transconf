__author__ = 'chijun'

import pickle

class List(list):
    pass


class BaseNode(object):
    SETUP = None

    def __init__(self):
        self.members = {}
        self.subs = []

    def __getitem__(self, name):
        return self.members.get('__'+name, None)

    def __setitem__(self, name, value):
        self.members['__'+name] = value

    def has(self):
        return self.subs

    @property
    def is_end(self):
        if not hasattr(self, 'subs'):
            return True
        else:
            if len(self.subs) == 0:
                return True
        return False

    def set_val(self, item, val):
        if (item not in self.__dict__) or  \
           (not isinstance(self.__dict__[item], list)):
            self.__dict__[item] = List()
            setattr(self.__dict__[item], 'is_end', True)
        if not isinstance(val, list):
            val = [val]
        for v in val:
            self.__dict__[item].append(v)

    def set_item(self, item, obj):
        self.__dict__[item] = obj

    def has_item(self, item):
        if item in self.__dict__:
            if isinstance(self.__dict__[item], str):
                return True
        return False

    def get_obj(self, item):
        return self.__dict__.get(item, None)

    def set_obj(self, item, name, obj):
        self.__dict__[item][name] = obj

    def has_obj(self, item, name):
        obj = self.get_obj(item)
        if isinstance(obj, dict):
            if name in obj:
                return True
        return False

    def add_obj(self, item, name):
        obj = self.get_obj(item)
        if isinstance(obj, dict):
            obj = self.__dict__['__backup_'+item]
        else:
            self.__dict__['__backup_'+item] = obj
            self.__dict__[item] = {}
        if name not in self.__dict__[item]:
            cp = pickle.dumps(obj)
            self.set_obj(item, name, pickle.loads(cp))

    def setup(self, *args, **kwargs):
        self['setup'] = self.SETUP
        callback = self['setup']
        if callable(callback):
            callback(*args, **kwargs)


class Fields(object):
    def __init__(self):
        self.need = []

    def add_need(self, *args):
        for item in args:
            if item not in self.need:
                self.need.append(item)

    def get_need(self):
        return self.need

    def clear(self):
        self.need = []
