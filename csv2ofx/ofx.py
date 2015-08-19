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

from . import File
from . import utils


class OFX(File):
    def __init__(self, mapping, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:
            resp_type (str): the time in mmddyy_hhmmss format
            'INTRATRNRS' or 'STMTTRNRS'

        Returns:
            (str): the OFX content
        """
        super(OFX, self).__init__(mapping, **kwargs)
        self.resp_type = kwargs.get('resp_type', 'INTRATRNRS')
        self.def_type = kwargs.get('def_type', 'CHECKING')
        self.account_types = {
            'CHECKING': ('checking'),
            'SAVINGS': ('savings'),
            'MONEYMRKT': ('market'),
            'CREDITLINE': ('visa', 'master', 'express', 'discover')
        }

    def header(self, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:
            time_stamp (str): the time in mmddyy_hhmmss format

        Returns:
            (str): the OFX content

        Examples:
            >>> (20120101111111) == "<OFX>\n\t<SIGNONMSGSRSV1>\n\t\t<SONRS>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n\t\t\t<DTSERVER>20120101111111</DTSERVER>\n\t\t\t<LANGUAGE>ENG</LANGUAGE>\n\t\t</SONRS>\n\t</SIGNONMSGSRSV1>\n"
        """
        kwargs.setdefault('language', 'ENG')
        time_stamp = kwargs['time_stamp'].strftime('%Y%m%d')

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

    def footer(self):
        """ Gets OFX transfer end

        Returns:
            (str): the OFX content

        Examples:
            >>> () == "\t\t</INTRATRNRS>\n\t</BANKMSGSRSV1>\n</OFX>"
        """
        return "\t\t</%s>\n\t</BANKMSGSRSV1>\n</OFX>" % self.resp_type

    def account_start(self, **kwargs):
        """ Gets OFX format transaction account start content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> ('USD', 1, 'account', 'type', 20120101, 20120101) == "\t\t\t<STMTRS>\n\t\t\t\t<CURDEF>USD</CURDEF>\n\t\t\t\t<BANKACCTFROM>\n\t\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t</BANKACCTFROM>\n\t\t\t\t<BANKTRANLIST>\n\t\t\t\t\t<DTSTART>20120101</DTSTART>\n\t\t\t\t\t<DTEND>20120101</DTEND>\n"
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
            >>> (20120101111111, {'type': 'type', 'amount': 100, 'id': 1, 'check_num': 1, 'Payee': 'payee', 'desc': 'memo'}) == "\t\t\t\t\t<STMTTRN>\n\t\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t\t</STMTTRN>\n"
        """
        content = '\t\t\t\t\t<STMTTRN>\n'
        content += '\t\t\t\t\t\t<TRNTYPE>%(tran_type)s</TRNTYPE>\n' % kwargs
        content += '\t\t\t\t\t\t<DTPOSTED>%(time_stamp)s</DTPOSTED>\n' % kwargs
        content += '\t\t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n' % kwargs
        content += '\t\t\t\t\t\t<FITID>%(id)s</FITID>\n' % kwargs
        content += '\t\t\t\t\t\t<CHECKNUM>%(check_num)s</CHECKNUM>\n' % kwargs
        content += '\t\t\t\t\t\t<NAME>%(payee)s</NAME>\n' % kwargs
        content += '\t\t\t\t\t\t<MEMO>%(desc)s</MEMO>\n' % kwargs
        content += '\t\t\t\t\t</STMTTRN>\n'
        return content

    def account_end(self, **kwargs):
        """ Gets OFX format transaction account end content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> (150, 20120101111111) == "\t\t\t\t</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t<BALAMT>150</BALAMT>\n\t\t\t\t\t<DTASOF>20120101111111</DTASOF>\n\t\t\t\t</LEDGERBAL>\n\t\t\t</STMTRS>\n"
        """
        content = '\t\t\t\t</BANKTRANLIST>\n'

        if kwargs.get('balance'):
            content += '\t\t\t\t<LEDGERBAL>\n'
            content += '\t\t\t\t\t<BALAMT>%(balance)s</BALAMT>\n' % kwargs
            content += '\t\t\t\t\t<DTASOF>%(time_stamp)s</DTASOF>\n' % kwargs
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
            >>> ('USD', 20120101111111, 1, 'account', 'type', {'split_account_id': 2, 'split_account': 'split_account', 'amount': 100}) == "\t\t\t<INTRARS>\n\t\t\t\t<CURDEF>USD</CURDEF>\n\t\t\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t\t\t<XFERINFO>\n\t\t\t\t\t<BANKACCTFROM>\n\t\t\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTFROM>\n\t\t\t\t\t<BANKACCTTO>\n\t\t\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTTO>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t</XFERINFO>\n\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t</INTRARS>\n"
        """
        content = '\t\t\t<INTRARS>\n'
        content += '\t\t\t\t<CURDEF>%(currency)s</CURDEF>\n' % kwargs
        content += '\t\t\t\t<SRVRTID>%(time_stamp)s</SRVRTID>\n' % kwargs
        content += '\t\t\t\t<XFERINFO>\n'
        content += '\t\t\t\t\t<BANKACCTFROM>\n'
        content += '\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTID>%(account_id)s</ACCTID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n' % kwargs
        content += '\t\t\t\t\t</BANKACCTFROM>\n'
        content += '\t\t\t\t\t<BANKACCTTO>\n'
        content += '\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTID>%(split_account_id)s</ACCTID>\n' % kwargs
        content += '\t\t\t\t\t\t<ACCTTYPE>%(split_account_type)s</ACCTTYPE>\n' % kwargs
        content += '\t\t\t\t\t</BANKACCTTO>\n'
        content += '\t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n' % kwargs
        content += '\t\t\t\t</XFERINFO>\n'
        content += '\t\t\t\t<DTPOSTED>%(time_stamp)s</DTPOSTED>\n'
        content += '\t\t\t</INTRARS>\n' % kwargs
        return content
