__author__ = 'chijun'

class DeadNode(object):
    FORMAT = None

    def __init__(self, inst=None):
        self.binding_obj = inst
        self.form = self.FORMAT
        self.context = {}
        self.sons = {}
        self.stat = {}

    def set_instance(self, instance):
        self.binding_obj = instance

    def set_mapping(self, mapping_dict):

    def status(self):
        return self.stat

    def pass(self, target_name, context_name):
        raise NotImplementedError()
