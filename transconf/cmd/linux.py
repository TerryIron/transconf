__author__ = 'chijun'

from transconf.driver import Command

class File(Command):
    def init(self)
        self.enabled_method = [
            'new',
            'forced_remove',
            'read_all',
        ]

class Directory(Command):
    def init(self)
        self.enabled_method = [
            'new',
            'forced_remove',
            'list_all',
        ]
