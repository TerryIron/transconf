from message import RPC

RPC.CONNECTION_TYPE = 'sync'
rpc = RPC('amqp://guest:guest@localhost:5672')

class A(object):
    def __init__(self):
        self.name = None

    def process(self):
        print '111111111'
        @rpc.receive('create_server_1')
        def create(body):
            print  body
            print 'Create one!'
        print '222222222'
        yield create()
        print '333333333'

        @rpc.receive('delete_server')
        def delete(body):
            print  body
            print 'Delete one!'
        print '444444444'
        yield delete()
        print '555555555'

    @rpc.receive('create_server_2')
    def create(self, body):
        print  body
        print 'Create it!'

    @rpc.receive('delete_server')
    def delete(self, body):
        print  body
        print 'Delete one!'



a = A()
#a.create()
for d in a.process():
    print d
