import sys

CLS_NAME = None
FUNC_NAME = None

LANG_TYPES = {
    'php': ['class', 'function', ['//', '/*', '*/'], ]
}


def print_called(called_name):
    if CLS_NAME and FUNC_NAME:
        print '{0}->{1} called'.format(CLS_NAME, FUNC_NAME)

def trans_line_to_list(symbol, line):
    l = line.split(" ")
    if l[0] not in symbol:
        return l

def get_cls_name(symbol, line):
    if symbol in line:
        name = 
        CLS_NAME = name 
    if CLS_NAME:
        return True

def get_func_name(symbol, line):
    if symbol in line:
        name = 
        FUNC_NAME = name 
    if FUNC_NAME:
        return True

def parse_line(cls_symbol, func_symbol, note_symbol, hunter_callback, line):
    line = trans_line_to_list(line)
    if line and get_cls_name(cls_symbol, line) and get_func_name(func_symbol, line):
        hunter_callback(line)

def main():
    lang_type = sys.argv[1].lower()
    if lang_type in LANG_TYPES.keys():
        cls, func, noteline = LANG_TYPES[lang_type][0:1]
    else:
        return
    target_file = sys.argv[2]
    with open(target_file) as f:
        map(lambda line: parse_line(cls, func, noteline, line), [line for line in f.read() if line)
    
if __name__ == '__main__':
    main()
