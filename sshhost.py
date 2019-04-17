#!/usr/bin/env python
import os
import pprint
import re
import sys


args = sys.argv[1:]
if len(args) != 1:
    print('Usage: sshhost <part of hostname or IP address>')
    sys.exit(1)
search_string = args[0]
re_string = re.compile(r'(.*)' + search_string + r'(.*)')

data = ''
with open(os.path.expanduser('~/.ssh/config'), 'rt') as f:
    data = f.readlines()

hosts = list()
host = dict()
for row in data:
    if row.isspace():
        continue
    key, value = row.strip().split(' ')
    if key.lower() == 'host':
        hosts.append(host)
        host = dict()
    host[key.lower()] = value.lower()
hosts.append(host)

found = list()
for host in hosts:
    for item in host.values():
        if re_string.match(item):
            found.append(host)

if found:
    uniq = list({v['host']:v for v in found}.values())
    for host in uniq:
        print()
        pprint.pprint(host)
    sys.exit(0)

print('Nothing found')
sys.exit(1)
