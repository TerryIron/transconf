__author__ = 'chijun'

__all__ = ['BaseModel']


from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from namebus import NameBus


class BaseModelDriver(NameBus):
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
        super(BaseModelDriver, self).__init__()
        if db_engine:
            self.db_engine = create_engine(db_engine)
            self.metadata = MetaData(self.db_engine)
            self._session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.metadata,
                )
            )
            self._is_available = True
        else:
            self._is_available = False

    @property
    def session(self):
        return self._session

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
    def define_table(self, table_name, items):
        if self.available:
            table = self.table(table_name)
            if not isinstance(table, Table):
                table = Table(table_name, 
                              self.metadata, 
                              Column('id', Integer, primary_key=True),
                              *[Column(str(iname), String(int(length))) for iname, length in tuple(items)])  
                table.create()

    def undefine_table(self, table_name):
        if self.available:
            table = self.table(table_name)
            if isinstance(table, Table):
                table.drop()

    """
       Push new column into table

       @table_name: table name
       @items: input list by unit {'column_title': value}
    """
    def push_table(self, table_name, items):
        if self.available:
            table = self.table(table_name)
            if isinstance(table, Table):
                i = table.insert()
                i.execute(*[dic for dic in items if isinstance(dic, dict)])

    """
       Update pointed table's column by query line

       @table_name: table name
       @query_items: input list by unit (query_title, value)
       @items: input list by unit {'column_title': value}
    """
    def update_table(self, table_name, query_items, items):
        if self.available:
            pass

    """
       Pop column from table by query line

       @table_name: table name
       @query_items: input list by unit (query_title, value)
    """
    def pop_table(self, table_name, query_items):
        if self.available:
            pass

    def clear_table(self, table_name):
        if self.available:
            pass


class BaseModel(BaseModelDriver):
    STRUCT = None
    FORM = None
    SPLIT_DOT = '.'
    MEMBER_SPLIT_DOT = ':'

    def __init__(self, db_engine=None):
        self._form = self.FORM
        self._struct = self.STRUCT
        self.split = self.SPLIT_DOT
        self.member_split = self.MEMBER_SPLIT_DOT
        # First init db module
        super(BaseModel, self).__init__(db_engine)

    def _build_class_nodename(self, lst):
        return self.split.join(lst)

    def set_node_member(self, name_lst, key, value):
        real_name = self._build_class_nodename(name_lst)
        if real_name in self.namebus:
            n = self.get_namebus(real_name)
            if isinstance(n, dict):
                n[key] = value
                return True
        return False

    def set_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        self.set_namebus(real_name, {})

    def get_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        return self.get_namebus(real_name)

    def run(self, target_name, method_name, *args, **kwargs):
        raise NotImplementedError()

    @property
    def form(self):
        return self._form
        
    @property
    def struct(self):
        return self._struct

    # Init libaray or drivers from config before use it.
    def init(self, config=None):
        pass

    def start(self, config=None):
        pass

    def stop(self, config=None):
        pass
