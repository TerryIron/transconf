__author__ = 'chijun'

from paste.deploy.loadwsgi import *

############################################################                                                                                                                                              
## Object types
############################################################
from paste.deploy.loadwsgi import _PipeLine, _FilterApp
from paste.deploy.loadwsgi import ConfigLoader

############################################################                                                                                                                                              
## Loaders
############################################################
from paste.deploy.loadwsgi import _loaders


__all__ = ['loadapp', 'loadserver', 'loadfilter', 'appconfig']


class _ModelAPP(_PipeLine):
    name = 'model_application'
    config_prefixes = [['mod-app', 'model-app']]

MODELAPP = _ModelAPP()
        

class _Model(_FilterApp):
    name = 'model'
    config_prefixes = ['model']

MODEL = _Model()


class _CommandPack(_PipeLine):
    name = 'command_package'
    config_prefixes = [['cmd-pack', 'command-pack']]

COMMANDPACK = _CommandPack()


class _Command(_FilterApp):
    name = 'command'
    config_prefixes = ['command']

COMMAND = _Command()


class _PlatformPack(_PipeLine):
    name = 'platform_package'
    config_prefixes = [['pf-pack', 'platform-pack']]

PLATFORMPACK = _PlatformPack()


class _Platform(_FilterApp):
    name = 'platform'
    config_prefixes = ['platform']

PLATFORM = _Platform()


class _ConfigLoader(ConfigLoader):
    SECTION_PASTER = [
        ('filter-app:', '_filter_app_context'),
        ('pipeline:', '_pipeline_app_context'),
        ('platform:', '_platform_app_context'),
        ('model:', '_model_app_context'),
        ('model-app:', '_model_pack_context'),
        ('command:', '_command_app_context'),
        ('command-pack:', '_command_pack_context'),
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

    def _model_app_context(self, object_type, section, name,                                                                                                                                             
                           global_conf, local_conf, global_additions):
        return self._common_app_context(object_type, section, name,                                                                                                                                             
                                        global_conf, local_conf, global_additions,
                                        APP, MODEL)

    def _model_pack_context(self, object_type, section, name,                                                                                                                                             
                            global_conf, local_conf, global_additions):
        if 'model_pack' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'model_pack' setting"
                % (section, self.filename))
        model_pack = local_conf.pop('model_pack').split()

    def _command_app_context(self, object_type, section, name,                                                                                                                                             
                             global_conf, local_conf, global_additions):
        if 'next' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'next' setting"
                % (section, self.filename))
        next_name = local_conf.pop('next')
        context = LoaderContext(None, MODEL, None, global_conf,
                                local_conf, self)
        context.next_context = self.get_context(
            APP, next_name, global_conf)
        if 'use' in local_conf:
            context.filter_context = self._context_from_use(
                FILTER, local_conf, global_conf, global_additions,
                section)
        else:
            context.filter_context = self._context_from_explicit(
                FILTER, local_conf, global_conf, global_additions,
                section)
        return context

    def _command_pack_context(self, object_type, section, name,                                                                                                                                             
                              global_conf, local_conf, global_additions):
        if 'command_pack' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'command_pack' setting"
                % (section, self.filename))
        cmd_pack = local_conf.pop('command_pack').split()

    def _flatform_app_context(self, object_type, section, name,                                                                                                                                             
                              global_conf, local_conf, global_additions):
        pass

    def _flatform_pack_context(self, object_type, section, name,                                                                                                                                             
                               global_conf, local_conf, global_additions):
        if 'platform_pack' not in local_conf:
            raise LookupError(
                "The [%s] section in %s is missing a 'platform_pack' setting"
                % (section, self.filename))
        pf_pack = local_conf.pop('platform_pack').split()

ConfigLoader = _ConfigLoader
