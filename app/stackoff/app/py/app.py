__author__ = 'chijun'                                                                                                                                          

import sys
import os.path

sys.path.insert(0, sys.path[0] + '/..')

here = os.path.dirname(os.path.abspath(__file__))

from transconf.server.twisted.wsgi import TranServer, URLMiddleware
from transconf.model import Model
from twisted.web import client


def BuyList(lst):
    d = dict()
    i = 1
    for v in lst:
        v = v.split(':', 1)
        d['+' + str(i)] = ':'.join([v[0], str(int(v[1]) / 100)])
        i += 1
    return d


def SaleList(lst):
    d = dict()
    i = 1
    for v in lst:
        v = v.split(':', 1)
        d['-' + str(i)] = ':'.join([v[0], str(int(v[1]) / 100)])
        i += 1
    return d


class Stock(object):
    def __init__(self):
        self.code = None
        self.name = None
        self.today_start = None
        self.today_max = None
        self.buy_num = None
        self.buy_total = None
        self.today_min = None
        self.lastday_end = None
        self.current = None
        self.buylist = {}
        self.salelist = {}
        self.content = {}

    def process_content(self, content):
        content = content.split('=', 1)
        if not len(content) > 1:
            return
        content = content[1].split(',')
        if not len(content) > 1:
            return
        return content

    def __call__(self, code, content):
        content = self.process_content(content)
        if not content:
            return
        self.code = code
        self.name = content[0]
        self.today_start = content[1]
        self.lastday_end = content[2]
        self.current = content[3]
        self.today_max = content[4]
        self.today_min = content[5]
        self.buy_num = content[8]
        self.buy_total = content[9]
        self.buylist = BuyList((content[11] + ':' + content[10],
                               content[13] + ':' + content[12],
                               content[15] + ':' + content[14],
                               content[17] + ':' + content[16],
                               content[19] + ':' + content[18]
                               ))
        self.salelist = SaleList((content[21] + ':' + content[20],
                                 content[23] + ':' + content[22],
                                 content[25] + ':' + content[24],
                                 content[27] + ':' + content[26],
                                 content[29] + ':' + content[28]
                                 ))
        content = {}
        content['name'] = self.name.decode('gbk')
        content['today_start'] = self.today_start
        content['lastday_end'] = self.lastday_end
        content['current'] = self.current
        content['today_max'] = self.today_max
        content['today_min'] = self.today_min
        content['buy_num'] = self.buy_num
        content['buy_total'] = self.buy_total
        content['list'] = []
        keys = self.buylist.keys()
        keys.sort()
        for i in keys:
            i = i[1]
            content['list'].append((('+' + i, self.buylist['+' + i]), ('-' + i, self.salelist['-' + i])))
        return content


STOCK = Stock()


class TestModel(Model):
    FORM = [
        {'node': 'stackoff',
         'public': ['GET', 'mod:self:stock']
        },
        {'node': 'stackoff/get',
         'public': ['GET', 'mod:self:getdata']
        },
    ]

    def stock(self):
        with open('{0}/index.html'.format(self['document_path']), 'r') as f:
            data = f.readlines()
            return data

    @staticmethod
    def getdata(code):
        stocks = []
        for stock_code in code.split(','):
            if stock_code.startswith('6'):
                stock_code = 'sh' + stock_code
            elif stock_code.startswith('0'):
                stock_code = 'sz' + stock_code
            stocks.append(stock_code)
        code = ','.join(stocks)
        d = client.getPage('http://hq.sinajs.cn/list={0}'.format(code))
        d.addCallback(lambda content: STOCK(code, content))
        return d


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
