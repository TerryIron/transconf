__author__ = 'chijun'

import rsa
import zlib
import os.path

from transconf.utils import from_config_option
from transconf.server.twisted import CONF as global_conf
from transconf.server.twisted.log import getLogger

LOG = getLogger(__name__)

SSL_PRIVATE_PEM = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----

"""

SSL_PUBLIC_PEM = """
-----BEGIN RSA PUBLIC KEY-----
MIICCgKCAgEAq/noz1PLh36vwU2z9/Q+7YGWgywnRAH7wCDufrgI34sKHG/OwXMb
ND0eISeFhmDz6iLKQ8P12o4wysZDCrIch+PZph9Q6UPOmtlNPhGcxhnL5pthgRxI
7xufLRCdmekAUPhU2DP5rXLog/qg2FJgvbR618qM+yDfUv8kuFoJ1vzZKuptWCJd
G7mDFoXkFqFVFAODhgxEOfOZ1U9gQaKv2lA0ae1oFgKzP9qaCCpw1I0QwDIw0MzQ
X9C7vQoYTERiaqsabmy0+0pN6fD4kkmLndsrdeBpGcTtt4yDtD23xJfCSOuAiIw7
j5+wYwpFBJo5wgbyC/4KeFsKnSfETjDbsU/bXNWivJsSddFuvUZSrdl6EWEqmx1L
CwrQzVgjSq5gaZlvlxQ8Khewej+OzdNNPmX0aGaNHJl1e7iE91Nn4YL3QTlA3hog
MTF/gTduVQVoEujZGFM45hXf5/qEZyCgDRmdpdtCwmMHbtuVxq7ONQOgTRWrX+cf
I15b4kiNEsWGDUzpyliocKBD7reidYwMGbYiwA4CB0aZii5W5A7/e5xi5P5buqvL
tBNIVrAMcjXojcTqXRMjVlVBP2f01UacImEFyTsQwKYbdMVK6npYXZLUrcg+G+uX
rWLSSKJSM3wQma8GBHx3zWB/8nL3EgrjIkcBwKGo0/FiNT5ENLJyfdkCAwEAAQ==
-----END RSA PUBLIC KEY-----
"""


class Crypto(object):
    """
    加密处理对象

    """

    @property
    @from_config_option('ssl_private_pem', SSL_PRIVATE_PEM)
    def private_pem(self):
        """
        Returns:
            私有钥匙

        """
        return global_conf

    @property
    @from_config_option('ssl_public_pem', SSL_PUBLIC_PEM)
    def public_pem(self):
        """
        Returns:
            公有钥匙

        """
        return global_conf

    @property
    def local_private_pem(self):
        """
        Returns:
            本地私有钥匙

        """
        def _get_private_pem():
            p = self.private_pem
            if os.path.isfile(p):
                return open(p).read()
            else:
                return p
        if not hasattr(self, '_local_private_pem'):
            setattr(self, '_local_private_pem', rsa.PrivateKey.load_pkcs1(_get_private_pem()))
        return getattr(self, '_local_private_pem')

    @property
    def local_public_pem(self):
        """
        Returns:
            本地公有钥匙

        """
        def _get_public_pem():
            p = self.public_pem
            if os.path.isfile(p):
                return open(p).read()
            else:
                return p
        if not hasattr(self, '_local_public_pem'):
            setattr(self, '_local_public_pem', rsa.PublicKey.load_pkcs1(_get_public_pem()))
        return getattr(self, '_local_public_pem')

    @property
    @from_config_option('enable_ssl', True)
    def enable_crypto_ssl(self):
        """
        Returns:
            bool: 是否使用SSL加密

        """
        return global_conf

    def _encode_crypto_ssl(self, body):
        body = zlib.compress(body, 9)
        LOG.debug('Pickle encode length:{0}'.format(len(body)))
        body = rsa.encrypt(body, self.local_public_pem)
        return body

    def _decode_crypto_ssl(self, body):
        LOG.debug('Recv RSA encrypt length:{0}'.format(len(body)))
        body = rsa.decrypt(body, self.local_private_pem)
        signature = rsa.sign(body, self.local_private_pem, 'SHA-1')
        v = rsa.verify(body, signature, self.local_public_pem)
        return zlib.decompress(body) if v else None

    def _get_enables(self):
        enables = [i.split('enable_crypto_')[1] for i in dir(self)
                   if i.startswith('enable_crypto_') and getattr(self, i)]
        enables.sort()
        return enables

    def encode(self, body):
        """
        数据加码

        Args:
            body: 基本数据

        Returns:
            加码后数据

        """
        for ce in self._get_enables():
            ce = getattr(self, '_encode_crypto_' + ce)
            if callable(ce):
                body = ce(body)
        return body

    def decode(self, body):
        """
        数据解码

        Args:
            body: 基本数据

        Returns:
            解码后数据

        """
        for de in self._get_enables():
            de = getattr(self, '_decode_crypto_' + de)
            if callable(de):
                body = de(body)
        return body
