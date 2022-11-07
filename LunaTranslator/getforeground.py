import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QPushButton

from PyQt5.QtCore import QCoreApplication ,Qt ,QProcess
 
import win32api,win32gui,win32process,win32con,win32print,win32ui
import ctypes
import json
from ctypes import c_int32,c_char_p,c_uint32,c_float
import time,threading,multiprocessing
import os
import win32,win32event
from queue import Queue
from utils.magpie import  callmagpie1
 
while True:
    m_hWnd=win32gui.GetForegroundWindow()
    pid=win32process.GetWindowThreadProcessId(m_hWnd) [1]
    title = win32gui.GetWindowText(m_hWnd)
    j=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
    name_ = win32process.GetModuleFileNameEx(
                            j, None)
    print(m_hWnd)
    print(win32gui.GetClassName(m_hWnd))
    print(name_)  
    time.sleep(1)
