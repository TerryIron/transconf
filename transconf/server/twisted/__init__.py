import os

from transconf.utils import from_config_option, as_config

CONF = as_config(os.path.join(os.path.dirname(__file__), 'default.ini'))


@from_config_option('connection', None, sect='database')
def get_sql_engine():
    return CONF


def get_service_conf(config=None):
    if isinstance(config, CONF.__class__):
        return config
    return CONF
