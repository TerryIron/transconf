# coding=utf-8

__author__ = 'chijun'

from transconf.configration import Configuration
from transconf.server.twisted import CONF


CONFIG = Configuration(CONF)
CONFIG.add_members('heartbeats', sect='controller:heartbeat:listen:items')
CONFIG.add_members('heartbeartcenters', sect='controller:heartbeat:fanout:items')
master_group = CONFIG.add_group('master', sect='controller:heartbeat:listen')
master_group.add_property('heartrate', option='heartrate', default_val=60)
master_group.add_property('interval_times', option='interval_times', default_val=3)
master_group.add_property('sql_engine', option='connection', default_val=None)
master_group.add_property('joined_cluster', option='joined_cluster', default_val=False)
master_group.add_property('cluster_uuid', option='cluster_uuid', default_val=None)
master_group.add_property('cluster_token', option='cluster_token', default_val=None)
master_group.add_property('cluster_mode', option='cluster_mode', default_val='memory')
master_group.add_property('cluster_channel_id', option='cluster_channel_id', default_val=1)
master_group.add_property('cluster_hostname', option='cluster_hostname', default_val='rabbit@localhost')
slaver_group = CONFIG.add_group('slaver', sect='controller:heartbeat:fanout')
slaver_group.add_property('heartrate', option='heartrate', default_val=60)
slaver_group.add_property('joined_cluster', option='joined_cluster', default_val=False)
slaver_group.add_property('cluster_uuid', option='cluster_uuid', default_val=None)
slaver_group.add_property('cluster_token', option='cluster_token', default_val=None)
slaver_group.add_property('cluster_mode', option='cluster_mode', default_val='memory')
slaver_group.add_property('cluster_channel_id', option='cluster_channel_id', default_val=1)
slaver_group.add_property('cluster_hostname', option='cluster_hostname', default_val='rabbit@localhost')
manage_group = CONFIG.add_group('manage')
manage_group.add_property('group_name', option='local_group_name')
manage_group.add_property('group_type', option='local_group_type')
manage_group.add_property('group_uuid', option='local_group_uuid')


def get_available_heartbeats():
    return [uuid for uuid, is_enabled in CONFIG.heartbeats if bool(str(is_enabled).lower())]
