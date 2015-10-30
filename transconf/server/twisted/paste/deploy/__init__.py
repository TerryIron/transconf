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


class _ModelPipeLine(_PipeLine):
    name = 'modelpipeline'
    config_prefixes = ['model']

MODELPIPELINE = _ModelPipeLine()
        

class _Model(_FilterApp):
    name = 'model'
    config_prefixes = ['model']

MODEL = _Model()


class _CommandPipeLine(_PipeLine):
    name = 'commandpipeline'
    config_prefixes = ['commandpipeline']

COMMANDPIPELINE = _CommandPipeLine()


class _Command(_FilterApp):
    name = 'command'
    config_prefixes = ['command']

COMMAND = _Command()


class _ConfigLoader(ConfigLoader):
    pass

ConfigLoader = _ConfigLoader
