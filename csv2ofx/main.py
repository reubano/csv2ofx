#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.main
~~~~~~~~~~~~

Provides the primary ofx and qif conversion functions

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import time
import sys
import itertools as it

from importlib import import_module
from imp import find_module, load_module
from pkgutil import iter_modules
from operator import itemgetter
from os import path as p
from io import open
from datetime import datetime as dt
from argparse import RawTextHelpFormatter, ArgumentParser

from builtins import *
from dateutil.parser import parse
from pprint import pprint
from meza.io import read_csv, IterStringIO, write

from . import utils
from .ofx import OFX
from .qif import QIF


parser = ArgumentParser(
    description="description: csv2ofx converts a csv file to ofx and qif",
    prog='csv2ofx', usage='%(prog)s [options] <source> <dest>',
    formatter_class=RawTextHelpFormatter)

TYPES = ['CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE', 'Bank', 'Cash']
mappings = import_module('csv2ofx.mappings')
MODULES = tuple(itemgetter(1)(m) for m in iter_modules(mappings.__path__))


parser.add_argument(
    dest='source', nargs='?', help='the source csv file (defaults to stdin)')
parser.add_argument(
    dest='dest', nargs='?', help='the output file (defaults to stdout)')
parser.add_argument(
    '-a', '--account', metavar='TYPE', dest='account_type', choices=TYPES,
    help="default account type 'CHECKING' for OFX and 'Bank' for QIF.")
parser.add_argument(
    '-e', '--end', metavar='DATE', help="end date", default=str(dt.now()))
parser.add_argument(
    '-l', '--language', help="the language", default='ENG')
parser.add_argument(
    '-s', '--start', metavar='DATE', help="the start date")
parser.add_argument(
    '-m', '--mapping', metavar='MAPPING_NAME', help="the account mapping",
    default='default', choices=MODULES)
parser.add_argument(
    '-x', '--custom', metavar='FILE_PATH', help="path to a custom mapping file")
parser.add_argument(
    '-c', '--collapse', metavar='FIELD_NAME', help=(
        'field used to combine transactions within a split for double entry '
        'statements'))
parser.add_argument(
    '-S', '--split', metavar='FIELD_NAME', help=(
        'field used for the split account for single entry statements'))
parser.add_argument(
    '-C', '--chunksize', metavar='ROWS', type=int, default=2 ** 14,
    help="number of rows to process at a time")
parser.add_argument(
    '-L', '--list-mappings', help="list the available mappings",
    action='store_true', default=False)
parser.add_argument(
    '-V', '--version', help="show version and exit", action='store_true',
    default=False)
parser.add_argument(
    '-q', '--qif', help="enables 'QIF' output instead of 'OFX'",
    action='store_true', default=False)
parser.add_argument(
    '-o', '--overwrite', action='store_true', default=False,
    help="overwrite destination file if it exists")
parser.add_argument(
    '-D', '--server-date', help="OFX server date (default: source file mtime)")
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="display the options and arguments passed to the parser")
parser.add_argument(
    '-v', '--verbose', help="verbose output", action='store_true',
    default=False)

args = parser.parse_args()


def run():  # noqa: C901
    if args.debug:
        pprint(dict(args._get_kwargs()))
        exit(0)

    if args.version:
        from . import __version__ as version
        print('v%s' % version)
        exit(0)

    if args.list_mappings:
        print(', '.join(MODULES))
        exit(0)

    if args.custom:
        name = p.splitext(p.split(args.custom)[1])[0]
        found = find_module(name, [p.dirname(p.abspath(args.custom))])
        module = load_module(name, *found)
    else:
        module = import_module('csv2ofx.mappings.%s' % args.mapping)

    mapping = module.mapping

    okwargs = {
        'def_type': args.account_type or 'Bank' if args.qif else 'CHECKING',
        'split_header': args.split,
        'start': parse(args.start) if args.start else None,
        'end': parse(args.end) if args.end else None
    }

    source = open(args.source, newline=None) if args.source else sys.stdin
    cont = QIF(mapping, **okwargs) if args.qif else OFX(mapping, **okwargs)

    try:
        records = read_csv(source, has_header=cont.has_header)
        groups = cont.gen_groups(records, args.chunksize)
        trxns = cont.gen_trxns(groups, args.collapse)
        cleaned_trxns = cont.clean_trxns(trxns)
        data = utils.gen_data(cleaned_trxns)
        body = cont.gen_body(data)

        if args.server_date:
            server_date = parse(args.server_date)
        else:
            try:
                mtime = p.getmtime(source.name)
            except AttributeError:
                mtime = time.time()

            server_date = dt.fromtimestamp(mtime)

        header = cont.header(date=server_date, language=args.language)
        footer = cont.footer(date=server_date)
        filtered = filter(None, [header, body, footer])
        content = it.chain.from_iterable(filtered)
        kwargs = {'overwrite': args.overwrite, 'chunksize': args.chunksize}
    except:
        source.close()
        raise

    dest = open(args.dest, newline=None) if args.dest else sys.stdout

    try:
        write(dest, IterStringIO(content), **kwargs)
    except KeyError as err:
        msg = 'Field %s is missing from file. Check `mapping` option.' % err
    except TypeError as err:
        msg = 'No data to write. %s. ' % str(err)

        if args.collapse:
            msg += 'Check `start` and `end` options.'
        else:
            msg += 'Try again with `-c` option.'
    else:
        msg = 0

        exit(msg)
    finally:
        source.close() if args.source else None
        dest.close() if args.dest else None


if __name__ == '__main__':
    run()
