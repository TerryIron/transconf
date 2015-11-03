__author__ = 'chijun'

import os.path

from paste.deploy.compat import unquote

############################################################                                                                                                                                              
## Object types
############################################################
from paste.deploy.loadwsgi import _ObjectType, _PipeLine, _FilterApp, _App
from paste.deploy.loadwsgi import ConfigLoader, LoaderContext
from paste.deploy.loadwsgi import loadcontext, loadobj
from paste.deploy.loadwsgi import FILTER

############################################################                                                                                                                                              
## Loaders
############################################################
from paste.deploy.loadwsgi import _loaders

from paste.deploy.loadwsgi import *

__all__ = ['loadapp', 'loadserver', 'loadfilter', 'appconfig']



#class _ModelPack(_PipeLine):
#    name = 'model_package'
#    config_prefixes = [['mod-pack', 'model-pack']]
#
#MODELPACK = _ModelPack()
#        
#
#class _Model(_FilterApp):
#    name = 'model'
#    config_prefixes = [['model', 'mod']]
#    egg_protocols = ['paste.model_factory', 'paste.mod_factory']
#
#
#MODEL = _Model()
#
#
#class _CommandPack(_PipeLine):
#    name = 'command_package'
#    config_prefixes = [['cmd-pack', 'command-pack']]
#
#COMMANDPACK = _CommandPack()
#
#
#class _Command(_FilterApp):
#    name = 'command'
#    config_prefixes = [['command', 'cmd']]
#    egg_protocols = ['paste.command_factory', 'paste.cmd_factory']
#
#COMMAND = _Command()


class _APP(_App):
    egg_protocols = ['paste.app_factory', 
                     'paste.composite_factory',
                     'paste.platform_factory',
                     'paste.composit_factory']
    config_prefixes = [['app', 'application'], 
                       ['platform', 'pf'],
                       ['composite', 'composit'], 'pipeline', 'filter-app']

    def invoke(self, context):
        if context.protocol == 'paste.platform_factory':
            return fix_call(context.object,
                            context.loader, context.global_conf,
                            1**context.local_conf)
        return super(_APP, self).invoke(context)

APP = _APP()


class _Platform(_ObjectType):
    name = 'platform'
    config_prefixes = [['platform', 'pf']]
    egg_protocols = ['paste.platform_factory']

    def invoke(self, context): 
        app = context.app_context.create()
        filters = [c.create() for c in context.filter_contexts]
        filters.reverse()
        for filter in filters:
            if filter: app = filter(app)
        return app

PLATFORM = _Platform()


def loadapp(uri, name=None, **kw):
    return loadobj(APP, uri, name=name, **kw) 


