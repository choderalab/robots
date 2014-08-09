import win32com.client.CLSIDToClass, pythoncom, pywintypes
import win32com.client.util
from pywintypes import IID
import pythoncom
from win32com.client import Dispatch,DispatchWithEvents
import time

VERSION = 2
def checkVersion(version):
    if version != VERSION:
        print "ERROR: PyEvo version mismatch! Expected %d got %d"%(version,VERSION)
        exit(1)

#Constants specific to EVOWARE
class EVOConstants:
    PP_EMERGENCY                  =1          # from enum tagSC_EmergencyLevel
    PP_HIGHEMERGENCY              =2          # from enum tagSC_EmergencyLevel
    PP_NORMAL                     =0          # from enum tagSC_EmergencyLevel
    LAMP_GREEN                    =1          # from enum tagSC_LampStatus
    LAMP_GREENFLASHING            =2          # from enum tagSC_LampStatus
    LAMP_OFF                      =0          # from enum tagSC_LampStatus
    LAMP_REDFLASHING              =3          # from enum tagSC_LampStatus
    PS_BUSY                       =1          # from enum tagSC_ProcessStatus
    PS_ERROR                      =3          # from enum tagSC_ProcessStatus
    PS_FINISHED                   =2          # from enum tagSC_ProcessStatus
    PS_IDLE                       =0          # from enum tagSC_ProcessStatus
    PS_STOPPED                    =4          # from enum tagSC_ProcessStatus
    SS_ABORTED                    =3          # from enum tagSC_ScriptStatus
    SS_BUSY                       =2          # from enum tagSC_ScriptStatus
    SS_ERROR                      =7          # from enum tagSC_ScriptStatus
    SS_IDLE                       =1          # from enum tagSC_ScriptStatus
    SS_PAUSED                     =6          # from enum tagSC_ScriptStatus
    SS_PIPETTING                  =5          # from enum tagSC_ScriptStatus
    SS_SIMULATION                 =8          # from enum tagSC_ScriptStatus
    SS_STATUS_ERROR               =9          # from enum tagSC_ScriptStatus
    SS_STOPPED                    =4          # from enum tagSC_ScriptStatus
    SS_UNKNOWN                    =0          # from enum tagSC_ScriptStatus
    STATUS_ABORTED                =262144     # from enum tagSC_Status
    STATUS_BUSY                   =131072     # from enum tagSC_Status
    STATUS_CONNECTION_ERROR       =16777216   # from enum tagSC_Status
    STATUS_DEADLOCK               =4096       # from enum tagSC_Status
    STATUS_ERROR                  =2097152    # from enum tagSC_Status
    STATUS_EXECUTIONERROR         =8192       # from enum tagSC_Status
    STATUS_IDLE                   =65536      # from enum tagSC_Status
    STATUS_INITIALIZED            =16         # from enum tagSC_Status
    STATUS_INITIALIZING           =8          # from enum tagSC_Status
    STATUS_LOADING                =2          # from enum tagSC_Status
    STATUS_LOGON_ERROR            =8388608    # from enum tagSC_Status
    STATUS_NOINTRUMENTS           =1          # from enum tagSC_Status
    STATUS_NOTINITIALIZED         =4          # from enum tagSC_Status
    STATUS_PAUSED                 =1024       # from enum tagSC_Status
    STATUS_PAUSEREQUESTED         =512        # from enum tagSC_Status
    STATUS_PIPETTING              =1048576    # from enum tagSC_Status
    STATUS_RESOURCEMISSING        =2048       # from enum tagSC_Status
    STATUS_RUNNING                =256        # from enum tagSC_Status
    STATUS_SHUTDOWN               =64         # from enum tagSC_Status
    STATUS_SHUTTINGDOWN           =32         # from enum tagSC_Status
    STATUS_SIMULATION             =4194304    # from enum tagSC_Status
    STATUS_STOPPED                =524288     # from enum tagSC_Status
    STATUS_TIMEVIOLATION          =16384      # from enum tagSC_Status
    STATUS_UNKNOWN                =0          # from enum tagSC_Status
    STATUS_UNLOADING              =128        # from enum tagSC_Status
    TIP_ACTIVE                    =4          # from enum tagSC_TipType
    TIP_DITI                      =1          # from enum tagSC_TipType
    TIP_DITILOVOL                 =3          # from enum tagSC_TipType
    TIP_FIXLOVOL                  =2          # from enum tagSC_TipType
    TIP_STANDARD                  =0          # from enum tagSC_TipType
    TIP_TEMO384                   =8          # from enum tagSC_TipType
    TIP_TEMO384IMPULSE            =7          # from enum tagSC_TipType
    TIP_TEMO96DITI                =6          # from enum tagSC_TipType
    TIP_TEMOFIXED                 =5          # from enum tagSC_TipType
    VS_ITERATION                  =1          # from enum tagSC_VariableScope
    VS_PROCESS                    =0          # from enum tagSC_VariableScope
    STATUS = {
        262144   :"ABORTED               ",
        131072   :"BUSY                  ",
        16777216 :"CONNECTION_ERROR      ",
        4096     :"DEADLOCK              ",
        2097152  :"ERROR                 ",
        8192     :"EXECUTIONERROR        ",
        65536    :"IDLE                  ",
        16       :"INITIALIZED           ",
        8        :"INITIALIZING          ",
        2        :"LOADING               ",
        8388608  :"LOGON_ERROR           ",
        1        :"NOINTRUMENTS          ",
        4        :"NOTINITIALIZED        ",
        1024     :"PAUSED                ",
        512      :"PAUSEREQUESTED        ",
        1048576  :"PIPETTING             ",
        2048     :"RESOURCEMISSING       ",
        256      :"RUNNING               ",
        64       :"SHUTDOWN              ",
        32       :"SHUTTINGDOWN          ",
        4194304  :"SIMULATION            ",
        524288   :"STOPPED               ",
        16384    :"TIMEVIOLATION         ",
        0        :"UNKNOWN               ",
        128      :"UNLOADING             ",
    }

