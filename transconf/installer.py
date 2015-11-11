__author__ = 'chijun'

import sys
import uuid

import pkg_resources
from paste.deploy.converters import asbool
from paste.script.appinstall import Installer
from paste.script.templates import Template, var
from tempita import paste_script_template_renderer


class TransconfTemplate(Template):
    _template_dir = ('transconf', 'templates/default_project')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Transconf application template'
    egg_plugins = ['PasteScript', 'Transconf']
    vars = [
        var('template_engine', 'mako/genshi/jinja2/etc: Template language',
            default='mako'),
        var('group_name', 'Project\'s group name for AMQP',
            default='test'),
        var('group_type', 'Project\'s group type for AMQP',
            default='test_type'),
        var('group_uuid', 'Project\'s group uuid for AMQP',
            default=None),
    ]
    ensure_names = ['description', 'author', 'author_email', 'url']

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        vars['template_engine'] = 'mako'

        template_engine = 'mako'

        if template_engine == 'mako':
            # Support a Babel extractor default for Mako
            vars['babel_templates_extractor'] = \
                ("('templates/**.mako', 'mako', {'input_encoding': 'utf-8'})"
                 ",\n%s#%s" % (' ' * 4, ' ' * 8))
        else:
            vars['babel_templates_extractor'] = ''

        # Ensure these exist in the namespace
        for name in self.ensure_names:
            vars.setdefault(name, '')

        vars['version'] = vars.get('version', '0.1')
        vars['zip_safe'] = asbool(vars.get('zip_safe', 'false'))
        vars['group_name'] = vars.get('group_name', 'test')
        vars['group_type'] = vars.get('group_type', 'test_type')
        vars['group_uuid'] = vars.get('group_uuid', uuid.uuid1())


class MinimalTransconfTemplate(TransconfTemplate):
    pass


class TransconfInstaller(Installer):
    use_cheetah = False
    config_file = 'etc/deployment.ini_tmpl'

    def config_content(self, command, vars):
        """
        Called by ``self.write_config``, this returns the text content
        for the config file, given the provided variables.
        """
        modules = [line.strip()
                    for line in self.dist.get_metadata_lines('top_level.txt')
                    if line.strip() and not line.strip().startswith('#')]
        if not modules:
            print >> sys.stderr, 'No modules are listed in top_level.txt'
            print >> sys.stderr, \
                'Try running python setup.py egg_info to regenerate that file'
        for module in modules:
            if pkg_resources.resource_exists(module, self.config_file):
                return self.template_renderer(
                    pkg_resources.resource_string(module, self.config_file),
                    vars, filename=self.config_file)
        # Legacy support for the old location in egg-info
        return super(TransconfInstaller, self).config_content(command, vars)
