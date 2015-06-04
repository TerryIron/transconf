__author__ = 'chijun'

from common.parser import BaseParser, Index

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
    ...                    },
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
    ...                    {'node': 'hw_addr',
    ...                     'regex': ['^.*HWaddr ([0-9a-e:]+.*)']
    ...                    },
    ...           ]}
    ...    ]        
    >>> k = FormParser()
    >>> k.register_struct(StructV1)
    >>> p = k.gen_parser(FORMAT)
    >>> print len(p.unit)
    >>> for a, b, c in p.unit:
    ...     print a.idx, b, c
    """


    def __init__(self):
        self.ext_struct = set()

    def register_struct(self, struct):
        self.ext_struct.add(struct)

    def _walk_form_unit_item(self, struct, form_unit):
        for unit_name, unit_var in form_unit.items(): 
            yield struct.check_input(unit_name, unit_var)

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
                'fid': None, 
                'items': [],
                'node_name': None,
                'father': None,
            }
        buf = new_buf()
        for n, f, k, v in self._parse_form(form):
            if n != v:
                #Init buffer
                if not buf['node_name']:
                    buf['node_name'] = n
                if not buf['father']:
                    buf['father'] = f
                if not buf['fid']:
                    buf['fid'] = Index()
                    buf['fid'].set(0)
                buf['fid'].set(buf['fid'].idx + 1)
                #Diff buffer with current data
                if buf['node_name'] != n:
                    old_items = buf['items']
                    old_name= buf['node_name']
                    buf['node_name'] = n
                    buf['items'] = []
                    yield (buf['fid'], old_name, old_items)
                    if not buf['father'] != n:
                        if buf['father'] == 'ROOT':
                            old_fid = buf['fid']
                            buf['fid'] = Index()
                            buf['fid'].set(-1)
                        else:
                            old_fid = buf['fid']
                            buf['fid'] = Index()
                            buf['fid'].set(old_fid.idx)
                    buf['node_name'] = n
                buf['father'] = f
                buf['items'].append((k, v))
        yield (buf['fid'], buf['node_name'], buf['items'])

    def gen_parser(self, form):
        p = BaseParser()
        for fid, node_name, items in self._gen_parser(p, form):
            if not p.update(fid, node_name, items):
                return None
        return p
        

if __name__ == '__main__':                                                                                                                                                                                
    import doctest
    doctest.testmod()
