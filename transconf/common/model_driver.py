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


__author_ = 'chijun'

try:
    import cPickle as pickle
except:
    import pickle

from urlparse import urlparse, urlunparse
from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import session as local_session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base as local_declarative_base


__all__ = ['declarative_base', 'BaseModelDriver', 'BaseBackend',
           'make_connection', 'StrColumn', 'IntColumn', 'MapColumn']


class IntColumn(Column):
    """
    数字列
    """
    def __init__(self, primary_key=False, **kwargs):
        super(IntColumn, self).__init__(Integer, primary_key=primary_key)


class StrColumn(Column):
    """
    字母列
    """
    def __init__(self, length, **kwargs):
        super(StrColumn, self).__init__(String(length))


# Don't use it in BaseMixin
class MapColumn(Column):
    """
    映射列
    """
    def __init__(self, table_name, item_name, **kwargs):
        super(MapColumn, self).__init__(ForeignKey('.'.join([table_name, item_name])))


class BaseMixin(object):
    """
    列表工厂
    """

    @declared_attr
    def __tablename__(cls):
        """

        Returns:
            str: 列表名

        """
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = IntColumn(primary_key=True)

    def _update_from_dict(cls, dic_data):
        """
        从字典更新表

        Args:
            dic_data(dict): 字典输入

        Returns:
            None

        """
        return None if [setattr(cls, k, v) for k, v in dic_data.items() if
                        hasattr(cls, k) and getattr(cls, k, None) != v] else None

    def update(cls, table_obj):
        """
        更新表

        Args:
            dic_data(dict): 字典输入

        Returns:
            None

        """
        return cls._update_from_dict(table_obj.to_dict())

    def to_dict(cls):
        """
        生成字典

        Returns:
            dict: 字典

        """
        d = pickle.loads(pickle.dumps(cls.__dict__))
        d.pop('_sa_instance_state')
        return d


def declarative_base(cls=BaseMixin):
    return local_declarative_base(cls=cls)


def make_connection(db_url, need_split=False):
    o_items = urlparse(db_url)
    if o_items.path:
        if need_split:
            database = o_items.path.split('/')[-1]
            n_items, n_items[2] = list(o_items), ''
            db_engine = create_engine(urlunparse(n_items))
            return db_engine, database
        else:
            return create_engine(db_url)


class BaseModelDriver(object):
    """
    模型后端数据库
    后端数据库概况图：

        VirtHomeInstance
          ||
          \/
    ------------------------------------------------
    |                 BaseModelDriver              |
    |                  ||                          |
    |                  \/       _                  |
    |NameBusA         ModelTypeA| FORM             |
    |   ||             ||       | STRUCT           |
    |   \/             \/       -                  |
    |NameBus   ---- > DataBase                     |
    |   ||             ||                          |
    |   ||             ||                          |
    |   ||             ||                          |
    |   ||             ||                          |
    |   \/             \/                          |
    |Memory(Handler)  Mysql(Data)                  |
    ------------------------------------------------

    Data                                   Handler
         | Table A -> nodeA API control            | NodeA
         | Table B -> nodeB API control            | NodeB
         | Table C -> nodeC API control            | NodeC
    """

    def __init__(self, db_engine_obj):
        self.metadata = None
        self._session = None
        if isinstance(db_engine_obj, str):
            db_engine, database = make_connection(db_engine_obj, need_split=True)
            self.installModule(db_engine, database)
            self.make_session(db_engine)
            self.db_engine = db_engine
        else:
            self.make_session(db_engine_obj)
            self.db_engine = db_engine_obj

    def make_session(self, db_engine):
        self.metadata = MetaData(db_engine)
        self._session = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=db_engine)
        )

    @staticmethod
    def installModule(db_engine, database):
        conn = db_engine.connect()
        conn.execute("COMMIT")
        # Do not substitute user-supplied database names here.
        try:
            conn.execute("CREATE DATABASE %s" % database)
        except:
            pass
        conn.close()

    @property
    def session(self):
        return self._session()

    def getTable(self, name):
        """
        获取表

        Args:
            name(str): 表对象

        Returns:
            object: 表对象

        """
        try:
            table = Table(name,
                          self.metadata,
                          autoload=True)
            return table
        except NoSuchTableError:
            pass

    def hasTable(self, table_class):
        table = self.getTable(table_class.__tablename__)
        if not isinstance(table, Table):
            return False
        return True

    def defineTable(self, table_class):
        """
        创建表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if not self.hasTable(table_class):
            table_class.metadata.create_all(self.db_engine)

    def undefineTable(self, table_class):
        """
        删除表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if self.hasTable(table_class):
            table_class.__table__.drop(self.db_engine)

    def clearTable(self, table_class):
        """
        清空表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if self.hasTable(table_class):
            table_class.__table__.drop(self.db_engine)
        table_class.metadata.create_all(self.db_engine)


class BaseBackend(BaseModelDriver):
    __tableclass__ = None

    def create(self):
        self.defineTable(self.__tableclass__)

    def drop(self):
        self.undefineTable(self.__tableclass__)

    def clear(self):
        self.clearTable(self.__tableclass__)

    def get(self, dict_data):
        return self.session.query(self.__tableclass__).filter_by(**dict_data).all()

    def update(self, data_set, new_data, limit=1000):
        data_set = data_set if isinstance(data_set, list) else [data_set]
        for i, data in enumerate(data_set[::limit]):
            data = data_set[i*limit:i*limit + limit]
            for d in data:
                self.session.query(self.__tableclass__).filter_by(**d).update(new_data)

    def add(self, data_set, limit=1000):
        data_set = data_set if isinstance(data_set, list) else [data_set]
        for i, data in enumerate(data_set[::limit]):
            data = data_set[i*limit:i*limit + limit]
            for d in data:
                record = self.__tableclass__(**d)
                self.session.add(record)
            self.session.commit()

    def delete(self, data_set, limit=1000):
        data_set = data_set if isinstance(data_set, list) else [data_set]
        for i, data in enumerate(data_set[::limit]):
            data = data_set[i*limit:i*limit + limit]
            for d in data:
                self.session.query(self.__tableclass__).filter_by(**d).delete()
