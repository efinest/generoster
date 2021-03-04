import wx
from sel_diag import selDiag
from sel_diag import selAttrDiag
from sel_diag import selGearDiag

Stats = ["Strength", "Toughness", "Movement", "Martial", "Ranged", "Defense",
         "Discipline", "Willpower", "Command", 	"MTN", "RTN", "MORALE", "Wounds", "Attacks", "Size"]

'''
Display Mex Properties
Display Max Traits

Settings Tab -> Datafiles (path, age), Show/Hide Base faction traits
Create Roster Dialogue

check for bad/missing datafiles on load

select trait cancel error

Dependent traits
- delete with parent

Trait Filter
Rare Filter (only applicable traits)

Hybrid
Forbidden Lore
Exotic Biest

Monsters / Biest Monster

Add Powers

Name Change -> redraw all  # Needs to change trigger to on focus change for redraw

Row Height Consistency

Progression points?

Validation routine

Limit which classes can build from which classes

Auto select lists with only one option

Pick display (default to Pick Attribute, other hide Pick)

'''

def readfile(filename):
    info =  {}
    with open('data/' + filename, 'r', encoding="utf8") as fp:
        # Top line provides field list for hashing
        line = fp.readline()
        line.strip()
        field_list = line.split(",")

        line = fp.readline()
        while line:
            line.strip()
            data = line.split(",")
            if (data[0]):                   # Make sure there is data in the line
                 info[data[0]] = {}
                 for index in range(0,len(data)):
                     info[data[0]][field_list[index]] = data[index]
            line = fp.readline()
    fp.close()
    return(info)

# Move to main, create a set and propagate subroutine
#Initial data load
Domain = readfile('main.csv')       # dict for domain construction info
TraitList = readfile('traits.csv')  # dict for traits
GearList = readfile('gear.csv')     # dict for gear
AdvGear = readfile('opt_gear.cvs')  # dict for gear added via traits
OptList = {}
OptList["HideBase"] = 0

