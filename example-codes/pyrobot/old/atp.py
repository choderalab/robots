# gridEvents.py
import csv
import sys, os, subprocess
import wx
import wx.grid as gridlib

from database import MySQLDatabase
from os import path
from toolbox import tecan

PLOT_EXP_DATA_EXE = 'plotExpData'
PLOT_EXP_DATA_LINUX = '/home/ayelet/pyrobot/PlotExpData'

####################################################

def connect():
    return MySQLDatabase(host='hldbv02', user='ronm', 
                         passwd='a1a1a1', db='tecan')
    
    """
    return MySQLDatabase(host='132.77.80.238', user='ronm', 
                         passwd='a1a1a1', db='tecan')
    """
    
    #from toolbox.database import SqliteDatabase
    #return SqliteDatabase("C:\\TEMP\\mydatabase.sqlite", flag='r')
    
########################################################################
def getExpId(db):
    exp_id_list = []
    des_list=[]
    for row in db.Execute("SELECT distinct(exp_ID) eid from tecan_readings ORDER BY eid DESC"):
        exp_id_list.append(row[0])
        des_list.append(GetDes(db,row[0]))
    print exp_id_list
    print des_list
    return exp_id_list,des_list

def getPlate(db, exp_ID):
    result_list = []
    for row in db.Execute("SELECT distinct(plate) from tecan_readings WHERE exp_ID='%s'" % exp_ID):
        plate = str(row[0])
        desc = GetDes(db,exp_ID,plate)
        result_list.append((plate, desc))
    return result_list

def GetDes(db,exp_ID,plate=-1) :
    for row in db.Execute("SELECT distinct(description) from tecan_experiments WHERE exp_ID='%s'" % exp_ID):
        print(row[0])
        return str(row[0])
    return "No Des."


def getReadingLabel(db, plate):
    reading_label_list = []
    for row in db.Execute("SELECT distinct(reading_label) from tecan_readings WHERE plate='%s'" % plate):
        reading_label_list.append(str(row[0]))
    return reading_label_list


################################################################################


###################################################3



###################################################

class PromptingComboBox(wx.ComboBox) :
    def __init__(self, parent, value, choices=[], style=0, **par):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN, choices=choices, **par)
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.ignoreEvtText = False

    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        print "event ! combo box"
        print self.GetCurrentSelection()
        print self.GetValue()
        widget = event.GetEventObject()
        print widget.GetName()
        print self.GetId()
        event.Skip()

    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        found = False
        for choice in self.choices :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.SetValue(choice)
                self.SetInsertionPoint(len(currentText))
                self.SetMark(len(currentText), len(choice))
                found = True
                break
        if not found:
            event.Skip()
        

        

########################################################################

