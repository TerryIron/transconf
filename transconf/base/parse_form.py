__author__ = 'chijun'

from struct import *
#from common.parser import BaseParser


class FormUnitTypeError(Exception):
    """Raised when unit type error"""

class FormParser(object):
    """
      Parse form data to a parser object.
    """

    def __init__(self):
        self.ext_struct = set()

    def register_struct(self, struct):
        self.ext_struct.add(struct)

    def _parse_item(self, father, name, value):
        print 'father: {0}, name: {1}, value: {2}'.format(father, name, value)

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
            if len(form_unit) == len([k for k in form_unit if k in struct.keys()]):
                return struct

    def _parse_form(self, form, father='ROOT'):
        for form_unit in self._walk_form_unit(form):
            struct = self._get_struct(form_unit)
            if not struct:
                raise FormUnitTypeError('Form: {0}'.format(form_unit))
            for branch in [form_unit.pop(b) for b in struct.get_branchname() if b in form_unit]:
                for f, k, v in self._parse_form(branch, form_unit[struct.name]):
                    yield (f, k, v)
            for k, v in self._walk_form_unit_item(struct, form_unit):
                yield (father, k, v)

    def parse(self, form):
        for fa, a, b in self._parse_form(form):
            self._parse_item(fa, a, b)

    def build_parser(self, form):
        pass

FORMAT = [{'node': 'if_name',
               'regex': ['^([0-9a-z]+) .*'],
               'subs': [
                    {'node': 'ip_addr',
                     'regex': ['^.*inet addr:([0-9.]+)']
                    },
                    {'node': 'hw_addr',
                     'regex': ['^.*HWaddr ([0-9a-e:]+.*)']
                    },
                    {'node': 'mask',
                     'regex': ['^.*Mask:([0-9.]+)']
                    },
                    {'node': 'boardcast',
                     'regex': ['^.*Bcast:([0-9.]+)']
                    }
               ]
    }]        
k = FormParser()
k.register_struct(StructV1)
k.parse(FORMAT)
