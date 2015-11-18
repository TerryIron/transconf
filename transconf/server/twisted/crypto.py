__author__ = 'chijun'

import base64
import os.path
from OpenSSL.crypto import load_privatekey, FILETYPE_PEM, sign

from transconf.utils import from_config_option
from transconf.server.twisted import CONF as global_conf

SSL_PRIVATE_PEM = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDGJ2aGEQ0ivLwENmHuRSeaf2bYzp9zoRcdUsdKzt4vqI1EAByy
1JNWNgAP4dcpajlBtrrQlm/akQ7IlN9yEpVPnrXGOHICAxb/mdBesSIY1Km2oE6W
CcHRnUaEjoX6K0lcFTdmUwkDeCon+UghJBhRtqClbjqOvXTiau7ufLk2BQIDAQAB
AoGAXnC64VzRGORA6/ULWadmB7F+0AgyYMa/IH+qclID/Uzk/yragrTj/+u+vdMS
XC+/WD2B7hY0+0O1ew3RLSoENNYUPKj4oIkVI+NTG8ZWtpmfS6M0OpuY8OqanS1l
uavhsVPHS53t+l0jWyp26jvVkaLt+vEL6MMy43JkA9/2yIUCQQDyl1SU1z6QDrOm
7VFTpYlwLo2S7v5E7ajxXI5Rd4lE9N7u2GSfvEZXiSuXbM4sYHFzV4zXyo3TVhnI
3iUxNbA3AkEA0RtITA2gFhXBMBPqYZrpAQyDW/DTixFHqgITe0OsTIOSosF2DmSH
d7zO/qC99Z0QMl9MxVxHC9dXuT1pNtaVowJBAMWJDlmIj6wUHJufgOqgz7ImZiew
LiIId9nZqRWTRZZ94o4QbJdZYtnimzlZYuTlv1vRfaE1kZj18lcK9LQGaK8CQQDE
No2Ij+B/2LoGmyl7nRi22z8HrttRy00rwfb123J5+ZxHDLHyn3JecNTrKXoWVuMz
4SjwqL4h5ldygqWPx5txAkBvlCw7p5+R1X8hkCXR+CUUfACp2IL7QMkOWKyEpWao
DbTKvkg2N/1hanKWXrfDYVxNy8cy6hehA9Pm2f0gZNIl
-----END RSA PRIVATE KEY-----
"""


class Crypto(object):

    @property
    @from_config_option('ssl_private_pem', SSL_PRIVATE_PEM)
    def private_pem(self):
        return global_conf

    @property
    def local_private_pem(self):
        p = self.private_pem
        if os.path.isfile(p):
            return open(p).read()
        else:
            return p

    @property
    @from_config_option('enable_ssl', True)
    def enable_crypto_ssl(self):
        return global_conf

    def _encode_crypto_ssl(self, body):
        key = load_privatekey(FILETYPE_PEM, self.local_private_pem)
        d = sign(key, body, 'sha1')
        body = base64.b64encode(d)
        return body

    def _decode_crypto_ssl(self, body):
        # TODO by chijun
        # Not implement error
        key = load_privatekey(FILETYPE_PEM, self.local_private_pem)
        d = sign(key, body, 'sha1')
        body = base64.b64decode(d)
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
