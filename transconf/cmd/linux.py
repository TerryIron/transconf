__author__ = 'chijun'

from transconf.driver import Command
from transconf.command.reg import register_local_cmd


@register_local_cmd('regular_file')
class File(Command):
    def init(self):
        self.enabled_method = [
            'new',
            'forced_remove',
            'read_all',
        ]


@register_local_cmd('regular_dir')
class Directory(Command):
    def init(self):
        self.enabled_method = [
            'new',
            'forced_remove',
            'list_all',
        ]
