__author_ = 'chijun'

import cPickle as pickle

from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session as local_session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base as local_declarative_base


__all__ = ['declarative_base', 'BaseModelDriver', 'StrColumn', 'IntColumn', 'MapColumn']


class IntColumn(Column):
    def __init__(self, primary_key=False):
        super(IntColumn, self).__init__(Integer, primary_key=primary_key)


class StrColumn(Column):
    def __init__(self, length):
        super(StrColumn, self).__init__(String(length))


class MapColumn(Column):
    def __init__(self, table_name, item_name):
        super(MapColumn, self).__init__(ForeignKey('.'.join([table_name, item_name])))


class BaseMixin(object):

    @declared_attr 
    def __tablename__(cls): 
        return cls.__name__.lower()

    @declared_attr 
    def id(cls): 
        if not hasattr(cls, 'id'):
            setattr(cls, 'id', IntColumn(True))
        return cls.id

    def update_from_dict(cls, dic_data):
        return None if [setattr(cls, k, v) for k, v in dic_data.items() if getattr(cls, k, None) != v] else None

    def update(cls, table_obj):
        return cls.update_from_dict(table_obj.to_dict())

    def to_dict(cls):
        d = pickle.loads(pickle.dumps(cls.__dict__))
        d.pop('_sa_instance_state')
        return d


def declarative_base(cls=BaseMixin):
    return local_declarative_base(cls=cls)


class BaseModelDriver(object):
    """
        This class is used to register model into DB.
        
        Overview of DB table instance:

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

    def __init__(self, db_engine=None):
        #super(BaseModelDriver, self).__init__()
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
        try:
            table = Table(table_name, 
                          self.metadata,
                          autoload=True)
            return table
        except NoSuchTableError:
            pass

    """
       Create a new table

       @table_name: table name
       @items: input list by unit (title, length)
    """
    def define_table(self, table_class):
        if self.available:
            table = self.table(table_class.__tablename__)
            if not isinstance(table, Table):
                table_class.metadata.create_all(self.db_engine)

    def undefine_table(self, table_class):
        if self.available:
            table = self.table(table_class.__tablename__)
            if isinstance(table, Table):
                table_class.__table__.drop(self.db_engine)

    def clear_table(self, table_class):
        if self.available:
            table = self.table(table_class.__tablename__)
            if isinstance(table, Table):
                table_class.__table__.drop(self.db_engine)
                table_class.metadata.create_all(self.db_engine)

