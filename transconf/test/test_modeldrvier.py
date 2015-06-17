import sys 

sys.path.insert(0, sys.path[0] + '/..')

from common.model_driver import *


class UserCollection(BaseTable):
    __tablename__ = 'managers_online'

    name = StrColumn(10)
    age = StrColumn(3)
    from_country = StrColumn(20)

    def __init__(self, name, age, from_country):
        self.name = name
        self.age = age
        self.from_country = from_country

d = BaseModelDriver("mysql://root:123.com@localhost/test")
d.define_table(UserCollection)
session = d.session
session.add(UserCollection('clouduser', 10, 'shanghai'))
session.commit()
