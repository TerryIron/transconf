__author__ = 'chijun'

import sys
import os.path

sys.path.insert(0, sys.path[0] + '/../..')

here = os.path.dirname(os.path.abspath(__file__))

from transconf.server.twisted.wsgi import TranMiddleware, TranServer, URLMiddleware
from transconf.model import Model


class TestModel(Model):
    FORM = [
        {'node': 'helloworld/{name}',
         'public': ['GET', 'mod:self:test']
         },
        {'node': 'stock/{name}',
         'public': ['GET', 'mod:self:stock']
         },
        {'node': 'abb/ccc/{name}',
         'public': ['GET', 'mod:self:stock']
         },
        {'node': 'a/c/b/{name}',
         'public': ['GET', 'mod:self:stock']
         },
    ]

    def test(self, name):
        return ['helloworld', name]

    def stock(self, name):
        if name == 'sh':
            with open('/mnt/echarts/shstock.html', 'r') as f:
                data = f.readlines()
                return data


class TestHandler(URLMiddleware):
    def __call__(self, req):
        return super(TestHandler, self).__call__(req)


class HeartHandler(TranMiddleware):
    def __call__(self, req):
        return super(HeartHandler, self).__call__(req)


if __name__ == '__main__':
    from transconf.server.paste.deploy import loadapp

    app = loadapp('config:test.ini', 
                  'main',
                  relative_to=here)
    server = TranServer()
    server.setup_mq(app['mainrpc'])
    server.setup_url(app['mainurl'])
    server.start()

