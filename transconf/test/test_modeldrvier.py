import sys 

sys.path.insert(0, sys.path[0] + '/..')

from common.model import BaseModelDriver


d = BaseModelDriver("mysql://root:123.com@localhost/test")
d.define_table('managers_online', [('name', 10), ('age', 3), ('from_country', 20)])
d.push_table('managers_online', [{'name': 'clouduser', 'age': '10', 'from_country': 'shanghai'}])
d.push_table('managers_online', [{'name': 'clouduser', 'age': 10, 'from_country': 'shanghai'}])
