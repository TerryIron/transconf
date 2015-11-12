__author__ = 'chijun'

from transconf.command_driver import Command
from transconf.common.reg import register_local_cmd


@register_local_cmd
class File(Command):
    def init(self):
        self.enabled_method = [
            'new',
            'forced_remove',
            'read_all',
        ]


@register_local_cmd
class Directory(Command):
    def init(self):
        self.enabled_method = [
            'new',
            'forced_remove',
            'list_all',
        ]
