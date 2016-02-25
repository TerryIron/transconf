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
