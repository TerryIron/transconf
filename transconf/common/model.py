__author__ = 'chijun'

__all__ = ['BaseModel']

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
        self.db_engine = db_engine
        super(BaseModelDriver, self).__init__()


class BaseModel(BaseModelDriver):
    STRUCT = None
    FORM = None
    SPLIT_DOT = '.'

    def __init__(self, db_engine=None):
        self._form = self.FORM
        self._struct = self.STRUCT
        self.split = self.SPLIT_DOT
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
