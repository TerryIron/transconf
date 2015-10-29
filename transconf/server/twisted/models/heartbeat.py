__author__ = 'chijun'

import time

from transconf.common.reg import register_model, get_model
from transconf.model import Model
from transconf.configure import Configure
from transconf.server.twisted.internet import get_public_client
from transconf.server.twisted.event import Task, EventDispatcher
from transconf.server.twisted import CONF as global_conf
from transconf.server.twisted import get_sql_engine 
from transconf.utils import from_config, from_config_option, as_config
from transconf.utils import from_model_option, as_model_action
from transconf.server.twisted.netshell import ActionRequest
from transconf.backend.heartbeat import HeartBeatCollectionBackend, HeartBeatIsEnabledBackend

SERVER_CONF = global_conf

sql_engine = get_sql_engine()

BACKEND = HeartBeatCollectionBackend(sql_engine)

CONF_BACKEND = HeartBeatIsEnabledBackend(sql_engine)


class HeartBeatNotFound(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} can not found.'.format(group_name, group_type)

class HeartRateErr(Exception):
    def __str__(group_name, group_type):
        return 'Group name:{0}, Group type:{1} got a invalid heartrate.'.format(group_name, group_type)


CONFIG = Configure(SERVER_CONF)
CONFIG.add_members('heartbeats', sect='controller:heartbeat:listen', avoid_options='heartrate')
CONFIG.add_members('heartbeartcenters', sect='controller:heartbeat:fanout', avoid_options='heartrate')
master_group = CONFIG.add_group('master', sect='controller:heartbeat:listen')
master_group.add_property('heartrate', option='heartrate', default_val='60')
slaver_group = CONFIG.add_group('slaver', sect='controller:heartbeat:fanout')
slaver_group.add_property('heartrate', option='heartrate', default_val='60')
manage_group = CONFIG.add_group('manage')
manage_group.add_property('group_name', option='local_group_name')
manage_group.add_property('group_type', option='local_group_type')
manage_group.add_property('group_uuid', option='local_group_uuid')


@register_model('heartbeat')                                                                                                                                                                    
class HeartBeat(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'alive', 'dead'
    # Ver: (0, 1, 1) by chijun
    # 1 add get_fanout_members
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heart',
             'public': ['alive', 'mod:heartbeat:heartbeat'],
            }
    ]

    #@as_model_action('mycmd', 'heartcondition_register')
    #def _register_actions(self, config):
    #    return config

    #@property
    #@from_config(sect='controller:heartbeat:fanout')
    #def _conf_group_names(self):
    #    return SERVER_CONF

    #@property
    #@from_config_option('local_group_name', None)
    #def _conf_group_name(self):
    #    return SERVER_CONF

    #@property
    #@from_config_option('local_group_type', None)
    #def _conf_group_type(self):
    #    return SERVER_CONF

    #@property
    #@from_config_option('local_group_uuid', None)
    #def _conf_group_uuid(self):
    #    return SERVER_CONF

    #@property
    #@from_config_option('heartrate', 60, sect='controller:heartbeat:fanout')
    #def _conf_heartrate(self):
    #    return SERVER_CONF

    def get_fanout_members(self):
        #for g_option, is_enabled in self._conf_group_names:
        for g_option, is_enabled in CONFIG.heartbeartcenters:
            g = g_option.split('.')
            if (len(g) > 1) and ((is_enabled and g_option) not in self.UNEXPECTED_OPTIONS):
                yield (g[0], g[1], is_enabled)  

    def init(self, config=None):
        self.CONFIG = Configure(config)
        command_group = self.CONFIG.add_group('command_group', sect='model_action')
        command_group.add_property('heartbeat', option='heartbeat')
        
    def start(self, config=None):
        self.is_start = None
        #if self._register_actions(config):
            #self.heartbeat(int(self._conf_heartrate))
        self.heartbeat(int(CONFIG.slaver.heartrate))

    def heartbeat(self, timeout):
        # Check if has call heartbeat event-loop, don't call it again.
        if self.is_start:
            return True
        self.is_start = True
        #local_name = self._conf_group_name
        #local_type = self._conf_group_type
        #local_uuid = self._conf_group_uuid
        local_name = CONFIG.manage.group_name
        local_type = CONFIG.manage.group_type
        local_uuid = CONFIG.manage.group_uuid
        if local_name and local_type and local_uuid:
            for g_name, typ, is_enabled in self.get_fanout_members():
                client = get_public_client(g_name, typ, type='fanout')
                req = ActionRequest(self.CONFIG.command_group.heartbeat,
                #req = ActionRequest(self.mycmd['heartcondition_register'],
                                    dict(group_name=local_name, 
                                         uuid=local_uuid,
                                         available=str(True),
                                         group_type=local_type))
                event = EventDispatcher(client, req, need_close=False)
                t = Task(lambda: event.startWithoutResult())
                t.LoopingCall(timeout)


