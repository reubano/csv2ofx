
import sys, os
import csv

import wx
from wx import xrc
import wx.grid as grd


class SimpleCSVGrid(grd.PyGridTableBase):
    """
        A very basic instance that allows the csv contents to be used
        in a wx.Grid
    """
    def __init__(self,csv_path):
        grd.PyGridTableBase.__init__(self)
          # delimiter, quote could come from config file perhaps
        csv_reader = csv.reader(open(csv_path,'r'),delimiter=',',quotechar='"')
        self.grid_contents = [row for row in csv_reader]
        
        # the 1st row is the column headers
        self.grid_cols = len(self.grid_contents[0])
        self.grid_rows = len(self.grid_contents)
        
    def GetNumberRows(self):
        return self.grid_rows-1
    
    def GetNumberCols(self):
        return self.grid_cols
    
    def IsEmptyCell(self,row,col):
        return len(self.grid_contents[row+1][col]) == 0
    
    def GetValue(self,row,col):
        return self.grid_contents[row+1][col]
    
    def GetColLabelValue(self,col):
        return self.grid_contents[0][col]
        


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
        
        # handle events
        self.Bind ( wx.EVT_MENU, self.OnClose, id=xrc.XRCID("ID_MENU_CLOSE"))
        self.Bind ( wx.EVT_BUTTON, self.OnClose, id=xrc.XRCID("ID_BTN_CLOSE"))
        self.Bind ( wx.EVT_MENU, self.OnImport, id=xrc.XRCID("ID_MENU_IMPORT"))
        self.Bind ( wx.EVT_BUTTON, self.OnImport, id=xrc.XRCID("ID_BTN_IMPORT"))
        self.Bind ( wx.EVT_MENU, self.OnExport, id=xrc.XRCID("ID_MENU_EXPORT"))
        self.Bind ( wx.EVT_BUTTON, self.OnExport, id=xrc.XRCID("ID_BTN_EXPORT"))
        
        # the grid
        #self.grid=grd.Grid(self.frame)
        #self.grid.EnableEditing(False)
        #self.res.AttachUnknownControl ( "ID_GRID", self.grid )
        self.grid = xrc.XRCCTRL(self.frame,"ID_GRID")
        
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
        else:
            print "Export"
        
        
        
        
    
        
        
        