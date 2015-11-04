__author__ = 'chijun'

import sys
import os.path

sys.path.insert(0, sys.path[0] + '/../..')

here = os.path.dirname(os.path.abspath(__file__))

from transconf.server.twisted.wsgi import TranMiddleware, TranServer

class HeartHandler(TranMiddleware):
    def __call__(self, req):
        return super(HeartHandler, self).__call__(req)

if __name__ == '__main__':
    from transconf.server.paste.deploy import loadapp

    app = loadapp('config:test.ini', 
                  'main',
                  relative_to=here)
    server = TranServer('compute', app)
    server.start()

