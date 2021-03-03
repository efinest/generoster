import wx

class selGearDiag(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, title="Gear Selection", size=(720, 800), style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self)

    def CreateGearList(self, clvl, prior_gear, list):
        sizer = wx.BoxSizer()
        gearGrid = wx.GridBagSizer(hgap=10, vgap=0)
        self.gear = prior_gear

        # print header
        okBtn = wx.Button(self, -1, "Click to Finish Selecting Gear")
        okBtn.SetBackgroundColour((100, 100, 100))
        okBtn.SetForegroundColour((255, 255, 255))
        self.Bind(wx.EVT_BUTTON, self.onOK, okBtn)
        gearGrid.Add(okBtn, pos=(0, 0), span=(1,5), flag=wx.EXPAND)
        fields = ["Pick Amount", "Unit", "Name", "Notes", "Cost"]
        col = 0
        for field in fields:
            label = wx.StaticText(self, label=field, style=wx.ALIGN_CENTER)
            label.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            gearGrid.Add(label, pos=(1, col), flag=wx.ALIGN_CENTER)
            col += 1
        row = 2
        (x, y) = label.GetSize()
        for key in list.keys():
            # Skip if
            # Filter by clvl
            if int(list[key]['Prop']) > clvl:
                continue

            # Select a specific #
            col = 0
            if not list[key]['Category']  == "Primitive":
                selWid = wx.SpinCtrl(self, -1, "0", min=0, max=100, size=(-1, -1))
                if key in prior_gear.keys():  selWid.SetValue(prior_gear[key])
                self.Bind(wx.EVT_SPINCTRL, lambda event, k=key: self.onCheck(event, k), selWid)
                if not (row % 2):
                    selWid.SetBackgroundColour((100, 100, 100))
                    selWid.SetForegroundColour((255, 255, 255))
                gearGrid.Add(selWid, pos=(row, col), flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTER)

            # Select for entire unit
            col += 1
            selWid = wx.CheckBox(self, -1, "", size=(-1,-1))
            if key in prior_gear.keys(): selWid.SetValue(True)
            self.Bind(wx.EVT_CHECKBOX, lambda event, k=key: self.onCheck(event, k), selWid)
            if not (row % 2):
                selWid.SetBackgroundColour((100, 100, 100))
                selWid.SetForegroundColour((255, 255, 255))
            gearGrid.Add(selWid, pos=(row, col), flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER)

            # Name
            col += 1
            label = wx.StaticText(self, label=key)
            if not (row % 2):
               label.SetBackgroundColour((100, 100, 100))
               label.SetForegroundColour((255, 255, 255))
            gearGrid.Add(label, pos=(row, col), flag= wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL)

            # Notes
            col += 1
            label = wx.StaticText(self, label=list[key]['Notes'])
            if not (row % 2):
                label.SetBackgroundColour((100, 100, 100))
                label.SetForegroundColour((255, 255, 255))
            gearGrid.Add(label, pos=(row, col), flag= wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL)

            # Cost
            col += 1
            label = wx.StaticText(self, label=list[key]['Cost'], style=wx.ALIGN_CENTER)
            if not (row % 2):
                label.SetBackgroundColour((100, 100, 100))
                label.SetForegroundColour((255, 255, 255))
            gearGrid.Add(label, pos=(row, col), flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL)

            row += 1
        gearGrid.AddGrowableCol(3)
        sizer.Add(gearGrid, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        self.panel.SetSizer(sizer)  # Add to panel

    def onCheck(self, event, k):
        print("Picked {} {}".format(k,event.GetEventObject().GetValue()))

        if (event.GetEventObject().GetValue()):
            self.gear[k] = int(event.GetEventObject().GetValue())
            if event.GetEventObject().GetName() == "check":  self.gear[k] = 99999
        else:
            del self.gear[k]

        print("G: {}".format(self.gear))

    def onOK(self, event):
             self.EndModal(wx.ID_OK)

class selAttrDiag(wx.Dialog):
    #########################################
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, title="Attribute Selection", size=(800, 500), style=wx.DEFAULT_FRAME_STYLE)
        panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.root = self.tree.AddRoot('Hidden Root')
        self.tree.SetItemData(self.root, ('key', 'value'))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, self.tree)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        panel.SetSizer(sizer)  # Add to panel

    def CreateTree(self, prune, TList):
        # No need to create a selection if there's only one option
        if prune:
            TList = prune.split('; ')

        # Create treelist
        for stat in TList:
            leaf = self.tree.AppendItem(self.root, stat)
            self.tree.SetItemData(leaf, "{}".format(stat))
            #self.tree.SetItemData(leaf, "Increase {} 1".format(stat))

    #########################################
    def onSelChanged(self, event):
        self.return_value = self.tree.GetItemData(event.GetItem())
        if self.return_value:
            self.EndModal(wx.ID_OK)

