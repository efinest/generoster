import wx
from generoster import GeneRoster
#import sel_diag
from unit_tab import UnitTab

if __name__ == '__main__':
    app = wx.App()
    frame = GeneRoster()
    frame.Centre()
    frame.Show()
    app.MainLoop()
