    
from utils.config import globalconfig   
import time
import os 
from traceback import print_exc

import win32pipe, win32file,win32con
try:
    win32pipe.WaitNamedPipe("\\\\.\\Pipe\\ocrwaitsignal",win32con.NMPWAIT_WAIT_FOREVER)
    hPipe = win32file.CreateFile( "\\\\.\\Pipe\\ocrwaitsignal", win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
            None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
    #win32file.WriteFile(hPipe,'haha'.encode('utf8'))
    print(win32file.ReadFile(hPipe, 65535, None)[1].decode('utf8'))
except:
    print_exc() 