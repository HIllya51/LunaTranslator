import sys
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QPushButton

from PyQt5.QtCore import QCoreApplication ,Qt ,QProcess
 
import win32api,win32gui,win32process,win32con,win32print,win32ui
import ctypes
import json
from ctypes import c_int32,c_char_p,c_uint32,c_float
import time,threading,multiprocessing
import os
import win32,win32event,win32pipe
from queue import Queue 

while True:
    m_hWnd=win32gui.GetForegroundWindow()
    pid=win32process.GetWindowThreadProcessId(m_hWnd) [1]
    title = win32gui.GetWindowText(m_hWnd)
    print(title)
    if title.encode('utf8')[:10]==b'\xe5\x83\x8b\xe5\x83\xab\xe5\x83\xaa\xe5\xb4\x99\xe5\xa9\xb0\xe4\xba\x82\xe4\xbf\xa2\xe4\xbf\xb4\xe6\x96\x89\xe4\xba\x83\xe4\xb8\x82- \xe5\x83\x86\xe4\xb9\x95\xe5\x83\xbe\xe5\x83\xaf\xe5\x84\x9e\xe5\x83\x8c -'[:10]: 
        with open('C:/dataH/Magpie_v0.9.1/ScaleModels.json','r')as ff:
                effectsJson= json.load(ff)   
        flags=0#0x2000|0x2|0x200 
        effects=json.dumps(effectsJson[0]['effects']).replace('"','\\"')
        #threading.Thread(target=subprocess.run ,args=(f'C:/Users/11737/source/repos/magpiecmdrunner/x64/Release/magpiecmdrunner.exe C:/dataH/Magpie_v0.9.1 {m_hWnd} {flags} "{effects}"',)).start()
        
        path=os.path.abspath('./files/Magpie_v0.9.1')
        
        pipename="\\\\.\\Pipe\\wait_for_quit_full_screen"+str(time.time())
        x=subprocess.Popen(f'C:/Users/11737/source/repos/magpiecmdrunner/x64/Release/magpiecmdrunner.exe {path} {m_hWnd} {flags} "{effects}" 0, 1, 0, -1, 0 {pipename}')
        time.sleep(3)
        
        win32pipe.CreateNamedPipe( pipename, win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT, win32pipe.PIPE_UNLIMITED_INSTANCES, 0, 0, win32pipe.NMPWAIT_WAIT_FOREVER, None);
         
        # time.sleep(2)
        # x=subprocess.Popen(f'C:/Users/11737/source/repos/magpiecmdrunner/x64/Release/magpiecmdrunner.exe {path} {m_hWnd} {flags} "{effects}" 0, 1, 0, -1, 0')
        # time.sleep(3)
         
        # win32pipe.CreateNamedPipe( "\\\\.\\Pipe\\HAHAHAHA_wait_for_quit_full_screen", win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT, win32pipe.PIPE_UNLIMITED_INSTANCES, 0, 0, win32pipe.NMPWAIT_WAIT_FOREVER, None);
        #x.kill()
        break
    time.sleep(1)
 