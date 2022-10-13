 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QListView,QDialogButtonBox ,QApplication,QPushButton
from PyQt5.QtGui import  QStandardItemModel,QPixmap,QColor,QIcon,QStandardItem ,QFont
from PyQt5.QtWinExtras  import QtWin 
import win32gui 
import win32api,win32process,win32con
import sys
import time   
import qtawesome
class AttachProcessDialog(QDialog):
    def getExeIcon(self,name ): 
        try:
            large, small = win32gui.ExtractIconEx(name,0)
            pixmap =QtWin.fromHICON(large[0])
            return pixmap
        except:
            return None
       
    def ListProcess(self):
          
        # def __(proc):
        #     try: 
        #         name=proc.exe().lower()
        #         if name[-4:]=='.exe' and ':\\windows\\' not in name   and '\\microsoft\\' not in name:
        #                     #print(pid,name)
        #                     return True
        #         else:
        #             return False
        #     except psutil.AccessDenied :
        #         return False 
        # t1=time.time()
        # process=filter(__,psutil.process_iter()) 
         
        # a = [(proc.pid,proc.exe(),proc.name()) for proc in process] 
         
        # #print(1,time.time()-t1)

        windows_list = []
        ret=[]
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list)
        for hwnd in windows_list:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                
                 
                #for pid in pids:
                if True:
                    try:
                        classname = win32gui.GetClassName(hwnd)
                        title = win32gui.GetWindowText(hwnd)
                        #print(f'classname:{classname} title:{title}') 
                        tid, pid=win32process.GetWindowThreadProcessId(hwnd) 
                        hwnd=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                        name_=win32process.GetModuleFileNameEx(hwnd,None) 
                        name=name_.lower()
                        if name[-4:]!='.exe' or ':\\windows\\'  in name   or '\\microsoft\\'  in name:
                            continue
                        import os
                        ret.append([pid,name_,hwnd])
                    except:
                        pass
        #print(windows_list)
        #print(ret)
        return ret
    iconcache={}
    def selectwindow(self):
        import PyHook3
        hm = PyHook3.HookManager()
        def OnMouseEvent(event): 
            
            p=win32api.GetCursorPos()

            hwnd=win32gui.WindowFromPoint(p)

            
            #for pid in pids:
            if True:
                try:
                    tid, pid=win32process.GetWindowThreadProcessId(hwnd)
                    #print(pid,  win32gui.GetWindowText(hwnd))
                    hwnd=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, pid)
                    name_=win32process.GetModuleFileNameEx(hwnd,None) 
                    #print(name_) 
                    self.processEdit.setText(name_)
                    self.processIdEdit.setText(str(pid))
                    self.selectedp=(pid,name_,hwnd)
                except: 
                    pass
            hm.UnhookMouse()   
            return True
        hm.MouseAllButtonsDown = OnMouseEvent
        hm.HookMouse()
    def __init__(self ):
        super(AttachProcessDialog, self).__init__( ) 
        self.setWindowModality(Qt.WindowModal)
        self.resize(800,400)
        self.selectedp=-1  
        self.setWindowTitle('选择进程')
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        f=QFont() 
        f.setPointSize(13)
        self.setFont(f)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        t1=time.time()
        self.layout1=QVBoxLayout()
        self.label=QLabel('如果没看见想要附加的进程，尝试使用管理员权限运行，也可以尝试点击下方按钮后点击游戏窗口') 
        self.button=QPushButton('点击此按钮后点击游戏窗口')
        self.button.clicked.connect(self.selectwindow)
        self.layout1.addWidget(self.label)
        self.layout1.addWidget(self.button)
        self.layout2=QHBoxLayout()
        self.processIdEdit=QLineEdit()
        self.layout2.addWidget(QLabel('进程号，找不到的情况下可以手动输入'))
        self.layout2.addWidget(self.processIdEdit)
        self.processEdit=QLineEdit()
        self.layout3=QHBoxLayout()
        self.layout3.addWidget(QLabel('程序名'))
        self.layout3.addWidget(self.processEdit)
        self.processList=QListView()
        self.buttonBox=QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout1.addLayout(self.layout2)
        self.layout1.addLayout(self.layout3)
        self.layout1.addWidget(self.processList)
        self.layout1.addWidget(self.buttonBox)
        self.setLayout(self.layout1) 
        #print(time.time()-t1)
        model=QStandardItemModel(self.processList)
        self.model=model 
        transparent=QPixmap(100,100)
        transparent.fill(QColor.fromRgba(0))
        #print(time.time()-t1)
        self.processlist=self.ListProcess()
        #print(time.time()-t1)
        self.processList.setModel(model)
        for pid,pexe,hwnd  in self.processlist: 
            if pexe in self.iconcache:
                icon=self.iconcache[pexe]
            else:
                icon=self.getExeIcon(pexe)

                if icon is None:
                    icon=transparent
                icon=QIcon(icon)
                self.iconcache[pexe]=icon
            item=QStandardItem(icon , pexe)
            item.setEditable(False)
            model.appendRow(item)
        #print(time.time()-t1)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject) 
        
        self.processList.clicked.connect(self.selectedfunc)
        #self.processList.doubleClicked.connect(self.accept)
        #print(time.time()-t1)
        def ff(process):
            for i in range(model.rowCount()):
                self.processList.setRowHidden(i,not (process.lower() in model.item(i).text().lower()))
        self.processEdit.textEdited.connect(ff)
        def gg(process):
            self.selectedp=(int(process),'',0)
        self.processIdEdit.textEdited.connect(gg)
        #print(time.time()-t1)
        #self.processEdit.returnPressed.connect(self.accept)
        
    def selectedfunc(self,index): 
        self.processEdit.setText(self.processlist[index.row()][1] )
        self.processIdEdit.setText(str(self.processlist[index.row()][0]  ))
        self.selectedp=self.processlist[index.row()] 
        
if __name__=='__main__':
    app = QApplication(sys.argv) 
    a=AttachProcessDialog()
    a.show()

    app.exit(app.exec_())