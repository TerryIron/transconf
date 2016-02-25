# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'



from transconf.utils import as_config
from transconf.server.twisted.service import serve_forever, serve_stop
from transconf.server.twisted.internet import RPCTranServer as _RPCTranServer
from transconf.server.twisted.internet import TopicTranServer as _TopicTranServer 
from transconf.server.twisted.internet import FanoutTranServer as _FanoutTranServer
from transconf.server.twisted.service import URLTranServer as _URLTranServer
from transconf.server.twisted.event import EventMiddleware
from transconf.server.twisted.url import URLMiddleware as _URLMiddleware
from transconf.server import twisted
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)


class WSGIMiddleware(object):
    @classmethod
    def factory(cls, global_config, **local_config):
        twisted.CONF = as_config(global_config['__file__'])
        sh = local_config.pop('shell') if 'shell' in local_config else None

        def _factory(app, start_response=None):
            c = cls(app, **local_config)
            if sh:
                c.handler = sh
            if hasattr(c, 'process_request'):
                return c.process_request(app)
            else:
                return c
        return _factory


class URLMiddleware(_URLMiddleware, WSGIMiddleware):
    pass


class TranMiddleware(EventMiddleware, WSGIMiddleware):
    pass


class TranWSGIServer(object):

    def setup(self, middleware):
        self.middleware = middleware

    def process_request(self, request):
        try:
            d = self.middleware(request)
            if hasattr(d, 'process_request'):
                return d.process_request(request)
            else:
                return d
        except Exception as e:
            LOG.error(e)


class RPCTranServer(TranWSGIServer, _RPCTranServer):
    pass


class TopicTranServer(TranWSGIServer, _TopicTranServer):
    pass


class FanoutTranServer(TranWSGIServer, _FanoutTranServer):
    pass


class URLTranServer(TranWSGIServer, _URLTranServer):
    pass


class TranServer(object):
    def __init__(self, pool_size=1000):
        self.pool_size = pool_size

    def setup_mq(self, app):
        for s in (RPCTranServer, TopicTranServer, FanoutTranServer):
            serve = s()
            serve.setup(app)
            serve.register()

    def setup_app(self, app, port=9889):
        serve = URLTranServer(app)
        serve.register(port)

    def start(self):
        serve_forever(pool_size=self.pool_size)

    def stop(self):
        serve_stop()

    def wait(self):
        raise NotImplementedError()
