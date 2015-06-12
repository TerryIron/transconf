__author__ = 'chijun'

import pika

CONNECTION_TYPE = 'twisted'
PORT = 5672
HOST = 'localhost'

def rpc_connection_adapter(type_name=CONNECTION_TYPE, *args, **kwargs):
    if type_name == 'twisted':
        return pika.TwistedConnection(*args, **kwargs)
    elif type_name == 'tonado':
        return pika.TornadoConnection(*args, **kwargs)
    elif type_name == 'sync':
        return pika.BlockingConnection(*args, **kwargs)
    elif type_name == 'async':
        return pika.AsyncoreConnection(*args, **kwargs)
    elif type_name == 'libev':
        return pika.LibevConnection(*args, **kwargs)
    elif type_name == 'select':
        return pika.SelectConnection(*args, **kwargs)

class RPCMaster(object):
    def __init__(self, host=HOST, port=PORT):
        self.connection = rpc_connection_adapter()
        self.channel = self.connection.channel()
        self.topic = None

class RPCWorker(object):
    def __init__(self, master_host, port=PORT):
        pass

m = RPCMaster()
