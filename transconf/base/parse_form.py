__author__ = 'chijun'

from common.parser import BaseParser

class FormUnitTypeError(Exception):
    """Raised when unit type error"""

class FormParser(object):
    """
      Parse form data to a parser object.
    >>> from struct import *
    >>> FORMAT = [{'node': 'if_name',
    ...            'regex': ['^([0-9a-z]+) .*'],
    ...            'subs': [
    ...                    {'node': 'ip_addr',
    ...                     'regex': ['^.*inet addr:([0-9.]+)']
    ...                   },
    ...                    {'node': 'hw_addr',
    ...                     'regex': ['^.*HWaddr ([0-9a-e:]+.*)']
    ...                    },
    ...                    {'node': 'mask',
    ...                     'regex': ['^.*Mask:([0-9.]+)']
    ...                    },
    ...                    {'node': 'boardcast',
    ...                     'regex': ['^.*Bcast:([0-9.]+)']
    ...                    }
    ...           ]},
    ...           {'node': 'test_node',
    ...            'regex': ['^([0-9a-z]+) .*'],
    ...            'subs': [
    ...                    {'node': 'ip_addr',
    ...                     'regex': ['^.*inet addr:([0-9.]+)']
    ...                   },
    ...           ]}
    ...    ]        
    >>> k = FormParser()
    >>> k.register_struct(StructV1)
    >>> p = k.gen_parser(FORMAT)
    """


    def __init__(self):
        self.ext_struct = set()

    def register_struct(self, struct):
        self.ext_struct.add(struct)

    def _walk_form_unit_item(self, struct, form_unit):
        for unit_name, unit_var in form_unit.items(): 
            if struct.check_input(unit_name, unit_var):
                yield unit_name, unit_var

    def _walk_form_unit(self, form):
        for form_unit in form: 
            if self._check_form_unit(form_unit):
                yield form_unit

    def _check_form_unit(self, form_unit):
        return True if type(form_unit) == dict else False

    def _get_struct(self, form_unit):
        for struct in self.ext_struct:
            # Simple check ?
            if len(form_unit) == len([k for k in form_unit if k in struct.keys()]):
                return struct

    def _parse_form(self, form, father='ROOT'):
        for form_unit in self._walk_form_unit(form):
            struct = self._get_struct(form_unit)
            if not struct:
                raise FormUnitTypeError('Form: {0}'.format(form_unit))
            for branch in [form_unit.pop(b) for b in struct.get_branchname() if b in form_unit]:
                for n, f, k, v in self._parse_form(branch, form_unit[struct.name]):
                    yield (n, f, k, v)
            node_name = struct.get_nodename()
            for k, v in self._walk_form_unit_item(struct, form_unit):
                yield (form_unit[node_name], father, k, v)

    def _gen_parser(self, parser, form):
        p = parser
        def new_buf():
            return {
                'fid': 0, 
                'items': [],
                'node_name': None,
                'father': None,
            }
        buf = new_buf()
        for n, f, k, v in self._parse_form(form):
            #Init buffer
            if not buf['node_name']:
                buf['node_name'] = n
            if not buf['father']:
                buf['father'] = f
            #Diff buffer with current data
            if buf['node_name'] == n:
                #print 1, n, f, k, v
                if n != v:
                    buf['items'].append((k, v))
            else:
                #print 2, n, f, k, v
                old_name = buf['node_name']
                buf['node_name'] = n
                old_items = buf['items']
                buf['items'] = []
                yield (buf['fid'], old_name, old_items)
            buf['father'] = f
            print n, f, k, v

    def gen_parser(self, form):
        p = BaseParser()
        for fid, node_name, items in self._gen_parser(p, form):
            print fid, node_name, items
            p.update(fid, node_name, items)
        return p
        

if __name__ == '__main__':                                                                                                                                                                                
    import doctest
    doctest.testmod()
