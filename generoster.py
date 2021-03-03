import wx
import pickle
import wx.lib.agw
import wx.lib.agw.labelbook as LB
from wx.lib.agw.fmresources import *
from unit_tab import UnitTab

class GeneRoster(wx.Frame):
    def __init__(self):
        # Init window
        wx.Frame.__init__(self, None, -1, "GeneRoster", size=(1000, 900))

        # Create panel
        p = wx.Panel(self)

        self.nb = LB.LabelBook(p, -1, size=(400, 200), style=wx.NB_LEFT,
            agwStyle=INB_LEFT|INB_FIT_LABELTEXT|INB_FIT_BUTTON|INB_SHOW_ONLY_TEXT|INB_USE_PIN_BUTTON)
        vertSizer = wx.BoxSizer(wx.VERTICAL)

        # Create initial notebook page
        self.base = UnitTab(self.nb)
        self.nb.AddPage(self.base, "New Faction")
        self.base.initTab("", "", 0, "New Faction")
        self.base.DrawTab()

        vertSizer.Add(self.nb, 1, wx.EXPAND, 0)
        p.SetSizer(vertSizer)

        ### Pass self.nb to save/delete routines
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()  # File Menu under Menubar
        fileNew = fileMenu.Append(-1, "New", "New Faction")
        self.Bind(wx.EVT_MENU, self.onNew, fileNew)
        fileMenu.AppendSeparator()
        fileOpen = fileMenu.Append(-1, "Open", "Open Faction")
        self.Bind(wx.EVT_MENU, self.onOpen, fileOpen)
        fileMenu.AppendSeparator()
        fileSave = fileMenu.Append(-1, "Save", "Save Faction")
        self.Bind(wx.EVT_MENU, self.onSave, fileSave)
        fileMenu.AppendSeparator()
        fileExit = fileMenu.Append(-1, "Exit", "Exit the Application")
        self.Bind(wx.EVT_MENU, self.onExit, fileExit)
        menuBar.Append(fileMenu, "&File")  # Add File Menu to Menubar
        optsMenu = wx.Menu()
        optsShow = optsMenu.Append(-1, "Display", "Configure Default Display")
        optsPath = optsMenu.Append(-1, "Path", "Configure Default Paths")
        menuBar.Append(optsMenu, "&Settings")
        self.SetMenuBar(menuBar)  # Attach menubar to frame

        # Add everything to the sizers to show
        p.Layout()

    #########################################
    def onNew(self, event):
        # Delete existing tabs/info
        while self.nb.GetPageCount() > 1:
            self.nb.DeletePage(1)
            self.nb.SendSizeEvent()
        self.base.tab['domain'] = ""
        self.base.tab['name'] = "New Faction"
        self.nb.SetPageText(0, "L0: {}".format(self.base.tab['name']))
        self.base.ptr['children'] = []
        self.base.DrawTab()

    #########################################
    def onOpen(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "", "GeneRoster files (*.rst)|*.rst",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        datafile = openFileDialog.GetPath()
        openFileDialog.Destroy()

### if datafile doesn't exist or is blank return()
        if datafile:
            # Delete existing tabs/info
            while self.nb.GetPageCount() > 1:
                self.nb.DeletePage(1)
                self.nb.SendSizeEvent()
            self.base.tab['domain'] = ""
            self.base.ptr['children'] = []

            # Load data
            with open(datafile, 'rb') as file:
                load = pickle.load(file)
            file.close()

            # Populate GUI
            for t in load.keys():
                print("L{} {}".format(t, load[t]))

            self.nb.SetPageText(self.nb.GetSelection(), "L0: {}".format(load[0]['name']))
            self.buildTabs(load, 0, self.base)
            self.base.DrawTab()

    #########################################
    def buildTabs(self, list, index, unit):
        print("Key {} Kids {}".format(index, list[index]['kids']))
        # put all of tab data back
        for key in list[index].keys():
            unit.tab[key] = list[index][key]
        print("Tab created: {}".format(unit.tab))

        for child in list[index]['kids']:
            unit.onAddUnit("", list[child]['clvl'], list[child]['name'])
            self.buildTabs(list, child, unit.ptr['children'][-1])

    #########################################
    def onSave(self, event):
        openFileDialog = wx.FileDialog(self, "Save", "", "", "GeneRoster files (*.rst)|*.rst", wx.FD_SAVE)

        openFileDialog.ShowModal()
        datafile = openFileDialog.GetPath()
        openFileDialog.Destroy()

        # Get a list of tab objects
        self.tabArray = []
        self.listTabs(self.base)

        sav = {}
        count = 0
        for t in self.tabArray:
            sav[count] = t.tab
            count += 1
        print("SAV {}".format(sav))

        ### if it doesn't end in .rst append that
        if not datafile.endswith(".rst"):
            datafile += ".rst"
        if datafile:
            with open(datafile, 'wb') as file:
                print(pickle.dumps(sav))
                file.write(pickle.dumps(sav))  # use `pickle.loads` to do the reverse
            file.close()

    #########################################
    def onExit(self, event):
        self.Close()

    #########################################
    def listTabs(self, roster):
        roster.tab['kids'] = []
        roster.tab['key'] = len(self.tabArray)
        self.tabArray.append(roster)

        for child in roster.ptr['children']:
            roster.tab['kids'].append(len(self.tabArray))
            self.listTabs(child)




