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
import argparse
import itertools as it

from inspect import ismodule, getmembers
from pprint import pprint
from importlib import import_module
from os import path as p
from datetime import datetime as dt
from dateutil.parser import parse
from argparse import RawTextHelpFormatter, ArgumentParser

from tabutils.io import read_csv, IterStringIO, write

from . import utils
from .ofx import OFX
from .qif import QIF


parser = ArgumentParser(
    description="description: csv2ofx converts a csv file to ofx and qif",
    prog='csv2ofx', usage='%(prog)s [options] <source> <dest>',
    formatter_class=RawTextHelpFormatter)

_types = ['CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE', 'Bank', 'Cash']
# print(getmembers('csv2ofx'))
_mappings = [n for n, v in getmembers('csv2ofx.mappings', ismodule)]
_basedir = p.dirname(__file__)


parser.add_argument(
    dest='source', type=argparse.FileType('rU'), nargs='?', default=sys.stdin,
    help=('the source csv file (defaults to stdin)'))
parser.add_argument(
    dest='dest', type=argparse.FileType('w'), nargs='?', default=sys.stdout,
    help=('the output file (defaults to stdout)'))
parser.add_argument(
    '-a', '--account', metavar='TYPE', dest='account_type', choices=_types,
    help=("default account type 'CHECKING' for OFX and 'Bank' for QIF."))
parser.add_argument(
    '-e', '--end', metavar='DATE', help="end date", default=str(dt.now()))
parser.add_argument(
    '-l', '--language', help="the language", default='ENG')
parser.add_argument(
    '-s', '--start', metavar='DATE', help="the start date",
    default='2015-01-01')
parser.add_argument(
    '-m', '--mapping', help="the account mapping",
    default='default')
parser.add_argument(
    '-c', '--collapse', metavar='FIELD_NAME', help=(
        'field used to combine transactions within a split for double entry '
        'statements'))
parser.add_argument(
    '-S', '--split', metavar='FIELD_NAME', help=(
        'field used for the split account for single entry statements'))
parser.add_argument(
    '-C', '--chunksize', metavar='ROWS', default=10 ** 6,
    help="number of rows to process at a time")
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
    '-d', '--debug', action='store_true', default=False,
    help="display the options and arguments passed to the parser")
parser.add_argument(
    '-v', '--verbose', help="verbose output", action='store_true',
    default=False)

args = parser.parse_args()


def run():
    if args.debug:
        pprint(dict(args._get_kwargs()))
        exit(0)

    if args.version:
        from . import __version__ as version
        print('v%s' % version)
        exit(0)

    mapping = import_module('csv2ofx.mappings.%s' % args.mapping).mapping

    okwargs = {
        'def_type': args.account_type or 'Bank' if args.qif else 'CHECKING',
        'split_header': args.split,
        'start': parse(args.start),
        'end': parse(args.end)
    }

    cont = QIF(mapping, **okwargs) if args.qif else OFX(mapping, **okwargs)
    records = read_csv(args.source, has_header=cont.has_header)
    groups = cont.gen_groups(records, args.chunksize)
    trxns = cont.gen_trxns(groups, args.collapse)
    cleaned_trxns = cont.clean_trxns(trxns)
    data = utils.gen_data(cleaned_trxns)
    body = cont.gen_body(data)

    try:
        mtime = p.getmtime(args.source.name)
    except AttributeError:
        mtime = time.time()

    server_date = dt.fromtimestamp(mtime)
    header = cont.header(date=server_date, language=args.language)
    footer = cont.footer(date=server_date)
    content = it.chain([header, body, footer])
    kwargs = {'overwrite': args.overwrite, 'chunksize': args.chunksize}

    try:
        write(args.dest, IterStringIO(content), **kwargs)
    except TypeError as e:
        msg = str(e)

        if not args.collapse:
            msg += 'Try again with `-c` option.'

        exit(msg)


if __name__ == '__main__':
    run()
