import wx
import pickle
import wx.lib.agw
import wx.lib.agw.labelbook as LB
from wx.lib.agw.fmresources import *
from unit_tab import UnitTab
import xlsxwriter

class GeneRoster(wx.Frame):
    def __init__(self):
        # Init window
        wx.Frame.__init__(self, None, -1, "GeneRoster", size=(1200, 1000))

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
        optsXLSX = optsMenu.Append(-1, "Export Loadouts", "Export Loadouts to spreadsheet")
        self.Bind(wx.EVT_MENU, self.onOutput, optsXLSX)
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
    def onOutput(self, event):
        self.tabArray = []
        self.listTabs(self.base)

        Stats = ["Strength", "Toughness", "Movement", "Martial", "Ranged", "Defense",
                 "Discipline", "Willpower", "Command", "MTN", "RTN", "MORALE", "Wounds", "Attacks", "Size"]

        workbook = xlsxwriter.Workbook('loadouts.xlsx')
        worksheet = workbook.add_worksheet("Loadouts")
        h1 = workbook.add_format()
        h1.set_font_size(10)
        h1.set_bold()
        h1.set_underline()
        h1.set_align("center")
        h1.set_border(1)

        t1 = workbook.add_format()
        t1.set_font_size(10)
        t1.set_border(1)
        t1.set_align("vcenter")
        t1.set_text_wrap()

        t2 = workbook.add_format()
        t2.set_font_size(10)
        t2.set_align("center")
        t2.set_align("vcenter")
        t2.set_border(1)

        header = ["Qty", "Name", "Description", "Cost", "Total"]
        row = 0
        col = 0
        for name in header:
            worksheet.write(row, col, name, h1)
            col += 1
        row += 1

        for t in self.tabArray:
            print("T {}".format(t.tab))
            for unit in t.tab['loads']:
                (name, qty, gear, gcost, cost) = unit.split('|')
                # Needs level and traits
                # sarge upgrade option
                desc = "Models: {}; Gear: {}".format(qty, gear)
                worksheet.write(row, 0, 0, t2)        # qty of this taken
                worksheet.write(row, 1, name, h1)     # name + ???
                worksheet.merge_range(row+1, 1, row+4, 1, "", t1)
                worksheet.merge_range(row, 2, row+4, 2, desc, t1) # description
                worksheet.write(row, 3, cost, t2)     # cost
                worksheet.write_formula(row, 4, "={}{} * {}{}".format("A", row+1, "D", row+1), t2) # row total
                # write out trait summary
                col = 5
                for stat in Stats:
                    worksheet.write(row, col, stat, t1)
                    worksheet.write(row, col+1, t.tab[stat], t2)
                    col += 2
                    if (col > 9):
                        col = 5
                        row += 1
                row += 1

        worksheet.merge_range(row, 0, row, 3, "Army Total", h1)
        worksheet.write_formula(row, 4, "=sum(E2:E{})".format(row-1), h1)

        width = [ 3, 14, 40, 4, 4, 8, 3, 8, 3, 8, 3]
        for count in range(len(width)):
            worksheet.set_column(count,count, width[count])

        workbook.close()

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




