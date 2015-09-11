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

from functools import partial
from operator import itemgetter
from inspect import ismodule, getmembers
from pprint import pprint
from importlib import import_module
from os import path as p
from datetime import datetime as dt
from dateutil.parser import parse
from argparse import RawTextHelpFormatter, ArgumentParser

from tabutils.io import read_csv
from tabutils.process import xmlize

from . import utils
from .ofx import OFX
from .qif import QIF


parser = ArgumentParser(
    description="description: csv2ofx converts a csv file to ofx and qif",
    prog='csv2ofx', usage='%(prog)s [options] <source> <dest>',
    formatter_class=RawTextHelpFormatter)

_types = ['CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE', 'Bank', 'Cash']
# print(getmembers('csv2ofx'))
_mappings = [n for n, v in getmembers('mappings', ismodule)]
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
    '-c', '--collapse', metavar='FIELD NAME', help=(
        'field used to combine transactions within a split for double entry '
        'statements'))
parser.add_argument(
    '-S', '--split', metavar='FIELD NAME', help=(
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

def gen_groups(chunks, obj, qif):
    for chunk in chunks:
        if qif:
            cleansed = chunk
        else:
            # cleansed = chunk
            cleansed = [
                {k: xmlize([v]).next() for k, v in c.items()} for c in chunk]

        keyfunc = obj.id if obj.is_split else obj.account
        grouped = utils.group_transactions(cleansed, keyfunc)

        for group, transactions in grouped:
            yield (group, transactions)


def gen_trxns(groups, obj, collapse):
    for group, transactions in groups:
        if obj.is_split and args.collapse:
            # group transactions by collapse field and sum the amounts
            groupby = itemgetter(args.collapse)
            byaccount = utils.group_transactions(transactions, groupby)
            op = lambda values: sum(map(utils.convert_amount, values))
            merger = partial(utils.merge_dicts, obj.amount, op)
            trxns = [merger(dicts) for _, dicts in byaccount]
        else:
            trxns = transactions

        yield (group, trxns)


def gen_main_trxns(groups, obj):
    for group, trxns in groups:
        _args = [trxns, obj.convert_amount]

        # if it's split, transactions skipping is all or none
        if obj.is_split and obj.skip_transaction(trxns[0]):
            continue
        elif obj.is_split and not utils.verify_splits(*_args):
            raise Exception('Splits do not sum to zero.')
        elif obj.is_split:
            main_pos = utils.get_max_split(*_args)[0]
        else:
            main_pos = 0

        yield (group, main_pos, trxns)


def gen_ofx_content(groups, obj):
    for group, main_pos, trxns in groups:
        keyfunc = lambda enum: enum[0] != main_pos
        sorted_trxns = sorted(enumerate(trxns), key=keyfunc)

        if obj.is_split and len(sorted_trxns) > 2:
            raise TypeError('Group %s has too many splits.\n' % group)

        for pos, trxn in sorted_trxns:
            data = obj.transaction_data(trxn)
            is_main = pos == main_pos

            if not obj.is_split and obj.skip_transaction(trxn):
                continue

            if is_main and not (obj.is_split or obj.split_account):
                yield obj.account_start(**data)

            if not (obj.is_split or obj.split_account):
                yield obj.transaction(**data)

            if (obj.is_split and is_main) or obj.split_account:
                yield obj.transfer(**data)

            if (obj.is_split and not is_main) or obj.split_account:
                yield obj.split_content(**data)

            if obj.split_account:
                yield obj.transfer_end(**data)

        if obj.is_split:
            yield obj.transfer_end(**data)
        elif not (obj.is_split or obj.split_account):
            yield obj.account_end(**data)


def gen_qif_content(groups, obj):
    prev_account = None

    for group, main_pos, trxns in groups:
        keyfunc = lambda enum: enum[0] != main_pos

        for pos, trxn in sorted(enumerate(trxns), key=keyfunc):
            data = obj.transaction_data(trxn)
            is_main = pos == main_pos

            if not obj.is_split and obj.skip_transaction(trxn):
                continue

            if is_main and prev_account != obj.account(trxn):
                yield obj.account_start(**data)

            if (obj.is_split and is_main) or not obj.is_split:
                yield obj.transaction(**data)
                prev_account = obj.account(trxn)

            if (obj.is_split and not is_main) or obj.split_account:
                yield obj.split_content(**data)

            if not obj.is_split:
                yield obj.transaction_end()

        if obj.is_split:
            yield obj.transaction_end()


def run():
    if args.debug:
        pprint(dict(args._get_kwargs()))
        exit(0)

    if args.version:
        from . import __version__ as version
        print('v%s' % version)
        exit(0)

    mapping = import_module('mappings.%s' % args.mapping).mapping

    okwargs = {
        'def_type': args.account_type,
        'split_account': args.split,
        'start': parse(args.start),
        'end': parse(args.end)
    }

    content_func = gen_qif_content if args.qif else gen_ofx_content
    OBJ = QIF if args.qif else OFX
    obj = OBJ(mapping, **okwargs)

    try:
        mtime = p.getmtime(args.source.name)
    except AttributeError:
        mtime = time.time()

    csv_content = read_csv(args.source, has_header=obj.has_header)

    # remove csv header
    csv_content.next()
    server_date = dt.fromtimestamp(mtime)
    content = utils.IterStringIO()

    # write content header
    content.write(obj.header(date=server_date, language=args.language))

    # get content body
    chunks = utils.chunk(csv_content, args.chunksize)
    groups = gen_groups(chunks, obj, args.qif)
    gtrxns = gen_trxns(groups, obj, args.collapse)
    main_gtrxns = gen_main_trxns(gtrxns, obj)
    body = content_func(main_gtrxns, obj)

    # write content body and footer
    content.write(body)
    content.write(obj.footer())

    try:
        # write content to file
        utils.write_file(args.dest, content, overwrite=args.overwrite)
    except TypeError as e:
        msg = str(e)

        if not args.collapse:
            msg += 'Try again with `-c` option.'

        exit(msg)

    # print(groups.next())


if __name__ == '__main__':
    run()
