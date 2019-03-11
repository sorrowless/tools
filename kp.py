#!/usr/bin/env python

import argparse
import os
import pprint
import sys

from pykeepass import PyKeePass
from pykeepass import group
from pykeepass import entry
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)


def find_groups(name, root_groups, result=[]):
    for grp in root_groups:
        if name.lower() in grp.path.lower():
            result.append(grp)
        subgroups = grp.subgroups
        find_groups(name, subgroups, result)


def find_entries(substring, db, glob=True):
    search_string = substring.lower()
    res = list()
    if glob:
        search_string = '.*%s.*' % search_string
    method_names = ['title', 'username', 'url', 'password', 'path']
    for method_name in method_names:
        method = getattr(db, 'find_entries_by_%s' % method_name)
        results = method(search_string, regex=True, flags='i')
        for result in results:
            if result not in res:
                res.append(result)

    root_group = db.find_groups_by_path('/')
    res_groups = list()
    # Now any group in res_groups will have a substring in path
    find_groups(substring, root_group, res_groups)
    for grp in res_groups:
        # As group has substring in path, it means any entry in this group
        # will have this substring in path too. There is no other way to do
        # this, sorry
        group_entries = db.find_entries_by_title('.*', regex=True, group=grp)
        for entr in group_entries:
            if entr not in res:
                res.append(entr)

    return res


def find_in_entry(substring, entr):
    substring = substring.lower()
    if isinstance(entr, entry.Entry):
        subentries = [entr.group.path, entr.title, entr.username,
                      entr.password, entr.url]
    elif isinstance(entr, group.Group):
        subentries = [entr.path]
    for subentry in subentries:
        if subentry and (substring in subentry.lower()):
            return True
    return False


def find_in_entries(entries, entry_names):
    survivors = entries.copy()
    while entry_names:
        entry_name = entry_names.pop()
        for index, entr in enumerate(entries):
            if not find_in_entry(entry_name, entr):
                survivors.remove(entr)
        survivors = find_in_entries(survivors, entry_names)
    return survivors


def print_entry(entr, verbosity):
    info = dict()

    def _get_fields(count):
        _info = dict()
        fields = ('group', 'username', 'password', 'title', 'url')
        if count == 2:
            fields = fields[:3]
        for field in fields:
            if field == 'group':
                _info[field] = entr.group.path
            else:
                _info[field] = getattr(entr, field)
        return _info

    if not verbosity:
        print(entr.password, end="")
    elif verbosity == 1:
        print("%s - %s" % (entr.group.path, entr.username), file=sys.stderr)
        print(entr.password, end="")
    else:
        info = _get_fields(verbosity)

    if info:
        pprint.pprint(info)
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        help="Increase verbosity",
                        action='count')
    parser.add_argument('words', nargs='+', help="Word to search")
    args = parser.parse_args()

    kp_database = os.environ['KP_DATABASE']
    kp_password = os.environ['KP_PASSWORD']
    kp = PyKeePass(kp_database, kp_password)

    entries = find_entries(args.words[-1], kp)

    if not entries:
        print('Nothing found')
        sys.exit(1)
    if len(args.words) > 1:
        res = find_in_entries(entries, args.words[:-1])
        for entr in res:
            print_entry(entr, args.verbose)
    else:
        for entr in entries:
            print_entry(entr, args.verbose)


if __name__ == '__main__':
    main()