class SelectionListBox(wx.ListBox):
    
    def __init__(self,parent):
        wx.ListBox.__init__(self,parent)
        self.selectionDict = {}
        
        self.Bind(wx.EVT_LISTBOX, self.EvtSelListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.EvtDeleteSelection)
    
    #    self.Bind(wx.EVT_RIGHT_DOWN, self.RightClickSelectionListBox)
    
    #def RightClickSelectionListBox(self,event):
    #    if (self.GetStringSelection()) :
    #        del self.selectionDict[self.GetStringSelection()]
    #        self.Delete(self.Selection())
        
        
    
    def EvtSelListBox(self, event):
        selection = self.GetStringSelection()
        if selection == u'':
            return
        print "Selection LIST BOX TOGGLED", selection
        
        expID_key = self.selectionDict[selection]['expID_key']
        self.Parent.experimentComboBox.SetValue(expID_key)
        plate = self.selectionDict[selection]['plate']

        self.Parent.UpdatePlateListBox(plate)
        self.Parent.measurementListBox.Enable(True)
            
        reading_labels_fromDB = getReadingLabel(self.Parent.db, plate=plate)
        items = []
        for i in reading_labels_fromDB:
            items.append(i)
            self.Parent.measurementListBox.SetItems(items) 
        for i in range(len(items)):
            self.Parent.measurementListBox.SetSelection(i,True)
        
        reading_labels_fromDict = self.selectionDict[selection]['reading_labels']
        for label in reading_labels_fromDict :
            self.Parent.measurementListBox.SetStringSelection(label)
        
        self.Parent.LoadPlateLabels()
        cells = self.selectionDict[self.GetStringSelection()]['cells']
        self.Parent.myGrid.ClearSelection()
        for row, col in cells:
            self.Parent.myGrid.SelectBlock(row,col,row,col,True)
        #    print" "        
        
    def EvtDeleteSelection(self, event):
        selection = self.GetStringSelection()
        if selection == u'':
            return
        print "Selection LIST BOX Double-clicked", selection
        del self.selectionDict[selection]
        key_list = sorted(self.selectionDict.keys())
        self.SetItems(key_list)
        self.Parent.myGrid.ClearSelection()
        self.Update()
        
    def genKey(self, expID, expDesc, plate, plateDesc):
        return "%s | %s - %s | %s" % (expID, expDesc, plate, plateDesc)
        
    def updateGridSelections(self, expID, expDesc, plate, plateDesc, reading_labels, cells):
        if (not reading_labels): ### prevents loading data when labels are not selected 
            return
        key = self.genKey(expID, expDesc, plate, plateDesc)
        self.selectionDict[key] = {'expID':expID,
                                   'expID_key':expID + ' | ' + expDesc,
                                   'plate':plate,
                                   'reading_labels':reading_labels,
                                   'cells':cells}
        key_list = sorted(self.selectionDict.keys())
        self.SetItems(key_list)
        current_key_index = key_list.index(key)
        self.SetSelection(current_key_index)
        self.Update()
        
