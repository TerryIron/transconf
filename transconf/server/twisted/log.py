#coding=utf-8

__author__ = 'chijun'

import logging

from transconf.server.twisted import get_service_conf
from transconf.utils import from_config_option

__LOG__ = None


def getLogger(name=None):
    CONF = get_service_conf()

    @from_config_option('log_path', None)
    def conf_log_path():
        return CONF

    @from_config_option('log_normal_formatter', '[%(asctime)s [%(levelname)s]] %(message)s')
    def conf_log_formatter():
        return CONF

    @from_config_option('log_debug_formatter', '[%(asctime)s [%(levelname)s] <%(module)s.py>%(funcName)s] %(message)s')
    def conf_log_debug_formatter():
        return CONF

    @from_config_option('log_debug', 'false')
    def conf_log_level():
        return CONF
    global __LOG__
    if not __LOG__:
        logger = logging.getLogger(name)
        path = conf_log_path()
        if path:
            handler = logging.FileHandler(path)
        else:
            handler = logging.StreamHandler()

        def configure(is_debug):
            if not is_debug:
                formatter = conf_log_formatter()
                logger.setLevel('INFO')
            else:
                formatter = conf_log_debug_formatter()
                logger.setLevel('DEBUG')
            handler.setFormatter(logging.Formatter(formatter))
        configure(bool(conf_log_level().lower()))
        logger.addHandler(handler)
        __LOG__ = logger
    else:
        logger = __LOG__
    return logger
