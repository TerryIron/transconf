__author__ = 'chijun'                                                                                                                                          

import sys
import os.path

sys.path.insert(0, sys.path[0] + '/..')

here = os.path.dirname(os.path.abspath(__file__))

from transconf.server.twisted.wsgi import TranServer, URLMiddleware
from transconf.model import Model
from exchange import getStockData


class TestModel(Model):
    FORM = [
        {'node': 'stackoff',
         'public': ['GET', ('mod', 'self', 'stock')]
        },
        {'node': 'stackoff/get',
         'public': ['GET', ('mod', 'self', 'getdata')]
        },
    ]

    def stock(self):
        with open('{0}/index.html'.format(self['document_path']), 'r') as f:
            data = f.readlines()
            return data

    @staticmethod
    def getdata(code):
        return getStockData(code)


class TestHandler(URLMiddleware):
    def __call__(self, req):
        return super(TestHandler, self).__call__(req)


if __name__ == '__main__':
    from transconf.server.paste.deploy import loadapp

    app = loadapp('config:app.ini',
                  'main',
                  relative_to=here)
    server = TranServer()
    server.setup_app(app['mainurl'])
    server.start()
