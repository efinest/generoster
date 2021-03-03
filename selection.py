class TraitSelection(wx.Dialog):
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
    def CreateTree(self, filter):
        ### remove domain as a parameter... should be part of the tree/filtering
        treedict = {}
        traitlist = []
        for domain in Domain.keys():
            for trait in Domain[domain]["TraitDict"].keys():
                category = Domain[domain]["TraitDict"][trait]["Category"]
                branch = Domain[domain]["TraitDict"][trait]["Branch"]
                tier = Domain[domain]["TraitDict"][trait]["Tier"]
                cost = Domain[domain]["TraitDict"][trait]["Cost"]
                display = Domain[domain]["TraitDict"][trait]["Display"]

                # If there is a filter, only create branches that match the filter
                for test in filter:
                    skip = 1
                    if test:
                        if test in domain: skip = 0
                        if test in category: skip = 0
                        if test in branch: skip = 0
                        if test in tier: skip = 0
                if (skip == 1):
                    continue

                if tier == "T2":
                    tier = "Tier 2"
                else:
                    tier = "Tier 1"
                traitlist.append('|'.join((domain, category, branch, tier, trait, cost, display)))
        traitlist.sort()

        for trait in traitlist:
            (domain, category, branch, tier, name, cost, display) = trait.split('|')

            if not domain in treedict:
                treedict[domain] = self.tree.AppendItem(self.root, domain)
                self.tree.SetItemData(treedict[domain], "")

            if not (domain + category) in treedict:
                treedict[domain + category] = self.tree.AppendItem(treedict[domain], category)
                self.tree.SetItemData(treedict[domain + category], "")

            if not (domain + category + branch) in treedict:
                treedict[domain + category + branch] = self.tree.AppendItem(treedict[domain + category], branch)
                self.tree.SetItemData(treedict[domain + category + branch], "")

            if not (domain + category + branch + tier) in treedict:
                treedict[domain + category + branch + tier] = self.tree.AppendItem(treedict[domain + category + branch],
                                                                                   "Tier " + tier)
                self.tree.SetItemData(treedict[domain + category + branch + tier], "")

            item_data = name + " (" + display + ") [" + cost + "]"
            leaf = self.tree.AppendItem(treedict[domain + category + branch + tier], item_data)  # + ": "
            self.tree.SetItemData(leaf, ";".join((domain, name)))
        self.tree.ExpandAll()
        # sizer.Layout()
        self.Center()

    #########################################
    def onSelChanged(self, event):
        self.return_value = self.tree.GetItemData(event.GetItem())
        if ";" in self.return_value:
            self.EndModal(wx.ID_OK)
