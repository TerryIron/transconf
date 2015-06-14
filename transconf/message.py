__author__ = 'chijun'

import pika

CONNECTION_TYPE = 'twisted'
PORT = 5672
HOST = 'localhost'

def rpc_connection_adapter(parms, type_name=CONNECTION_TYPE, *args, **kwargs):
    if type_name == 'twisted':
        return pika.TwistedConnection(parms, *args, **kwargs)
    elif type_name == 'tonado':
        return pika.TornadoConnection(parms, *args, **kwargs)
    elif type_name == 'sync':
        return pika.BlockingConnection(parms, *args, **kwargs)
    elif type_name == 'async':
        return pika.AsyncoreConnection(parms, *args, **kwargs)
    elif type_name == 'libev':
        return pika.LibevConnection(parms, *args, **kwargs)
    elif type_name == 'select':
        return pika.SelectConnection(parms, *args, **kwargs)


class RPC(object):
    def __init__(self, host=HOST, port=PORT):
        self.parms = pika.ConnectionParameters(host=host, port=port)
        self.connection = rpc_connection_adapter(self.parms)

    def send(self, topic, routing_key):
        def _send(self, func):
            def do_send(self, *args, **kwargs):
                message = func(*args, **kwargs)
                channel = self.connection.channel()
                if routing_key:
                    return channel.basic_publish(exchange=topic or '',
                                                 routing_key=routing_key,
                                                 body=message)
            return do_send
        return _send


    def receive(self, topic, routing_key):
        def _receive(self, func):
            def do_receive(self, *args, **kwargs):
                def _callback(ch, method, properties, body):
                    return func(body, *args, **kwargs)
                channel = self.connection.channel()
                channel.basic_consume(_callback,
                                      queue=func.__name__,
                                      no_ack=True)
                return channel.start_consuming()
            return do_receive
    return _receive
