__author__ = 'chijun'


class Name(object):
    def __init__(self, name=None):
        self.nm = [name]

    @property
    def name(self):
        return self.nm

    def set(self, name):
        self.nm = [name]

    def append(self, name):
        self.nm.append(name)

    def push(self, name):
        self.nm.insert(0, name)


class FormUnitTypeError(Exception):
    """Raised when unit type error"""


class FormParser(object):
    """
      Parse form data to a parser object.
    >>> from models.sys.ifconfig import Ifconfig
    >>> from common.reg import register_local_driver
    >>> k = FormParser()
    >>> i = Ifconfig('1234567')
    >>> p = k.translate(i)
    """


    def __init__(self):
        self.ext_struct = set()

    def _reset(self):
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

    def _gen_parser(self, form):
        """
           Ver: 0.1.0 by chijun
           Not: Only support 3 for node object's maxdepth.
        """
        def new_buf():
            return {
                'items': [],
                'node_name': None,
                'father': None,
                'fname': None,
            }
        buf = new_buf()
        for n, f, k, v in self._parse_form(form):
            if n != v:
                #Init buffer
                if not buf['node_name']:
                    buf['node_name'] = n
                if not buf['father']:
                    buf['father'] = f
                if not buf['fname']:
                    buf['fname'] = Name(n)
                #Diff buffer with current data
                if buf['node_name'] != n:
                    old_items = buf['items']
                    buf['items'] = []
                    old_name= buf['node_name']
                    buf['node_name'] = n
                    old_fname = buf['fname']
                    buf['fname'] = Name(n)
                    if f != buf['father']:
                        old_fname.push(f)
                    yield (old_fname, old_items)
                buf['fname'].push(f)
                buf['father'] = f
                buf['items'].append((k, v))
        yield (buf['fname'], buf['items'])

    def translate(self, model):
        self._reset()
        self.register_struct(model.struct)
        for node_name, items in self._gen_parser(model.form):
            name = node_name.name
            model.set_nodeobj(name)
            for k, v in items:
                model.set_node_member(name, k, v)
        for i, j in model.namebus.items():
            print i, j

if __name__ == '__main__':                                                                                                                                                                                
    #import doctest
    #doctest.testmod()
    from models.sys.ifconfig import Ifconfig
    k = FormParser()
    i = Ifconfig('1234567')
    p = k.translate(i)
