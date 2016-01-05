# coding=utf-8

__author__ = 'chijun'

import os
import copy
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from twisted.internet.base import defer


class Parser(object):
    def __init__(self):
        self.struct = {}
        self.driver = webdriver.PhantomJS()

    def init(self, **kwargs):
        pass

    @classmethod
    def factory(cls, **stock_dic):
        def __wrap(**kwargs):
            app = cls()
            app.struct.update(stock_dic)
            app.init(**kwargs)
            return app
        return __wrap

    def pullData(self, data):
        new_data = copy.copy(self.struct)
        for k in new_data.keys():
            new_data[k] = data.get(k, '')
        return new_data

    def getAPI(self, code):
        raise NotImplementedError()

    def getContent(self, code):
        d = defer.succeed({})
        d.addCallback(lambda r: self.driver.get(self.getAPI(code)))
        d.addCallback(lambda r: self.driver.find_element_by_tag_name('body'))
        return d

    def processContent(self, content):
        if not isinstance(content, WebElement):
            raise Exception('Parse Error')
        return content

    def process(self, url):
        d = self.getContent(url)
        d.addCallback(lambda content: self.processContent(content))
        d.addCallback(lambda data: self.pullData(data))
        return d


class WYParser(Parser):
    def getAPI(self, code):
        code = str(code)
        if code.startswith('6'):
            return "http://quotes.money.163.com/0{0}.html#9b01".format(code)
        elif code.startswith('0'):
            return "http://quotes.money.163.com/1{0}.html#2u01".format(code)

    def processContent(self, content):
        content = super(WYParser, self).processContent(content)
        elements = [e.text.split(" ") for e in content.find_elements_by_tag_name('tr') if len(e.text.split(" ")) > 2]
        _name, _code, _current, _change, _changePer = elements[1][0].split("\n")[:]
        _todayStart, _lastEnd = elements[1][1].split("\n")[:]
        _high, _low = elements[1][2].split("\n")[:]
        _volume, _trade = elements[1][3].split("\n")[:]
        _volumePer, _tradeChange = elements[1][4].split("\n")[0:2]
        data = dict(base=dict(name=_name,
                              code=_code,
                              current=_current,
                              change=_change,
                              changePer=_changePer,
                              todayStart=_todayStart.encode('ascii', 'ignore'),
                              lastEnd=_lastEnd.encode('ascii', 'ignore'),
                              high=_high.encode('ascii', 'ignore'),
                              low=_low.encode('ascii', 'ignore'),
                              volume=_volume.encode('ascii', 'ignore'),
                              trade=_trade.encode('ascii', 'ignore'),
                              volumePer=_volumePer.encode('ascii', 'ignore'),
                              tradeChange=_tradeChange.encode('ascii', 'ignore'),
                              marketPrice=elements[1][6].encode('ascii', 'ignore'),
                              tradePer=elements[1][7].encode('ascii', 'ignore'),
                              yearHigh=elements[1][8].encode('ascii', 'ignore')[2:],
                              yearLow=elements[1][9].encode('ascii', 'ignore')[2:],
                              ),
                    trade=dict(tradeIn_1=elements[9][1:],
                               tradeIn_2=elements[10][1:],
                               tradeIn_3=elements[11][1:],
                               tradeIn_4=elements[12][1:],
                               tradeIn_5=elements[13][1:],
                               tradeOut_1=elements[8][1:],
                               tradeOut_2=elements[7][1:],
                               tradeOut_3=elements[6][1:],
                               tradeOut_4=elements[5][1:],
                               tradeOut_5=elements[4][1:],
                               )
                    )
        return data


class Stock(object):
    def __init__(self, parser, **kwargs):
        self.parser = parser()
        self.parser.init(**kwargs)

    def __call__(self, code):
        return self.parser.process(code)


STOCK_DATA = dict(base=None,
                  trade=None
                  )
STOCK = Stock(WYParser.factory(**STOCK_DATA))


def getStockData(code):
    return STOCK(code)
