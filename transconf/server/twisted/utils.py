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


from transconf.server.request import Request


class PeerRequest(Request):
    def to_dict(self):
        return dict(peer_host=self.peer_host,
                    peer_port=self.peer_port)

    @staticmethod
    def is_peer_request(request_info):
        if 'peer_host' and 'peer_port' in request_info:
            return True
        else:
            return False


'''
    Here instance 'found_var_name' is only support normal object and dict.
    We push peer info into request when received data be ready in twisted's transport.
'''


def need_peer_info(found_var_name):
    def _need_peer_info(func):
        def __need_peer_info(self, *args, **kwargs):
            if found_var_name in kwargs:
                peer = self.transport.getPeer()
                target = kwargs[found_var_name]
                if isinstance(target, dict):
                    target['peer_host'] = peer.host
                    target['peer_port'] = peer.port
                else:
                    setattr(target, 'peer_host', peer.host)
                    setattr(target, 'peer_port', peer.port)
            return func(self, *args, **kwargs)
        return __need_peer_info
    return _need_peer_info