#Event handling from evoware
class EVOSystemEvents:
    def OnStatusChanged(self, status):
        """method StatusChanged"""
        #helper for colored status messages
        def debug(message):
            #color message red when printing
            #print '\033[1;31m' + message + '\033[1;m'
            print message
        statusString = ""
        for key,value in EVOConstants.STATUS.items():
            if status & key == key:
                statusString += value
        debug("STATUS: " + statusString)
    def OnUserPromptEvent(self, ID, text, caption, choices, answer):
        print "UserPrompt" + text
        print "Choices:"
        print choices
#    def OnErrorEvent(self, a1, a2, endTime, device, macro, Object, message, status, processName, processID):
#        print "Error:" + str(message)
#         errorCodes = {14:'Drivers initialization was successful.', 11:'Run finished'}
    def OnErrorEvent(*args):
        print "Error:"
        print args

#Different types of plates that can be used
class PlateTypes:
    #name prefixed with P because python can't start classes with numbers
    class P96WellEppendorf:
        name = "96 Well Eppendorf"
        columns = 8
        rows = 12

class Location:
    def __init__(self,grid,site):
        self.grid = grid
        self.site = site
    def __repr__(self):
        return "Location:(%d,%d,%d,%d)"%(self.grid,self.site,self.row,self.column)
class Plate:
    wells = []
    def __init__(self,grid,site,plateType):
        self.location = Location(grid,site)
        self.plateType = plateType
        def getWellFromIndex(index):
            #return a well object with location described by index 0-95
            row = index / self.plateType.rows + 1
            column = index % self.plateType.rows + 1
            return Well(self, row, column)
        self.wells = [getWellFromIndex(i) for i in range(0,self.plateType.rows * self.plateType.columns)]
    def __repr__(self):
        return "Plate:(%d,%d)"%(self.location.grid,self.location.site)
    def getFreeWell(self):
        #search and find an unused well, return it, and set it to used
        for well in self.wells:
            if well.unused:
                well.unused = False
                return well
    def getWellAtIndex(self,index):
        self.wells[index].unused = False
        return self.wells[index]

class Well:
    def __init__(self,plate,row,column):
        self.plate = plate
        self.row = row
        self.column = column
        self.unused = True
    def __repr__(self):
        return "Well:(%d,%d,Used:%s)"%(self.row,self.column,str(not self.unused))
class TipPlateTypes:
    class DiTi1000ul:
        name = "DiTi 1000ul"
        columns = 8
        rows = 12
    class DiTi200ul:
        name = "DiTi 200 ul"
        columns = 8
        rows = 12
    class DiTi10ul:
        name = "DiTi 10ul"
        columns = 8
        rows = 12
class Tip:
    pickedUp = False
    used = True
    def __init__(self,tipPlate,row,column):
        self.tipPlate = tipPlate
        self.row = row
        self.column = column
class TipPlate:
    tips = []
    def __init__(self,grid,site,tipPlateType):
        self.location = Location(grid,site)
        self.tipPlateType = tipPlateType
        self.nextTipFree = 0
    def getFreeTip(self):
        if self.nextTipFree > (self.tipPlateType.columns - 1) * self.tipPlateType.rows - 1:
            print "ERROR: No more free tips!"
            return None
        freeRow = self.nextTipFree / self.tipPlateType.rows + 1
        freeColumn = self.nextTipFree % self.tipPlateType.rows + 1
        self.nextTipFree += 1
        return Tip(self, freeRow, freeColumn)


