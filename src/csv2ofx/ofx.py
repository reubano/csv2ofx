
from datetime import datetime
import time

def export ( path, mapping, grid):
    """
        path: path to save the file
        mapping: mapping selected from mappings.py
        data: grid with csv data from csvutils.py
    """
     
    accounts={}
    today = datetime.now().strftime('%Y%m%d')
    for row in range(grid.GetNumberRows()):
        # which account            
        if mapping['skip'](row,grid): continue
        
        uacct="%s-%s" % (mapping['BANKID'](row,grid), mapping['ACCTID'](row,grid))
        acct = accounts.setdefault(uacct,{})
        
        acct['BANKID'] = mapping['BANKID'](row,grid)
        acct['ACCTID'] = mapping['ACCTID'](row,grid)
        acct['TODAY'] = today
        currency = acct.setdefault('CURDEF',mapping['CURDEF'](row,grid))
        if currency != mapping['CURDEF'](row,grid):
            print "Currency not the same."
        trans=acct.setdefault('trans',[])
        tran=dict([(k,mapping[k](row,grid)) for k in ['DTPOSTED','TRNAMT','FITID','PAYEE','MEMO','CHECKNUM']])
        tran['TRNTYPE'] = tran['TRNAMT'] >0 and 'CREDIT' or 'DEBIT'
        trans.append(tran)
        
        
    # output
    
    out=open(path,'w')
    
    out.write (
        """
        <OFX>
            <SIGNONMSGSRSV1>
               <SONRS>
                <STATUS>
                    <CODE>0</CODE>
                        <SEVERITY>INFO</SEVERITY>
                    </STATUS>
                    <DTSERVER>%(DTSERVER)s</DTSERVER>
                <LANGUAGE>ENG</LANGUAGE>
            </SONRS>
            </SIGNONMSGSRSV1>
            <BANKMSGSRSV1><STMTTRNRS>
                <TRNUID>%(TRNUID)d</TRNUID>
                <STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>
                
        """ % {'DTSERVER':today,
              'TRNUID':int(time.mktime(time.localtime()))}
    )
        
    for acct in accounts.values():
        out.write(
            """
            <STMTRS>
                <CURDEF>%(CURDEF)s</CURDEF>
                <BANKACCTFROM>
                    <BANKID>%(BANKID)s</BANKID>
                    <ACCTID>%(ACCTID)s</ACCTID>
                    <ACCTTYPE>CHECKING</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>%(TODAY)s</DTSTART>
                    <DTEND>%(TODAY)s</DTEND>
                    
            """ % acct
        )
        
        for tran in acct['trans']:
            out.write (
                """
                        <STMTTRN>
                            <TRNTYPE>%(TRNTYPE)s</TRNTYPE>
                            <DTPOSTED>%(DTPOSTED)s</DTPOSTED>
                            <TRNAMT>%(TRNAMT)s</TRNAMT>
                            <FITID>%(FITID)s</FITID>
                            
                """ % tran
            )
            if tran['CHECKNUM'] is not None and len(tran['CHECKNUM'])>0:
                out.write(
                """
                            <CHECKNUM>%(CHECKNUM)s</CHECKNUM>
                """ % tran
                )
            out.write(
                """
                            <NAME>%(PAYEE)s</NAME>
                            <MEMO>%(MEMO)s</MEMO>
                """ % tran
            )
            out.write(
                """
                        </STMTTRN>
                """
            )
        
        out.write (
            """
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>0</BALAMT>
                    <DTASOF>%s</DTASOF>
                </LEDGERBAL>
            </STMTRS>
            """ % today
        )
        
    out.write ( "</STMTTRNRS></BANKMSGSRSV1></OFX>" )
    out.close()
    print "Exported %s" % path
    
    
    
    

    
    
    
