__author__ = 'chijun'

import sys
import os
import os.path
import unittest

sys.path.insert(0, sys.path[0] + '/../..')

here = os.path.dirname(os.path.abspath(__file__))

from transconf.server.twisted.wsgi import TranMiddleware, TranServer, URLMiddleware
from transconf.model import Model, Resource


class TestModel(Model):
    FORM = []

    def __init__(self):
        super(TestModel, self).__init__()

TestModel = TestModel()


@TestModel.route('helloworld/{name}', 'GET')
def test(name):
    return [name]


class Test2(Resource):
    def __init__(self, value):
        self.value = value
        super(Test2, self).__init__()

    def test_name(self, name):
        return [self.value, name]

Test2 = Test2(10)
Test2.add_rule('helloworld2/{name}', 'GET', 'test_name')
TestModel.add_resource(Test2)


class TestHandler(URLMiddleware):
    def __call__(self, req):
        return super(TestHandler, self).__call__(req)


class HeartHandler(TranMiddleware):
    def __call__(self, req):
        return super(HeartHandler, self).__call__(req)


class AppUnitTest(unittest.TestCase):
    def testAPP(self):
        from multiprocessing import Process
        import urllib
        import time

        def start_app():
            from transconf.server.paste.deploy import loadapp

            app = loadapp('config:test_route.ini',
                          'main',
                          relative_to=here)
            server = TranServer()
            server.setup_mq(app['mainrpc'])
            server.setup_app(app['mainurl'])
            server.start()

        p = Process(target=start_app)
        p.start()
        time.sleep(5)
        d = urllib.urlopen("http://127.0.0.1:9889/v1/helloworld/jack")
        text = d.read()
        self.assertIn('jack', text)
        d = urllib.urlopen("http://127.0.0.1:9889/v1/helloworld2/jack")
        text = d.read()
        self.assertIn('jack', text)
        os.kill(int(p.pid), 9)


if __name__ == '__main__':
    unittest.main()