class _ConfigLoader(ConfigLoader):
    SECTION_PASTER = [
        ('filter-app:', '_filter_app_context'),
        ('pipeline:', '_pipeline_app_context'),
        ('platform:', '_platform_app_context'),
        #('model:', '_model_app_context'),
        #('model-pack:', '_model_pack_context'),
        #('command:', '_command_app_context'),
        #('command-pack:', '_command_pack_context'),
    ]

    def get_context(self, object_type, name=None, global_conf=None):
        if self.absolute_name(name):
            return loadcontext(object_type, name,
                               relative_to=os.path.dirname(self.filename),
                               global_conf=global_conf)
        section = self.find_config_section(
            object_type, name=name)
        if global_conf is None:
            global_conf = {}
        else:
            global_conf = global_conf.copy()
        defaults = self.parser.defaults()
        global_conf.update(defaults)
        local_conf = {}
        global_additions = {}
        get_from_globals = {}
        for option in self.parser.options(section):
            if option.startswith('set '):
                name = option[4:].strip()
                global_additions[name] = global_conf[name] = (
                    self.parser.get(section, option))
            elif option.startswith('get '):
                name = option[4:].strip()
                get_from_globals[name] = self.parser.get(section, option)
            else:
                if option in defaults:
                    # @@: It's a global option (?), so skip it
                    continue
                local_conf[option] = self.parser.get(section, option)
        for local_var, glob_var in get_from_globals.items():
            local_conf[local_var] = global_conf[glob_var]
        if object_type in (APP, FILTER) and 'filter-with' in local_conf:
            filter_with = local_conf.pop('filter-with')
        else:
            filter_with = None
        if 'require' in local_conf:
            for spec in local_conf['require'].split():
                pkg_resources.require(spec)
            del local_conf['require']
        #Additional sections
        is_section_func = False
        for sect, parser in self.SECTION_PASTER:
            parser_func = getattr(self, parser)
            if callable(parser_func):
                if section.startswith(sect):
                    context = parser_func(
                        object_type, section, name=name,
                        global_conf=global_conf, local_conf=local_conf,
                        global_additions=global_additions)
                    is_section_func = True
                    break
        if not is_section_func:
            if 'use' in local_conf:
                context = self._context_from_use(
                    object_type, local_conf, global_conf, global_additions,
                    section)
            else:
                context = self._context_from_explicit(
                    object_type, local_conf, global_conf, global_additions,
                    section)
        if filter_with is not None:
            filter_with_context = LoaderContext(
                obj=None,
                object_type=FILTER_WITH,
                protocol=None,
                global_conf=global_conf, local_conf=local_conf,
                loader=self)
            filter_with_context.filter_context = self.filter_context(
                name=filter_with, global_conf=global_conf)
            filter_with_context.next_context = context
            return filter_with_context
        return context

    def _common_app_context(self, object_type, section, name,                                                                                                                                             
                           global_conf, local_conf, global_additions, 
                           context_obj, context_loader, context_use_loader):
        if 'next' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'next' setting"
                % (section, self.filename))
        next_name = local_conf.pop('next')
        context = LoaderContext(None, context_loader, None, global_conf,
                                local_conf, self)
        context.next_context = self.get_context(
            context_obj, next_name, global_conf)
        if 'use' in local_conf:
            context.filter_context = self._context_from_use(
                context_use_loader, local_conf, global_conf, global_additions,
                section)
        else:
            context.filter_context = self._context_from_explicit(
                context_use_loader, local_conf, global_conf, global_additions,
                section)
        return context

    def _platform_app_context(self, object_type, section, name,                                                                                                                                             
                              global_conf, local_conf, global_additions):
        if 'platform' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'platform' setting"
                % (section, self.filename))
        platform = local_conf.pop('platform').split()
        if local_conf:
            raise LookupError(
                "The [%s] pipeline section in %s has extra "
                "(disallowed) settings: %s"
                % (', '.join(local_conf.keys())))
        context = LoaderContext(None, PLATFORM, None, global_conf,
                                local_conf, self)
        context.app_context = self.get_context(APP, platform[-1], global_conf)
        context.filter_contexts = [
            self.get_context(APP, name, global_conf)
            for name in platform[:-1]]
        return context

    #def _model_app_context(self, object_type, section, name,                                                                                                                                             
    #                       global_conf, local_conf, global_additions):
    #    pass

    #def _model_pack_context(self, object_type, section, name,                                                                                                                                             
    #                        global_conf, local_conf, global_additions):
    #    if 'model_pack' not in local_conf:
    #        raise LookupError(
    #            "The [%s] section in %s is missing a 'model_pack' setting"
    #            % (section, self.filename))
    #    model_pack = local_conf.pop('model_pack').split()

    #def _command_app_context(self, object_type, section, name,                                                                                                                                             
    #                         global_conf, local_conf, global_additions):
    #    pass

    #def _command_pack_context(self, object_type, section, name,                                                                                                                                             
    #                          global_conf, local_conf, global_additions):
    #    if 'command_pack' not in local_conf:
    #        raise LookupError(
    #            "The [%s] section in %s is missing a 'command_pack' setting"
    #            % (section, self.filename))
    #    cmd_pack = local_conf.pop('command_pack').split()


def _loadconfig(object_type, uri, path, name, relative_to,
                global_conf):                                                                                                                              
    isabs = os.path.isabs(path)
    # De-Windowsify the paths:
    path = path.replace('\\', '/')
    if not isabs:
        if not relative_to:
            raise ValueError(
                "Cannot resolve relative uri %r; no relative_to keyword "
                "argument given" % uri)
        relative_to = relative_to.replace('\\', '/')
        if relative_to.endswith('/'):
            path = relative_to + path
        else:
            path = relative_to + '/' + path
    if path.startswith('///'):
        path = path[2:]
    path = unquote(path)
    loader = _ConfigLoader(path)
    if global_conf:
        loader.update_defaults(global_conf, overwrite=False)
    return loader.get_context(object_type, name, global_conf)

_loaders['config'] = _loadconfig