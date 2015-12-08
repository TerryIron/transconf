__author__ = 'chijun'


from transconf.server.twisted.wsgi import TranMiddleware
from transconf.server.crypto import Crypto
from transconf.utils import Exception


class RSAAuthorizeFailed(Exception):
    pass


class RSACheckout(TranMiddleware, Crypto):
    def process_request(self, context):
        context = self.decode(context)
        if context:
            return context
        else:
            raise RSAAuthorizeFailed()
