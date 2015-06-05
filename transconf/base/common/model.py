__author__ = 'chijun'

__all__ = ['BaseModel']

from utils import NameSpace

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
        self.database_name = self.TYPE

@NameSpace
class BaseModel(BaseModelDriver):
    FORMAT = None
    STRUCT_CLASS = None

    def __init__(self, name, db_engine):
        super(BaseModel, self).__init__(db_engine)
        self.name = name
