# coding=utf-8

__author__ = 'chijun'

from transconf.configration import Configuration
from transconf.server.twisted import CONF


CONFIG = Configuration(CONF)
CONFIG.add_members('heartbeats', sect='controller:heartbeat:listen:items')
CONFIG.add_members('heartbeartcenters', sect='controller:heartbeat:fanout:items')
master_group = CONFIG.add_group('master', sect='controller:heartbeat:listen')
master_group.add_property('heartrate', option='heartrate', default_val='60')
master_group.add_property('interval_times', option='interval_times', default_val='3')
master_group.add_property('sql_engine', option='connection', default_val=None)
slaver_group = CONFIG.add_group('slaver', sect='controller:heartbeat:fanout')
slaver_group.add_property('heartrate', option='heartrate', default_val='60')
manage_group = CONFIG.add_group('manage')
manage_group.add_property('group_name', option='local_group_name')
manage_group.add_property('group_type', option='local_group_type')
manage_group.add_property('group_uuid', option='local_group_uuid')


def get_available_heartbeats():
    return [uuid for uuid, is_enabled in CONFIG.heartbeats if bool(str(is_enabled).lower())]
