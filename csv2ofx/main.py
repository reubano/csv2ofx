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
from tabutils.process import xmlize, chunk

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


def gen_groups(chunks, cont, qif):
    for chnk in chunks:
        if qif:
            cleansed = chnk
        else:
            cleansed = [
                {k: xmlize([v]).next() for k, v in c.items()} for c in chnk]

        keyfunc = cont.id if cont.is_split else cont.account
        yield utils.group_transactions(cleansed, keyfunc)


def gen_trxns(groups, cont, collapse=False):
    for group, transactions in groups:
        if cont.is_split and collapse:
            # group transactions by collapse field and sum the amounts
            groupby = itemgetter(collapse)
            byaccount = utils.group_transactions(transactions, groupby)
            op = lambda values: sum(map(utils.convert_amount, values))
            merger = partial(utils.merge_dicts, cont.amount, op)
            trxns = [merger(dicts) for _, dicts in byaccount]
        else:
            trxns = transactions

        yield (group, trxns)


def gen_main_trxns(groups, cont):
    for group, trxns in groups:
        _args = [trxns, cont.convert_amount]

        # if it's split, transactions skipping is all or none
        if cont.is_split and cont.skip_transaction(trxns[0]):
            continue
        elif cont.is_split and not utils.verify_splits(*_args):
            raise Exception('Splits do not sum to zero.')
        elif cont.is_split:
            main_pos = utils.get_max_split(*_args)[0]
        else:
            main_pos = 0

        keyfunc = lambda enum: enum[0] != main_pos
        sorted_trxns = sorted(enumerate(trxns), key=keyfunc)
        yield (group, main_pos, sorted_trxns)


def gen_base_data(groups, cont):
    for group, main_pos, sorted_trxns in groups:
        for pos, trxn in sorted_trxns:

            if not cont.is_split and cont.skip_transaction(trxn):
                continue

            base_data = {
                'data': cont.transaction_data(trxn),
                'account': cont.account(trxn),
                'is_main': pos == main_pos,
                'split_account': cont.split_account,
                'is_split': cont.is_split,
                'len': len(sorted_trxns),
                'cont': cont,
                'group': group
            }

            yield base_data


def splitless_content(gd, prev_group, content=''):
    if prev_group and prev_group != gd['group']:
        content += gd['cont'].account_end(**gd['data'])

    if gd['is_main']:
        content += gd['cont'].account_start(**gd['data'])

    content += gd['cont'].transaction(**gd['data'])
    return content


def split_like_content(gd, prev_group, content=''):
    if gd['is_split'] and gd['len'] > 2:
        # OFX doesn't support more than 2 splits
        raise TypeError('Group %s has too many splits.\n' % gd['group'])

    if prev_group and prev_group != gd['group'] and gd['is_split']:
        content += gd['cont'].transfer_end(**gd['data'])

    if (gd['is_split'] and gd['is_main']) or gd['split_account']:
        content += gd['cont'].transfer(**gd['data'])

    if (gd['is_split'] and not gd['is_main']) or gd['split_account']:
        content += gd['cont'].split_content(**gd['data'])

    if gd['split_account']:
        content += gd['cont'].transfer_end(**gd['data'])

    return content


def gen_ofx_content(grouped_data, prev_group=None):
    for gd in grouped_data:
        if gd['is_split'] or gd['split_account']:
            yield split_like_content(gd, prev_group)
        else:
            yield splitless_content(gd, prev_group)

        prev_group = gd['group']

    if gd['is_split']:
        yield gd['cont'].transfer_end(**gd['data'])
    elif not gd['split_account']:
        yield gd['cont'].account_end(**gd['data'])


def gen_qif_content(grouped_data, prev_account=None, prev_group=None):
    for gd in grouped_data:
        if prev_group and prev_group != gd['group'] and gd['is_split']:
            yield gd['cont'].transaction_end()

        if gd['is_main'] and prev_account != gd['account']:
            yield gd['cont'].account_start(**gd['data'])

        if (gd['is_split'] and gd['is_main']) or not gd['is_split']:
            yield gd['cont'].transaction(**gd['data'])
            prev_account = gd['account']

        if (gd['is_split'] and not gd['is_main']) or gd['split_account']:
            yield gd['cont'].split_content(**gd['data'])

        if not gd['is_split']:
            yield gd['cont'].transaction_end()

        prev_group = gd['group']

    if gd['is_split']:
        yield gd['cont'].transaction_end()


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
        'split_header': args.split,
        'start': parse(args.start),
        'end': parse(args.end)
    }

    content_func = gen_qif_content if args.qif else gen_ofx_content
    Content = QIF if args.qif else OFX
    cont = Content(mapping, **okwargs)

    try:
        mtime = p.getmtime(args.source.name)
    except AttributeError:
        mtime = time.time()

    csv_content = read_csv(args.source, has_header=cont.has_header)
    csv_content.next()  # remove csv header
    server_date = dt.fromtimestamp(mtime)
    content = utils.IterStringIO()
    content.write(cont.header(date=server_date, language=args.language))
    chunks = chunk(csv_content, args.chunksize)
    groups = it.chain.from_iterable(gen_groups(chunks, cont, args.qif))
    grouped_trxns = gen_trxns(groups, cont, args.collapse)
    main_gtrxns = gen_main_trxns(grouped_trxns, cont)
    grouped_data = gen_base_data(main_gtrxns, cont)
    body = content_func(grouped_data)
    content.write(body)
    content.write(cont.footer())

    try:
        kwargs = {
            'overwrite': args.overwrite,
            'chunksize': args.chunksize
        }
        utils.write_file(args.dest, content, **kwargs)
    except TypeError as e:
        msg = str(e)

        if not args.collapse:
            msg += 'Try again with `-c` option.'

        exit(msg)


if __name__ == '__main__':
    run()
