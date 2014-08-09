# -*- coding: mbcs -*-
# Created by makepy.py version 0.5.00
# By python version 2.7.1 (r271:86832, Nov 27 2010, 18:30:46) [MSC v.1500 32 bit (Intel)]
# From type library 'Evoapi.exe'
# On Tue Mar 15 22:09:16 2011
"""Evoapi 1.0 Type Library"""
makepy_version = '0.5.00'
python_version = 0x20701f0

import win32com.client.CLSIDToClass, pythoncom, pywintypes
import win32com.client.util
from pywintypes import IID
from win32com.client import Dispatch

# The following 3 lines may need tweaking for the particular server
# Candidates are pythoncom.Missing, .Empty and .ArgNotFound
defaultNamedOptArg=pythoncom.Empty
defaultNamedNotOptArg=pythoncom.Empty
defaultUnnamedArg=pythoncom.Empty

CLSID = IID('{9409CAF9-848C-42E6-BA54-5CF75D813884}')
MajorVersion = 1
MinorVersion = 0
LibraryFlags = 8
LCID = 0x0

class constants:
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

from win32com.client import DispatchBaseClass
class IDatabase(DispatchBaseClass):
	"""IDatabase Interface"""
	CLSID = IID('{575FAB44-765A-4AB3-8983-639C4D1C5D59}')
	coclass_clsid = IID('{D00B09FA-95F6-4A3E-A0D6-E9625C17A0D7}')

	def AddSlot(self, className=defaultNamedNotOptArg, SlotName=defaultNamedNotOptArg, slotType=defaultNamedNotOptArg, slotValue=defaultNamedNotOptArg):
		"""method AddSlot"""
		return self._oleobj_.InvokeTypes(4, LCID, 1, (24, 0), ((8, 1), (8, 1), (8, 1), (8, 1)),className
			, SlotName, slotType, slotValue)

	def FindObjects(self, NameFilter=defaultNamedNotOptArg, SlotFilter=defaultNamedNotOptArg):
		"""Find database objects"""
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(1, LCID, 1, (8, 0), ((8, 1), (8, 1)),NameFilter
			, SlotFilter)

	def GetSlot(self, ObjectName=defaultNamedNotOptArg, SlotName=defaultNamedNotOptArg):
		"""Get slot value"""
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(2, LCID, 1, (8, 0), ((8, 1), (8, 1)),ObjectName
			, SlotName)

	def SetSlot(self, ObjectName=defaultNamedNotOptArg, SlotName=defaultNamedNotOptArg, Value=defaultNamedNotOptArg):
		"""method SetSlot"""
		return self._oleobj_.InvokeTypes(3, LCID, 1, (24, 0), ((8, 1), (8, 1), (8, 1)),ObjectName
			, SlotName, Value)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class IDevice(DispatchBaseClass):
	"""IDevice Interface"""
	CLSID = IID('{B7608A05-B681-42EF-BD69-DFB44A74B5C1}')
	coclass_clsid = IID('{33869BD6-3E45-4632-8938-88C7F138C9D6}')

	def Execute(self, Command=defaultNamedNotOptArg):
		"""Execute command"""
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(2, LCID, 1, (8, 0), ((8, 1),),Command
			)

	def GetDriverVersion(self):
		"""Get driver version info"""
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(1, LCID, 1, (8, 0), (),)

	def GetName(self):
		"""Get device name"""
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(3, LCID, 1, (8, 0), (),)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class IMCSRcvr(DispatchBaseClass):
	"""IMCSRcvr Interface"""
	CLSID = IID('{CF126D49-9F4D-4257-8B8B-F4C759CD0469}')
	coclass_clsid = IID('{C52BA4FE-30BC-42CA-9AB2-4D249FD77FE1}')

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class IPlannerEvent(DispatchBaseClass):
	"""IPlannerEvent Interface"""
	CLSID = IID('{F9468956-F5B8-4275-8F1B-62FD41967B7C}')
	coclass_clsid = IID('{194E08AF-FA21-4DA1-8342-9AF11D274244}')

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class IScript(DispatchBaseClass):
	"""IScript Interface"""
	CLSID = IID('{F18E7145-FE6F-41EE-A374-E4AB6B846A15}')
	coclass_clsid = IID('{95173C7F-BC29-4809-9729-622F4A4CC01C}')

	def AddCarrier(self, CarrierName=defaultNamedNotOptArg, gridNo=defaultNamedNotOptArg):
		"""method AddCarrier"""
		return self._oleobj_.InvokeTypes(4, LCID, 1, (24, 0), ((8, 0), (3, 0)),CarrierName
			, gridNo)

	def AddLabware(self, rackName=defaultNamedNotOptArg, gridNo=defaultNamedNotOptArg, siteNo=defaultNamedNotOptArg, rackLabel=defaultNamedNotOptArg):
		"""method AddLabware"""
		return self._oleobj_.InvokeTypes(5, LCID, 1, (24, 0), ((8, 0), (3, 0), (3, 0), (8, 0)),rackName
			, gridNo, siteNo, rackLabel)

	def AddScriptLine(self, scriptLine=defaultNamedNotOptArg):
		"""method AddScriptLine"""
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((8, 0),),scriptLine
			)

	def ReadScript(self, scriptName=defaultNamedNotOptArg):
		"""method ReadScript"""
		return self._oleobj_.InvokeTypes(2, LCID, 1, (24, 0), ((8, 1),),scriptName
			)

	def RemoveCarrier(self, gridNo=defaultNamedNotOptArg):
		"""method RemoveCarrier"""
		return self._oleobj_.InvokeTypes(9, LCID, 1, (24, 0), ((3, 0),),gridNo
			)

	def RemoveLabware(self, gridNo=defaultNamedNotOptArg, siteNo=defaultNamedNotOptArg):
		"""method RemoveLabware"""
		return self._oleobj_.InvokeTypes(7, LCID, 1, (24, 0), ((3, 0), (3, 0)),gridNo
			, siteNo)

	def RemoveLabwareByLabel(self, labwareLabel=defaultNamedNotOptArg):
		"""method RemoveLabwareByLabel"""
		return self._oleobj_.InvokeTypes(8, LCID, 1, (24, 0), ((8, 1),),labwareLabel
			)

	def SaveScript(self, fileName=defaultNamedNotOptArg):
		"""method SaveScript"""
		return self._oleobj_.InvokeTypes(10, LCID, 1, (24, 0), ((8, 1),),fileName
			)

	def SetLabwareLabel(self, gridNo=defaultNamedNotOptArg, siteNo=defaultNamedNotOptArg, newLabel=defaultNamedNotOptArg):
		"""method SetLabwareLabel"""
		return self._oleobj_.InvokeTypes(6, LCID, 1, (24, 0), ((3, 0), (3, 0), (8, 0)),gridNo
			, siteNo, newLabel)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class ISystem(DispatchBaseClass):
	"""ISystem Interface"""
	CLSID = IID('{134BAC43-378A-4994-91C4-9231076E8DED}')
	coclass_clsid = IID('{E15F0BB3-770C-4E29-8DC8-BABA6E424E8C}')

	def CancelProcess(self, ProcessID=defaultNamedNotOptArg):
		"""Cancel process"""
		return self._oleobj_.InvokeTypes(10, LCID, 1, (24, 0), ((3, 1),),ProcessID
			)

	def ExecuteScriptCommand(self, bstrCommand=defaultNamedNotOptArg):
		"""Directly execute a script command"""
		return self._oleobj_.InvokeTypes(36, LCID, 1, (24, 0), ((8, 1),),bstrCommand
			)

	# Result is of type IDevice
	def GetDevice(self, Index=defaultNamedNotOptArg):
		"""Get device interface by name or index"""
		ret = self._oleobj_.InvokeTypes(11, LCID, 1, (9, 0), ((12, 1),),Index
			)
		if ret is not None:
			ret = Dispatch(ret, u'GetDevice', '{B7608A05-B681-42EF-BD69-DFB44A74B5C1}')
		return ret

	def GetDeviceCount(self):
		"""Get number of device drivers"""
		return self._oleobj_.InvokeTypes(14, LCID, 1, (3, 0), (),)

	def GetLCCount(self):
		"""Returns the number of liquid classes"""
		return self._oleobj_.InvokeTypes(29, LCID, 1, (3, 0), (),)

	def GetLCInfo(self, Index=defaultNamedNotOptArg, lcName=pythoncom.Missing, isDefault=pythoncom.Missing, isCustomized=pythoncom.Missing):
		"""Gets the liquid class info"""
		return self._ApplyTypes_(30, 1, (24, 0), ((3, 1), (16392, 2), (16395, 2), (16395, 2)), u'GetLCInfo', None,Index
			, lcName, isDefault, isCustomized)

	def GetNumberOfRacks(self, ScriptID=defaultNamedNotOptArg):
		"""Get number of racks used in the script"""
		return self._oleobj_.InvokeTypes(21, LCID, 1, (3, 0), ((3, 1),),ScriptID
			)

	def GetProcessStatus(self, ProcessID=defaultNamedNotOptArg):
		"""Get process status"""
		return self._oleobj_.InvokeTypes(13, LCID, 1, (3, 0), ((3, 1),),ProcessID
			)

	def GetProcessStatusEx(self, ProcessID=defaultNamedNotOptArg):
		"""Get extended process status"""
		return self._oleobj_.InvokeTypes(43, LCID, 1, (3, 0), ((3, 1),),ProcessID
			)

	def GetProcessVariable(self, ProcessID=defaultNamedNotOptArg, VariableName=defaultNamedNotOptArg, Scope=defaultNamedNotOptArg):
		"""method GetProcessVariable"""
		return self._ApplyTypes_(26, 1, (12, 0), ((3, 1), (8, 1), (3, 1)), u'GetProcessVariable', None,ProcessID
			, VariableName, Scope)

	def GetRack(self, ScriptID=defaultNamedNotOptArg, Index=defaultNamedNotOptArg, Name=pythoncom.Missing, Label=pythoncom.Missing
			, Location=pythoncom.Missing, Grid=pythoncom.Missing, Site=pythoncom.Missing, CarrierName=pythoncom.Missing):
		"""Get rack info"""
		return self._ApplyTypes_(22, 1, (24, 0), ((3, 1), (3, 1), (16392, 2), (16392, 2), (16387, 2), (16387, 2), (16387, 2), (16392, 2)), u'GetRack', None,ScriptID
			, Index, Name, Label, Location, Grid
			, Site, CarrierName)

	def GetScriptStatus(self, ScriptID=defaultNamedNotOptArg):
		"""Get script status"""
		return self._oleobj_.InvokeTypes(12, LCID, 1, (3, 0), ((3, 1),),ScriptID
			)

	def GetScriptStatusEx(self, ScriptID=0):
		"""Get extended script status"""
		return self._oleobj_.InvokeTypes(42, LCID, 1, (3, 0), ((3, 49),),ScriptID
			)

	def GetScriptVariable(self, ScriptID=defaultNamedNotOptArg, VariableName=defaultNamedNotOptArg):
		"""method GetScriptVariable"""
		return self._ApplyTypes_(27, 1, (12, 0), ((3, 1), (8, 1)), u'GetScriptVariable', None,ScriptID
			, VariableName)

	def GetStatus(self):
		"""method GetStatus"""
		return self._oleobj_.InvokeTypes(28, LCID, 1, (3, 0), (),)

	def GetSubLCCount(self, Index=defaultNamedNotOptArg):
		"""Returns the count of sub-liquid classes of a liquid class"""
		return self._oleobj_.InvokeTypes(31, LCID, 1, (3, 0), ((3, 1),),Index
			)

	def GetSubLCInfo(self, lcIndex=defaultNamedNotOptArg, subLCIndex=defaultNamedNotOptArg, tipType=pythoncom.Missing, isAllVolumes=pythoncom.Missing
			, minVolume=pythoncom.Missing, maxVolume=pythoncom.Missing):
		"""Gets the sub-liquid class info"""
		return self._ApplyTypes_(32, 1, (24, 0), ((3, 1), (3, 1), (16387, 2), (16395, 2), (16389, 2), (16389, 2)), u'GetSubLCInfo', None,lcIndex
			, subLCIndex, tipType, isAllVolumes, minVolume, maxVolume
			)

	def GetSystemInfo(self, bRunningInPlusMode=pythoncom.Missing, bRunningInSimulationMode=pythoncom.Missing, strSoftwareVersionNumber=u'0', strInstrumentSerialNumber=u'0'):
		"""Get system information"""
		return self._ApplyTypes_(41, 1, (24, 32), ((16395, 2), (16395, 2), (16392, 50), (16392, 50)), u'GetSystemInfo', None,bRunningInPlusMode
			, bRunningInSimulationMode, strSoftwareVersionNumber, strInstrumentSerialNumber)

	def GetWindowHandles(self, MainWinHandle=pythoncom.Missing, ScriptWinHandle=pythoncom.Missing, WorktableWinHandle=pythoncom.Missing, LogWinHandle=pythoncom.Missing):
		"""method GetWindowHandles"""
		return self._ApplyTypes_(34, 1, (24, 0), ((16387, 2), (16387, 2), (16387, 2), (16387, 2)), u'GetWindowHandles', None,MainWinHandle
			, ScriptWinHandle, WorktableWinHandle, LogWinHandle)

	def HideGUI(self, Hide=defaultNamedNotOptArg):
		"""Show/Hide user interface"""
		return self._oleobj_.InvokeTypes(18, LCID, 1, (24, 0), ((3, 1),),Hide
			)

	def Initialize(self):
		"""Initialize device drivers"""
		return self._oleobj_.InvokeTypes(8, LCID, 1, (24, 0), (),)

	def Logoff(self):
		"""Log off"""
		return self._oleobj_.InvokeTypes(25, LCID, 1, (24, 0), (),)

	def Logon(self, UserName=defaultNamedNotOptArg, Password=defaultNamedNotOptArg, Plus=defaultNamedNotOptArg, Simulation=defaultNamedNotOptArg):
		"""Log on"""
		return self._oleobj_.InvokeTypes(24, LCID, 1, (24, 0), ((8, 1), (8, 1), (3, 1), (3, 1)),UserName
			, Password, Plus, Simulation)

	def Pause(self):
		"""Pause system"""
		return self._oleobj_.InvokeTypes(5, LCID, 1, (24, 0), (),)

	def PrepareProcess(self, ProcessName=defaultNamedNotOptArg):
		"""Prepare system to start a process"""
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((8, 1),),ProcessName
			)

	def PrepareScript(self, scriptName=defaultNamedNotOptArg):
		"""Prepare a script for execution"""
		return self._oleobj_.InvokeTypes(3, LCID, 1, (3, 0), ((8, 1),),scriptName
			)

	def ReadLiquidClasses(self):
		"""Reloads liquid classes database"""
		return self._oleobj_.InvokeTypes(33, LCID, 1, (24, 0), (),)

	def ResetStoredADHInfo(self):
		"""Reset stored automatic DiTi handling information"""
		return self._oleobj_.InvokeTypes(40, LCID, 1, (24, 0), (),)

	def Resume(self):
		"""Resume after system has been paused"""
		return self._oleobj_.InvokeTypes(6, LCID, 1, (24, 0), (),)

	def SetDoorLocks(self, Close=defaultNamedNotOptArg):
		"""Open/close door locks"""
		return self._oleobj_.InvokeTypes(17, LCID, 1, (24, 0), ((3, 1),),Close
			)

	def SetLamp(self, Status=defaultNamedNotOptArg):
		"""method SetLamp"""
		return self._oleobj_.InvokeTypes(16, LCID, 1, (24, 0), ((3, 1),),Status
			)

	def SetProcessVariable(self, ProcessID=defaultNamedNotOptArg, VariableName=defaultNamedNotOptArg, Scope=defaultNamedNotOptArg, Value=defaultNamedNotOptArg):
		"""Set script variable"""
		return self._oleobj_.InvokeTypes(19, LCID, 1, (24, 0), ((3, 1), (8, 1), (3, 1), (12, 1)),ProcessID
			, VariableName, Scope, Value)

	def SetRack(self, ScriptID=defaultNamedNotOptArg, Index=defaultNamedNotOptArg, Location=defaultNamedNotOptArg, Barcode=defaultNamedNotOptArg):
		"""Set rack info"""
		return self._oleobj_.InvokeTypes(23, LCID, 1, (24, 0), ((3, 1), (3, 1), (3, 1), (8, 1)),ScriptID
			, Index, Location, Barcode)

	def SetRemoteMode(self, Enable=defaultNamedNotOptArg):
		"""Set remote mode on/off"""
		return self._oleobj_.InvokeTypes(15, LCID, 1, (24, 0), ((3, 1),),Enable
			)

	def SetScriptVariable(self, ScriptID=defaultNamedNotOptArg, VariableName=defaultNamedNotOptArg, Value=defaultNamedNotOptArg):
		"""Set value of a script variable"""
		return self._oleobj_.InvokeTypes(20, LCID, 1, (24, 0), ((3, 1), (8, 1), (12, 1)),ScriptID
			, VariableName, Value)

	def Shutdown(self):
		"""Shutdown device drivers"""
		return self._oleobj_.InvokeTypes(9, LCID, 1, (24, 0), (),)

	def StartADH(self):
		"""Start automatic DiTi handling"""
		return self._oleobj_.InvokeTypes(39, LCID, 1, (24, 0), (),)

	def StartADHLoadProcess(self, Emergency=1):
		"""Start initial load processes for automatic DiTi handling"""
		return self._oleobj_.InvokeTypes(37, LCID, 1, (24, 0), ((3, 49),),Emergency
			)

	def StartADHUnloadProcess(self):
		"""Start automatic DiTi handling unload process"""
		return self._oleobj_.InvokeTypes(38, LCID, 1, (24, 0), (),)

	def StartProcess(self, ProcessName=defaultNamedNotOptArg, Objects=defaultNamedNotOptArg, Priority=0, Emergency=0):
		"""Start one process"""
		return self._oleobj_.InvokeTypes(2, LCID, 1, (3, 0), ((8, 1), (8, 1), (2, 49), (3, 49)),ProcessName
			, Objects, Priority, Emergency)

	def StartScript(self, ScriptID=defaultNamedNotOptArg, StartLine=0, EndLine=0):
		"""Start script"""
		return self._oleobj_.InvokeTypes(4, LCID, 1, (24, 0), ((3, 1), (2, 49), (2, 49)),ScriptID
			, StartLine, EndLine)

	def Stop(self):
		"""Stop system"""
		return self._oleobj_.InvokeTypes(7, LCID, 1, (24, 0), (),)

	def WriteToTraceFile(self, bstrTrace=defaultNamedNotOptArg):
		"""Write a entry to the trace file"""
		return self._oleobj_.InvokeTypes(35, LCID, 1, (24, 0), ((8, 1),),bstrTrace
			)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}

