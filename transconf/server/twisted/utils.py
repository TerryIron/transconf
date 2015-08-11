__author__ = 'chijun'


from transconf.server.request import Request
from transconf.server.twisted.event import EventMiddleware


class TranMiddleware(EventMiddleware):
    def process_request(self, context):
        return super(TranMiddleware, self).process_request(context)


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

