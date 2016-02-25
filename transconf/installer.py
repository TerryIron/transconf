# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


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
        var('group_name', 'Group name of your project',
            default='test'),
        var('group_type', 'Group type of your project',
            default='test_type'),
        var('group_uuid', 'Group uuid of your project',
            default=uuid.uuid1()),
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
