__author__ = 'chijun'

__all__ = ['BaseModel']


from sqlalchemy import *

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
            self.db = {}
        else:
            self.db_engine = None

    def available(self):
        if not self.db_engine:
            return False
        else:
            return True

   """
      Create a new table

      @table_name: table name
      @items: input list by unit (title, length)
   """
    def define_table(self, table_name, items):
        if self.available() and table_name not in self.db:
            table = Table(table_name, 
                          self.db_engine, 
                          Column('id', Integer, primary_key=True),
                          *[Column(iname, String(length) for iname, length in tuple(items)],
                         )  
            table.create()
            self.db[table_name] = table

    def clear_table(self, table_name):
        if self.available() and table_name in self.db:
            table = Table(table_name, 
                          self.db_engine,
                          autoload=True)
            self.db[table_name] = table

    def undefine_table(self, table_name):
        if self.available() and table_name in self.db:
            table = self.db[table_name]
            table.drop()
            self.db.pop(table_name)

   """
      Push new column into table

      @table_name: table name
      @items: input list by unit {'column_title': value}
   """

    def push_table(self, table_name, items):
        if self.available() and table_name in self.db:
            table = self.db[table_name]
            i = table.insert()
            for dic in items:
                i.execute(**dic)

   """
      Update pointed table's column by query line

      @table_name: table name
      @query_items: input list by unit (query_title, value)
      @items: input list by unit {'column_title': value}
   """
    def update_table(self, table_name, query_items, items):
        if self.available() and table_name in self.db:
            pass

   """
      Pop column from table by query line

      @table_name: table name
      @query_items: input list by unit (query_title, value)
   """
    def pop_table(self, table_name, query_items):
        if self.available() and table_name in self.db:
            pass

    def commit(self):
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
