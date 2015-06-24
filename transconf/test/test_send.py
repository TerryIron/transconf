import sys                                                                                                                                                                                                

sys.path.insert(0, sys.path[0] + '/..')

from message import RPC

RPC.CONNECTION_TYPE = 'sync'
rpc = RPC('amqp://guest:guest@localhost:5672')

class A(object):
    def __init__(self):
        self.name = None

    def create_all(self):
        @rpc.simple_send('create_server_1')
        def create(self):
            print 'Create one!'
            return {'SEND': 'will creat one'}
        create(self)
        @rpc.simple_send('create_server_2')
        def create_it(self):
            print 'Create it!'
            return {'SEND': 'will creat it'}
        return create_it(self)

    @rpc.simple_send('delete_server')
    def delete(self):
        print 'Delete one!'
        return {'DEL': 'will delet one'}


a = A()
a.create_all()
a.delete()
