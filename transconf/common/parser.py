__author__ = 'chijun'


__all__ = ['BaseParser', 'Index']


class Index(object):
    def __init__(self, idx=None):
        self.uid = idx

    @property
    def idx(self):
        return self.uid

    def set(self, idx):
        self.uid = idx


class Unit(object):
    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value


class BaseParser(object):
    """
        Internal unit format:
          A
         / \
        B   C

          Index NodeName    Unit
           ||     ||         ||
           \/     \/         \/
        [ 
          (0, node_name, ((k, v), (k, v) ......)),  # object A
          (A, node_name, ((k, v), (k, v) ......)),  # object B
          (A, node_name, ((k, v), (k, v) ......)),  # object C
        ]

        Parse data from father-node to sub-node.
    """
    def __init__(self):
        self.unit = []

    def _pre_node(self):
        pass

    def _next_node(self):
        pass

    def _pre_member(self):
        pass

    def _next_member(self):
        pass

    @property
    def len(self):
        return len(self.unit)

    def update(self, father, node_name, items):
        if isinstance(father, Index):
            self.unit.append((father, node_name, tuple([Unit(k, v) for k, v in items])))
            return True
        return False
        
    def translate(self, file_name):
        for line in open(file_name, 'r').read():
            print line

