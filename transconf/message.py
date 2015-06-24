__author__ = 'chijun'

import uuid
import json
import pika
import pika_pool



class RPC(object):
    CONNECTION_ATTEMPTS = 3
    CONNECTION = pika.BlockingConnection

    def __init__(self, amqp_url, max_size=20, max_overflow=10, timeout=10):
        self.parms = pika.URLParameters(
            amqp_url +
            '?socket_timeout={0}&'
            'connection_attempts={1}'.format(timeout,
                                             self.CONNECTION_ATTEMPTS)
        )
        self.pool = pika_pool.QueuedPool(
            create=lambda: self.CONNECTION(self.parms),
            max_size=max_size,
            max_overflow=max_overflow,
            timeout=timeout,
            recycle=3600,
            stale=45,
        )

    def simple_send(self, queue_name, auto_delete=False):
        def _send(func):
            def do_send(*args, **kwargs):
                body = func(*args, **kwargs)
                with self.pool.acquire() as cxn:
                    cxn.channel.queue_declare(queue=queue_name,
                                              auto_delete=auto_delete)
                    cxn.channel.basic_publish(
                        body=json.dumps({
                            'body': body,
                        }),
                        exchange='',
                        routing_key=queue_name,
                        properties=pika.BasicProperties(
                            content_type='application/json',
                            content_encoding='utf-8',
                            delivery_mode=2,
                        )
                    )
                    return True
            return do_send
        return _send

    def simple_receive(self, queue_name, auto_delete=False):
        def _receive(func):
            def do_receive(*args, **kwargs):
                with self.pool.acquire() as cxn:
                    def task_callback(ch, method, header, body):
                        data = json.loads(body)
                        b = data.get('body', None)
                        if b: 
                            ret = func(b, *args, **kwargs)
                            return ret
                    cxn.channel.queue_declare(queue=queue_name,
                                              auto_delete=auto_delete)
                    cxn.channel.basic_qos(prefetch_count=1)
                    cxn.channel.basic_consume(task_callback,
                                              queue=queue_name,
                                              no_ack=True)
            return do_receive
        return _receive


