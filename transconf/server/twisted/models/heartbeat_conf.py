# coding=utf-8

__author__ = 'chijun'

from transconf.configration import Configuration
from transconf.server.twisted import CONF as global_conf
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend


SERVER_CONF = global_conf


CONFIG = Configuration(SERVER_CONF)
CONFIG.add_members('heartbeats', sect='controller:heartbeat:listen', avoid_options='heartrate')
CONFIG.add_members('heartbeartcenters', sect='controller:heartbeat:fanout', avoid_options='heartrate')
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


BACKEND = HeartBeatCollectionBackend(master_group.sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(master_group.sql_engine)


def configure_heartcondition():
    CONF_BACKEND.create()
    CONF_BACKEND.clear()
    BACKEND.create()
    BACKEND.clear()
    for uuid, is_enabled in CONFIG.heartbeats:
        if str(is_enabled).lower() == 'true':
            CONF_BACKEND.update(dict(uuid=uuid))
