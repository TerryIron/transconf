__author__ = 'chijun'

import os
import sys

from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp
from tempita import paste_script_template_renderer

from transconf.server.paste.deploy import loadapp


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
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('controllers', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your controller name should not be the same as '
                    'the package name %r.' % base_package)
            # Validate the name
            name = name.replace('-', '_')
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)


class RestControllerCommand(ControllerCommand):

    """Main command to create controller"""
    def command(self):
        pass


class ShellCommand(ControllerCommand):

    """Main command to create a new shell"""
    def command(self):
        pass


class RouteCommand(ControllerCommand):

    """Main command to create a new shell"""
    def command(self):
        pass
