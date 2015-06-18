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
#f = session.query(UserCollection).filter_by(name='test').first()
for i in range(1000):
    session = d.session
    u = UserCollection('test', i, 'shanghai')
    session.add(u)
    session.commit()
session.query(UserCollection).filter_by(name='test').delete()
for k, v in session.__dict__.items():
    print k, v
print dir(session)
