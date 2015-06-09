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

    def __init__(self, config, db_engine=None):
        self._form = self.FORM
        self._struct = self.STRUCT
        super(BaseModel, self).__init__(db_engine)
        self.init(config)

    @property
    def form(self):
        return self._form
        
    @property
    def struct(self):
        return self._struct

    def init(self, config):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
