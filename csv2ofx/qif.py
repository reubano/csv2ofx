#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.qif
~~~~~~~~~~~

Provides methods for generating qif files

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from . import File
from . import utils


class QIF(File):
    def __init__(self, mapping=None, **kwargs):
        super(QIF, self).__init__(mapping, **kwargs)
        self.def_type = kwargs.get('def_type', 'Bank')
        self.account_types = {
            'Bank': (
                'checking', 'savings', 'market', 'receivable', 'payable',
                'visa', 'master', 'express', 'discover'),
            'Cash': ('cash',)
        }

    def header(self, **kwargs):
        return None

    def transaction_data(self, tr):
        """ gets QIF transaction data

        Args:
            tr (List[str]): the transaction

        Kwargs:

        Returns:
            (List[str]):   the QIF content

        Examples:
            >>> from mappings.mint import mapping
            >>> tr = {'Transaction Type': 'debit', 'Amount': 1000.00, \
'Date': '06/12/10', 'Description': 'payee', 'Original Description': \
'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': \
'account'}
            >>> QIF(mapping).transaction_data(tr)
            {u'account': u'account', u'check_num': None, u'account_type': \
u'Bank', u'account_id': 'e268443e43d93dab7ebef303bbe9642f', u'payee': \
u'payee', u'tran_class': None, u'split_account': u'Checking', u'notes': \
u'notes', u'tran_type': u'debit', u'split_account_id': \
'195917574edc9b6bbeb5be9785b6a479', u'bank_id': \
'e268443e43d93dab7ebef303bbe9642f', u'currency': u'USD', u'amount': \
Decimal('-1000.00'), u'split_account_type': u'Bank', u'date': \
datetime.datetime(2010, 6, 12, 0, 0), u'id': \
'b045c43277d797f8a6993ee6668958d9', u'bank': u'account', u'desc': \
u'description notes'}
        """
        data = super(QIF, self).transaction_data(tr)
        args = [self.account_types, self.def_type]
        sa_type = utils.get_account_type(data['split_account'], *args)

        desc = data.get('desc') or ''
        notes = data['notes']
        tran_class = data['tran_class']

        # qif doesn't support notes or class so add them to description
        sep = ' ' if desc else ''
        desc += '%s%s' % (sep, notes) if notes else ''
        sep = ' ' if desc else ''
        desc += '%s%s' % (sep, tran_class) if tran_class else ''

        new_data = {
            'account_type': utils.get_account_type(data['account'], *args),
            'split_account_type': sa_type,
            'desc': desc}

        data.update(new_data)
        return data

    def account_start(self, **kwargs):
        """ Gets QIF format account content

        Kwargs:
            account (str): the account

        Returns:
             (str): the QIF content

        Examples:
            >>> kwargs = {'account': 'account', 'account_type': 'type'}
            >>> QIF().account_start(**kwargs).replace('\\n', '').replace(\
'\\t', '')
            u'!AccountNaccountTtype^'
        """
        return "!Account\nN%(account)s\nT%(account_type)s\n^\n" % kwargs

    def transaction(self, **kwargs):
        """ Gets QIF format transaction content

        Kwargs:
            (str): account_type the account type

        Returns:
            (str): content the QIF content

        Examples:
            >>> kwargs = {'payee': 'payee', 'amount': 100, 'check_num': 1, \
'date': '01/01/12', 'account_type': 'type'}
            >>> QIF().transaction(**kwargs).replace('\\n', '').replace(\
'\\t', '')
            u'!Type:typeN1D01/01/12PpayeeT100'
        """
        content = "!Type:%(account_type)s\n" % kwargs
        content += "N%(check_num)s\n" % kwargs if 'check_num' in kwargs else ''
        content += "D%(date)s\nP%(payee)s\nT%(amount)s\n" % kwargs
        return content

    def split_content(self, split_account, **kwargs):
        """ Gets QIF format split content

        Args:

        Kwargs:

        Returns:
            (str): the QIF content

        Examples:
            >>> kwargs =  {'desc': 'desc', 'amount': 100}
            >>> QIF().split_content('account', **kwargs).replace(\
'\\n', '').replace('\\t', '')
            u'SaccountEdesc100'
        """
        content = "S%s\nE" % split_account
        content += "%(desc)s\n%(amount)s\n" % kwargs
        return content

    def account_end(self, **kwargs):
        """ Gets QIF transaction end

        Returns:
            (str): the QIF content

        Examples:
            >>> QIF().account_end().replace('\\n', '').replace('\\t', '')
            u'^'
        """
        return "^\n"

    def footer(self):
        return None
