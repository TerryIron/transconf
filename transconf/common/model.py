__author_ = 'chijun'

__all__ = ['BaseModel']


from transconf.common.namebus import NameBus


class BaseModel(NameBus):
    STRUCT = None
    FORM = None
    SPLIT_DOT = '.'
    MEMBER_SPLIT_DOT = ':'

    def __init__(self):
        super(BaseModel, self).__init__()
        self._form = self.FORM
        self._struct = self.STRUCT
        self.split = self.SPLIT_DOT
        self.member_split = self.MEMBER_SPLIT_DOT
        self.backend = None

    def _build_class_nodename(self, lst):
        return self.split.join(lst)

    def set_node_member(self, name_lst, key, value):
        real_name = self._build_class_nodename(name_lst)
        if real_name in self.namebus:
            n = self.get_namebus(real_name)
            if isinstance(n, dict):
                n[key] = value
                return True
        return False

    def set_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        self.set_namebus(real_name, {})

    def get_nodeobj(self, name_lst):
        real_name = self._build_class_nodename(name_lst)
        return self.get_namebus(real_name)

    def set_backend(self, backend):
        self.backend = backend

    def run(self, target_name, method_name, *args, **kwargs):
        raise NotImplementedError()

    @property
    def form(self):
        return self._form
        
    @property
    def struct(self):
        return self._struct

    """
       Pre-init model's dependences and owned driver which 
       from its form-data. 
    """
    def init(self, config=None):
        pass

    """
        Define auto-script code when it being startup.
    """
    def start(self, config=None):
        pass

    """
        Define auto-script code when it being shutdown.
    """
    def stop(self, config=None):
        pass
