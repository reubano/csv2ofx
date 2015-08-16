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
class OFX(Account)
    def __init__(self, resp_type='INTRATRNRS', **kwargs):
        super(Account, self).__init__(**kwargs)
        self.resp_type = resp_type

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
        kwargs.update({'time_stamp': kwargs['time_stamp'].strftime('%Y%m%d')})

        return
            """
            DATA:OFXSGML\n
            ENCODING:UTF-8\n
            <OFX>\n.
            \t<SIGNONMSGSRSV1>\n
            \t\t<SONRS>\n
            \t\t\t<STATUS>\n
            \t\t\t\t<CODE>0</CODE>\n
            \t\t\t\t<SEVERITY>INFO</SEVERITY>\n
            \t\t\t</STATUS>\n
            \t\t\t<DTSERVER>%(time_stamp)s</DTSERVER>\n
            \t\t\t<LANGUAGE>%(language)s</LANGUAGE>\n
            \t\t</SONRS>\n
            \t</SIGNONMSGSRSV1>\n
            """ % kwargs


    def response_start(self):
        """ Gets OFX format transaction content
        Returns:
            (str): the OFX content

        Examples:
            >>> () == "\t<BANKMSGSRSV1>\n\t\t<INTRATRNRS>\n\t\t\t<TRNUID></TRNUID>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n"
        """
        return
            """
            \t<BANKMSGSRSV1>\n
            \t\t<%s>\n
            \t\t\t<TRNUID></TRNUID>\n
            \t\t\t<STATUS>\n
            \t\t\t\t<CODE>0</CODE>\n
            \t\t\t\t<SEVERITY>INFO</SEVERITY>\n
            \t\t\t</STATUS>\n
            """ % self.resp_type

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
        kwargs.update(
            {
                'start_date': kwargs['start_date'].strftime('%Y%m%d'),
                'end_date': kwargs['end_date'].strftime('%Y%m%d'),
            })
        content =
            """
            \t\t\t<STMTRS>\n
            \t\t\t\t<CURDEF>%(currency)s</CURDEF>\n
            \t\t\t\t<BANKACCTFROM>\n
            \t\t\t\t\t<BANKID>%(account_id)s</BANKID>\n
            \t\t\t\t\t<ACCTID>%(account)s</ACCTID>\n
            \t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n
            \t\t\t\t</BANKACCTFROM>\n
            \t\t\t\t<BANKTRANLIST>\n
            \t\t\t\t\t<DTSTART>%(start_date)s</DTSTART>\n
            \t\t\t\t\t<DTEND>%(end_date)s</DTEND>\n
            """ % kwargs

        return None if kwargs.get('transfer') else content

    def transaction(self, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> (20120101111111, {'type': 'type', 'amount': 100, 'id': 1, 'check_num': 1, 'Payee': 'payee', 'desc': 'memo'}) == "\t\t\t\t\t<STMTTRN>\n\t\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t\t</STMTTRN>\n"
        """
        return
            """
            \t\t\t\t\t<STMTTRN>\n
            \t\t\t\t\t\t<TRNTYPE>%(tran_type)s</TRNTYPE>\n
            \t\t\t\t\t\t<DTPOSTED>%(time_stamp)s</DTPOSTED>\n
            \t\t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n
            \t\t\t\t\t\t<FITID>%(id)s</FITID>\n
            \t\t\t\t\t\t<CHECKNUM>%(check_num)s</CHECKNUM>\n
            \t\t\t\t\t\t<NAME>%(payee)s</NAME>\n
            \t\t\t\t\t\t<MEMO>%(desc)s</MEMO>\n
            \t\t\t\t\t</STMTTRN>\n
            """ % kwargs

    def account_end(self, **kwargs):
        """ Gets OFX format transaction account end content

        Kwargs:

        Returns:
            (str): the OFX content

        Examples:
            >>> (150, 20120101111111) == "\t\t\t\t</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t<BALAMT>150</BALAMT>\n\t\t\t\t\t<DTASOF>20120101111111</DTASOF>\n\t\t\t\t</LEDGERBAL>\n\t\t\t</STMTRS>\n"
        """
        content = """
            \t\t\t\t</BANKTRANLIST>\n
            \t\t\t\t<LEDGERBAL>\n
            \t\t\t\t\t<BALAMT>%(balance)s</BALAMT>\n
            \t\t\t\t\t<DTASOF>%(time_stamp)s</DTASOF>\n
            \t\t\t\t</LEDGERBAL>\n
            \t\t\t</STMTRS>\n
            """ % kwargs
        return None if kwargs.get('transfer') else content

    def transfer(self, **kwargs):
        """ Gets OFX transfer start

        Kwargs:
            account_type (str): the account types

        Returns:
            (str): the QIF content

        Examples:
            >>> ('USD', 20120101111111, 1, 'account', 'type', {'split_account_id': 2, 'split_account': 'split_account', 'amount': 100}) == "\t\t\t<INTRARS>\n\t\t\t\t<CURDEF>USD</CURDEF>\n\t\t\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t\t\t<XFERINFO>\n\t\t\t\t\t<BANKACCTFROM>\n\t\t\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTFROM>\n\t\t\t\t\t<BANKACCTTO>\n\t\t\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTTO>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t</XFERINFO>\n\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t</INTRARS>\n"
        """
        return
            """
            \t\t\t<INTRARS>\n
            \t\t\t\t<CURDEF>%(currency)s</CURDEF>\n
            \t\t\t\t<SRVRTID>%(time_stamp)s</SRVRTID>\n
            \t\t\t\t<XFERINFO>\n
            \t\t\t\t\t<BANKACCTFROM>\n
            \t\t\t\t\t\t<BANKID>%(account_id)s</BANKID>\n
            \t\t\t\t\t\t<ACCTID>%(account)s</ACCTID>\n
            \t\t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n
            \t\t\t\t\t</BANKACCTFROM>\n
            \t\t\t\t\t<BANKACCTTO>\n
            \t\t\t\t\t\t<BANKID>%(split_account_id)s</BANKID>\n
            \t\t\t\t\t\t<ACCTID>%(split_account)s</ACCTID>\n
            \t\t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n
            \t\t\t\t\t</BANKACCTTO>\n
            \t\t\t\t\t<TRNAMT>%(amount)s</TRNAMT>\n
            \t\t\t\t</XFERINFO>\n
            \t\t\t\t<DTPOSTED>%(time_stamp)s</DTPOSTED>\n
            \t\t\t</INTRARS>\n
            """ % kwargs
