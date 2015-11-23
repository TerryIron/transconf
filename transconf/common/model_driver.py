__author_ = 'chijun'

try:
    import cPickle as pickle
except:
    import pickle

from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import session as local_session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base as local_declarative_base


__all__ = ['declarative_base', 'BaseModelDriver', 'StrColumn', 'IntColumn', 'MapColumn']


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
        return None if [setattr(cls, k, v) for k, v in dic_data.items() if hasattr(cls, k) and getattr(cls, k, None) != v] else None

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

"""
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


class BaseModelDriver(object):
    """
    模型后端数据库

    """

    def __init__(self, db_engine=None):
        """
        初始化

        Args:
            db_engine: 数据库地址

        Returns:
            object: 数据库对象

        """
        if db_engine:
            self.db_engine = create_engine(db_engine)
            self.metadata = MetaData(self.db_engine)
            self._session = scoped_session(
                                sessionmaker(
                                    autocommit=False,
                                    autoflush=False,
                                    bind=self.db_engine)
                                )
            self._is_available = True
        else:
            self._is_available = False

    @property
    def session(self):
        return self._session()

    @property
    def available(self):
        return self._is_available

    def table(self, table_name):
        """
        获取表

        Args:
            table_name(str): 表对象

        Returns:
            object: 表对象

        """
        try:
            table = Table(table_name,
                          self.metadata,
                          autoload=True)
            return table
        except NoSuchTableError:
            pass

    def define_table(self, table_class):
        """
        创建表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if self.available:
            table = self.table(table_class.__tablename__)
            if not isinstance(table, Table):
                table_class.metadata.create_all(self.db_engine)

    def undefine_table(self, table_class):
        """
        删除表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if self.available:
            table = self.table(table_class.__tablename__)
            if isinstance(table, Table):
                table_class.__table__.drop(self.db_engine)

    def clear_table(self, table_class):
        """
        清空表

        Args:
            table_name(str): 表对象

        Returns:
            None

        """
        if self.available:
            table = self.table(table_class.__tablename__)
            if isinstance(table, Table):
                table_class.__table__.drop(self.db_engine)
                table_class.metadata.create_all(self.db_engine)

