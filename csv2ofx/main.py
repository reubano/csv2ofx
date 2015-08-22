#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" csv2ofx converts a csv file to ofx and qif """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import time
import sys
import argparse

from functools import partial
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
    default='2010-01-01')
parser.add_argument(
    '-m', '--mapping', help="the account mapping",
    default='default')
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
    '-c', '--collapse', action='store_true', default=False, help=(
        'combine splits from the same account and date if the transactions\n'
        'arerecorded double entry style (e.g. full data export from xero.com\n'
        'or Quickbooks)'))
parser.add_argument(
    '-t', '--transfer', action='store_true', default=False, help=(
        "treat ofx transactions as transfers between two accounts"))
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


def gen_content(chunks, obj, ofx, transfer):
    for chunk in chunks:
        if ofx:
            cleansed = [
                {k: xmlize([v]).next() for k, v in c.items()} for c in chunk]
        else:
            cleansed = chunk

        if obj.is_split:
            # group transactions by id
            grouped = utils.group_transactions(cleansed, obj.id)
        else:
            # group transactions by account
            grouped = utils.group_transactions(cleansed, obj.account)

        for _, transactions in grouped:
            if obj.is_split and args.collapse:
                # group transactions by account and sum the amounts
                byaccount = utils.group_transactions(transactions, obj.account)
                merger = partial(utils.merge_dicts, obj.amount, sum)
                trxns = map(merger, byaccount.values())
            else:
                trxns = transactions

            _args = [trxns, obj.convert_amount]

            if obj.is_split and obj.skip_transaction(trxns[0]):
                continue
            elif obj.is_split and not utils.verify_splits(*_args):
                raise Exception('Splits do not sum to zero.')
            elif obj.is_split:
                main_pos, main_trxn = utils.get_max_split(*_args)
            else:
                main_pos, main_trxn = 0, trxns[0]

            main_data = obj.transaction_data(main_trxn)

            if ofx and transfer:
                yield obj.transfer(**main_data)
            else:
                yield obj.account_start(**main_data)
                yield obj.transaction(**main_data)

            for pos, transaction in enumerate(trxns):
                if not pos == main_pos:
                    continue

                data = obj.transaction_data(transaction)

                if not obj.is_split and obj.skip_transaction(transaction):
                    continue

                if not ofx and obj.is_split:
                    content = obj.split_content(**data)
                elif ofx and transfer:
                    content = obj.transfer(**data)
                else:
                    content = obj.transaction(**data)

                yield content

            if not (ofx and transfer):
                yield obj.account_end(**data)


def run():
    if args.debug:
        pprint(dict(args._get_kwargs()))
        exit(0)

    if args.version:
        from . import __version__ as version
        print('v%s' % version)
        exit(0)

    ofx = not args.qif
    mapping = import_module('mappings.%s' % args.mapping).mapping

    okwargs = {
        'def_type': args.account_type,
        'resp_type': 'INTRATRNRS' if args.transfer else 'STMTTRNRS',
        'start': parse(args.start),
        'end': parse(args.end)
    }

    OBJ = QIF if args.qif else OFX
    obj = OBJ(mapping, **okwargs)

    try:
        mtime = p.getmtime(args.source.name)
    except AttributeError:
        mtime = time.time()

    csv_content = read_csv(args.source, has_header=obj.has_header)
    csv_content.next()  # remove header
    server_date = dt.fromtimestamp(mtime)
    content = utils.IterStringIO()
    content.write(obj.header(date=server_date, language=args.language))
    chunks = utils.chunk(csv_content, args.chunksize)
    new_content = gen_content(chunks, obj, ofx, args.transfer)
    content.write(new_content)
    content.write(obj.footer())
    utils.write_file(args.dest, content, overwrite=args.overwrite)


if __name__ == '__main__':
    run()
