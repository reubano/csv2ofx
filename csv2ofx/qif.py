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


class QIF(File):
    def __init__(self, mapping, **kwargs):
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
            time_stamp (str): the time stamp

        Kwargs:

        Returns:
            (List[str]):   the QIF content

        Examples:
            >>> tr = {'Transaction Type': 'debit', 'amount': 1000.00, \
'Date': '06/12/10', 'Description': 'payee', 'Original Description': \
'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': \
'account'}
            >>> QIF({}).transaction_data(tr)
            {'amount': '-1000', 'Payee': 'payee', 'Date': '06/12/10', 'desc': \
'description notes', 'id': '4fe86d9de995225b174fb3116ca6b1f4', 'check_num': \
None, 'type': 'debit', 'split_account': 'Checking', 'split_account_id': \
'195917574edc9b6bbeb5be9785b6a479'}
        """
        data = super(QIF, self).transaction_data(tr)
        desc = data.get('desc') or ''
        notes = data['notes']
        tran_class = data['tran_class']

        # qif doesn't support notes or class so add them to description
        sep = ' ' if desc else ''
        desc += '%s%s' % (sep, notes) if notes else ''
        sep = ' ' if desc else ''
        desc += '%s%s' % (sep, tran_class) if tran_class else ''
        data.update({'desc': desc})
        return data

    def account_start(self, **kwargs):
        """ Gets QIF format account content

        Kwargs:
            account (str): the account

        Returns:
             (str): the QIF content

        Examples:
            >>> ('account', 'type') == "!Account\nNaccount\nTtype\n^\n"
        """
        return "!Account\nN%(account)s\nT%(account_type)s\n^\n" % kwargs

    def transaction(self, **kwargs):
        """ Gets QIF format transaction content

        Kwargs:
            (str): account_type the account type

        Returns:
            (str): content the QIF content

        Examples:
            >>> kwargs = {'Payee': 'payee', 'amount': 100, 'check_num': 1, \
'Date': '01/01/12'})
            >>> transaction(**kwargs)
            "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
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
            >>> split_content('account', {'desc': 'desc', 'amount': 100})
            "Saccount\nEdesc\n100\n"
        """
        content = "S%s\nE" % split_account
        content += "%(desc)s\n\%(amount)s\n" % kwargs
        return content

    def account_end(self, **kwargs):
        """ Gets QIF transaction end

        Returns:
            (str): the QIF content

        Examples:
            >>> () == "^\n"
        """
        return "^\n"

    def footer(self):
        return None
