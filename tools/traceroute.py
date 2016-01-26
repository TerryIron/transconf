#!/usr/bin/env python

import urllib
import json
import sys
import commands


def traceroute(url):
    output = commands.getoutput('traceroute {0}'.format(url))
    output = [i for i in output.split(' ')[7:] if len(i.split('.')) == 4]
    j = []
    for i in output:
        if i not in j:
            ip_location(i)
        j = [i]


def ip_location(ip):
    f = urllib.urlopen('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip={0}'.format(ip)).read()
    j = json.loads(f.split('=')[1][:-1])
    if j.get('ret', 0) != 1:
        location = 'local'
    else:
        location = '{0}:{1}:{2}'.format(j.get('country', '').encode('utf8'), 
                                        j.get('province', '').encode('utf8'), 
                                        j.get('city', '').encode('utf8'))
        if location.endswith('::'):
            location = location[:-2]
    print 'IP:{0}, Location:{1}'.format(ip, location)


if __name__ == "__main__":
    traceroute(sys.argv[1])
