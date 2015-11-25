#coding=utf-8

__author__ = 'chijun'

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.server.twisted.internet import get_client
from transconf.server.twisted.event import Task, EventDispatcher
from transconf.server.twisted import get_sql_engine
from transconf.utils import from_config, from_config_option, as_config
from transconf.utils import from_model_option, as_model_action
from transconf.server.twisted.netshell import ActionRequest
from transconf.backend.compute import ComputeResource


@register_model('compute_resource')
class Compute(Model):
    pass
