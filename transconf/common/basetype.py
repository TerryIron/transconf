__author__ = 'chijun'


class BaseType(object):

    def check(self, data):
        raise NotImplementedError()

    def convert(self, data):
        raise NotImplementedError()
