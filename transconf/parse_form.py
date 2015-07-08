__author__ = 'chijun'


class FormUnitTypeError(Exception):
    """Raised when unit type error"""


class FormParser(object):
    """
      Parse form data to a parser object.
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
                for n, f, k, typ, v in self._parse_form(branch, form_unit[struct.name]):
                    yield (n, f, k, typ, v)
            node_name = struct.get_nodename()
            for k, typ, v in self._walk_form_unit_item(struct, form_unit):
                yield (form_unit[node_name], father, k, typ, v)

    def _gen_parser(self, form):
        """
           Ver: 0.1.0 by chijun
           Not: Only support node object's maxdepth=3.
        """
        # Init buffer by lambda expression
        new_buf = lambda : {
                'items': [],
                'node_name': None,
                'father': None,
                'fname': None,
            }
        new_name = lambda x: [x]
        buf = new_buf()
        for n, f, k, typ, v in self._parse_form(form):
            if n != v:
                if not buf['node_name']:
                    buf['node_name'] = n
                if not buf['father']:
                    buf['father'] = f
                if not buf['fname']:
                    buf['fname'] = new_name(n)
                #Diff buffer with current data
                if buf['node_name'] != n:
                    old_items = buf['items']
                    buf['items'] = []
                    old_name= buf['node_name']
                    buf['node_name'] = n
                    old_fname = buf['fname']
                    buf['fname'] = new_name(n)
                    if f != buf['father']:
                        old_fname.insert(0, f)
                    yield (old_fname, old_items)
                if f != buf['fname'][0]:
                    buf['fname'].insert(0, f)
                buf['father'] = f
                buf['items'].append((k, (typ, v)))
        yield (buf['fname'], buf['items'])

    def translate(self, model):
        self._reset()
        self.register_struct(model.struct)
        for node_name, items in self._gen_parser(model.form):
            model.set_nodeobj(node_name)
            for k, item  in items:
                model.set_node_member(node_name, k, item)

