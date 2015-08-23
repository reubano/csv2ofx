#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.ofx
~~~~~~~~~~~

Provides methods for generating OFX files

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
from . import File
from . import utils


class OFX(File):
    def __init__(self, mapping=None, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:
            resp_type (str): the time in mmddyy_hhmmss format
            'INTRATRNRS' or 'STMTTRNRS'

        Returns:
            (str): the OFX content
        """
        super(OFX, self).__init__(mapping, **kwargs)

        if kwargs.get('split_account'):
            self.resp_type = 'INTRATRNRS'
        else:
            self.resp_type = 'STMTTRNRS'

        self.def_type = kwargs.get('def_type', 'CHECKING')
        self.account_types = {
            'CHECKING': ('checking', 'income', 'receivable', 'payable'),
            'SAVINGS': ('savings',),
            'MONEYMRKT': ('market', 'cash', 'expenses'),
            'CREDITLINE': ('visa', 'master', 'express', 'discover')
        }

    def header(self, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:
            date (date): the datetime

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'date': dt(2012, 1, 15)}
            >>> OFX().header(**kwargs).replace('\\n', '').replace('\\t', '')
            u'DATA:OFXSGMLENCODING:UTF-8<OFX><SIGNONMSGSRSV1><SONRS><STATUS>\
<CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><DTSERVER>20120115</DTSERVER>\
<LANGUAGE>ENG</LANGUAGE></SONRS></SIGNONMSGSRSV1><BANKMSGSRSV1><INTRATRNRS>\
<TRNUID></TRNUID><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>'
        """
        kwargs.setdefault('language', 'ENG')
        time_stamp = kwargs['date'].strftime('%Y%m%d%H%M%S')  # yyyymmddhhmmss

        content = 'DATA:OFXSGML\n'
        content += 'ENCODING:UTF-8\n'
        content += '<OFX>\n'
        content += '\t<SIGNONMSGSRSV1>\n'
        content += '\t\t<SONRS>\n'
        content += '\t\t\t<STATUS>\n'
        content += '\t\t\t\t<CODE>0</CODE>\n'
        content += '\t\t\t\t<SEVERITY>INFO</SEVERITY>\n'
        content += '\t\t\t</STATUS>\n'
        content += '\t\t\t<DTSERVER>%s</DTSERVER>\n' % time_stamp
        content += '\t\t\t<LANGUAGE>%(language)s</LANGUAGE>\n' % kwargs
        content += '\t\t</SONRS>\n'
        content += '\t</SIGNONMSGSRSV1>\n'
        content += '\t<BANKMSGSRSV1>\n'
        content += '\t\t<%s>\n' % self.resp_type
        content += '\t\t\t<TRNUID></TRNUID>\n'
        content += '\t\t\t<STATUS>\n'
        content += '\t\t\t\t<CODE>0</CODE>\n'
        content += '\t\t\t\t<SEVERITY>INFO</SEVERITY>\n'
        content += '\t\t\t</STATUS>\n'
        return content

    def transaction_data(self, tr):
        """ gets OFX transaction data

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
            >>> OFX(mapping).transaction_data(tr)
            {u'account_type': u'CHECKING', u'account_id': \
'e268443e43d93dab7ebef303bbe9642f', u'memo': u'description notes', \
u'split_account_id': '195917574edc9b6bbeb5be9785b6a479', u'currency': u'USD', \
u'date': datetime.datetime(2010, 6, 12, 0, 0), u'id': \
'0b9df731dbf286154784222755482d6f', u'bank': u'account', u'account': \
u'account', u'split_account': u'Checking', u'bank_id': \
'e268443e43d93dab7ebef303bbe9642f', u'class': None, u'payee': u'payee', \
u'amount': Decimal('-1000.00'), u'split_account_type': u'CHECKING', \
u'check_num': None, u'type': u'debit'}
        """
        data = super(OFX, self).transaction_data(tr)
        args = [self.account_types, self.def_type]
        sa_type = utils.get_account_type(data['split_account'], *args)
        memo = data.get('memo')
        _class = data.get('class')

        if memo and _class:
            memo = '%s %s' % (memo, _class)
        else:
            memo = memo or _class

        new_data = {
            'account_type': utils.get_account_type(data['account'], *args),
            'split_account_type': sa_type,
            'memo': memo}

        data.update(new_data)
        return data

    def footer(self):
        """ Gets OFX transfer end

        Returns:
            (str): the OFX content

        Examples:
            >>> OFX().footer().replace('\\n', '').replace('\\t', '')
            u'</INTRATRNRS></BANKMSGSRSV1></OFX>'
        """
        return "\t\t</%s>\n\t</BANKMSGSRSV1>\n</OFX>\n" % self.resp_type

    def account_start(self, **kwargs):
        """ Gets OFX format transaction account start content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'start': dt(2012, 1, 1), 'end': dt(2012, 2, 1)}
            >>> akwargs = {'currency': 'USD', 'bank_id': 1, 'account_id': 1, \
'account_type': 'type'}
            >>> OFX(**kwargs).account_start(**akwargs).replace(\
'\\n', '').replace('\\t', '')
            u'<STMTRS><CURDEF>USD</CURDEF><BANKACCTFROM><BANKID>1</BANKID>\
<ACCTID>1</ACCTID><ACCTTYPE>type</ACCTTYPE></BANKACCTFROM><BANKTRANLIST>\
<DTSTART>20120101</DTSTART><DTEND>20120201</DTEND>'
        """
        kwargs.update({
            'start_date': self.start.strftime('%Y%m%d'),
            'end_date': self.end.strftime('%Y%m%d')})

        content = '\t\t\t<STMTRS>\n'
        content += '\t\t\t\t<CURDEF>%(currency)s</CURDEF>\n' % kwargs
        content += '\t\t\t\t<BANKACCTFROM>\n'
        content += '\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n' % kwargs
        content += '\t\t\t\t\t<ACCTID>%(account_id)s</ACCTID>\n' % kwargs
        content += '\t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n' % kwargs
        content += '\t\t\t\t</BANKACCTFROM>\n'
        content += '\t\t\t\t<BANKTRANLIST>\n'
        content += '\t\t\t\t\t<DTSTART>%(start_date)s</DTSTART>\n' % kwargs
        content += '\t\t\t\t\t<DTEND>%(end_date)s</DTEND>\n' % kwargs
        return content

    def transaction(self, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'date': dt(2012, 1, 15), 'type': 'type', \
'amount': 100, 'id': 1, 'check_num': 1, 'payee': 'payee', 'memo': 'memo'}
            >>> OFX().transaction(**kwargs).replace('\\n', '').replace( \
'\\t', '')
            u'<STMTTRN><TRNTYPE>type</TRNTYPE><DTPOSTED>20120115000000\
</DTPOSTED><TRNAMT>100</TRNAMT><FITID>1</FITID><CHECKNUM>1</CHECKNUM><NAME>\
payee</NAME><MEMO>memo</MEMO></STMTTRN>'
        """
        time_stamp = kwargs['date'].strftime('%Y%m%d%H%M%S')  # yyyymmddhhmmss

        content = '\t\t\t\t\t<STMTTRN>\n'
        content += '\t\t\t\t\t\t<TRNTYPE>%(type)s</TRNTYPE>\n' % kwargs
        content += '\t\t\t\t\t\t<DTPOSTED>%s</DTPOSTED>\n' % time_stamp
        content += '\t\t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n' % kwargs
        content += '\t\t\t\t\t\t<FITID>%(id)s</FITID>\n' % kwargs
        content += '\t\t\t\t\t\t<CHECKNUM>%(check_num)s</CHECKNUM>\n' % kwargs
        content += '\t\t\t\t\t\t<NAME>%(payee)s</NAME>\n' % kwargs

        if kwargs.get('memo'):
            content += '\t\t\t\t\t\t<MEMO>%(memo)s</MEMO>\n' % kwargs

        content += '\t\t\t\t\t</STMTTRN>\n'
        return content

    def account_end(self, **kwargs):
        """ Gets OFX format transaction account end content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'balance': 150, 'date': dt(2012, 1, 15)}
            >>> OFX().account_end(**kwargs).replace('\\n', '').replace('\\t', '')
            u'</BANKTRANLIST><LEDGERBAL><BALAMT>150</BALAMT><DTASOF>\
20120115000000</DTASOF></LEDGERBAL></STMTRS>'
        """
        time_stamp = kwargs['date'].strftime('%Y%m%d%H%M%S')  # yyyymmddhhmmss
        content = '\t\t\t\t</BANKTRANLIST>\n'

        if kwargs.get('balance'):
            content += '\t\t\t\t<LEDGERBAL>\n'
            content += '\t\t\t\t\t<BALAMT>%(balance)s</BALAMT>\n' % kwargs
            content += '\t\t\t\t\t<DTASOF>%s</DTASOF>\n' % time_stamp
            content += '\t\t\t\t</LEDGERBAL>\n'

        content += '\t\t\t</STMTRS>\n'
        return content

    def transfer(self, **kwargs):
        """ Gets OFX transfer start

        Kwargs:
            account_type (str): the account type

        Returns:
            (str): the QIF content

        Examples:
            >>> kwargs = {'currency': 'USD', 'date': dt(2012, 1, 15), \
'bank_id': 1, 'account_id': 1, 'account_type': 'type', 'split_account_id': 2, \
'split_account': 'split_account', 'split_account_type': 'type', 'amount': 100 \
, 'id': 'jbaevf'}
            >>> OFX().transfer(**kwargs).replace('\\n', '').replace('\\t', '')
            u'<INTRARS><CURDEF>USD</CURDEF><SRVRTID>jbaevf</SRVRTID>\
<XFERINFO><BANKACCTFROM><BANKID>1</BANKID><ACCTID>1</ACCTID><ACCTTYPE>type\
</ACCTTYPE></BANKACCTFROM><BANKACCTTO><BANKID>1</BANKID><ACCTID>2</ACCTID>\
<ACCTTYPE>type</ACCTTYPE></BANKACCTTO><TRNAMT>100</TRNAMT></XFERINFO>\
<DTPOSTED>20120115000000</DTPOSTED></INTRARS>'
        """
        content = '\t\t\t<INTRARS>\n'
        content += '\t\t\t\t<CURDEF>%(currency)s</CURDEF>\n' % kwargs
        content += '\t\t\t\t<SRVRTID>%(id)s</SRVRTID>\n' % kwargs
        content += '\t\t\t\t<XFERINFO>\n'
        content += '\t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n' % kwargs
        content += '\t\t\t\t\t<BANKACCTFROM>\n'
        content += '\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTID>%(account_id)s</ACCTID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTTYPE>%(account_type)s' % kwargs
        content += '</ACCTTYPE>\n'
        content += '\t\t\t\t\t</BANKACCTFROM>\n'
        return content

    def split_content(self, **kwargs):
        content = '\t\t\t\t\t<BANKACCTTO>\n'
        content += '\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n' % kwargs

        if kwargs.get('split_account'):
            content += '\t\t\t\t\t\t<ACCTID>%(split_account_id)s' % kwargs
        else:
            content += '\t\t\t\t\t\t<ACCTID>%(account_id)s' % kwargs

        content += '</ACCTID>\n'

        if kwargs.get('split_account'):
            content += '\t\t\t\t\t\t<ACCTTYPE>%(split_account_type)s' % kwargs
        else:
            content += '\t\t\t\t\t\t<ACCTTYPE>%(account_type)s' % kwargs

        content += '</ACCTTYPE>\n'
        content += '\t\t\t\t\t</BANKACCTTO>\n'
        return content

    def transfer_end(self, **kwargs):
        time_stamp = kwargs['date'].strftime('%Y%m%d%H%M%S')  # yyyymmddhhmmss
        content = '\t\t\t\t</XFERINFO>\n'
        content += '\t\t\t\t<DTPOSTED>%s</DTPOSTED>\n' % time_stamp
        content += '\t\t\t</INTRARS>\n'
        return content
