__author__ = 'chijun'

class Index(object):
    def __init__(self, idx=None):
        self.uid = idx

    @property
    def idx(self):
        return self.uid

    def set(self, idx):
        self.uid = idx


class FormUnitTypeError(Exception):
    """Raised when unit type error"""

class FormParser(object):
    """
      Parse form data to a parser object.
    >>> from models.sys.ifconfig import Ifconfig
    >>> from common.reg import register_local_driver
    >>> k = FormParser()
    >>> i = Ifconfig('1234567')
    >>> p = k.gen_real_model(i)
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
                    yield (buf['fid'], f, old_name, old_items)
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
        yield (buf['fid'], buf['father'], buf['node_name'], buf['items'])

    def gen_real_model(self, model):
        self._reset()
        self.register_struct(model.struct)
        for fid, f, node_name, items in self._gen_parser(model.form):
            print fid, f, node_name, items
        
        

if __name__ == '__main__':                                                                                                                                                                                
    #import doctest
    #doctest.testmod()
    from models.sys.ifconfig import Ifconfig
    k = FormParser()
    i = Ifconfig('1234567')
    p = k.gen_real_model(i)