class UnitTab(wx.ScrolledWindow):
    #########################################
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollbars(20, 20, 50, 50)

        self.boldfont = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.italfont = wx.Font(-1, wx.DEFAULT, wx.ITALIC, wx.NORMAL)
        self.border = 0
        self.flags = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vertSizer)  # Add gridbagsizer to be main sizer
        self.showSizer = 0
        self.parent = parent

        self.ptr= {}

        # Do these needs to be assigned here?
        self.ptr['children'] = []
        self.ptr['parent'] = []

    def initTab(self, domain, prior, level, name):
        if prior:
            self.ptr['parent'] += prior
        else:
            self.ptr['parent'].append(self.parent)

        self.tab = {}
        self.tab['clvl'] = level
        self.tab['domain'] = domain
        self.tab['gear'] = ""
        self.tab['max'] = 0
        self.tab['name'] = name
        self.tab['prop'] = 0
        self.tab['loads'] = []
        self.ptr['children'] = []

    def getCtraits(self):
        domain = self.tab['domain']
        level = str(self.tab['clvl'])

        # stores tab object
        self.tab['ctotal'] = 0
        self.tab['ctraits'] = []
        self.tab['filter'] = domain.split(": ")
        #self.tab['gear'] = ["All Primitive and Common Gear"]
        self.tab['multiplier'] = 1      # default multiplier, could use get instead

        if Domain[domain][level]:
            pairs = Domain[domain][level].split('|')
            for pair in pairs:
                (key, value) = pair.split(':')
                if key == "base":
                    self.tab['multiplier'] = int(value)
                if key == "max":
                    self.tab['max'] = int(value)
                if key == "mod":
                    Tlist = value.split(';')
                    label = "Increase {} {}".format(Tlist[0], Tlist[1])
                    self.tab['ctraits'].append( '|'.join( (label, "mod", "0", "","") ) )
                if key == "prop":
                    self.tab['prop'] = int(value)
                if key == "stat":
                    Tlist = value.split(';')
                    self.tab['ctraits'].append( '|'.join( ("", "Pick", Tlist[1], Tlist[0],"") ) )
                if key == "T":
                    Tlist = value.split(';')
                    for x in range(0, int(Tlist[0])):
                        if (len(Tlist) > 2):
                            pv = Tlist[2]
                        else:
                            pv = '0'
                        # Format = Selection (initially empty) | Operation | Cost | Filter | Combined
                        self.tab['ctraits'].append('|'.join(("", "Trait", pv, Tlist[1], "")))

    def DrawTab(self):
        # Remove prior data grid
        if (self.showSizer):
            ### Just hiding for now... probably should delete unused widgets
            self.vertSizer.Hide(self.showSizer)

        # Create another for hiding all prior data
        self.showSizer = wx.BoxSizer(wx.VERTICAL)
        self.vertSizer.Add(self.showSizer, flag=wx.EXPAND)

        # Print title/domain selection/info
        self.displayClassTitleInfo()

        if self.tab.get("domain", "") != "":
            # Always uses base stats since we'll modify them with each trait added below
            for stat in Stats:
                if (stat == "MTN") or (stat == "RTN") or (stat == "MORALE"):
                    self.tab[stat] = 0
                else:
                    self.tab[stat] = int(Domain[self.tab['domain']][stat])


            traitSizer = self.displayClassTraits()  # Returns Traits Table

            self.tab['MTN'] += self.tab['Martial'] + self.tab['Defense']
            self.tab['RTN'] += self.tab['Movement'] + self.tab['Defense']
            self.tab['MORALE'] += self.tab['Discipline'] + self.tab['Willpower']

            self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)
            self.displayClassSubSel()
            self.displayClassAttributes()  # Display Attribute Table
            self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)
            self.showSizer.Add(traitSizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
            self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)
            self.displayTotals()
            self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)
            self.displayLoadouts()
            self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)

        self.showSizer.Layout()
        self.vertSizer.Layout()

        ### Redraw children too
        for c in self.ptr['children']:
            c.DrawTab()

    def displayClassTitleInfo(self):
        # Collect Faction/Unit Name in a grid
        NameDomainGrid = wx.GridBagSizer(hgap=3, vgap=0)
        label = wx.StaticText(self, label="Name:", style=self.flags)
        label.SetFont(self.boldfont)
        NameDomainGrid.Add(label, pos=(0, 0), flag=self.flags)
        title = wx.TextCtrl(self, size=(-1, -1), value=self.tab['name'])
        title.Bind(wx.EVT_TEXT, self.setTabName)
        NameDomainGrid.Add(title, pos=(0, 1), flag=self.flags)

        # Domain can only be selected on "0" base page
        if (self.tab['clvl']) == 0:
            label = wx.StaticText(self, label="Domain:", style=self.flags)
            label.SetFont(self.boldfont)
            NameDomainGrid.Add(label, pos=(1, 0), flag=self.flags)
            Factions = list(Domain.keys())
            selDomain = wx.ComboBox(self, -1, self.tab.get("domain", ""), choices=Factions, style=wx.CB_DROPDOWN)
            selDomain.Bind(wx.EVT_COMBOBOX, self.onDomainSel)
            NameDomainGrid.Add(selDomain, pos=(1, 1), flag=self.flags)
        else:
            (x,y) = title.GetSize()
            print("Height {}".format(y))
            #label = wx.StaticText(self, label=self.tab.get("domain", ""), size=(-1, -1), style=self.flags)
            #NameDomainGrid.Add(label, pos=(1, 1), flag=self.flags)
            prior = "Built from {} class".format(self.ptr['parent'][-1].tab['name'])
            delClassBtn = wx.Button(self, -1, prior)
            self.Bind(wx.EVT_BUTTON, self.onDelClass, delClassBtn)
            NameDomainGrid.Add(delClassBtn, pos=(1, 0), span=(1,2), flag=self.flags)

