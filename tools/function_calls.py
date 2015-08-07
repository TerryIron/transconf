import sys
import re

RE = re.compile('([a-zA-Z]+).*')

LEN = 0
CLS_NAME = None
FUNC_NAME = None
CALLED_FUNC = []


def parse_php_contents(line):
    if '=' in line:
        new_called = trans_name(get_name('new', line))
        if new_called:
            print_called(new_called)
    def get_cls():
        try:
            d = re.compile('([a-zA-Z]+::).*').match(get_include_name(['::'], line).strip()).groups()
            return d[0][0:-2]
        except:
            pass
    func_called = get_cls()
    if func_called:
        print_called(func_called)

LANG_TYPES = {
    'php': ['class', 'function', ['//', '/*', '*', '*/'], parse_php_contents]
}

def print_called(called_name):
    global LEN, CALLED_FUNC, CLS_NAME, FUNC_NAME
    if called_name in CALLED_FUNC:
        return
    if CLS_NAME and FUNC_NAME:
        CALLED_FUNC.append(called_name)
        if LEN == 0:
            print '{0}->{1} called {2}'.format(CLS_NAME, FUNC_NAME, called_name)
            LEN = len('{0}->{1} '.format(CLS_NAME, FUNC_NAME))
        elif LEN > 0:
            buf = '' 
            for i in xrange(LEN):
                buf += ' '
            print '{0}called {1}'.format(buf, called_name)

def trans_name(name):
    try:
        name = name.strip()
        d = RE.match(name).groups()
        return d[0]
    except:
        pass

def trans_line_to_list(symbol, line):
    for s in symbol:
        if s in line:
            return
    return line.split(" ")

def get_symbol_index(symbol, line):
    if symbol in line:
        return line.index(symbol)

def get_include_name(name, line):
    for i in line:
        if len(name) <= len([n for n in name if n in i]):
            return i

def get_name(symbol, line):
    try:
        i = get_symbol_index(symbol, line)
        return line[i+1]
    except:
        return None

def get_cls_name(symbol, line):
    global CLS_NAME
    if symbol in line:
        name = trans_name(get_name(symbol, line))
        if name:
            CLS_NAME = name
    if CLS_NAME:
        return True

def get_func_name(symbol, line):
    global FUNC_NAME, CALLED_FUNC, LEN
    if symbol in line:
        name = trans_name(get_name(symbol, line))
        if name:
            FUNC_NAME = name
            CALLED_FUNC = []
            LEN = 0
    if FUNC_NAME:
        return True

def parse_line(cls_symbol, func_symbol, note_symbol, callback, line):
    line = trans_line_to_list(note_symbol, line)
    if line: 
        if get_cls_name(cls_symbol, line) and get_func_name(func_symbol, line):
            callback(line)

def main():
    lang_type = sys.argv[1].lower()
    if lang_type in LANG_TYPES.keys():
        cls, func, noteline, callback  = LANG_TYPES[lang_type]
    else:
        return
    target_file = sys.argv[2]
    with open(target_file, 'r') as f:
        map(lambda line: parse_line(cls, func, noteline, callback, line), [l for l in f.readlines() if l.strip() != '\n'])
    
if __name__ == '__main__':
    main()
