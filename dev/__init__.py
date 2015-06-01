__author__ = 'chijun'

__version__ = (0, 1, 2)

import re

from base import Mapping, BaseObj
from plugin import Fields

__all__ = ['ContentParser']


class ContentParser(object):
    FORMAT = None
    NODE_CLASS = None

    def __init__(self, split='\n'):
        if not isinstance(self.FORMAT, list):
            raise TypeError('Please define FORMAT as a list')
        self.mapping = Mapping()
        self.ex_mapping = Mapping()
        self.stack = BaseObj()
        self.scope = BaseObj()
        self.base = None
        self.data = None  # Backup the output
        self.split = split
        self.re_index = 0
        self._found = False
        self.pre_val = None
        self.pre_name = None

    def build(self):
        f = Fields()
        f.add_need('regex')
        f.add_need('regex_split')
        return self.NODE_CLASS()(f)

    def set_split(self, split):
        self.split = split

    def _search_node(self, node_name):
        if self.scope.size > 1:
            if node_name in self.scope.current():
                return True
            else:
                self.scope.pop()
                self.stack.pop()
                return self._search_node(node_name)
        return self.scope.has(node_name)

    def _process_value(self, node, node_name, node_property, value):
        if self._search_node(node_name):
            if node_property.subs:
                # create a new node if it is a root
                if not self.stack.is_empty():
                    typ, nd, name = self.stack.current()
                    # Create a node which assigned to previous node
                    son = getattr(nd, typ)[name]
                    son.add_obj(node_name, value)
                    self.stack.push((node_name, son, value))
                else:
                    # Create a node by name
                    node.add_obj(node_name, value)
                    self.stack.push((node_name, node, value))
                self.scope.push(node_property.subs)
            else:
                # put this value to existed node
                if not self.stack.is_empty():
                    # set the value of target object
                    typ, nd, name = self.stack.current()
                    getattr(nd, typ)[name].set_val(node_name, value)
                else:
                    # set the value as the property
                    node.set_val(node_name, value)
            return True
        return False

    def _process_output(self, node, node_name, node_property, output):
        if output and output.groups()[0]:
            val = output.groups()[0].strip()
            if node_property['regex_split']:
                val = val.split(node_property['regex_split'])
            # Avoid different node get sample values in one line
            if self._found and \
               val == self.pre_val and \
               self.pre_name != node_name:
                return False
            self._found = self._process_value(node, node_name, node_property, val)
            self.pre_val = val
            self.pre_name = node_name
            if self._found:
                regex_len = len(node_property['regex'])
                if not self.ex_mapping.is_empty():
                    _name, (_node, _ex) = self.ex_mapping.current()
                    if node_name != _name:
                        if regex_len > 1:
                            self.ex_mapping.set({_name: [_node, _ex]})
                            self._init_regex_id()
                            self._next_regex_id()
                    else:
                        _id = self._next_regex_id()
                        if _id > len(_ex['regex']):
                            self.ex_mapping.pop()
                            self._init_regex_id()
                else:
                    if regex_len > 1:
                        self.ex_mapping.set({node_name: [node, node_property]})
                        self._init_regex_id()
                        self._next_regex_id()
            else:
                if not self.ex_mapping.is_empty():
                    self.ex_mapping.pop()
                self._init_regex_id()
            return True
        return False

    def _next_regex_id(self):
        self.re_index += 1
        return self.re_index

    def _init_regex_id(self):
        self.re_index = 0

    def _do_parses(self, line):
        for name, (node, ex) in self.mapping.get():
            output = re.match(ex['regex'][0], line)
            self._process_output(node, name, ex, output)

    def _do_parse(self, line):
        self.pre_val = None
        self.pre_name = None
        if not self.ex_mapping.is_empty():
            name, (node, ex) = self.ex_mapping.pop()
            output = re.match(ex['regex'][self.re_index], line)
            if not self._process_output(node, name, ex, output):
                self._do_parses(line)
        else:
            self._do_parses(line)

    def _clear_all(self):
        self.re_index = 0
        self.regex = None
        self.mapping.clear()
        self.scope.clear()
        self.stack.clear()

    def parse(self, data):
        self.data = data
        output = data.split(self.split)
        name, (obj, e) = self.mapping.pop(0)
        self.scope.push(e.subs)
        map(self._do_parse, output)

    """Get the base data from command output."""
    def scan(self):
        raise NotImplementedError

    def run(self):
        self._found = False
        self._clear_all()
        self.base = self.build()
        self.base.setup(self.base, self.mapping, *self.FORMAT)
        self.parse(self.scan())
        return self.base
