__author__ = 'chijun'

from common.model_driver import *


class DataNotFound(Exception):
    """Raised when any data can not be found """

class HeartBeatCollection(BaseTable):
    __tablename__ = 'heartbeat'

    host = StrColumn(15)
    available = StrColumn(5)
    is_used = StrColumn(5)
    heartbeat_count = IntColumn()
    cpu_cost = IntColumn()

    def __init__(self, host, available, is_used, heartbeat_count, cpu_cost):
        if host and \ 
           available and \
           is_used and \
           heartbeat_count and \
           cpu_cost:
            self.host = host
            self.available = available
            self.is_used = is_used
            self.heartbeat_count = heartbeat_count
            self.cpu_cost = cpu_cost
        else:
            raise DataNotFound()


class HeartBeatBackend(BaseModelDriver):
    def create_all_tables(self):
        self.define_table(HeartBeatCollection)

    def drop_all_tables(self):
        self.undefine_table(HeartBeatCollection)

    def register_heart(self, dic_data):
        try:
            heart= HeartBeatCollection(**dic_data)
            host = self.session.query(HeartBeatCollection).filter_by(host=dic_data['host']).first()
            if not host:
                session = self.session
                session.add(heart)
                session.commit()
        except e as DataNotFound:
            raise e

    def update_heart_status(self, dic_data):
        try:
            heart= HeartBeatCollection(**dic_data)
            host = self.session.query(HeartBeatCollection).filter_by(host=dic_data['host']).first()
            if host:
                host.update(heart)
                session.commit()
        except e as DataNotFound:
            raise e
