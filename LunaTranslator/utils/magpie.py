import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication 

from PyQt5.QtCore import QCoreApplication ,Qt  
  
import ctypes
import json,win32api,win32gui
from ctypes import c_int32,c_char_p,c_uint32,c_float
import time,threading 
import os
 
class Dict2Obj(dict):
    
    def __getattr__(self, key): 
        if key not in self:
            return None
        else:
            value = self[key]
            if isinstance(value,dict):
                value = Dict2Obj(value)
            return value 
def callmagpie(  queue):# 0x2000|\0x2|\0x200):  
    app1=QApplication(sys.argv)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  
    FlagMasks={ 
          "NoCursor":0x1,
          "AdjustCursorSpeed":0x2,
          "SaveEffectSources":0x4,
          "SimulateExclusiveFullscreen":0x8,
          "DisableLowLatency":0x10,
          "BreakpointMode":0x20,
          "DisableWindowResizing":0x40,
          "DisableDirectFlip":0x80,
          "Is3DMode":0x100,
          "CropTitleBarOfUWP":0x200,
          "DisableEffectCache":0x400,
          "DisableVSync":0x800,
          "WarningsAreErrors":0x1000,
          "ShowFPS":0x2000,
    }
    FlagMasks=Dict2Obj(FlagMasks)
    savethread=None
    def _t():
        
         
        while True:
            _=queue.get()
             
            cwd,hwnd,ScaleMode,flags,captureMode=_
            settings=Dict2Obj(flags)
            flags=settings.NoCursor *FlagMasks.NoCursor   |\
                          settings.AdjustCursorSpeed *FlagMasks.AdjustCursorSpeed   |\
                          settings.DebugSaveEffectSources *FlagMasks.SaveEffectSources   |\
                          settings.DisableLowLatency *FlagMasks.DisableLowLatency   |\
                          settings.DebugBreakpointMode *FlagMasks.BreakpointMode   |\
                          settings.DisableWindowResizing *FlagMasks.DisableWindowResizing   |\
                          settings.DisableDirectFlip *FlagMasks.DisableDirectFlip   |\
                          settings.Is3DMode *FlagMasks.Is3DMode   |\
                          settings.CropTitleBarOfUWP *FlagMasks.CropTitleBarOfUWP   |\
                          settings.DebugDisableEffectCache *FlagMasks.DisableEffectCache   |\
                          settings.SimulateExclusiveFullscreen *FlagMasks.SimulateExclusiveFullscreen   |\
                          settings.DebugWarningsAreErrors *FlagMasks.WarningsAreErrors   |\
                          (1-settings.VSync)*FlagMasks.DisableVSync  | \
                           settings.ShowFPS *FlagMasks.ShowFPS  
            os.chdir(cwd) 
            
            
            dll=ctypes.CDLL('./MagpieRT.dll')
            MagpieRT_Initialize=dll.Initialize
            MagpieRT_Initialize.argtypes=[ c_uint32,  c_char_p,c_int32,c_int32]
            MagpieRT_Run=dll.Run
            MagpieRT_Run.argtypes=[ c_uint32,c_char_p,c_uint32,c_uint32,c_float,c_uint32,c_int32,c_uint32,c_uint32,c_uint32,c_uint32,c_uint32]
            MagpieRT_Run.restype=c_char_p   
            with open('ScaleModels.json','r')as ff:
                effectsJson= json.load(ff)   
            MagpieRT_Initialize(6,c_char_p('Runtime.log'.encode('utf8')),100000,1)
             
            threading.Thread(target=MagpieRT_Run,args=(hwnd,c_char_p(json.dumps(effectsJson[ScaleMode]['effects']).encode('utf8')),flags,captureMode,settings.CursorZoomFactor,settings.CursorInterpolationMode,settings.AdapterIdx,settings.MultiMonitorUsage,0,0,0,0)).start()
            #MagpieRT_Run(hwnd ,c_char_p(json.dumps(effectsJson[ScaleMode]['effects']).encode('utf8')),flags,captureMode,settings.CursorZoomFactor,settings.CursorInterpolationMode,settings.AdapterIdx,settings.MultiMonitorUsage,0,0,0,0)
            
    threading.Thread(target=_t).start()
    sys.exit(app1.exec_())