class EVO:
    def __init__(self):
       self.system = DispatchWithEvents('EVOAPI.System',EVOSystemEvents)
    def logon(self):
        self.system.Logon(WorkTableSettings.username,WorkTableSettings.password,0,WorkTableSettings.isRealRobot)
        while (self.system.GetStatus() & EVOConstants.STATUS_LOADING == EVOConstants.STATUS_LOADING):
            time.sleep(1)
        print "Ready"
    def logoff(self):
        self.system.Logoff()
    def shutdown(self):
	self.logoff()
        self.system.Shutdown()
    def prepareScript(self,scriptName):
        self.scriptID = self.system.PrepareScript(scriptName)
    def startScript(self,scriptName):
        self.scriptID = self.system.PrepareScript(scriptName)
        self.system.Initialize()
        time.sleep(5) #TODO: add correct while loop
        self.system.StartScript(self.scriptID,0,0)
        time.sleep(2) #TODO: add correct loop
    def startInteractive(self):
        self.startScript("InteractiveScript")
        #return EVOScripter(self,True)

class EVOScripter:
    def __init__(self,evo,interactive=False):
        self.interactive = interactive
        self.evo = evo
        if not interactive:
            self.script = Dispatch('EVOAPI.Script')
            self.script.ReadScript("BaseScript.esc")
        else:
            evo.startInteractive()
    def execute(self,command):
        if self.interactive:
            try:
                self.evo.system.ExecuteScriptCommand(command)
            except pythoncom.com_error, (hr, msg, exc, arg):
                print "Exception caught in EVOWare call:"
                print "Attempted to run script command: " + command
        else:
            self.script.AddScriptLine(command)
    def save(self,name):
        self.script.SaveScript(name + ".esc")
    def moveRoMaHome(self):
        self.execute("ROMA(2,80,75,0,0,0,150,1,0);")

    class Helper:
        @staticmethod
        def getTipEncoding(tipNumber):
            return 1 << (tipNumber - 1)

        @staticmethod
        def getMultiTipEncoding(numberOfTips):
            encoding = 0
            for i in range(1,1+numberOfTips):
                encoding += getTipEncoding(i)
            return encoding

        @staticmethod
        def getTipAmountString(tipNumber, amount):
            param = ""
            for i in range(1,13):
                if i == tipNumber:
                    param += '"' + str(amount) + '"'
                else:
                    param += "0"
                if not i == 12:
                    param += ","
            return param

        @staticmethod
        def getWellEncoding(row,column,maxRows,maxColumns):
            selString = '{0:02X}{1:02X}'.format(maxColumns, maxRows)
            
            bitCounter = 0
            bitMask = 0
            for x in range(1,maxColumns+1):
                for y in range(1,maxRows+1):
                    if x == column and y == row:
                        bitMask |= 1 << bitCounter
                    bitCounter += 1
                    if bitCounter > 6:
                        selString += chr(ord('0') + bitMask)
                        bitCounter = 0
                        bitMask = 0
            if bitCounter > 0:
                selString += chr(ord('0') + bitMask)
            return selString
    #end class Helper
        
    def pickUpTips(self,numberOfTips):
        tipEncoding = self.Helper.getMultiTipEncoding(numberOfTips)
        self.execute("GetDITI2(" + tipEncoding + ',"' + WorkTableSettings.tipName +
                     '",1,0,10,70);')
    def wash(numberOfTips):
        tipEncoding = str(self.Helper.getMultiTipEncoding(numberOfTips))
        command = 'Wash(' + tipEncoding + ',' + str(WorkTableSettings.washWasteLocation.grid) + ',' + str(WorkTableSettings.washWasteLocation.site-1) + ',' + \
                str(WorkTableSettings.washCleanerLocation.grid) + ',' + \
                str(WorkTableSettings.washCleanerLocation.site-1) + ',"' + \
                str(WorkTableSettings.wasteVolume) + '",' + str(WorkTableSettings.wasteDelay) + ',"' + str(WorkTableSettings.cleanerVolume) + '",' + \
                str(WorkTableSettings.cleanerDelay) + ',10,70,30,1,0,1000,0);'
        self.execute(command)
    def resetTipCount(self,numberOfTips):
        command = 'Set_DITI_Counter2("' + WorkTableSettings.tipName + '","' + str(WorkTableSettings.ditiLocation.grid) + '","' + str(WorkTableSettings.ditiLocation.site + 1) + '","1",0)'
        self.execute(command)
    def dropTips(self,numberOfTips):
        tipEncoding = self.Helper.getMultiTipEncoding(numberOfTips)
        self.execute("DropDITI(" + tipEncoding + ',"' + str(WorkTableSettings.wasteLocation.grid) + ',' + str(WorkTableSettings.washLocation.site - 1) + '",10,70,0);')
    #putDITIsBack
    def aspirate(self,tipNumber, grid, site, row, column, liquidClass, amount):
        command = 'Aspirate(' + str(self.Helper.getTipEncoding(tipNumber)) + ',"' + \
            liquidClass + '",' + self.Helper.getTipAmountString(tipNumber, amount) + ',' + \
            str(grid) + ',' + str(site) + ',1,"' + self.Helper.getWellEncoding(row, column, 8, 12) + \
            '",0,0);'
        self.execute(command)

    def dispense(self,tipNumber, grid, site, row, column, liquidClass, amount):
        command = 'Dispense(' + str(self.Helper.getTipEncoding(tipNumber)) + ',"' + \
            liquidClass + '",' + self.Helper.getTipAmountString(tipNumber, amount) + ',' + \
            str(grid) + ',' + str(site) + ',1,"' + self.Helper.getWellEncoding(row, column, 8, 12) + \
            '",0,0);'
        self.execute(command)

    def pickUpDITIs(self,tipNumber, grid, site, row, column, ditiname):
        command = 'PickUp_DITIs2(' + str(self.Helper.getTipEncoding(tipNumber)) + ',' + str(grid) + ',' + str(site) + \
            ',"' + self.Helper.getWellEncoding(row, column, 8, 12) + '",0,' + ditiname + ',0);'
        self.execute(command)
    def setDITIsBack(self,tipNumber, grid, site, row, column):
        command = 'Set_DITIs_Back(' + str(self.Helper.getTipEncoding(tipNumber)) + ',' + str(grid) + ',' + str(site) + \
            ',"' + self.Helper.getWellEncoding(row, column, 8, 12) + '",0,0);'
        self.execute(command)

    def transferRackFromHotel(self,sourceGrid,sourceSite,destGrid,destSite,rackType):
        command = 'Transfer_Rack("' + str(sourceGrid) + '","' + str(destGrid) + '",0,0,0,0,0,"","' + str(rackType) + '","Narrow","","","Hotel 9Pos Microplate","","MP 3Pos Flat","' + str(sourceSite) + '","(Not defined)","' + str(destSite + 1) + '");'
        self.execute(command)
    def transferRacktoHotel(self,sourceGrid,sourceSite,destGrid,destSite,rackType):
        command = 'Transfer_Rack("' + str(sourceGrid) + '","' + str(destGrid) + '",0,0,0,0,0,"","' + str(rackType) + '","Narrow","","","MP 3Pos Flat,"","Hotel 9Pos Microplate","' + str(sourceSite+1) + '","(Not defined)","' + str(destSite) + '");'
        self.execute(command)

