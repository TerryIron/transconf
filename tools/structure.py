#!/usr/bin/env python

import cffi
from ctypes import *


def format_data(data):
    if isinstance(data, str):
        try:
            value = chr(int(data))
        except:
            try:
                value = chr(int(data, '16'))
            except:
                value = ''.join([chr(i) for i in data])
    else:
        value = chr(data)
    return value


ffi = cffi.FFI()
ffi.cdef("""
    char* offsetchat(void** , int);
""")
ffi.set_source("_structure", """
    struct offset_t {
        unsigned long value;
        unsigned int offset_len;
        char *name;
    };
    static char* offsetchat(void** value, int len) {
        int i;
        char s[] = "hello";

        //for (i=0;i<=len;i++) {
        //    struct offset_t *a = (struct offset_t*)(value[i]);
        //}
        return s;
    }

""")

ffi.compile()


class Offset(Structure):
    _fields_ = [
        ('value', c_ulong),
        ('offset_len', c_uint),
        ('name', c_char_p),
    ]


NAME = 0
LEN = 1
VALUE = 2


def offset_struct_point(lst):
    new_lst = []
    for item in lst:
        name, length, value = item[NAME], item[LEN], item[VALUE]
        rel_length = length / 8
        if rel_length == 0:
            rel_length = 1
        if not value:
            value = 0
        inst = Offset(c_ulong(value), c_uint(rel_length), name)
        new_lst.append(inst)

    return new_lst
