__author__ = 'chijun'

__all__ = ['BaseModel']

from utils import NameSpace

class DriverType(object):
    def __ini__(self, typ):
        self.name = typ

    @property
    def type(self):
        return self.name

class BaseModelDriver(TableDriver):
    TYPE = None
    NAMESPACE = None
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
        |NameBusA         ModelTypeA| FORMAT           |
        |   ||             ||       | STRUCT           |
        |   ||             ||       | TYPE as db_name  | 
        |   \/             \/       -            |     |
        |NameBus   ---- > DataBase               |     |
        |   ||             ||  /\                |     |
        |   ||             ||  ||                |     |
        |   ||             ||  -------------------     |
        |   ||             ||                          |
        |   \/             \/                          |
        |Memory(Handler)  Mysql(Data)                  |
        ------------------------------------------------

        Data                                   Handler
             | Table A -> nodeA API control            | NodeA
             | Table B -> nodeB API control            | NodeB
             | Table C -> nodeC API control            | NodeC
    """

    def __init__(self, db_engine):
        self.db_engine = db_engine
        self.database_name = DriverType(self.TYPE).type
        self.init()

    def init(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
        

@NameSpace
class BaseModel(BaseModelDriver):
    STRUCT_CLASS = None
    FORM = None

    def __init__(self, name, db_engine):
        super(BaseModel, self).__init__(db_engine)
        self.form = self.FORM
        self.struct = self.STRUCT_CLASS
        self.name = name
