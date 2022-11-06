import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication 

from PyQt5.QtCore import QCoreApplication ,Qt  
  
import ctypes
import json,win32api,win32gui
from ctypes import c_int32,c_char_p,c_uint32,c_float
import time,threading 
import os
 

def callmagpie( cwd,queue):# 0x2000|0x2|0x200): 
    t=time.time()
    app1 = QApplication(sys.argv)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  
    def _t():
        os.chdir(cwd) 
        dll=ctypes.CDLL('./MagpieRT.dll')
        MagpieRT_Initialize=dll.Initialize
        MagpieRT_Initialize.argtypes=[ c_uint32,  c_char_p,c_int32,c_int32]
        MagpieRT_Run=dll.Run
        MagpieRT_Run.argtypes=[ c_uint32,c_char_p,c_uint32,c_uint32,c_float,c_uint32,c_int32,c_uint32,c_uint32,c_uint32,c_uint32,c_uint32]
        MagpieRT_Run.restype=c_char_p  
        MagpieRT_Initialize(6,c_char_p('Runtime.log'.encode('utf8')),100000,1)
        with open('ScaleModels.json','r')as ff:
            effectsJson= json.load(ff)   
         
        while True:
            hwnd,ScaleMode,flags,captureMode=queue.get() 
            MagpieRT_Run(hwnd ,c_char_p(json.dumps(effectsJson[ScaleMode]['effects']).encode('utf8')),flags,captureMode,1,0,-1,0,0,0,0,0)
         
    threading.Thread(target=_t).start()
    sys.exit(app1.exec_())