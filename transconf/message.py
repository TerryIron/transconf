__author__ = 'chijun'

import uuid
import json
import pika
import pika_pool


def rpc_connection_adapter(type_name, parms, *args, **kwargs):
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
    CONNECTION_ATTEMPTS = 2
    CONNECTION_TYPE = 'twisted'

    def __init__(self, amqp_url, max_size=20, max_overflow=10, timeout=10):
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
        )
        self.pool = pika_pool.QueuedPool(
            create=lambda: rpc_connection_adapter(self.CONNECTION_TYPE, self.parms),
            max_size=max_size,
            max_overflow=max_overflow,
            timeout=timeout,
            recycle=3600,
            stale=45,
        )
        self.routing = {}

    def send(self, exchange, queue_name):
        def _send(func):
            def do_send(*args, **kwargs):
                body = func(*args, **kwargs)
                with self.pool.acquire() as cxn:
                    cxn.channel.queue_declare(queue=queue_name)
                    cxn.channel.basic_publish(
                        body=json.dumps({
                            'body': body,
                        }),
                        exchange=exchange,
                        routing_key=queue_name,
                        properties=pika.BasicProperties(
                            content_type='application/json',
                            content_encoding='utf-8',
                            delivery_mode=2,
                        )
                    )
                    print " [x] Sent {0}".format(body)
                    return body
                return None
            return do_send
        return _send

    def receive(self, queue_name):
        print self.routing
        def _receive(func):
            def do_receive(*args, **kwargs):
                def _callback(ch, method, properties, body):
                    data = json.loads(body)
                    b = data.get('body', None)
                    if b: 
                        ret = func(b, *args, **kwargs)
                        print " [x] Received %r" % (b,)
                        return ret
                with self.pool.acquire() as cxn:
                    cxn.channel.basic_qos(prefetch_count=1)
                    cxn.channel.queue_declare(queue=queue_name)
                    print ' [*] Waiting for messages. To exit press CTRL+C'
                    cxn.channel.basic_consume(_callback,
                                              queue=queue_name,
                                              no_ack=True)
            return do_receive
        return _receive