class _IDatabaseEvents:
	"""_IDatabaseEvents Interface"""
	CLSID = CLSID_Sink = IID('{2EB1BBD0-9611-4574-8AA9-8F49E3FCCCF9}')
	coclass_clsid = IID('{D00B09FA-95F6-4A3E-A0D6-E9625C17A0D7}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:


class _IDeviceEvents:
	"""_IDeviceEvents Interface"""
	CLSID = CLSID_Sink = IID('{411B7705-5E52-4FE7-89CF-9A115D8EB871}')
	coclass_clsid = IID('{33869BD6-3E45-4632-8938-88C7F138C9D6}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:


class _IMCSRcvrEvents:
	"""_IMCSRcvrEvents Interface"""
	CLSID = CLSID_Sink = IID('{04DF064E-DDEB-49C8-A0F9-C2A1B6A60662}')
	coclass_clsid = IID('{C52BA4FE-30BC-42CA-9AB2-4D249FD77FE1}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:


class _IPlannerEventEvents:
	"""_IPlannerEventEvents Interface"""
	CLSID = CLSID_Sink = IID('{F8F837D9-AE56-4BFA-A34A-BC3F81ADEA90}')
	coclass_clsid = IID('{194E08AF-FA21-4DA1-8342-9AF11D274244}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:


class _IScriptEvents:
	"""_IScriptEvents Interface"""
	CLSID = CLSID_Sink = IID('{8C765062-9BA9-4D02-9AE1-30B8AC7088EA}')
	coclass_clsid = IID('{95173C7F-BC29-4809-9729-622F4A4CC01C}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:


class _ISystemEvents:
	"""_ISystemEvents Interface"""
	CLSID = CLSID_Sink = IID('{10BCAEAE-BA76-4D5B-971A-66A45F5382E5}')
	coclass_clsid = IID('{E15F0BB3-770C-4E29-8DC8-BABA6E424E8C}')
	_public_methods_ = [] # For COM Server support
	_dispid_to_func_ = {
		        4 : "OnStatusChanged",
		        1 : "OnErrorEvent",
		        2 : "OnUserPromptEvent",
		        3 : "OnLogonTimeoutEvent",
		}

	def __init__(self, oobj = None):
		if oobj is None:
			self._olecp = None
		else:
			import win32com.server.util
			from win32com.server.policy import EventHandlerPolicy
			cpc=oobj._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer)
			cp=cpc.FindConnectionPoint(self.CLSID_Sink)
			cookie=cp.Advise(win32com.server.util.wrap(self, usePolicy=EventHandlerPolicy))
			self._olecp,self._olecp_cookie = cp,cookie
	def __del__(self):
		try:
			self.close()
		except pythoncom.com_error:
			pass
	def close(self):
		if self._olecp is not None:
			cp,cookie,self._olecp,self._olecp_cookie = self._olecp,self._olecp_cookie,None,None
			cp.Unadvise(cookie)
	def _query_interface_(self, iid):
		import win32com.server.util
		if iid==self.CLSID_Sink: return win32com.server.util.wrap(self)

	# Event Handlers
	# If you create handlers, they should have the following prototypes:
#	def OnStatusChanged(self, Status=defaultNamedNotOptArg):
#		"""method StatusChanged"""
#	def OnErrorEvent(self, StartTime=defaultNamedNotOptArg, EndTime=defaultNamedNotOptArg, Device=defaultNamedNotOptArg, Macro=defaultNamedNotOptArg
#			, Object=defaultNamedNotOptArg, Message=defaultNamedNotOptArg, Status=defaultNamedNotOptArg, ProcessName=defaultNamedNotOptArg, ProcessID=defaultNamedNotOptArg
#			, MacroID=defaultNamedNotOptArg):
#		"""method ErrorEvent"""
#	def OnUserPromptEvent(self, ID=defaultNamedNotOptArg, Text=defaultNamedNotOptArg, Caption=defaultNamedNotOptArg, Choices=defaultNamedNotOptArg
#			, Answer=pythoncom.Missing):
#		"""Raised when a user prompt is to be opened."""
#	def OnLogonTimeoutEvent(self):
#		"""Logon time has expired"""


from win32com.client import CoClassBaseClass
# This CoClass is known by the name 'Evoapi.Database.1'
class Database(CoClassBaseClass): # A CoClass
	# Database Class
	CLSID = IID('{D00B09FA-95F6-4A3E-A0D6-E9625C17A0D7}')
	coclass_sources = [
		_IDatabaseEvents,
	]
	default_source = _IDatabaseEvents
	coclass_interfaces = [
		IDatabase,
	]
	default_interface = IDatabase

# This CoClass is known by the name 'Evoapi.Device.1'
class Device(CoClassBaseClass): # A CoClass
	# Device Class
	CLSID = IID('{33869BD6-3E45-4632-8938-88C7F138C9D6}')
	coclass_sources = [
		_IDeviceEvents,
	]
	default_source = _IDeviceEvents
	coclass_interfaces = [
		IDevice,
	]
	default_interface = IDevice

# This CoClass is known by the name 'Evoapi.MCSRcvr.1'
class MCSRcvr(CoClassBaseClass): # A CoClass
	# MCSRcvr Class
	CLSID = IID('{C52BA4FE-30BC-42CA-9AB2-4D249FD77FE1}')
	coclass_sources = [
		_IMCSRcvrEvents,
	]
	default_source = _IMCSRcvrEvents
	coclass_interfaces = [
		IMCSRcvr,
	]
	default_interface = IMCSRcvr

# This CoClass is known by the name 'Evoapi.PlannerEvent.1'
class PlannerEvent(CoClassBaseClass): # A CoClass
	# PlannerEvent Class
	CLSID = IID('{194E08AF-FA21-4DA1-8342-9AF11D274244}')
	coclass_sources = [
		_IPlannerEventEvents,
	]
	default_source = _IPlannerEventEvents
	coclass_interfaces = [
		IPlannerEvent,
	]
	default_interface = IPlannerEvent

# This CoClass is known by the name 'Evoapi.Script.1'
class Script(CoClassBaseClass): # A CoClass
	# Script Class
	CLSID = IID('{95173C7F-BC29-4809-9729-622F4A4CC01C}')
	coclass_sources = [
		_IScriptEvents,
	]
	default_source = _IScriptEvents
	coclass_interfaces = [
		IScript,
	]
	default_interface = IScript

# This CoClass is known by the name 'Evoapi.System.1'
class System(CoClassBaseClass): # A CoClass
	# System Class
	CLSID = IID('{E15F0BB3-770C-4E29-8DC8-BABA6E424E8C}')
	coclass_sources = [
		_ISystemEvents,
	]
	default_source = _ISystemEvents
	coclass_interfaces = [
		ISystem,
	]
	default_interface = ISystem

IDatabase_vtables_dispatch_ = 1
IDatabase_vtables_ = [
	(( u'FindObjects' , u'NameFilter' , u'SlotFilter' , u'ObjectList' , ), 1, (1, (), [ 
			(8, 1, None, None) , (8, 1, None, None) , (16392, 10, None, None) , ], 1 , 1 , 4 , 0 , 28 , (3, 0, None, None) , 0 , )),
	(( u'GetSlot' , u'ObjectName' , u'SlotName' , u'Value' , ), 2, (2, (), [ 
			(8, 1, None, None) , (8, 1, None, None) , (16392, 10, None, None) , ], 1 , 1 , 4 , 0 , 32 , (3, 0, None, None) , 0 , )),
	(( u'SetSlot' , u'ObjectName' , u'SlotName' , u'Value' , ), 3, (3, (), [ 
			(8, 1, None, None) , (8, 1, None, None) , (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 36 , (3, 0, None, None) , 0 , )),
	(( u'AddSlot' , u'className' , u'SlotName' , u'slotType' , u'slotValue' , 
			), 4, (4, (), [ (8, 1, None, None) , (8, 1, None, None) , (8, 1, None, None) , (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 40 , (3, 0, None, None) , 0 , )),
]

IDevice_vtables_dispatch_ = 1
IDevice_vtables_ = [
	(( u'GetDriverVersion' , u'VersionInfo' , ), 1, (1, (), [ (16392, 10, None, None) , ], 1 , 1 , 4 , 0 , 28 , (3, 0, None, None) , 0 , )),
	(( u'Execute' , u'Command' , u'Result' , ), 2, (2, (), [ (8, 1, None, None) , 
			(16392, 10, None, None) , ], 1 , 1 , 4 , 0 , 32 , (3, 0, None, None) , 0 , )),
	(( u'GetName' , u'Name' , ), 3, (3, (), [ (16392, 10, None, None) , ], 1 , 1 , 4 , 0 , 36 , (3, 0, None, None) , 0 , )),
]

IMCSRcvr_vtables_dispatch_ = 1
IMCSRcvr_vtables_ = [
]

IPlannerEvent_vtables_dispatch_ = 1
IPlannerEvent_vtables_ = [
]

IScript_vtables_dispatch_ = 1
IScript_vtables_ = [
	(( u'AddScriptLine' , u'scriptLine' , ), 1, (1, (), [ (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 28 , (3, 0, None, None) , 0 , )),
	(( u'ReadScript' , u'scriptName' , ), 2, (2, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 32 , (3, 0, None, None) , 0 , )),
	(( u'AddCarrier' , u'CarrierName' , u'gridNo' , ), 4, (4, (), [ (8, 0, None, None) , 
			(3, 0, None, None) , ], 1 , 1 , 4 , 0 , 36 , (3, 0, None, None) , 0 , )),
	(( u'AddLabware' , u'rackName' , u'gridNo' , u'siteNo' , u'rackLabel' , 
			), 5, (5, (), [ (8, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 40 , (3, 0, None, None) , 0 , )),
	(( u'SetLabwareLabel' , u'gridNo' , u'siteNo' , u'newLabel' , ), 6, (6, (), [ 
			(3, 0, None, None) , (3, 0, None, None) , (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 44 , (3, 0, None, None) , 0 , )),
	(( u'RemoveLabware' , u'gridNo' , u'siteNo' , ), 7, (7, (), [ (3, 0, None, None) , 
			(3, 0, None, None) , ], 1 , 1 , 4 , 0 , 48 , (3, 0, None, None) , 0 , )),
	(( u'RemoveLabwareByLabel' , u'labwareLabel' , ), 8, (8, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 52 , (3, 0, None, None) , 0 , )),
	(( u'RemoveCarrier' , u'gridNo' , ), 9, (9, (), [ (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
	(( u'SaveScript' , u'fileName' , ), 10, (10, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 60 , (3, 0, None, None) , 0 , )),
]

ISystem_vtables_dispatch_ = 1
ISystem_vtables_ = [
	(( u'PrepareProcess' , u'ProcessName' , ), 1, (1, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 28 , (3, 0, None, None) , 0 , )),
	(( u'StartProcess' , u'ProcessName' , u'Objects' , u'Priority' , u'Emergency' , 
			u'ProcessID' , ), 2, (2, (), [ (8, 1, None, None) , (8, 1, None, None) , (2, 49, '0', None) , 
			(3, 49, '0', None) , (16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 32 , (3, 0, None, None) , 0 , )),
	(( u'PrepareScript' , u'scriptName' , u'ScriptID' , ), 3, (3, (), [ (8, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 36 , (3, 0, None, None) , 0 , )),
	(( u'StartScript' , u'ScriptID' , u'StartLine' , u'EndLine' , ), 4, (4, (), [ 
			(3, 1, None, None) , (2, 49, '0', None) , (2, 49, '0', None) , ], 1 , 1 , 4 , 0 , 40 , (3, 0, None, None) , 0 , )),
	(( u'Pause' , ), 5, (5, (), [ ], 1 , 1 , 4 , 0 , 44 , (3, 0, None, None) , 0 , )),
	(( u'Resume' , ), 6, (6, (), [ ], 1 , 1 , 4 , 0 , 48 , (3, 0, None, None) , 0 , )),
	(( u'Stop' , ), 7, (7, (), [ ], 1 , 1 , 4 , 0 , 52 , (3, 0, None, None) , 0 , )),
	(( u'Initialize' , ), 8, (8, (), [ ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
	(( u'Shutdown' , ), 9, (9, (), [ ], 1 , 1 , 4 , 0 , 60 , (3, 0, None, None) , 0 , )),
	(( u'CancelProcess' , u'ProcessID' , ), 10, (10, (), [ (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 64 , (3, 0, None, None) , 0 , )),
	(( u'GetDevice' , u'Index' , u'Device' , ), 11, (11, (), [ (12, 1, None, None) , 
			(16393, 10, None, "IID('{B7608A05-B681-42EF-BD69-DFB44A74B5C1}')") , ], 1 , 1 , 4 , 0 , 68 , (3, 0, None, None) , 0 , )),
	(( u'GetScriptStatus' , u'ScriptID' , u'Status' , ), 12, (12, (), [ (3, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 72 , (3, 0, None, None) , 0 , )),
	(( u'GetProcessStatus' , u'ProcessID' , u'Status' , ), 13, (13, (), [ (3, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 76 , (3, 0, None, None) , 0 , )),
	(( u'GetDeviceCount' , u'Count' , ), 14, (14, (), [ (16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 80 , (3, 0, None, None) , 0 , )),
	(( u'SetRemoteMode' , u'Enable' , ), 15, (15, (), [ (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 84 , (3, 0, None, None) , 0 , )),
	(( u'SetLamp' , u'Status' , ), 16, (16, (), [ (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 88 , (3, 0, None, None) , 0 , )),
	(( u'SetDoorLocks' , u'Close' , ), 17, (17, (), [ (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 92 , (3, 0, None, None) , 0 , )),
	(( u'HideGUI' , u'Hide' , ), 18, (18, (), [ (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 96 , (3, 0, None, None) , 0 , )),
	(( u'SetProcessVariable' , u'ProcessID' , u'VariableName' , u'Scope' , u'Value' , 
			), 19, (19, (), [ (3, 1, None, None) , (8, 1, None, None) , (3, 1, None, None) , (12, 1, None, None) , ], 1 , 1 , 4 , 0 , 100 , (3, 0, None, None) , 0 , )),
	(( u'SetScriptVariable' , u'ScriptID' , u'VariableName' , u'Value' , ), 20, (20, (), [ 
			(3, 1, None, None) , (8, 1, None, None) , (12, 1, None, None) , ], 1 , 1 , 4 , 0 , 104 , (3, 0, None, None) , 0 , )),
	(( u'GetNumberOfRacks' , u'ScriptID' , u'Count' , ), 21, (21, (), [ (3, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 108 , (3, 0, None, None) , 0 , )),
	(( u'GetRack' , u'ScriptID' , u'Index' , u'Name' , u'Label' , 
			u'Location' , u'Grid' , u'Site' , u'CarrierName' , ), 22, (22, (), [ 
			(3, 1, None, None) , (3, 1, None, None) , (16392, 2, None, None) , (16392, 2, None, None) , (16387, 2, None, None) , 
			(16387, 2, None, None) , (16387, 2, None, None) , (16392, 2, None, None) , ], 1 , 1 , 4 , 0 , 112 , (3, 0, None, None) , 0 , )),
	(( u'SetRack' , u'ScriptID' , u'Index' , u'Location' , u'Barcode' , 
			), 23, (23, (), [ (3, 1, None, None) , (3, 1, None, None) , (3, 1, None, None) , (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 116 , (3, 0, None, None) , 0 , )),
	(( u'Logon' , u'UserName' , u'Password' , u'Plus' , u'Simulation' , 
			), 24, (24, (), [ (8, 1, None, None) , (8, 1, None, None) , (3, 1, None, None) , (3, 1, None, None) , ], 1 , 1 , 4 , 0 , 120 , (3, 0, None, None) , 0 , )),
	(( u'Logoff' , ), 25, (25, (), [ ], 1 , 1 , 4 , 0 , 124 , (3, 0, None, None) , 0 , )),
	(( u'GetProcessVariable' , u'ProcessID' , u'VariableName' , u'Scope' , u'Value' , 
			), 26, (26, (), [ (3, 1, None, None) , (8, 1, None, None) , (3, 1, None, None) , (16396, 10, None, None) , ], 1 , 1 , 4 , 0 , 128 , (3, 0, None, None) , 0 , )),
	(( u'GetScriptVariable' , u'ScriptID' , u'VariableName' , u'Value' , ), 27, (27, (), [ 
			(3, 1, None, None) , (8, 1, None, None) , (16396, 10, None, None) , ], 1 , 1 , 4 , 0 , 132 , (3, 0, None, None) , 0 , )),
	(( u'GetStatus' , u'Status' , ), 28, (28, (), [ (16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 136 , (3, 0, None, None) , 0 , )),
	(( u'GetLCCount' , u'lcCount' , ), 29, (29, (), [ (16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 140 , (3, 0, None, None) , 0 , )),
	(( u'GetLCInfo' , u'Index' , u'lcName' , u'isDefault' , u'isCustomized' , 
			), 30, (30, (), [ (3, 1, None, None) , (16392, 2, None, None) , (16395, 2, None, None) , (16395, 2, None, None) , ], 1 , 1 , 4 , 0 , 144 , (3, 0, None, None) , 0 , )),
	(( u'GetSubLCCount' , u'Index' , u'subLCCount' , ), 31, (31, (), [ (3, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 148 , (3, 0, None, None) , 0 , )),
	(( u'GetSubLCInfo' , u'lcIndex' , u'subLCIndex' , u'tipType' , u'isAllVolumes' , 
			u'minVolume' , u'maxVolume' , ), 32, (32, (), [ (3, 1, None, None) , (3, 1, None, None) , 
			(16387, 2, None, None) , (16395, 2, None, None) , (16389, 2, None, None) , (16389, 2, None, None) , ], 1 , 1 , 4 , 0 , 152 , (3, 0, None, None) , 0 , )),
	(( u'ReadLiquidClasses' , ), 33, (33, (), [ ], 1 , 1 , 4 , 0 , 156 , (3, 0, None, None) , 0 , )),
	(( u'GetWindowHandles' , u'MainWinHandle' , u'ScriptWinHandle' , u'WorktableWinHandle' , u'LogWinHandle' , 
			), 34, (34, (), [ (16387, 2, None, None) , (16387, 2, None, None) , (16387, 2, None, None) , (16387, 2, None, None) , ], 1 , 1 , 4 , 0 , 160 , (3, 0, None, None) , 0 , )),
	(( u'WriteToTraceFile' , u'bstrTrace' , ), 35, (35, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 164 , (3, 0, None, None) , 0 , )),
	(( u'ExecuteScriptCommand' , u'bstrCommand' , ), 36, (36, (), [ (8, 1, None, None) , ], 1 , 1 , 4 , 0 , 168 , (3, 0, None, None) , 0 , )),
	(( u'StartADHLoadProcess' , u'Emergency' , ), 37, (37, (), [ (3, 49, '1', None) , ], 1 , 1 , 4 , 0 , 172 , (3, 0, None, None) , 0 , )),
	(( u'StartADHUnloadProcess' , ), 38, (38, (), [ ], 1 , 1 , 4 , 0 , 176 , (3, 0, None, None) , 0 , )),
	(( u'StartADH' , ), 39, (39, (), [ ], 1 , 1 , 4 , 0 , 180 , (3, 0, None, None) , 0 , )),
	(( u'ResetStoredADHInfo' , ), 40, (40, (), [ ], 1 , 1 , 4 , 0 , 184 , (3, 0, None, None) , 0 , )),
	(( u'GetSystemInfo' , u'bRunningInPlusMode' , u'bRunningInSimulationMode' , u'strSoftwareVersionNumber' , u'strInstrumentSerialNumber' , 
			), 41, (41, (), [ (16395, 2, None, None) , (16395, 2, None, None) , (16392, 50, "u'0'", None) , (16392, 50, "u'0'", None) , ], 1 , 1 , 4 , 0 , 188 , (3, 32, None, None) , 0 , )),
	(( u'GetScriptStatusEx' , u'ScriptID' , u'Status' , ), 42, (42, (), [ (3, 49, '0', None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 192 , (3, 0, None, None) , 0 , )),
	(( u'GetProcessStatusEx' , u'ProcessID' , u'Status' , ), 43, (43, (), [ (3, 1, None, None) , 
			(16387, 10, None, None) , ], 1 , 1 , 4 , 0 , 196 , (3, 0, None, None) , 0 , )),
]

RecordMap = {
}

CLSIDToClassMap = {
	'{F18E7145-FE6F-41EE-A374-E4AB6B846A15}' : IScript,
	'{134BAC43-378A-4994-91C4-9231076E8DED}' : ISystem,
	'{95173C7F-BC29-4809-9729-622F4A4CC01C}' : Script,
	'{CF126D49-9F4D-4257-8B8B-F4C759CD0469}' : IMCSRcvr,
	'{D00B09FA-95F6-4A3E-A0D6-E9625C17A0D7}' : Database,
	'{B7608A05-B681-42EF-BD69-DFB44A74B5C1}' : IDevice,
	'{2EB1BBD0-9611-4574-8AA9-8F49E3FCCCF9}' : _IDatabaseEvents,
	'{04DF064E-DDEB-49C8-A0F9-C2A1B6A60662}' : _IMCSRcvrEvents,
	'{194E08AF-FA21-4DA1-8342-9AF11D274244}' : PlannerEvent,
	'{8C765062-9BA9-4D02-9AE1-30B8AC7088EA}' : _IScriptEvents,
	'{F8F837D9-AE56-4BFA-A34A-BC3F81ADEA90}' : _IPlannerEventEvents,
	'{C52BA4FE-30BC-42CA-9AB2-4D249FD77FE1}' : MCSRcvr,
	'{575FAB44-765A-4AB3-8983-639C4D1C5D59}' : IDatabase,
	'{33869BD6-3E45-4632-8938-88C7F138C9D6}' : Device,
	'{10BCAEAE-BA76-4D5B-971A-66A45F5382E5}' : _ISystemEvents,
	'{411B7705-5E52-4FE7-89CF-9A115D8EB871}' : _IDeviceEvents,
	'{F9468956-F5B8-4275-8F1B-62FD41967B7C}' : IPlannerEvent,
	'{E15F0BB3-770C-4E29-8DC8-BABA6E424E8C}' : System,
}
CLSIDToPackageMap = {}
win32com.client.CLSIDToClass.RegisterCLSIDsFromDict( CLSIDToClassMap )
VTablesToPackageMap = {}
VTablesToClassMap = {
	'{F18E7145-FE6F-41EE-A374-E4AB6B846A15}' : 'IScript',
	'{134BAC43-378A-4994-91C4-9231076E8DED}' : 'ISystem',
	'{B7608A05-B681-42EF-BD69-DFB44A74B5C1}' : 'IDevice',
	'{575FAB44-765A-4AB3-8983-639C4D1C5D59}' : 'IDatabase',
	'{CF126D49-9F4D-4257-8B8B-F4C759CD0469}' : 'IMCSRcvr',
	'{F9468956-F5B8-4275-8F1B-62FD41967B7C}' : 'IPlannerEvent',
}


NamesToIIDMap = {
	'_ISystemEvents' : '{10BCAEAE-BA76-4D5B-971A-66A45F5382E5}',
	'IScript' : '{F18E7145-FE6F-41EE-A374-E4AB6B846A15}',
	'IMCSRcvr' : '{CF126D49-9F4D-4257-8B8B-F4C759CD0469}',
	'_IScriptEvents' : '{8C765062-9BA9-4D02-9AE1-30B8AC7088EA}',
	'IPlannerEvent' : '{F9468956-F5B8-4275-8F1B-62FD41967B7C}',
	'IDevice' : '{B7608A05-B681-42EF-BD69-DFB44A74B5C1}',
	'_IDeviceEvents' : '{411B7705-5E52-4FE7-89CF-9A115D8EB871}',
	'ISystem' : '{134BAC43-378A-4994-91C4-9231076E8DED}',
	'IDatabase' : '{575FAB44-765A-4AB3-8983-639C4D1C5D59}',
	'_IPlannerEventEvents' : '{F8F837D9-AE56-4BFA-A34A-BC3F81ADEA90}',
	'_IDatabaseEvents' : '{2EB1BBD0-9611-4574-8AA9-8F49E3FCCCF9}',
	'_IMCSRcvrEvents' : '{04DF064E-DDEB-49C8-A0F9-C2A1B6A60662}',
}

win32com.client.constants.__dicts__.append(constants.__dict__)

