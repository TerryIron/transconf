#!/usr/bin/env python

from structure import *
from _structure import ffi, lib


def offsetchat(lst):
    s = offset_struct_point(lst)
    lib.offsetchat(s, len(s))
