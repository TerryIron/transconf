__author__ = 'chijun'

from common.model_driver import *


class InvalidData(Exception):
    """Raised when any data can not be found """


class HeartBeatCollection(BaseTable):
    __tablename__ = 'heartbeat'

    group_name = StrColumn(15)
    group_name = StrColumn(10)
    uuid = StrColumn(36)
    available = StrColumn(5)

    def __init__(self, group_name, group_type, uuid, available=False):
        self.group_name = group_name
        self.group_type = group_type
        self.uuid = uuid
        self.available = available


class HeartBeatBackend(BaseModelDriver):
    def create(self):
        self.define_table(HeartBeatCollection)

    def drop(self):
        self.undefine_table(HeartBeatCollection)

    def _ready_data(self, dic_data):
        try:
            record = HeartBeatCollection(**dic_data)
            target = self.session.query(HeartBeatCollection).filter_by(uuid=dic_data['uuid'])
            return (target, record)
        except TypeError:
            raise InvalidData(record)

    def has(self, group_name, group_type):
        target = self.session.query(HeartBeatCollection).filter_by(group_name=group_name,
                                                                   group_type=group_type)
        if target:
            return True
        else:
            return False

    def update(self, dic_data):
        target, record = self._ready_data(dic_data)
        if target:
            target.update(record)
        else:
            self.session.add(record)
        session.commit()

    def delete(self, dic_data):
        target, record = self._ready_data(dic_data)
        if target:
            target.delete()
