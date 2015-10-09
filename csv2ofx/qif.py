#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.qif
~~~~~~~~~~~

Provides methods for generating qif content

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from datetime import datetime as dt
from tabutils.fntools import chunk

from . import Content, utils


class QIF(Content):
    def __init__(self, mapping=None, **kwargs):
        """ QIF constructor
        Args:
            mapping (dict): bank mapper (see csv2ofx.mappings)
            kwargs (dict): Keyword arguments

        Kwargs:
            def_type (str): Default account type.
            split_header (str): Transaction field to use for the split account.
            start (date): Date from which to begin including transactions.
            end (date): Date from which to exclude transactions.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> QIF(mapping)  #doctest: +ELLIPSIS
            <csv2ofx.qif.QIF object at 0x...>
        """
        super(QIF, self).__init__(mapping, **kwargs)
        self.def_type = kwargs.get('def_type')
        self.prev_account = None
        self.prev_group = None
        self.account_types = {
            'Bank': ('checking', 'savings', 'market', 'income'),
            'Oth A': ('receivable',),
            'Oth L': ('payable',),
            'CCard': ('visa', 'master', 'express', 'discover', 'platinum'),
            'Cash': ('cash', 'expenses')
        }

    def header(self, **kwargs):
        return None

    def transaction_data(self, tr):
        """ gets QIF transaction data

        Args:
            tr (dict): the transaction

        Returns:
            (dict): the QIF transaction data

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {'Transaction Type': 'debit', 'Amount': 1000.00, \
'Date': '06/12/10', 'Description': 'payee', 'Original Description': \
'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': \
'account'}
            >>> QIF(mapping, def_type='Bank').transaction_data(tr)
            {u'account_type': u'Bank', u'account_id': \
'e268443e43d93dab7ebef303bbe9642f', u'memo': u'description notes', \
u'split_account_id': None, u'currency': u'USD', u'date': \
datetime.datetime(2010, 6, 12, 0, 0), u'class': None, u'bank': u'account', \
u'account': u'account', u'split_memo': u'description notes', \
u'split_account': None, u'bank_id': 'e268443e43d93dab7ebef303bbe9642f', \
u'id': 'ee86450a47899254e2faa82dca3c2cf2', u'payee': u'payee', \
u'amount': Decimal('-1000.00'), u'check_num': None, u'type': u'debit'}
        """
        data = super(QIF, self).transaction_data(tr)
        args = [self.account_types, self.def_type]
        memo = data.get('memo')
        _class = data.get('class')

        if memo and _class:
            split_memo = '%s %s' % (memo, _class)
        else:
            split_memo = memo or _class

        new_data = {
            'account_type': utils.get_account_type(data['account'], *args),
            'split_memo': split_memo}

        data.update(new_data)
        return data

    def account_start(self, **kwargs):
        """ Gets QIF format account content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            account (str): The account name.
            account_type (str): The account type. One of ['Bank', 'Oth A',
                'Oth L', 'CCard', 'Cash'] (required).

        Returns:
             (str): the QIF content

        Examples:
            >>> kwargs = {'account': 'account', 'account_type': 'Bank'}
            >>> QIF().account_start(**kwargs).replace('\\n', '').replace(\
'\\t', '')
            u'!AccountNaccountTBank^'
        """
        return "!Account\nN%(account)s\nT%(account_type)s\n^\n" % kwargs

    def transaction(self, **kwargs):
        """ Gets QIF format transaction content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            date (date): the transaction date (required)
            amount (number): the transaction amount (required)
            payee (number): the transaction amount (required)
            memo (str): the transaction memo
            class (str): the transaction classification
            check_num (str): a unique transaction identifier

        Returns:
            (str): content the QIF content

        Examples:
            >>> kwargs = {'payee': 'payee', 'amount': 100, 'check_num': 1, \
'date': dt(2012, 1, 1), 'account_type': 'Bank'}
            >>> QIF().transaction(**kwargs).replace('\\n', '').replace(\
'\\t', '')
            u'!Type:BankN1D01/01/12PpayeeT100.00'
        """
        kwargs.update({'time_stamp': kwargs['date'].strftime('%m/%d/%y')})

        if self.is_split:
            kwargs.update({'amount': kwargs['amount'] * -1})

        content = "!Type:%(account_type)s\n" % kwargs

        if kwargs.get('check_num'):
            content += "N%(check_num)s\n" % kwargs

        content += "D%(time_stamp)s\n" % kwargs
        content += "P%(payee)s\n" % kwargs

        if kwargs.get('memo'):
            content += "M%(memo)s\n" % kwargs

        if kwargs.get('class'):
            content += "L%(class)s\n" % kwargs

        content += "T%(amount)0.2f\n" % kwargs
        return content

    def split_content(self, **kwargs):
        """ Gets QIF format split content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            split_account (str): Account to use as the transfer recipient.
                (useful in cases when the transaction data isn't already split)

            account (str): A unique account identifier (required if a
                `split_account` isn't given).

            split_memo (str): the transaction split memo

        Returns:
            (str): the QIF content

        Examples:
            >>> kwargs =  {'account': 'account', 'split_memo': 'memo', \
'amount': 100}
            >>> QIF().split_content(**kwargs).replace('\\n', '').replace(\
'\\t', '')
            u'SaccountEmemo$100.00'
        """
        if kwargs.get('split_account'):
            content = "S%(split_account)s\n" % kwargs
        else:
            content = "S%(account)s\n" % kwargs

        if kwargs.get('split_memo'):
            content += "E%(split_memo)s\n" % kwargs

        content += "$%(amount)0.2f\n" % kwargs
        return content

    def transaction_end(self):
        """ Gets QIF transaction end

        Returns:
            (str): the QIF transaction end

        Examples:
            >>> QIF().transaction_end().replace('\\n', '').replace('\\t', '')
            u'^'
        """
        return "^\n"

    def footer(self, **kwargs):
        """ Gets QIF transaction footer.

        Returns:
            (None): the QIF footer

        Examples:
            >>> QIF().footer()
        """
        if self.is_split:
            return self.transaction_end()

    def gen_body(self, data):
        for gd in data:
            trxn_data = self.transaction_data(gd['trxn'])
            account = self.account(gd['trxn'])
            group = gd['group']

            if self.prev_group and self.prev_group != group and self.is_split:
                yield self.transaction_end()

            if gd['is_main'] and self.prev_account != account:
                yield self.account_start(**trxn_data)

            if (self.is_split and gd['is_main']) or not self.is_split:
                yield self.transaction(**trxn_data)
                self.prev_account = account

            if (self.is_split and not gd['is_main']) or self.split_account:
                yield self.split_content(**trxn_data)

            if not self.is_split:
                yield self.transaction_end()

            self.prev_group = group

    def gen_groups(self, records, chunksize=None):
        for chnk in chunk(records, chunksize):
            keyfunc = self.id if self.is_split else self.account

            for group in utils.group_transactions(chnk, keyfunc):
                yield group
