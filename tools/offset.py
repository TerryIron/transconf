#!/usr/bin/env python

import cffi


ffi = cffi.FFI()
ffi.cdef("""
    struct offset_t {
        unsigned long value;
        unsigned int offset_len;
        char name[32];
    };

    unsigned char* offset_chat(struct offset_t*, int);
    struct offset_t* offset_split(unsigned char*, int);

""")
FFI_OFFSET = ffi.verify("""
    #include <malloc.h>
    #include <string.h>

    struct offset_t {
        unsigned long value;
        unsigned int offset_len;
        char name[32];
    };

    static unsigned int* dword_chat(unsigned long* a, unsigned int* f, int len) {
        unsigned int* r;
        return r;
    }

    static unsigned short* word_chat(unsigned long* a, unsigned int* f, int len) {
        unsigned short* r;
        return r;
    }

    static unsigned char* byte_chat(unsigned long* a, unsigned int* f, int len) {
        unsigned char* r;
        return r;
    }

    // Support offset block size is 32.
    unsigned char* (*offset_func[5])(unsigned long*, unsigned int*, int) = {
        NULL,
        (unsigned char*)byte_chat,
        (unsigned char*)word_chat,
        NULL,
        (unsigned char*)dword_chat
    };

    static int offset_is_enough(unsigned long v) {
        int len;
        if (v == 0 || (v % 8) != 0) {
            return 0;
        }
        len = v / 8;
        if (len == 1 || len == 2 || len == 4) {
            return len;
        }
        return 0;
    }

    static unsigned char* offset_chat(struct offset_t* a, int len) {
        int i, j, buf_len, buf_offset_len;
        unsigned long val;
        unsigned int offset_len;
        int ret_len;
        char* name = NULL;
        unsigned char* ret_buf = NULL;
        unsigned char* ret = NULL;
        struct offset_t* u = NULL;
        unsigned long buf[len];
        unsigned int buf_offset[len];

        u = a;
        ret_len = 0;
        buf_len = 0;
        buf_offset_len = 0;
        for(i=0;i<len;i++) {
            val = u[i].value;
            name = u[i].name;
            offset_len = u[i].offset_len;
            if ((j = offset_is_enough((int)offset_len + buf_offset_len))) {
                ret_len += j;
                buf_len = 0;
                buf_offset_len = 0;
                // choose offset processing function?
                ret_buf = (*offset_func[j])((unsigned long*)&buf, (unsigned int*)&buf_offset, buf_len);
                // malloc/realloc result buffer first and ready to memcpy the buffer after result buffer!
                if (ret  != NULL) {
                    ret = (unsigned char*)realloc(ret, ret_len);
                    memcpy(ret + (ret_len - j), ret_buf, j);
                } else {
                    ret = (unsigned char*)calloc(ret_len, sizeof(unsigned char));
                    memcpy(ret, ret_buf, j);
                }
            } else {
                buf[buf_len] = val;
                buf_offset[buf_len] = offset_len;
                buf_offset_len += offset_len;
                buf_len += 1;
            }
        }

        return ret;
    }

    static struct offset_t* offset_split(unsigned char* a, int len) {
        struct offset_t* ret;
        return ret;
    }
""")


NAME = 0
LEN = 1
VALUE = 2


def format_data(data):
    if not data:
        return chr(0)
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


def new_offset_struct(lst):
    _len = len(lst)
    i = 0
    inst = ffi.new("struct offset_t [{0}]".format(_len))
    for item in lst:
        name, length, value = item[NAME], item[LEN], format_data(item[VALUE])
        if not value:
            value = 0
        inst[i].value = ffi.cast("unsigned long", value)
        inst[i].offset_len = ffi.cast("unsigned int", length)
        inst[i].name = name
        i += 1

    return inst, _len


def offset_chat(lst):
    s, l = new_offset_struct(lst)
    return FFI_OFFSET.offset_chat(s, l)


def offset_split(bytes):
    pass
