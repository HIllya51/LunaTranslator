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
from utils.magpie import  callmagpie
class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500) 
        # 取消窗口边框 
         
        # 添加环绕阴影   
        
         
        print(3)
        self.b=QPushButton(self)
        self.b.clicked.connect(self.close)
        self.b.setGeometry(0,0,100,20)
        self.b2=QPushButton(self)
        self.b2.clicked.connect(self.xx)
        self.b2.setGeometry(0,100,100,20)
    def close(self, a0  ) -> None: 
        self.pr.kill()
        super( ).close()
    def xx(self):
        while True:
            m_hWnd=win32gui.GetForegroundWindow()
            pid=win32process.GetWindowThreadProcessId(m_hWnd) [1]
            title = win32gui.GetWindowText(m_hWnd)
            if title.encode('utf8')[:10]==b'\xe5\x83\x8b\xe5\x83\xab\xe5\x83\xaa\xe5\xb4\x99\xe5\xa9\xb0\xe4\xba\x82\xe4\xbf\xa2\xe4\xbf\xb4\xe6\x96\x89\xe4\xba\x83\xe4\xb8\x82- \xe5\x83\x86\xe4\xb9\x95\xe5\x83\xbe\xe5\x83\xaf\xe5\x84\x9e\xe5\x83\x8c -'[:10]: 
            
                flags=0x2000|0x2|0x200 
                rect=win32gui.GetWindowRect(m_hWnd)
                import os 
                d=os.getcwd()
               
                lock=multiprocessing.Lock()

                self.pr=multiprocessing.Process(target=callmagpie,args= (m_hWnd,r'C:\dataH\Magpie_v0.9.1',lock))
                self.pr.start()
                lock.acquire()
                break
            time.sleep(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    demo = Demo()
    
    demo.show()
    sys.exit(app.exec_())
