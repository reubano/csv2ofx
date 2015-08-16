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

from inspect import ismodule, getmembers
from importlib import import_module
from os import unlink, getcwd, environ, path as p
from datetime import datetime as dt
from dateutil.parser import parse
from manager import Manager
from . import utils

manager = Manager()

DEF_ACCOUNTS = {'ofx': 'CHECKING', 'qif': 'Bank'}

TYPES = {
	'ofx': {
		'CHECKING': ('checking'),
		'SAVINGS': ('savings'),
		'MONEYMRKT': ('market'),
		'CREDITLINE': ('visa', 'master', 'express', 'discover')
	},
	'qif': {
		'Bank': (
			'checking', 'savings', 'market', 'receivable', 'payable', 'visa',
			'master', 'express', 'discover'
		),
		'Cash': ('cash',)
	}
}

_types = list(it.chain.from_iterable(v.keys() for v in TYPES.values()))
_mappings = [n for n, v in getmembers('mappings', ismodule)]
_basedir = p.dirname(__file__)

def _gen_content(obj, unique_accounts, **kwargs):
	for account in unique_accounts:
		kwargs.update({
			'account': account,
			'account_id': md5(account),
			'account_type': account_type})

		yield obj.account_start(**kwargs)
		the_content = split_content if qif else csv_content

		for transaction in the_content:
			kwargs.update({'time_stamp': parse(transaction[obj.head_date])}

			if qif and obj.split:
				data = map(obj.transaction_data, transaction)
				yield obj.transaction(**data[0])
				splitAccounts = getSplitAccounts(transaction)
				yield ''.join(map(obj.split, splitAccounts, data[1:]))
			else:
				data = obj.transaction_data(transaction, **kwargs)

			if (qif and not obj.split) or (ofx and not transfer):
				yield obj.transaction(**data)
			elif ofx and transfer:
				yield obj.transfer(**data)

			if qif and not obj.split:
				yield obj.split(splitAccount, **data)

			if qif:
				yield obj.transaction_end()

		if ofx:
			yield obj.account_end(**kwargs)

@manager.arg(
  'source', type=argparse.FileType('r'), nargs='?', help='the source csv file (defaults to stdin)', default=sys.stdin)
@manager.arg(
  'dest', type=argparse.FileType('w'), nargs='?', , help='the output file (defaults to stdout)'default=sys.stdout)
@manager.arg(
	'account_type', 'A', choices=_types, help=(
		"account type to use if no match is found, defaults to 'CHECKING'"
		"for OFX and 'Bank' for QIF."))
@manager.arg('currency', 'C', default='USD', help="the currency")

@manager.arg(
	'delimiter', 'D', metavar='CHAR', help="one character field delimiter",
	default=',')

@manager.arg('end', 'e', metavar='DATE', help="end date", default=str(dt.now()))
@manager.arg('language', 'l', help="the language", default='ENG')

@manager.arg(
	'primary', 'p', metavar='ACCOUNT',
	help="primary account used to pay credit cards", default='MITFCU Checking')

@manager.arg('start', 's', metavar='DATE', help="the start date", default='1/1/1900')
@manager.arg(
	'mapping', 'm', choices=_mappings, help="the account mapping", default='mint')

@manager.arg(
	'qif', 'q', help="enables 'QIF' output instead of 'OFX'", type=bool,
	default=False)
@manager.arg(
	'collapse', 'c', type=bool, default=False, help=(
		'combine splits from the same account and date if the transaction are
		'recorded double entry style (e.g. full data export from xero.com or
		'Quickbooks)'))
@manager.arg(
	'transfer', 't', type=bool, default=False, help=(
		"treat ofx transactions as transfers between accounts (sets the "
		"destination account to 'category'"))
@manager.arg(
	'overwrite', 'o', type=bool, default=False,
	help="overwrite destination file if it exists")
@manager.arg(
	'debug', 'd', type=bool, default=False,
	help="display the options and arguments passed to the parser")
@manager.arg('verbose', 'v', help="verbose output", type=bool, default=False

@manager.command
def convert(source, dest, **kwargs):
	if debug:
		print('[Command opts] ', kwargs)
		print('[Command args] ', source, dest)
		exit(0)

	mapping = kwargs['mapping']
	start_date = parse(kwargs['start'])
	end_date = parse(kwargs['end'])
	collapse = kwargs['collapse']
	resp_type = 'INTRATRNRS' if kwargs.get('transfer') else 'STMTTRNRS'
	qif = kwargs['qif']
	ofx = not qif
	otype = 'qif' if qif else 'ofx'
	def_type = kwargs.get('account_type', DEF_ACCOUNTS[otype])

	module = import_module('mappings.%s' % mapping)
	type_list = TYPES[otype]

	if p.isfile(source):
		server_date = time.gmtime(p.getmtime(source))
		csv_content = tabutils.read_csv(source)
	else:
		server_date = time.gmtime(time.time())
		csv_content = tabutils.read_csv_str(source)

	csv_content = xmlize(csv_content) if ofx else csv_content
	exit(0)
	obj = QIF(module.mapping) if qif else OFX(module.mapping, resp_type)
	split_content = makeSplits(csv_content)

	if obj.split and verifySplits(split_content):
		split_content = collapseSplits(split_content) if collapse else split_content

		# get accounts and keys
		maxAmounts = getMaxSplitAmounts(split_content)
		accounts = getAccounts(split_content, maxAmounts)

		# move main splits to beginning of transaction array
		split_content = func(split_content, keys)
	elif obj.split:
		pass
		# error
	else:
		accounts = getAccounts(split_content)

	account_types = getAccountTypes(accounts, type_list, def_type)
	unique_accounts = sorted(array_combine(accounts, account_types))
	content = utils.IterStringIO()

	if qif:
		content.write(obj.header())
	else:
		content.write(obj.header(time_stamp=server_date, language=language))
		content.write(obj.response_start())

	content.write(_gen_content(obj, unique_accounts, **kwargs))
	content.write(obj.footer())
	write_file(dest, content, chunksize=?, overwrite=overwrite)


@manager.command
def ver():
  """Show version"""
  from . import __version__ as version
  print('v%s' % version)


if __name__ == '__main__':
  manager.main()