class RobotScripter:
    def __init__(self,evo,interactive=False):
        self.evoScripter = EVOScripter(evo,interactive)
        self.nextWorkPlateLocFree = 0

    def aspirate(self,tipNumber, well, amount):
        liquidClass = "training"
        plateLocation = well.plate.location
        self.evoScripter.aspirate(tipNumber, plateLocation.grid, plateLocation.site, well.row, well.column, liquidClass, amount)
    def dispense(self,tipNumber, well, amount):
        liquidClass = "training"
        plateLocation = well.plate.location
        self.evoScripter.dispense(tipNumber, plateLocation.grid, plateLocation.site, well.row, well.column, liquidClass, amount)
    def pipetteMix(self, tipNumber, well, amount, numTimes):
        for i in range(0,numTimes):
            self.aspirate(tipNumber, well, amount)
            self.dispense(tipNumber, well, amount)

    def pickUpTip(self, tipNumber, tip):
        tipPlateLocation = tip.tipPlate.location
        self.evoScripter.pickUpDITIs(tipNumber, tipPlateLocation.grid, tipPlateLocation.site, tip.row, tip.column, tip.tipPlate.tipPlateType.name)
        tip.pickedUp = True

    def setBackTip(self, tipNumber, tip):
        tipPlateLocation = tip.tipPlate.location
        self.evoScripter.setDITIsBack(tipNumber, tipPlateLocation.grid, tipPlateLocation.site, tip.row, tip.column)
        tip.pickedUp = True

class WorkTableSettings:
    username = "teacan"
    password = "teacan"
    isRealRobot = 1

    #parameters
    liquidClass = "training"
    wasteVolume = 3.0
    wasteDelay = 500
    cleanerVolume = 4.0
    cleanerDelay = 500

    #locations - (grid,site)
    workPlate = Plate(16,1,PlateTypes.P96WellEppendorf)
    wasteLocation = Location(3,4)
    washWasteLocation = Location(1,2)
    washCleanerLocation = Location(1,1)
    ditiLocation = TipPlate(3,0,TipPlateTypes.DiTi1000ul)

