#coding=utf-8

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

from transconf.common.model_driver import *
from transconf.utils import Exception


class InvalidData(Exception):
    """Raised when any data can not be found """


class HeartBeatIsEnabled(declarative_base()):
    __tablename__ = 'enabled_heartbeat'
    uuid = StrColumn(36)

    def __init__(self, uuid):
        self.uuid = uuid


class HeartBeatCollection(declarative_base()):
    __tablename__ = 'heartbeat'

    uuid = StrColumn(36)
    group_name = StrColumn(30)
    group_type = StrColumn(10)
    available = StrColumn(5)
    is_alive = StrColumn(5)
    count = IntColumn()

    def __init__(self, group_name, group_type, uuid, count, is_alive=False, available=True):
        self.group_name = group_name
        self.group_type = group_type
        self.uuid = uuid
        self.available = str(available)
        self.is_alive = str(is_alive)
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
        if target and target.count > 0:
            return True
        return False

    def update(self, dic_data, need_update_count=True):
        target, record = self._ready_data(dic_data)
        if target:
            if hasattr(target, 'count'):
                record.count = int(target.count)
                if need_update_count:
                    record.count += 1
                    record.is_alive = str(True)
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

    def has(self, uuid):
        target = self.session.query(HeartBeatIsEnabled).filter_by(uuid=uuid).first()
        return True if target else False

    def uuids(self):
        return [record.uuid for record in self.session.query(HeartBeatIsEnabled) if record]

    def _ready_data(self, dic_data):
        try:
            record = HeartBeatIsEnabled(**dic_data)
            target = self.session.query(HeartBeatIsEnabled).filter_by(uuid=dic_data['uuid']).first()
            return (target, record)
        except TypeError:
            raise InvalidData(record)
        except:
            return (None, record)