### Sizing issues
        #NameDomainGrid.Add(selDomain, pos=(1, 2), flag=self.flags)
        NameDomainGrid.AddGrowableCol(1)
        #NameDomainGrid.RecalcSizes()
        self.showSizer.Add(NameDomainGrid, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

    def setTabName(self, event):
            self.tab['name'] = event.GetString()
            book = self.ptr['parent'][0]
            book.SetPageText(book.GetSelection(), "L{}: {}".format(self.tab['clvl'], event.GetString()))
            #self.DrawTab()   ### Changes focus

    def onDelClass(self,event):
        dlg = wx.MessageDialog(None, "Delete this class?", 'Delete', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()

        if result == wx.ID_YES:
### Delete any children pages
            page = self.ptr['parent'][0].GetSelection()
            self.ptr['parent'][-1].ptr['children'].remove(self)
            self.ptr['parent'][0].DeletePage(page) # RemovePage instead?

    def onDomainSel(self, event):
        # Set Domain for faction
        self.tab['domain'] = event.GetString()
        # Ctraits can't be assigned until a domain is picked, so we do it here
        self.getCtraits()

        # Delete all tabs after the first
        while self.ptr['parent'][0].GetPageCount() > 1:
            self.ptr['parent'][0].DeletePage(1)
        self.ptr['parent'][0].SendSizeEvent()

        # Redraw faction base page with domain selected
        self.DrawTab()

    def displayClassAttributes(self):
        statGrid = wx.GridBagSizer(hgap=3, vgap=0)  # Place to store stat info
        row = 0
        col = 0
        # Show class stats
        for stat in Stats:
            label = wx.StaticText(self, label=stat, style=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            value = wx.StaticText(self, label="{}".format(self.tab[stat]),
                                  style=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
            if (stat == "MTN") or (stat == "RTN") or (stat == "MORALE"):
                label.SetBackgroundColour((100, 100, 100))
                label.SetForegroundColour((255, 255, 255))
                value.SetBackgroundColour((100, 100, 100))
                value.SetForegroundColour((255, 255, 255))
            statGrid.Add(label, pos=(row, col), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, border=self.border)
            statGrid.Add(value, pos=(row, col + 1), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                         border=self.border)
            col += 2
            if (col > 4):
                col = 0
                row += 1
        statGrid.AddGrowableCol(1)
        statGrid.AddGrowableCol(3)
        statGrid.AddGrowableCol(5)
        self.showSizer.Add(statGrid, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

    def displayClassTraits(self):
        #  Recalc totals each time
        self.tab['ctotal'] = 0
        self.gear = ["All Primitive and Common Gear"]

        # Create Grid to store traits
        traitGrid = wx.GridBagSizer(hgap=3, vgap=0)  # Place to store trait info
        row = 0
        # Do Base/Inherited, Class, then Gear

 #### Do Base, Prior, Class, then Gear
        # Get Prior Items
        loop = self.getPriorTraits()

        # Print title if showing faction traits
        if not OptList['HideBase'] == 1 and len(loop) > 0:
            label = wx.StaticText(self, label="Faction Traits", style=self.flags)
            label.SetFont(self.boldfont)
            traitGrid.Add(label, pos=(row, 0), span=(1, 2), flag=self.flags, border=self.border)
            row += 1

        inherit = []
        for item in loop:
            print("item: {}".format(item))
            if '|' in item and not item.startswith('|'):
                self.doTraitMods(item, "Prior")

            if self.tab['clvl'] == 0 or item in self.ptr['parent'][1].tab['ctraits'] and OptList['HideBase'] == 0:
                widget = self.showTrait("Prior", item)
                widget.SetFont(self.italfont)
                traitGrid.Add(widget, pos=(row, 1), flag=self.flags, border=self.border)
                row += 1
            else:
                inherit.append(item)
            print("Showing {} Loop {}".format(item, inherit))

        # Start Class Traits
        label = wx.StaticText(self, label="Class {} Traits (Max Traits: {})".format(self.tab['clvl'], self.tab['max']), style=self.flags)
        label.SetFont(self.boldfont)
        traitGrid.Add(label, pos=(row, 0), span=(1, 2), flag=self.flags, border=self.border)
        row += 1
        # Do remaining inherited traits
        for item in inherit:
            widget = self.showTrait("Prior", item)
            widget.SetFont(self.italfont)
            traitGrid.Add(widget, pos=(row, 1), flag=self.flags, border=self.border)
            row += 1
        # Do traits for this class
        for item in self.tab['ctraits']:
            self.doTraitMods(item, "Class")
            widget = self.showTrait("Class", item)
            traitGrid.Add(widget, pos=(row, 1), flag=self.flags, border=self.border)
            if item.startswith('|'):
                self.Bind(wx.EVT_BUTTON, lambda event, t=item: self.onSelTrait(event, t), widget)
            elif type == "Class":
                if "|Trait|" in item or '|Pick|' in item:
                    delbtn = wx.Button(self, -1, "x", size=(36, -1))
                    self.Bind(wx.EVT_BUTTON, lambda event, t=item: self.onDelTrait(event, t), delbtn)
                    traitGrid.Add(delbtn, pos=(row, 0), flag=self.flags, border=self.border)
            row += 1

        # Start Gear Traits
        label = wx.StaticText(self, label="Gear Options (Max Properties: {})".format(self.tab['prop']), style=self.flags)
        label.SetFont(self.boldfont)
        traitGrid.Add(label, pos=(row, 0), span=(1, 2), flag=self.flags, border=self.border)
        row += 1
        self.gear.sort()
        for item in self.gear:
            widget = self.showTrait("Gear", item)
            traitGrid.Add(widget, pos=(row, 1), flag=self.flags, border=self.border)
            row += 1

        traitGrid.AddGrowableCol(1)
        return(traitGrid)

    def getTraitEffect(self, trait):
        (name, type, cost, filter, prior) = trait.split('|')

        if type == "Trait":
            if name in TraitList:
                return(name, TraitList[name].get("Display", ""))
            else:
                return("Increase ", "")
        else:
            return(name, "")

    def getPriorTraits(self):
        ret = []
        if len(self.ptr['parent']) > 1:
            parent = self.ptr['parent'][-1]
            for item in parent.tab['ctraits']:
                if not item.startswith('|') and ("|Trait|" in item or not item[-1] == '|'):
                    ret.append(item)
            return(parent.getPriorTraits() + ret)
        else:
            if Domain[self.tab['domain']]['Traits']:
                return(Domain[self.tab['domain']]['Traits'].split('|'))
            else:
                return([])

    def showTrait(self, type, item):
        if item.startswith('|'):
            (sel, action, pv, filter, parent) = item.split('|')
            return(wx.Button(self, -1, "Select {} {} [{}]".format(filter, action, pv)))

        if '|' in item:
            (sel, action, pv, filter, parent) = item.split('|')
            total = int(pv)
            if parent:
                prior = " - (Part of {}) - ".format(parent)
            else:
                prior = ""
            if action == "Trait":
                total += int(TraitList[sel]['Cost'])
                show = "[{}] {}{} ({} - {} - {}): {}".format(total, prior, sel, TraitList[sel]["Category"],
                                TraitList[sel]["Branch"], TraitList[sel]["Tier"], TraitList[sel]["Display"])
            else:
                show = "[{}] {}{}".format(pv, prior, sel)
            return (wx.StaticText(self, label=show, style=self.flags))
        else:
            if type == "Prior":
                show = "[0] " + item
            else:
                show = item
            return(wx.StaticText(self, label=show, style=self.flags))

    def displayTotals(self):
        # Point total Line at the bottom   Base x Multipier + Inherited + Current Class Options = Total
        Base = int(Domain[self.tab['domain']]['Cost'])
        # length of 0 = base faction, length of 1 means built off base, 2+ means built of another class
        if len(self.ptr['parent']) > 1:
            Base += int(self.ptr['parent'][1].tab['ctotal'])                 # Get base total cost

        self.Total = Base * self.tab['multiplier'] + self.tab['ctotal']
        TotalLine = "Totals: Base {} x {} + Class Totals {} = {}".format(Base,
            self.tab['multiplier'], self.tab['ctotal'], self.Total)
        label = wx.StaticText(self, label=TotalLine, style=self.flags)
        label.SetFont(self.boldfont)
        self.showSizer.Add(label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

    def displayClassSubSel(self):
        lvlSizer = wx.BoxSizer(wx.HORIZONTAL)

### Humans build on classes others do not except for 3_> 5?

        for count in range(self.tab['clvl']+1,4):
            btnAddUnit = wx.Button(self, -1, "Create Class {}".format(count))
            lvlSizer.Add(btnAddUnit)
            self.Bind(wx.EVT_BUTTON, lambda event, nlvl=count: self.onAddUnit(event, nlvl), btnAddUnit)

        self.showSizer.Add(lvlSizer, flag=wx.ALIGN_CENTER, border=5)
        self.showSizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND | wx.ALL, border=10)

    def displayLoadouts(self):
        addLoadout = wx.Button(self, -1, "Add Loadout")
        # Gear list for model
        self.gopts = GearList.copy()
        # Add adv gear chosen by traits / self.gear
        for gear in self.gear:
            if gear.endswith("pts"):
                words = gear.split(' ')
                last = words.pop(-1)
                name = " ".join(words)
                (cost, trash) = last.split("pt")
                if not name in self.gopts:
                    self.gopts[name] = {}
                    for key in AdvGear[name].keys():
                        self.gopts[name][key] = AdvGear[name][key]
                self.gopts[name]['Cost'] = str(int(self.gopts[name]['Cost']) + int(cost))
# Abundant Resources
# Mineral Riches
        self.Bind(wx.EVT_BUTTON, lambda event, a="new", i=0: self.onUpdateLoad(event, a, i), addLoadout)
        self.showSizer.Add(addLoadout, flag=wx.EXPAND | wx.ALL, border=10)

        if self.tab['loads']:
            loadGrid = wx.GridBagSizer(hgap=3, vgap=0)  # Place to store trait info
            row = 0
            # print header
            fields = ['Name', "# Models", "Gear Selected", "$$", "Total"]
            col = 1
            for field in fields:
                label = wx.StaticText(self, label=field, style=wx.ALIGN_CENTER, size=(len(field)*11, -1))
                label.SetFont(self.boldfont)
                loadGrid.Add(label, pos=(row, col), flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER)
                col += 1
            row += 1
            #for load in self.tab['loads']:
            for index in range(len(self.tab['loads'])):
                (name, qty, gear, gcost, total) = self.tab['loads'][index].split('|')
                # recalculate gear loadouts
                priorgear = self.chgGear2Dict(gear)
                (gcost, total, display) = self.gearCalc(qty, priorgear)
                self.tab['loads'][index] = "|".join((name, qty, display, gcost, total))
                # Del button
                delBtn = wx.Button(self, -1, "x", size=(36, -1))
                self.Bind(wx.EVT_BUTTON, lambda event, a="del", i=index: self.onUpdateLoad(event, a, i), delBtn)
                loadGrid.Add(delBtn, pos=(row, 0), flag=self.flags, border=self.border)
                # Name
                nameLbl = wx.TextCtrl(self, size=(150, -1), value=name)
                self.Bind(wx.EVT_TEXT, lambda event, a="name", i=index: self.onUpdateLoad(event, a, i), nameLbl)
                loadGrid.Add(nameLbl, pos=(row, 1), flag=self.flags, border=self.border)
                # Qty
                qtySpin = wx.SpinCtrl(self, -1, qty, min=0, max=100, size=(-1, -1))
                self.Bind(wx.EVT_SPINCTRL, lambda event, a="spin", i=index: self.onUpdateLoad(event, a, i), qtySpin)
                loadGrid.Add(qtySpin, pos=(row, 2), flag=self.flags, border=self.border)
                # Gear
                gearBtn = wx.Button(self, -1, gear)
                self.Bind(wx.EVT_BUTTON, lambda event, a="gear", i=index: self.onUpdateLoad(event, a, i), gearBtn)
                loadGrid.Add(gearBtn, pos=(row, 3), flag=self.flags, border=self.border)
                # gcost
                totLbl = wx.StaticText(self, label=gcost, style=self.flags)
                loadGrid.Add(totLbl, pos=(row, 4), flag=wx.ALIGN_CENTER)
                # Total
                totLbl = wx.StaticText(self, label=total, style=self.flags)
                loadGrid.Add(totLbl, pos=(row, 5), flag=wx.ALIGN_CENTER)
                row += 1
            self.showSizer.Add(loadGrid, flag=wx.EXPAND | wx.ALL, border=10)
            #loadGrid.AddGrowableCol(1)
            loadGrid.AddGrowableCol(3)

    def onUpdateLoad(self, event, action, index):
        if action == "new":
            load = "|0|Select Gear|0|0"
            self.tab['loads'].append(load)
            self.DrawTab()
        elif action == "del":
            # remove name from array
            self.tab['loads'].pop(index)
            self.DrawTab()
        else:
            ### append to GearList with selections
            # Name, Qty, Model Gear, Unit Gear, Total
            (name, qty, gear, gcost, total) = self.tab['loads'][index].split('|')
            if action == "name":
                # update name in array
                self.tab['loads'][index] = "|".join( (event.GetString(),qty, gear, gcost, total))
            elif action == 'spin':
                qty = str(event.GetPosition())
                # Turn Gear into a list
                priorgear = self.chgGear2Dict(gear)
                (gcost, total, display) = self.gearCalc(qty, priorgear)
                self.tab['loads'][index] = "|".join( (name, qty, display, gcost, total) )
                self.DrawTab()
            elif action == "gear":
                priorgear = self.chgGear2Dict(gear)
                dia = selGearDiag(self)
                dia.CreateGearList(self.tab['clvl'], priorgear, self.gopts)
                if dia.ShowModal() == wx.ID_OK:
                    (gcost, total, display) = self.gearCalc(qty, dia.gear)
                    gearline = "|".join((name, qty, display, gcost, total))
                    self.tab['loads'][index] = gearline
                    dia.Destroy()
                self.DrawTab()

    def chgGear2Dict(self, gearstr):
        data = {}
        for item in gearstr.split(', '):
            if " $" in item:
                (front, cost) = item.split(" $")
                if " x" in front:
                    (name, count) = front.split(" x")
                else:
                    name = front
                    count = 99999
                data[name] = int(count)
        return(data)

    def gearCalc(self, qty, select_gear):
        display_list = []
        model_gear = 0
        unit_gear = 0

        #gear_keys = select_gear.keys()
        #gear_keys.sort()

        for item in sorted(select_gear.keys()):
            if select_gear.get(item, 0) == 99999:
                display_list.append("{} ${}".format(item, self.gopts[item]['Cost']))
                if self.gopts[item]['Category'] == "Primitive":
                    unit_gear += int(self.gopts[item]['Cost'])
                    # Take half off primitive gear cost if it's a single model
                    if int(qty) == 1:  unit_gear -= int(.5 * int(self.gopts[item]['Cost']))
                else:
                    model_gear += int(self.gopts[item]['Cost'])
            elif select_gear.get(item, 0) > 0:
                display_list.append("{} x{} ${}".format(item, select_gear[item], self.gopts[item]['Cost']))
                unit_gear += int(self.gopts[item]['Cost']) * int(select_gear[item])
        if len(display_list) > 1:
            display = ", ".join(display_list)
        elif len(display_list) == 1:
            display = "".join(display_list)
        else:
            display = "Select Gear"

        if int(qty) == 0: unit_gear = 0
        gcost = str(model_gear * int(qty) + unit_gear)
        return(gcost, str(int(gcost) + int(qty) * int(self.Total)), display)

    def onAddUnit(self, event, nlvl, name="New Unit"):
        # Make a new tab
        new = UnitTab(self.ptr['parent'][0])
        self.ptr['parent'][0].AddPage(new, "L{}: {}".format(nlvl, name))
        # Assign a unit key
        new.initTab(self.tab['domain'], self.ptr['parent'] + [self], nlvl, name)
        new.getCtraits()
        new.DrawTab()
        self.ptr['children'].append(new)

    def onDelTrait(self, event, trait):
        # Every traits that makes it here should be in the format sel|action|pv|prune|parent
        if '|' in trait:
            (name, action, pv, filter, parent) = trait.split('|')
            # get location
            index = self.tab['ctraits'].index(trait)
            # update list
            self.tab['ctraits'][index] = '|'.join(("", action, pv, filter, parent))
### Need to check for orphaned subtraits :/
        self.DrawTab()

    def onSelTrait(self, event, trait):
        (sel, action, pv, prune, prior) = trait.split('|')

        index = self.tab['ctraits'].index(trait)

        if action == "Pick":
### Bypass call if list only contains 1 value?
            dia = selAttrDiag(self)
            dia.CreateTree(prune, ["Increase Strength 1", "Increase Toughness 1", "Increase Movement 1",
                        "Increase Martial 1", "Increase Ranged 1", "Increase Defense 1",
                        "Increase Discipline 1", "Increase Willpower 1",
                        "Increase Command 1", "Increase Wounds 1", "Increase Attacks 1"])

        if action == "Trait":
            dia = selDiag(self)
            if prune:
                dia.CreateTree(self.tab['filter'], prune.split(' '), TraitList)
            else:
                dia.CreateTree(self.tab['filter'], [], TraitList)

        if dia.ShowModal() == wx.ID_OK:
            name = dia.return_value
            # Update the cTrait list
            self.tab['ctraits'][index] = '|'.join((name, action, pv, prune, prior))
            dia.Destroy()

        if action == "Trait":
            for effect in TraitList[name]['Display'].split('; '):
                (qty, type, prune) = self.testTraitBranching(name, effect)
                for addition in range(qty):
                    # Insert Trait Line
                    index += 1
                    self.tab['ctraits'].insert(index, '|'.join(("", type, "0", prune, name)))
        self.DrawTab()

    def testTraitBranching(self, name, effect):
        branchTraits = {
            "Species Variant ": "{} T2".format(TraitList[name]['Branch']) ,
            "Rare Traits ":  "",
            "Mercenary Class ": "Armory",
            "Adaptive Science ": "Knowledge and Science"
        }
### Fix Rare Traits

        type = "Trait"
        count = 0
        prune = []
        for key in branchTraits.keys():
            if effect.startswith(key):
                 list = effect.split(" ")
                 count = int(list[2])
                 prune = branchTraits[key]
        if " or " in  effect:
            count = 1
            prune = '; '.join(effect.split(' or '))
            type = "Pick"
        return(count, type, prune)


    def doTraitMods(self, item, type):
        (sel, action, pv, filter, prior) = item.split('|')
        # PV changes
        # Check for trait effects on the profile
        if sel:
            if action == "mod":
                list = sel.split(" ")
                self.tab[list[1]] += int(list[2])
            if action == "Pick":
                if type == "Class": self.tab['ctotal'] += int(pv)
                if sel.startswith("Increase "):
                    list = sel.split(" ")
                    self.tab[list[1]] += int(list[2])
            if action == "Trait":
                # Add to class total
                self.tab['ctotal'] += int(pv) + int(TraitList[sel]['Cost'])
                # Remove if it's a faction trait
                if type == "Prior" and self.tab['clvl'] > 0:
                    if item in self.ptr['parent'][1].tab['ctraits']:
                        self.tab['ctotal'] -= int(pv) + int(TraitList[sel]['Cost'])
                # Resolve trait effects
                effects = TraitList[sel]['Display'].split('; ')
                for effect in effects:
                    if " or " in effect:
                        trash = 1 #(ignore)
                    elif effect.startswith("Increase "):
                        list = effect.split(" ")
                        self.tab[list[1]] += int(list[2])
                    elif effect.startswith("Decrease "):
                        list = effect.split(" ")
                        self.tab[list[1]] -= int(list[2])
                    elif effect.startswith("Armory: "):
                        list = effect.split(": ")
                        self.gear.append(list[1])