@register_model('heartcondition')                                                                                                                                                                    
class HeartCondition(Model):
    # Ver: (0, 1, 0) by chijun
    # 1 add outbound method 'has', 'register'
    # Ver: (0, 1, 1) by chijun
    # 1 add '_update_target', '_check_target', '_check_target_is_init'
    # 2 add '_check_heart_still_alive', '_check_has_available_targets'
    UNEXPECTED_OPTIONS = ['heartrate']
    FORM = [{'node': 'heartcond',
             'public': [
                        ['has', 'mod:heartcondition:has_heartbeat'],
                        ['add', 'mod:heartcondition:add_heartbeat'],
                        ['remove', 'mod:heartcondition:remove_heartbeat'],
                        ['checkin', 'mod:heartcondition:checkin'],
                       ]
            }
    ]

    #@property
    #@from_config_option('heartrate', 60, sect='controller:heartbeat:listen')
    #def _conf_heartrate(self):
    #    return SERVER_CONF

    def start(self, config=None):
        # Re-initialize sql table
        self._target_init()
        self._timestamp_init()
        configure_heartcondition()
        self.buf_available_uuid = CONF_BACKEND.uuids()

    def _check_heart_still_alive(self, group_name, group_type, uuid):
        #heartrate = self._conf_heartrate
        heartrate = CONFIG.master.heartrate
        cur_time = time.time()
        #Check this heartbeat was timeout?
        if int(cur_time - self._timestamp[uuid]) > int(heartrate):
            # Maybe heartbeat is lost?
            self._update_target(group_name, group_type, uuid, False, False)
            self._check_has_available_targets(group_name, group_type)

    def _check_heart_health(self, group_name, group_type, uuid):
        #heartrate = self._conf_heartrate
        heartrate = CONFIG.master.heartrate
        if uuid not in self._timestamp:
            self._timestamp[uuid] = time.time()
            return True
        else:
            cur_time = time.time()
            if int(cur_time - self._timestamp[uuid]) >= (int(heartrate) - 1):
                return cur_time
        raise HeartRateErr(group_name, group_type)

    def _target_init(self):
        if not hasattr(self, 'buf_group_target'):
            setattr(self, 'buf_group_target', {})

    def _timestamp_init(self):
        if not hasattr(self, '_timestamp'):
            setattr(self, '_timestamp', {})

    def _check_target(self, group_name, group_type):
        if not self.buf_group_target.get(group_name + '_' + group_type, None):
            return False
        return True

    def _update_target(self, group_name, group_type, uuid, available, need_count=True):
        BACKEND.update(dict(group_name=group_name,
                            group_type=group_type,
                            uuid=uuid,
                            available=str(available)),
                       need_count)

    def _check_has_available_targets(self, group_name, group_type):
        #Check if it has available uuid of group target? 
        if BACKEND.has(group_name, group_type):
            self.buf_group_target[group_name + '_' + group_type] = True
        else:
            self.buf_group_target[group_name + '_' + group_type] = False

    def checkin(self, context, heartrate=60, timeout=5):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        uuid = context.get('uuid', None)
        available = context.get('available', None) or False
        if group_name and group_type and uuid:
            try:
                cur_time = self._check_heart_health(group_name, group_type, uuid)
                if uuid not in self.buf_available_uuid:
                    #Heartbeat is not in enabled range.
                    return 
                self._timestamp[uuid] = cur_time
            except HeartRateErr:
                return 
            except:
                return 
        self._update_target(group_name, group_type, uuid, available)
        self._check_has_available_targets(group_name, group_type)
        t = Task(lambda:  self._check_heart_still_alive(group_name, group_type, uuid))
        t.CallLater(heartrate + timeout)

    def has_heartbeat(self, context):
        group_name = context.get('group_name', None)
        group_type = context.get('group_type', None)
        if not (group_name or group_type) \
            or not self._check_target(group_name, group_type):
            return False
        return True

    def add_heartbeat(self, context):
        uuid = context.get('uuid', None)
        if uuid not in CONF_BACKEND.uuids():
            CONF_BACKEND.update(dict(uuid=uuid))
            self.buf_available_uuid = CONF_BACKEND.uuids()

    def remove_heartbeat(self, context):
        uuid = context.get('uuid', None)
        if uuid in CONF_BACKEND.uuids():
            CONF_BACKEND.delete(dict(uuid=uuid))
            self.buf_available_uuid = CONF_BACKEND.uuids()


def if_available(group_name, group_type):
    def _if_available(func):
        def __if_available(*args, **kwargs):
            m = get_model('heartcondition')
            if m and m.has_heartbeat(dict(group_name=group_name, 
                                          group_type=group_type)):
                return func(*args, **kwargs)
            else:
                raise HeartBeatNotFound(group_name, group_type)
        return __if_available
    return _if_available


def configure_heartcondition():
    CONF_BACKEND.create()
    CONF_BACKEND.clear()
    BACKEND.create()
    BACKEND.clear()
    #@from_config(sect='controller:heartbeat:listen')
    #def get_heartbeat_members():
    #    return SERVER_CONF
    #for uuid, is_enabled in get_heartbeat_members():
    for uuid, is_enabled in CONFIG.heartbeats:
        #if str(is_enabled).lower() == 'true' and uuid not in HeartCondition().UNEXPECTED_OPTIONS:
        if str(is_enabled).lower() == 'true':
            CONF_BACKEND.update(dict(uuid=uuid))
