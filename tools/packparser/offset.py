#!/usr/bin/env python

import cffi


HEAD = """
    struct offset_t {
        unsigned long value;
        unsigned int offset_len;
        char name[32];
    };

    unsigned char* offset_chat(struct offset_t*, int);
    //struct offset_t* offset_split(unsigned char*, int);

"""

SRC = """
    #include <malloc.h>
    #include <string.h>

    struct offset_t {
        unsigned long value;
        unsigned int offset_len;
        char name[32];
    };

    static unsigned int dword_chat(unsigned long* a, unsigned int* offset, int len) {
        int i;
        unsigned int r;

        r = 0;
        for(i=0;i<len;i++) {
            r |= (a[i] & (0xffffffff >> (32 - offset[i]))) << (32 - offset[i]);
        }
        return r;
    }

    static unsigned short word_chat(unsigned long* a, unsigned int* offset, int len) {
        int i;
        unsigned short r;

        r = 0;
        for(i=0;i<len;i++) {
            r |= (a[i] & (0xffffffff >> (32 - offset[i]))) << (16 - offset[i]);
        }
        return r;
    }

    static unsigned char byte_chat(unsigned long* a, unsigned int* offset, int len) {
        int i;
        unsigned char r;

        r = 0;
        for(i=0;i<len;i++) {
            r |= (a[i] & (0xffffffff >> (32 - offset[i]))) << (8 - offset[i]);
        }
        return r;
    }

    // Support offset block size is 32.
    unsigned char* (*offset_func[5])(unsigned long*, unsigned int*, int) = {
        NULL,
        byte_chat,
        word_chat,
        NULL,
        dword_chat,
    };

    static int offset_is_enough(unsigned long v) {
        if (v == 0 || (v % 8) != 0) {
            return 0;
        }

        int len;
        len = v / 8;
        if (len == 1 || len == 2 || len == 4) {
            return len;
        }
        return 0;
    }


    static unsigned char* offset_chat(struct offset_t* a, int len) {
        int i, j, buf_len, buf_offset_len, ret_len;
        struct offset_t* u = NULL;
        unsigned char* ret = NULL;
        unsigned char* ret_buf = NULL;
        unsigned long buf[len];
        unsigned int buf_offset[len];

        u = a;
        ret_len = buf_len = buf_offset_len = 0;
        for(i=0;i<len;i++) {
            buf[buf_len] = u[i].value;
            buf_offset[buf_len] = u[i].offset_len;
            buf_offset_len += buf_offset[buf_len];
            buf_len += 1;

            if ((j = offset_is_enough((int)buf_offset_len))) {
                ret_len += j;
                // choose offset processing function?
                ret_buf = (*offset_func[j])((unsigned long*)&buf, (unsigned int*)&buf_offset, buf_len);
                // malloc/realloc result buffer first and ready to memcpy the buffer after result buffer!
                if (ret != NULL) {
                    ret = (unsigned char*)realloc(ret, ret_len);
                    memcpy(ret + (ret_len - j), &ret_buf, j * sizeof(unsigned char));
                } else {
                    ret = (unsigned char*)calloc(ret_len, sizeof(unsigned char));
                    memset(ret, 0, ret_len * sizeof(unsigned char));
                    memcpy(ret, &ret_buf, j * sizeof(unsigned char));
                }
                memset(&buf, 0, len * sizeof(unsigned long));
                memset(&buf_offset, 0, len * sizeof(unsigned int));
                buf_len = buf_offset_len = 0;
            }
        }

        return ret;
    }

    //static struct offset_t* offset_split(unsigned char* a, int len) {
    //    struct offset_t* ret;
    //    return ret;
    //}
"""

ffi = cffi.FFI()
ffi.cdef(HEAD)
FFI_OFFSET = ffi.verify(SRC)


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
    i = 0
    inst = ffi.new("struct offset_t [{0}]".format(len(lst)))
    for item in lst:
        name, length, value = item[NAME], item[LEN], format_data(item[VALUE])
        if not value:
            value = 0
        inst[i].value = ffi.cast("unsigned long", value)
        inst[i].offset_len = ffi.cast("unsigned int", length)
        inst[i].name = name
        i += 1

    return inst


def offset_chat(lst):
    s = new_offset_struct(lst)
    p = FFI_OFFSET.offset_chat(s, len(lst))
    print p


# def offset_split(bytes):
#     pass
