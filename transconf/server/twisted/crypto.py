__author__ = 'chijun'

import rsa
import base64
import os.path

from transconf.utils import from_config_option
from transconf.server.twisted import CONF as global_conf

SSL_PRIVATE_PEM = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDIA9KiADB5H7qe9CxDCPw44BQKSQ00RKN3oMmEAs7LTAx4r8l6
MbbBbsF4/t79uaHN3UXxrVL74nP5Ay7qBOkMUymRHTsfBnGwx+MhFuiHH5QP82pM
Tii9vzbbHqdHxYd5qqRJ/Br8exWNAmIIIPJ1OePQKVOHLHrAHwnz8s7V7QIDAQAB
AoGAKBGj+7JAA7PYhglyaId/R8GUIi9aRtNNUCTU2e5aER4ODYthuGoHK58NgTjF
4VxzzrL6VR0c17sY8pSxrE4JhYTNCMTh5/XfP23l5cNNP1hr45EvsV/lfOzluv4J
j6lOty1n/8Chd6KZt9SXS1Vb7sz5AE7Rrolx76+Y/SzZJr0CQQDs73cNF+laFtci
vYEAPKgGKODbC5V64iKm0kp0P2Hx86jczr19b8JNPd3rTo5ItkN5KhQ1CJtfHMT5
2ZjGPSa/AkEA2BvZGDdk3V7wZbr+L5wziR9zZell+MFVuwANA58kz2qz4onZ7ox9
76dlft2pItUZ2WA6qT3tjfyZ8+b3jsw6UwJBAK4m+X+jQr8YKLt9RROSggI9C8GV
iyLOkp/B1D4L1IdODKF4SGmpusyhm7t4ezbQ2Vl253FvyRwo/lOTcCrOCesCQGhG
F5wtrkd6NbiAX4GNdvhk6oNz+LXsY3dVcPIcaeCC9cULCtKli2aFeN2cCq458L0I
R4W90c++4HHlMfH+7O0CQQCRaytc9jq6p52fALqxD6pK/4YVbhuyLsMBE0RgkyLS
DzHUN5UzkFeG0jyBHu7CnUcYSrE7m5aMHyVcaiS3JM3P
-----END RSA PRIVATE KEY-----
"""

SSL_PUBLIC_PEM = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIA9KiADB5H7qe9CxDCPw44BQK
SQ00RKN3oMmEAs7LTAx4r8l6MbbBbsF4/t79uaHN3UXxrVL74nP5Ay7qBOkMUymR
HTsfBnGwx+MhFuiHH5QP82pMTii9vzbbHqdHxYd5qqRJ/Br8exWNAmIIIPJ1OePQ
KVOHLHrAHwnz8s7V7QIDAQAB
-----END PUBLIC KEY-----
"""


class Crypto(object):

    @property
    @from_config_option('ssl_private_pem', SSL_PRIVATE_PEM)
    def private_pem(self):
        return global_conf

    @property
    @from_config_option('ssl_public_pem', SSL_PUBLIC_PEM)
    def public_pem(self):
        return global_conf

    @property
    def local_private_pem(self):
        p = self.private_pem
        if os.path.isfile(p):
            return open(p).read()
        else:
            return p

    @property
    def local_public_pem(self):
        p = self.public_pem
        if os.path.isfile(p):
            return open(p).read()
        else:
            return p

    @property
    @from_config_option('enable_ssl', True)
    def enable_crypto_ssl(self):
        return global_conf

    def _encode_crypto_ssl(self, body):
        pubkey = rsa.PublicKey.load_pkcs1(self.local_public_pem)
        body = base64.b64encode(body)
        body = rsa.encrypt(body, pubkey)
        return body

    def _decode_crypto_ssl(self, body):
        pubkey = rsa.PublicKey.load_pkcs1(self.local_public_pem)
        privkey = rsa.PrivateKey.load_pkcs1(self.local_private_pem)
        body = rsa.decrypt(body, privkey)
        body = base64.b64decode(body)
        signature = rsa.sign(body, privkey, 'SHA-1')
        rsa.verify(body, signature, pubkey)
        return body

    def _encode(self, body):
        enables = [i.split('enable_crypto_')[1] for i in dir(self)
                   if i.startswith('enable_crypto_') and getattr(self, i)]
        enables.sort()
        for ce in enables:
            ce = getattr(self, '_encode_crypto_' + ce)
            if callable(ce):
                body = ce(body)
        return body

    def _decode(self, body):
        disables = [i.split('disable_crypto_')[1] for i in dir(self)
                    if i.startswith('disable_crypto_') and getattr(self, i)]
        disables.sort()
        for de in disables:
            de = getattr(self, '_decode_crypto_' + de)
            if callable(de):
                body = de(body)
        return body
