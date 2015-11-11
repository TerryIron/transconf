__author__ = 'chijun'

import os
import sys

from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp


class ControllerCommand(Command):
    group_name = 'transconf'
    min_args = 1
    max_args = 1

    """Main command to create controller"""
    def command(self):
        try:
            file_op = FileOp(source_dir=('transconf', 'templates'))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)


class RestControllerCommand(Command):
    group_name = 'transconf'
    min_args = 1
    max_args = 1

    """Main command to create controller"""
    def command(self):
        pass


class ShellCommand(Command):
    group_name = 'transconf'
    min_args = 1
    max_args = 1

    """Main command to create a new shell"""
    def command(self):
        pass


class RouteCommand(Command):
    group_name = 'transconf'
    min_args = 1
    max_args = 1

    """Main command to create a new shell"""
    def command(self):
        pass
