#!/usr/bin/env python

import argparse
import json
import os
import pprint
import re
import sys


parser = argparse.ArgumentParser(
    description='Process SSH config file and search for data in it.')
parser.add_argument('searchstring', type=str, default='.*',
                    help='A string for search')
parser.add_argument('-j', '--json', action='store_true',
                    help='Print an output in valid JSON format')
parser.add_argument('-s', '--short', action='store_true',
                    help='Print only host names from SSH config')

args = parser.parse_args()
re_string = re.compile(r'(.*)' + args.searchstring + r'(.*)')

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

uniq = list({v['host']: v for v in found}.values())
if uniq and args.short:
    for host in uniq:
        print(host['host'])
elif uniq and not args.json:
    for host in uniq:
        print()
        pprint.pprint(host)
elif uniq:
    print(json.dumps(uniq, indent=2))
else:
    print('Nothing found')
    sys.exit(1)
sys.exit(0)
