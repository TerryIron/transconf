__author__ = 'chijun'

from transconf.common.model_driver import *


class InvalidData(Exception):
    """Raised when any data can not be found """


class HeartBeatIsEnabled(BaseTable):
    __tablename__ = 'enabled_heartbeat'
    uuid = StrColumn(36)

    def __init__(self, uuid):
        self.uuid = uuid


class HeartBeatCollection(BaseTable):
    __tablename__ = 'heartbeat'

    group_name = StrColumn(30)
    group_type = StrColumn(10)
    uuid = StrColumn(36)
    available = StrColumn(5)
    count = IntColumn()

    def __init__(self, group_name, group_type, uuid, available, count):
        self.group_name = group_name
        self.group_type = group_type
        self.uuid = uuid
        self.available = available
        self.count = count


class HeartBeatCollectionBackend(BaseModelDriver):
    def create(self):
        self.define_table(HeartBeatCollection)

    def drop(self):
        self.undefine_table(HeartBeatCollection)

    def clear(self):
        self.clear_table(HeartBeatCollection)

    def _ready_data(self, dic_data):
        try:
            dic_data['count'] = 0
            record = HeartBeatCollection(**dic_data)
            target = self.session.query(HeartBeatCollection).filter_by(uuid=dic_data['uuid']).first()
            return (target, record)
        except TypeError:
            raise InvalidData(record)
        except:
            return (None, None)

    def has(self, group_name, group_type):
        target = self.session.query(HeartBeatCollection).filter_by(group_name=group_name,
                                                                   group_type=group_type,
                                                                   available=str(True)).first()
        return True if target else False

    def update(self, dic_data):
        target, record = self._ready_data(dic_data)
        if target:
            if hasattr(target, 'count'):
                record.count = int(target.count) + 1
            target.update(record)
        else:
            self.session.add(record)
        self.session.commit()

    def delete(self, dic_data):
        target, record = self._ready_data(dic_data)
        if target:
            target.delete()


class HeartBeatIsEnabledBackend(HeartBeatCollectionBackend):
    def create(self):
        self.define_table(HeartBeatIsEnabled)

    def drop(self):
        self.undefine_table(HeartBeatIsEnabled)

    def clear(self):
        self.clear_table(HeartBeatIsEnabled)

    def has(self, group_uuid):
        target = self.session.query(HeartBeatIsEnabled).filter_by(group_uuid=group_uuid).first()
        return True if target else False

    def _ready_data(self, dic_data):
        try:
            record = HeartBeatIsEnabled(**dic_data)
            target = self.session.query(HeartBeatIsEnabled).filter_by(uuid=dic_data['uuid']).first()
            return (target, record)
        except TypeError:
            raise InvalidData(record)
        except:
            return (None, record)
