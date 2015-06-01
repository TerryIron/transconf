__author__ = 'chijun'


class BaseObj(object):
    def __init__(self):
        self.obj = []

    def current(self):
        if not self.is_empty():
            return self.obj[-1]

    def push(self, obj):
        self.obj.append(obj)

    def pop(self, i=-1):
        return self.obj.pop(i)

    def get(self):
        return self.obj

    def clear(self):
        self.obj = []

    def is_empty(self):
        if not self.obj:
            return True
        return False

    @property
    def size(self):
        return len(self.obj)

    def has(self, obj, index=-1):
        if self.size > index:
            if obj in self.obj[index]:
                return True
        return False


class Mapping(BaseObj):
    def push(self, obj):
        for key, val in obj.items():
            self.obj.append((key, val))

    def set(self, obj):
        self.clear()
        self.push(obj)