########################################################################
class MyGrid(gridlib.Grid):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
      
        gridlib.Grid.__init__(self, parent)
        self.CreateGrid(8, 12)
        self.selectionListBox = parent.selectionListBox
        self.EnableEditing(False)
        self.EnableDragColSize(False)
        self.EnableDragRowSize(False)
        self.EnableDragCell(True)
        
        for c in range(12):
            self.SetColLabelValue(c,str(c+1))
        for r in range(8):
            self.SetRowLabelValue(r,chr(r+97).upper())
        
        
        
 
 
        # test all the events
        
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)
 
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)
 
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)
 
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
 
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)
        
    def GetSelection(self) :
        selection=[]
        for row in range(8):
            for col in range(12):
                if (self.IsInSelection(row,col)) :
                    selection.append((row,col))
        return selection
                   

    def OnCellLeftClick(self, evt):
        print "OnCellLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                 evt.GetCol(),
                                                 evt.GetPosition())
        evt.Skip()
 
    def OnCellRightClick(self, evt):
        print "OnCellRightClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition())
        evt.Skip()
 
    def OnCellLeftDClick(self, evt):
        print "OnCellLeftDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition())
        evt.Skip()
 
    def OnCellRightDClick(self, evt):
        print "OnCellRightDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition())
        evt.Skip()
 
    def OnLabelLeftClick(self, evt):
        print "OnLabelLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition())
        evt.Skip()
 
    def OnLabelRightClick(self, evt):
        print "OnLabelRightClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition())
        evt.Skip()
 
    def OnLabelLeftDClick(self, evt):
        print "OnLabelLeftDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                   evt.GetCol(),
                                                   evt.GetPosition())
        evt.Skip()
 
    def OnLabelRightDClick(self, evt):
        print "OnLabelRightDClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                    evt.GetCol(),
                                                    evt.GetPosition())
        evt.Skip()
 
    def OnRowSize(self, evt):
        print "OnRowSize: row %d, %s\n" % (evt.GetRowOrCol(),
                                           evt.GetPosition())
        evt.Skip()
 
    def OnColSize(self, evt):
        print "OnColSize: col %d, %s\n" % (evt.GetRowOrCol(),
                                           evt.GetPosition())
        evt.Skip()
 
 
    def OnCellChange(self, evt):
        print "OnCellChange: (%d,%d) GetPosition : %s" % (evt.GetRow(), evt.GetCol(), evt.GetPosition())
 
        # Show how to stay in a cell that has bad data.  We can't just
        # call SetGridCursor here since we are nested inside one so it
        # won't have any effect.  Instead, set coordinates to move to in
        # idle time.
        value = self.GetCellValue(evt.GetRow(), evt.GetCol())
        print " --> Cell was updated to %s \n" % (value)
        self.Parent.commitButton.SetForegroundColour("Red")
        
 
        if value == 'no good':
            self.moveTo = evt.GetRow(), evt.GetCol()
             
    def OnRangeSelect(self, evt):
        self.Parent.updateSelectionListBox()
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        print "OnRangeSelect: %s  top-left %s, bottom-right %s\n" % (msg, evt.GetTopLeftCoords(),
                                                                     evt.GetBottomRightCoords())
        evt.Skip()
        
    def OnSelectCell(self, evt):
        self.Parent.updateSelectionListBox()
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
            
       

        
        
        print "OnSelectCell: %s (%d,%d) %s\n" % (msg, evt.GetRow(),
                                                 evt.GetCol(), evt.GetPosition())
 
        # Another way to stay in a cell that has a bad value...
        row = self.GetGridCursorRow()
        col = self.GetGridCursorCol()
 
        if self.IsCellEditControlEnabled():
            self.HideCellEditControl()
            self.DisableCellEditControl()
 
        value = self.GetCellValue(row, col)
 
        if value == 'no good 2':
            return  # cancels the cell selection
 
        evt.Skip()
 
 
    def OnEditorShown(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           wx.MessageBox("Are you sure you wish to edit this cell?",
                        "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return
 
        print "OnEditorShown: (%d,%d) %s\n" % (evt.GetRow(), evt.GetCol(),
                                               evt.GetPosition())
        evt.Skip()
 
 
    def OnEditorHidden(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           wx.MessageBox("Are you sure you wish to  finish editing this cell?",
                        "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return
 
        print "OnEditorHidden: (%d,%d) %s\n" % (evt.GetRow(),
                                                evt.GetCol(),
                                                evt.GetPosition())
        evt.Skip()
 
 
    def OnEditorCreated(self, evt):
        print "OnEditorCreated: (%d, %d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetControl())
    def LoadFromCSV(self,event):
        wildcard = "CSV files(*.csv)|*.csv|" \
         "All files (*.*)|*.*"

        dialog = wx.FileDialog(None,message="Choose a file",
            defaultFile="",
            wildcard="CSV files(*.csv)|*.csv|"\
            "All files (*.*)|*.*",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        # Show the dialog and get user input
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetPath()
        else:
            sys.exit(0)
            dialog.Destroy()
            
        self.basename, self.extension = path.splitext(self.filename)
        if self.extension == '.csv':
            print self.filename
        else:
            print "Not CSV !\n"
            
        fi=open(self.filename)
        lines=fi.readlines()
        reader = csv.reader(lines)
        row_index=-1
       
        for row in reader:
            if len(row) == 12 :
                row_index+=1
                col_index=-1
                for col in row :
                    col_index+=1
                    self.SetCellValue(row_index, col_index,col)
            else:
                dlg = wx.MessageDialog(self, 'Please validate CSV file',
                                       'Error loading plate description',
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            
        self.Update()
            
########################################################################
  

class MyPanel(wx.Panel):
    
    def __init__(self, parent, id):
        
        wx.Panel.__init__(self, parent, id)
        
        # Connect to DB
        self.db = connect()
        
        # Map of action names to callable functions handling them
        self.actionMap = {'Generate CSV': self.GenerateCSVEvent,
                          'Run Uri Button': self.UriMethod,
                          'Plot Growth Curves': self.PlotGrowthCurves,
                          'Commit Experiment Description': self.CommitPlateLabels,}
        
        # Sizers
        topSizer    = wx.BoxSizer(wx.VERTICAL)
        titleSizer  = wx.BoxSizer(wx.HORIZONTAL)
        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        bagSizer    = wx.GridBagSizer(hgap=5, vgap=5)
        
        # Add icons
        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        titleIco = wx.StaticBitmap(self, wx.ID_ANY, bmp)
        title = wx.StaticText(self, wx.ID_ANY, 'ATP - Automatic Tecan Pipeline 1.0 ')
        title.SetFont(font)
        titleSizer.Add(titleIco, 0, wx.ALL, 5)
        titleSizer.Add(title, 0, wx.ALL, 5)
        
        # Bind event handlers
        self.Bind(wx.EVT_COMBOBOX, self.OnComboBoxClicked)
        self.Bind(wx.EVT_LISTBOX, self.OnListboxClick)
        
        # Experiment chooser
        self.experimentComboBox = wx.ComboBox(self, wx.ID_ANY, value="Select Experiment",
                                              choices=self.GenerateExperimentComboBoxChoices(),
                                              style=wx.CB_DROPDOWN)
        bagSizer.Add(self.experimentComboBox, pos=(0,0),span=(1,1),
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        
        # Plate chooser
        self.plateComboBox = wx.ComboBox(self, wx.ID_ANY, value="Select Plate",
                                         choices=['Null\t'],
                                         style=wx.CB_SORT|wx.CB_DROPDOWN)
        self.plateComboBox.Enable(False)
        bagSizer.Add(self.plateComboBox, pos=(1,0),span=(1,1),
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        
        # Measurement picker
        self.measurementListBox_choices = ['Select Measurement']
        self.measurementListBox = wx.ListBox(self, -1, choices=self.measurementListBox_choices,
                                             style=wx.LB_MULTIPLE)
        self.measurementListBox.Enable(False)
        bagSizer.Add(self.measurementListBox, pos=(2,0), span=(1,1),
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        
        print "Displaying cb1 ID : \n"
        print self.experimentComboBox.GetId()
        print "Displaying cb2 ID : \n"
        print self.plateComboBox.GetId()
        print "Displaying cb3 ID : \n"
        print self.measurementListBox.GetId()
        
        # Is declated here sincve mygrid requires this object
        # myGrid uses the selectionListBox data member from 'self'
        self.selectionListBox = SelectionListBox(self)
        self.myGrid = MyGrid(self)
        bagSizer.Add(self.myGrid, pos=(0,1), span=(3,1),
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        
        # Load CSV
        self.loadCsvButton = wx.Button(self, wx.ID_ANY, 'Import plate labels')
        self.loadCsvButton.Bind(wx.EVT_BUTTON, self.myGrid.LoadFromCSV)
        bagSizer.Add(self.loadCsvButton, pos=(3,0), span=(1,1), 
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        
        # Commit labels
        self.commitButton = wx.Button(self, wx.ID_ANY, 'Commit Labels')
        bagSizer.Add(self.commitButton, pos=(3,1), span=(1,1),
                     flag=wx.ALL|wx.EXPAND,
                     border=5)
        self.commitButton.Bind(wx.EVT_BUTTON, self.CommitPlateLabels)

        # Add nested sizers
        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        
        topSizer.Add(bagSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        
        # Selection box was declared earlier since MyGrid required this object
        # -- self.selectionListBox = SelectionListBox(self)
        topSizer.Add(self.selectionListBox, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        
        # Choose an action to perform with selected data.
        self.actionsCombo = wx.ComboBox(self, wx.ID_ANY, 'Choose Action',
                                        choices=['None'] + sorted(self.actionMap.keys()))
        topSizer.Add(self.actionsCombo, 0, wx.ALL|wx.EXPAND, 5)
        
        # Button for running the given action.
        self.runAction = wx.Button(self, wx.ID_ANY, 'Run Action')
        self.runAction.Bind(wx.EVT_BUTTON, self.RunChosenAction)
        topSizer.Add(self.runAction, 0, wx.ALL|wx.EXPAND, 5)

        # Placeholde for something Niv wants to do?       
        query='#  #'
        self.sqltext= wx.StaticText(self, -1, query, style=wx.ALIGN_CENTRE)
        topSizer.Add(self.sqltext, 0, wx.ALL, 5)
        
        self.SetSizer(topSizer)
        topSizer.Fit(self)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
          
        self.SetSizer(topSizer)

    def RunChosenAction(self, event):
        print 'Run chosen action'
        
        exp = self.GetCurrentExpID()
        plate = self.GetCurrentPlate()
        grid = self.myGrid.GetSelection()
        if not exp or not plate or not grid:
            dlg = wx.MessageDialog(self, 'You did not select an experiment, plate, or cells.',
                                   'Select data before running an action',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()
            return
        
        
        val = self.actionsCombo.GetValue()
        callable = self.actionMap.get(val, None)
        if callable:
            callable(event)
        else:
            dlg = wx.MessageDialog(self, 'Please choose a valid action',
                                   'You did not choose a valid action to run',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        
        event.Skip()
        
    def Import2DB(self, event):

        #app = wx.App(False)
        dialog = wx.FileDialog(None, style=wx.OPEN)
        # Show the dialog and get user input
        if dialog.ShowModal() == wx.ID_OK:
            tar_fname = dialog.GetPath()
        else:
            dialog.Destroy()
            return
            
        if not os.path.exists(tar_fname):
            return
        
        dialog_num_plates = wx.TextEntryDialog(self,
            'Please enter the number of plates',
            'Number of plates', '1')
        dialog_num_plates.ShowModal()
        number_of_plates = int(dialog_num_plates.GetValue())
    
        #message = "Importing data into DB..."
        #self.busy = PBI.PyBusyInfo(message, parent=None, title="Importing to DB")
        MES = tecan.CollectData(tar_fname, number_of_plates)
        exp_id = tecan.GetExpDate(MES)
        self.db.Execute("DELETE FROM tecan_readings WHERE exp_id='%s'" % exp_id)
        """dlg = wx.ProgressDialog("Retriving data from DB",
                               "Time Remaining",
                               maximum = count,
                               parent=self,
                               style = wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                )"""
        counter = -1
        for plate_id, plate_values in sorted(MES.iteritems()):
            for reading_label, label_values in sorted(plate_values.iteritems()):
                print "Importing plate %d label %s " % (plate_id, reading_label)
                for time_in_sec, time_values in sorted(label_values.iteritems()):
                    for well, value in sorted(time_values.iteritems()):
                        counter += 1
                        #dlg.Update(counter)
                        self.db.Insert('tecan_readings', [exp_id, plate_id,
                            reading_label, well[0], well[1], time_in_sec, value])
                self.db.Commit()
        dlg = wx.MessageDialog(self, 'Import completed successfully:\n%s' % exp_id,
                            'Done Import',
                            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        self.experimentComboBox.SetItems(self.GenerateExperimentComboBoxChoices())
   
        
        #dlg.Destroy()
        #del self.busy
    
    def GenerateExperimentComboBoxChoices(self):
        experimentComboBox_choices = []
        experimentComboBox_exp_list, experimentComboBox_des_list = getExpId(self.db) #This line returns the Exp. names AND the Des of exp. from the data base.
        for i in range(0, len(experimentComboBox_exp_list)):
            if experimentComboBox_des_list[i]: 
                experimentComboBox_choices.append(" | ".join([experimentComboBox_exp_list[i], experimentComboBox_des_list[i]]))
            else : 
                experimentComboBox_choices.append(experimentComboBox_exp_list[i])
                
        return experimentComboBox_choices

    def ChangeExperimentDescription(self, event):
        try:
            from agw import pybusyinfo as PBI
        except ImportError: # if it's not there locally, try the wxPython lib.
            import wx.lib.agw.pybusyinfo as PBI
        val = self.experimentComboBox.GetValue()
        expID, desc = val.split(' | ')
        dlg = wx.TextEntryDialog(
                self, 'Please enter description for %s' % expID,
                'Description', desc)
        dlg.ShowModal()
        desc = dlg.GetValue()
        message = "Connecting DB..."
        self.busy = PBI.PyBusyInfo(message, parent=None, title="Connecting DB")
        self.db.Execute("DELETE FROM tecan_experiments WHERE exp_ID = '%s' AND plate = -1" % expID)
        self.db.Insert('tecan_experiments', [expID, -1, desc])
        self.db.Commit()
        del self.busy
        
        self.experimentComboBox.SetItems(self.GenerateExperimentComboBoxChoices())
        self.experimentComboBox.SetValue(" | ".join([expID, desc]))
        
        #Insert TO exp_des #

    def UriMethod(self, event):
        try:
            from agw import pybusyinfo as PBI
        except ImportError: # if it's not there locally, try the wxPython lib.
            import wx.lib.agw.pybusyinfo as PBI
        
        # Create an open file dialog
        dialog = wx.DirDialog(self, message='Pick a directory.', style=wx.DD_NEW_DIR_BUTTON)
        
        # Show the dialog and get user input
        if dialog.ShowModal() == wx.ID_OK:
            outpath = dialog.GetPath()
            outpath = "/".join(outpath.split('\\'))
            print 'Selected:', outpath
        else:
            print 'Nothing was selected.'
            return
        dialog.Destroy()
        # Only destroy a dialog after you're done with it.
        
        _expID, expDesc = self.GetCurrentExpID()
        dialog2 = wx.TextEntryDialog(self, 'Choose a prefix for the result files.',
                                     'Choose prefix', expDesc)
        if dialog2.ShowModal() == wx.ID_OK:
            prefix = dialog2.GetValue()
            outfname = outpath +'/' + prefix
        else:
            return

        csv_fname = outfname + '.csv'
        self.GenerateCSV(csv_fname)
        
        
        if sys.platform == "win32":   
            message = "Please wait while generating figures... (May take a few minutes)"
            busy = PBI.PyBusyInfo(message, parent=self, title="ATP - Automatic TECAN Pipeline")
            print "WINDWOS FOUND !!!"             # on a Windows port
            command = PLOT_EXP_DATA_EXE + ' -i %s -o %s' % (csv_fname, outfname)
            print command
            try:
                import win32pipe
            except ImportError:
                    raise ImportError, "The win32pipe module could not be found"
            #popen = win32pipe.popen
            win32pipe.popen(command,'r')
            print "win32"
            del busy
        else:
            if not os.path.exists(PLOT_EXP_DATA_LINUX):
                dlg = wx.MessageDialog(self, 
                    'Cannot locate PlotExpData executable: %s' % PLOT_EXP_DATA_LINUX,
                    'File not found', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            args = [PLOT_EXP_DATA_LINUX, '-i', csv_fname, '-o', outfname]
            print ' '.join(args)
            subprocess.call(args=args, executable=PLOT_EXP_DATA_LINUX)
        
        reportString = "Files generated:\n"
        for filename in os.listdir(outpath):
            try:
                basename, extension = filename.rsplit('.', 1)
            except ValueError:
                continue
            if basename[:len(prefix)] == prefix and extension == 'svg':
                reportString += filename + "\n"
        
        dlg = wx.MessageDialog(self, reportString,
                               'Report', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnListboxClick(self, event):
        if event.GetId() == self.selectionListBox.GetId():
            self.updateSelectionListBox()
        
    def GetCurrentExpID(self):
        expID = self.experimentComboBox.GetValue()
        return expID.split(" | ")
    
    def GetCurrentPlate(self):
        plate = self.plateComboBox.GetValue()
        return plate.split(" | ")
        
    def CommitPlateLabels(self, event):
        expID, expDesc = self.GetCurrentExpID()
        plate, plateDesc = self.GetCurrentPlate()
        self.db.Execute("DELETE FROM tecan_labels WHERE exp_id='%s' AND"
                        " plate='%s'" % (expID, plate))
        for row in range(8):
            for col in range(12):
                label = self.myGrid.GetCellValue(row, col)
                if not label:
                    label = "%s%d" % (chr(ord('A')+row), col+1)
                self.db.Insert('tecan_labels', [expID, plate, row, col, label])
        self.db.Commit()
        self.commitButton.SetForegroundColour("Black")
        self.commitButton.Refresh
        
    def LoadPlateLabels(self):
        expID, expDesc = self.GetCurrentExpID()
        plate, plateDesc = self.GetCurrentPlate()
        
        for row in range(8):
            for col in range(12):
                label = "%s%d" % (chr(ord('A')+row), col+1)
                self.myGrid.SetCellValue(row, col, label)
        for row,col,label in self.db.Execute("SELECT row, col, label FROM tecan_labels "
                                             "WHERE exp_id='%s' AND plate='%s'" % (expID, plate)):
            self.myGrid.SetCellValue(row, col, label)
        self.myGrid.Update()
        
    def updateSelectionListBox(self):
        cells = self.myGrid.GetSelection()
        if cells == []:
            return
        expID, expDesc = self.GetCurrentExpID()
        plate, plateDesc = self.GetCurrentPlate()
        reading_labels = [self.measurementListBox.GetString(i) for i in self.measurementListBox.GetSelections()]
        self.selectionListBox.updateGridSelections(expID, expDesc,
                                                   plate, plateDesc,
                                                   reading_labels, cells)
    
 
    def UpdatePlateListBox(self, selectedPlate=None):
        expID, expDesc = self.GetCurrentExpID()
        plates = getPlate(self.db, exp_ID=expID)
        items = [plate + " | " + desc for plate, desc in plates]
        self.plateComboBox.Enable(True)
        self.plateComboBox.SetItems(items)
        if selectedPlate:
            try:
                plate_index = [plate for plate, desc in plates].index(selectedPlate)
                self.plateComboBox.SetSelection(plate_index)
            except KeyError:
                pass
    
    def OnComboBoxClicked(self, event):
        print 'event reached panel class'

        self.commitButton.SetForegroundColour("Black")
        self.commitButton.Refresh()
        
        if event.GetId() == self.experimentComboBox.GetId():
            self.myGrid.ClearSelection()
            
            self.myGrid.EnableEditing(False)
            self.myGrid.ClearGrid()
            self.UpdatePlateListBox(None)
            self.plateComboBox.SetValue('Select Plate')
            self.measurementListBox.SetItems([]) 

            #self.statext.SetLabel('Present info regarding exp. " %s " here' % val)
            event.Skip()
        elif event.GetId() == self.plateComboBox.GetId():
            self.myGrid.ClearSelection()
            
            self.myGrid.EnableEditing(True)
            self.LoadPlateLabels()
            self.measurementListBox.Enable(True)
            #print  event.GetId()
            plate, plateDesc = self.GetCurrentPlate()
            reading_labels = getReadingLabel(self.db, plate=plate);
            print "here comes the items:"
            items=[]
            for i in reading_labels:
                items.append(str(i))
                print items
            self.measurementListBox.SetItems(items) 
            for i in range(len(items)) :
                self.measurementListBox.SetSelection(i,True)
            
            event.Skip()
        

    def GetCellLabel(self, expID, plate, row, col):
        for lab in self.db.Execute("SELECT label FROM tecan_labels "
                                   "WHERE exp_id = '%s' AND plate = '%s' "
                                   "AND row = %d AND col = %d" %
                                   (expID, plate, row, col)):
            return lab[0]
        return "%s%d" % (chr(ord('A')+row), col+1)

    def GetCellMeasurements(self, expID, plate, reading_label, row, col):
        return self.db.Execute("SELECT time, measurement FROM tecan_readings "
                               "WHERE exp_id = '%s' AND plate = '%s' "
                               "AND reading_label = '%s' "
                               "AND row = %d AND col = %d" %
                               (expID, plate, reading_label, row, col))

    def GenerateDataForSelectedCells(self):
        """
            returns a dictionary whose keys are reading-labels,
            and values are:
            (cell_label, [(time0, value0), (time1, value1), ...])
        """
        data = {}
        for vals in self.selectionListBox.selectionDict.values():
            expID = vals['expID']
            plate = vals['plate']
            reading_labels = vals['reading_labels']
            cells = vals['cells']
            for row, col in cells:
                cell_label = self.GetCellLabel(expID, plate, row, col)
                for reading_label in reading_labels:
                    measurements = self.GetCellMeasurements(expID, plate, reading_label, row, col)
                    data.setdefault(reading_label, []).append((cell_label, measurements))
        return data

    def PlotGrowthCurves(self, event):
        data = self.GenerateDataForSelectedCells()
        if len(data) > 0:
            # Create an open file dialog
            dialog = wx.FileDialog(None, style=wx.SAVE)
            # Show the dialog and get user input
            if dialog.ShowModal() == wx.ID_OK:
                pdf_fname = dialog.GetPath()
            else:
                print 'Nothing was selected.'
                return
            dialog.Destroy()

            dialog = wx.MessageDialog(self, 'Plot growth rates as well?',
                                      'Plot Growth Rates',
                                      wx.YES_DEFAULT | wx.NO)
            plot_growth_rate = (dialog.ShowModal() == wx.ID_YES)
            dialog.Destroy()

            tecan.PlotGrowthCurves(data, pdf_fname,
                                   plot_growth_rate=plot_growth_rate)
            dlg = wx.MessageDialog(self, 'Plots written succesfully to:\n%s' % pdf_fname,
                            'Done Plotting',
                            wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
                        
    def GenerateCSVEvent(self, event):
        self.GenerateCSV(None)
        
    def GenerateCSV(self, csv_fname=None):
        if csv_fname is None:
            # Create an open file dialog
            dialog = wx.FileDialog(None, style=wx.SAVE)
            # Show the dialog and get user input
            if dialog.ShowModal() == wx.ID_OK:
                csv_fname = dialog.GetPath()
                print 'Selected:', csv_fname
            else:
                print 'Nothing was selected.'
                return
            dialog.Destroy()

        csv.register_dialect('linux', delimiter=',', quotechar='"', lineterminator='\n')
        csv_writer = csv.writer(open(csv_fname, 'w'), dialect='linux')
        
        #dlg = PP.PyProgress(None, -1, "PyProgress Example",
        #                    "An Informative Message",                            
        #                   agwStyle=style)
        
        max = 1
        count = 0
        for vals in self.selectionListBox.selectionDict.values(): #Counting total cells
            expID = vals['expID']
            plate = vals['plate']
            reading_labels = vals['reading_labels']
            cells = vals['cells']
            max+=len(cells)
         
        dlg = wx.ProgressDialog("Retriving data from DB",
                               "Time Remaining",
                               maximum = max,
                               parent=self,
                               style = wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                )
         
        for vals in self.selectionListBox.selectionDict.values():
            dlg.Update(count)
            expID = vals['expID']
            plate = vals['plate']
            reading_labels = vals['reading_labels']
            cells = vals['cells']
            for row, col in cells:
                count+=1
                print "count %d /  max %d" % (count,max)
                dlg.Update(count)
                cell_label = self.GetCellLabel(expID, plate, row, col)
                for reading_label in reading_labels:
                    measurements = self.GetCellMeasurements(expID, plate, reading_label, row, col)
                    for time, value in measurements:
                        csv_writer.writerow([expID, plate, str(reading_label), 
                                             time, row, col, str(cell_label), value])
                       
        dlg.Destroy()
        
                    
            #CSV out put should contain : expID, Plate#,Reading_label,time,row,col,cell_label,mesuremt
            


########################################################################
class MyForm(wx.Frame):
    """"""
 
    #----------------------------------------------------------------------
    
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="Data Extractor",size=(1400,700))
        self.panel = MyPanel(self,-1)

        
 
if __name__ == "__main__":
    
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()
