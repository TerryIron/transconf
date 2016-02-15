#!/usr/bin/env python

import sys
import os.path
import urllib
import pickle
import xml.etree.ElementTree as ET


__all__ = ['parse_protocol']


__target_file__ = os.path.join(os.path.dirname(__file__), 'ip_protocols.py')


try:
    IP_PROTOCOLS = pickle.load(open(__target_file__, 'r'))
except:
    IP_PROTOCOLS = dict()
    update()


def parse_protocol(val):
    return IP_PROTOCOLS.get(val, None)


def update():
    f = urllib.urlopen('https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers')
    root = ET.fromstring(f.read())
    try:
        for i, j, k, p, r in root.findall('./body/div/div/div/table/'):
            IP_PROTOCOLS[i.text] = p.text if not k.text else k.text
    except ValueError:
        pass
    with open(__target_file__, 'w') as f:
        pickle.dump(IP_PROTOCOLS, f)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'update':
        update()
