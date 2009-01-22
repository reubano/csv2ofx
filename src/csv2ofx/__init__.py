
import sys, os, time

import wx
from wx import xrc
import wx.grid as grd

from csvutils import *
from mappings import *


        


class csv2ofx(wx.App):
    """
        class csv2ofx
        
        Extends wx.App
        
        Provides a data table to preview csv input.
    """
    def __init__(self):
        wx.App.__init__(self,redirect=False)
    
    def OnInit(self):
        """
           Initializes and shows frame from csv2ofx.xrc 
        """
        
        # load the xml resource
        script_dir = os.path.dirname ( __file__ )
        self.res = xrc.XmlResource ( "%s/csv2ofx.xrc" % script_dir )
        
        # load the frame from the resource        
        self.frame = self.res.LoadFrame ( None, "ID_CSV2OFX")
        
        # associate the MenuBar
        self.frame.SetMenuBar (
            self.res.LoadMenuBar("ID_MENUBAR")
        )

        # the grid
        self.grid = xrc.XRCCTRL(self.frame,"ID_GRID")
        self.grid.EnableEditing(False)
        
        # the mappings
        self.mappings = xrc.XRCCTRL(self.frame,"ID_MAPPINGS")
        for mapping in mappings.all_mappings:
            self.mappings.Append ( mapping, mappings.all_mappings[mapping] )
        self.mappings.SetSelection(0)

        
        # handle events
        self.Bind ( wx.EVT_MENU, self.OnClose, id=xrc.XRCID("ID_MENU_CLOSE"))
        self.Bind ( wx.EVT_BUTTON, self.OnClose, id=xrc.XRCID("ID_BTN_CLOSE"))
        self.Bind ( wx.EVT_MENU, self.OnImport, id=xrc.XRCID("ID_MENU_IMPORT"))
        self.Bind ( wx.EVT_BUTTON, self.OnImport, id=xrc.XRCID("ID_BTN_IMPORT"))
        self.Bind ( wx.EVT_MENU, self.OnExport, id=xrc.XRCID("ID_MENU_EXPORT"))
        self.Bind ( wx.EVT_BUTTON, self.OnExport, id=xrc.XRCID("ID_BTN_EXPORT"))
        
        
        # show the frame        
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True
        
    def OnClose(self,evt):
        """
            Close the application.
        """
        self.frame.Close()
        
    def OnImport(self,evt):
        """
            Import a csv file.
        """
        
        # create an open file dialog
        dlg = wx.FileDialog (
            self.frame,
            message="Open CSV File",
            wildcard="CSV Files (*.csv)|*.csv|All Files (*.*)|*.*",
            style=wx.OPEN|wx.CHANGE_DIR,            
        )
        if dlg.ShowModal() == wx.ID_OK:
            path=dlg.GetPath()
            self._open_file(path)
        dlg.Destroy()
    
    
    def _open_file(self,path):
        """
            Opens a csv file and loads it's contents into the data table.
            
            path: path to the csv file.
        """
        
        print "Open File %s" % path
                      
        self.grid_table = SimpleCSVGrid(path)        
        self.grid.SetTable(self.grid_table)
        
    def OnExport(self,evt):
        if not hasattr(self,'grid_table'):
            wx.MessageDialog(
                self.frame,
                "Use import to load a csv file.",
                "No CSV File loaded.",
                wx.OK|wx.ICON_ERROR                
            ).ShowModal()
            return
        
        dlg = wx.FileDialog(
            self.frame,
            message='Export OFX File',
            wildcard="OFX Files (*.ofx)|*.ofx",
            style=wx.SAVE|wx.CHANGE_DIR            
        )
        path=None
        try:
            if dlg.ShowModal() == wx.ID_OK:
                path=dlg.GetPath()
            else:
                return
        finally:
            dlg.Destroy();
        
        mapping=self.mappings.GetClientData(self.mappings.GetSelection())
        
        grid=self.grid_table
        accounts={}
        today = datetime.now().strftime('%Y%m%d')
        for row in range(self.grid_table.GetNumberRows()):
            # which account
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
        
        
        
        
    
        
        
        