class selDiag(wx.Dialog):
    #########################################
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, title="Trait Selection", size=(800, 500), style=wx.DEFAULT_FRAME_STYLE)
        panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.root = self.tree.AddRoot('Hidden Root')
        self.tree.SetItemData(self.root, ('key', 'value'))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, self.tree)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        panel.SetSizer(sizer)  # Add to panel

    #########################################
    def CreateTree(self, treelist, prune, TList):
        print("Select from: {}".format(treelist))
        # need to pass the armylist filter
        treedict = {}
        traitlist = []
        for t in TList.keys():
            tier = TList[t]["Tier"]
            pv = TList[t]["Cost"]
            show = TList[t]["Display"]

            # ArmyList filter
            skip = 1
            for test in treelist:
                # Test if matches Domain, Category, Branch
                if (test == TList[t]['Domain']) or (test == TList[t]['Category']) or (test == TList[t]['Branch']):
                    skip = 0
            if (skip == 1):
                continue

            # Trait Filter
            skip = 0
            for test in prune:

                if (test in TList[t]['Domain']) or (test in TList[t]['Category']) or (test in TList[t]['Branch']) or (test in tier):
                    #print ("Test: {} Matched: {} {} {} {}".format(test, TList[t]['Domain'],TList[t]['Category'],TList[t]['Branch'],tier))
                    trash = 1
                else:
                    skip = 1
                if (test == "Armory" and "Armory:" in TList[t]["Display"]):
                    skip = 0
            if (skip == 1):
                continue

            # Prep for printing
            if tier == "T2":
               tier = "Tier 2"
            else:
               tier = "Tier 1"
            traitlist.append('|'.join((TList[t]["Domain"], TList[t]["Category"], TList[t]["Branch"], tier, t, pv, show)))
        traitlist.sort()

        # Create tree
        for trait in traitlist:
            (domain, cat, branch, tier, name, pv, show) = trait.split('|')

            if not domain in treedict:
                treedict[domain] = self.tree.AppendItem(self.root, domain)
                self.tree.SetItemData(treedict[domain], "")
            if not (domain + cat) in treedict:
                treedict[domain + cat] = self.tree.AppendItem(treedict[domain], cat)
                self.tree.SetItemData(treedict[domain + cat], "")
            if not (domain + cat + branch) in treedict:
                treedict[domain + cat + branch] = self.tree.AppendItem(treedict[domain + cat], branch)
                self.tree.SetItemData(treedict[domain + cat + branch], "")
            if not (domain + cat + branch + tier) in treedict:
                treedict[domain+cat+branch+tier] = self.tree.AppendItem(treedict[domain+cat+branch],tier)
                self.tree.SetItemData(treedict[domain + cat + branch + tier], "")

            leaf = self.tree.AppendItem(treedict[domain + cat + branch + tier], "{}: {} [{}]".format(name, show, pv))
            self.tree.SetItemData(leaf, name)
        self.tree.ExpandAll()
        # sizer.Layout()
        self.Center()

    #########################################
    def onSelChanged(self, event):
        self.return_value = self.tree.GetItemData(event.GetItem())
        if self.return_value:
            self.EndModal(wx.ID_OK)
