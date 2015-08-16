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
class QIF(Account)
    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)

    def header(self, **kwargs):
        return None

    def transaction_data(self, tr, **kwargs):
        """ gets QIF transaction data

        Args:
            tr (List[str]): the transaction
            time_stamp (str): the time stamp

        Kwargs:

        Returns:
            (List[str]):   the QIF content

        Examples:
            >>> ({'Transaction Type': 'debit', 'amount': 1000.00, 'Date': '06/12/10', 'Description': 'payee', 'Original Description': 'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': 'account'}) == {'amount': '-1000', 'Payee': 'payee', 'Date': '06/12/10', 'desc': 'description notes', 'id': '4fe86d9de995225b174fb3116ca6b1f4', 'check_num': None, 'type': 'debit', 'split_account': 'Checking', 'split_account_id': '195917574edc9b6bbeb5be9785b6a479'}
        """
        data = super(Account, self).transaction_data(tr, **kwargs)
        desc = data['desc']
        notes = data['notes']
        tran_class = data['tran_class']

        # qif doesn't support notes or class so add them to description
        sep =  ' ' if desc else ''
        desc += '%s%s' % (sep, notes) if notes else None
        sep =  ' ' if desc else ''
        desc += '%s%s' % (sep, tran_class) if tran_class else None
        data.update({'desc': desc})
        return data

    def account_start(self, **kwargs):
        """ Gets QIF format account content

        Args:
            (str):  account     the account
            (str):  account_type    the account types

        Kwargs:

        Returns:
             (str): the QIF content

        Examples:
            >>> ('account', 'type') == "!Account\nNaccount\nTtype\n^\n"
        """
        return "!Account\nN%(account)s\nT%(account_type)s\n^\n" % kwargs

    def transaction(self, **kwargs):
        """ Gets QIF format transaction content

        Args:
            (str):  account_type    the account types

        Kwargs:

        Returns:
            (str):  content     the QIF content

        Examples:
            >>> ('type', {'Payee': 'payee', 'amount': 100, 'check_num': 1, 'Date': '01/01/12'}) == "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
            >>> ('type', {'Payee': 'payee', 'amount': 100, 'Date': '01/01/12'}) == "!Type:type\nD01/01/12\nPpayee\nT100\n"
        """
        amt = kwargs['amount']

        # switch signs if source is xero
        newAmt = amt[1:] if amt[0] == '-' else '-%s' % amt
        kwargs['amt'] = newAmt if source == 'xero' else amt

        content = "!Type:%(account_type)s\n" % kwargs
        content += "N%(check_num)s\n" % kwargs if 'check_num' in kwargs else ''
        content += "D%(date)s\nP%(payee)s\nT%(amt)s\n" % kwargs
        return content

    def split(self, split_account, **kwargs):
        """ Gets QIF format split content

        Args:

        Kwargs:

        Returns:
            (str): the QIF content

        Examples:
            >>> ('account', {'desc': 'desc', 'amount': 100}) == "Saccount\nEdesc\n100\n"
        """
        amt = kwargs['amount']

        # switch signs if source is xero
        newAmt = amt[1:] if amt[0] == '-' else '-%s' % amt
        kwargs['amt'] = newAmt if source == 'xero' else amt
        content = "S%s\nE" % split_account
        content += "%(desc)s\n\%(amt)s\n" % kwargs
        return content

    def transaction_end(self):
        """ Gets QIF transaction end

        Returns:
            (str): the QIF content

        Examples:
            >>> () == "^\n"
        """
        return "^\n"

    def footer(self):
        return None

