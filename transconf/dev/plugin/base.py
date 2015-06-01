__author__ = 'chijun'

from . import BaseNode
from . import Fields

__all__ = ['ExtensionNode']


class ExtensionNode(BaseNode):
    def __call__(self, f):
        if not isinstance(f, Fields):
            raise Exception('Please input Fields class')
        self.fields = f
        self.fields.add_need('node')
        self.SETUP = do_setup
        return self


def init_node(n, **kwargs):
    for field in n.fields.get_need():
        if field not in kwargs:
            n[field] = None
        else:
            n[field] = kwargs[field]


def do_setup(node, map, *args):
    for kwargs in args:
        ex = ExtensionNode()(node.fields)
        # Check attributes
        init_node(ex, **kwargs)
        if map.is_empty():
            node.subs = [i['node'] for i in args]
            map.push({'None': [node, node]})
        if 'subs' in kwargs.keys():
            subs = kwargs['subs']
            if not isinstance(subs, list):
                raise TypeError('Please put sons into a list')
            ex.subs = [i['node'] for i in subs]
            map.push({ex['node']: [node, ex]})
            do_setup(ex, map, *subs)
        else:
            map.push({ex['node']: [node, ex]})
        node.set_item(ex['node'], ex)
