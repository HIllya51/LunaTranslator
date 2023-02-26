 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QListView,QDialogButtonBox ,QApplication,QPushButton,QMainWindow
from PyQt5.QtGui import  QStandardItemModel,QPixmap,QColor,QIcon,QStandardItem ,QFont 
import functools

from utils.config import globalconfig ,_TR,_TRL
import sys
import time   ,os
from utils.getpidlist import getwindowhwnd,getpidexe,ListProcess,mouseselectwindow,getExeIcon
import qtawesome

from textsource.textractor import textractor
from gui.closeashidewindow import closeashidewindow
class AttachProcessDialog(closeashidewindow): 
        
    iconcache={}
    def selectwindowcallback(self,pid,hwnd,name_): 
                    if pid==os.getpid():
                         return
                    self.processEdit.setText(name_)
                    self.processIdEdit.setText(str(pid))
                    self.selectedp=(pid,name_,hwnd) 
    def __init__(self ,p,callback,hookselectdialog):
        super(AttachProcessDialog, self).__init__( p ) 
        self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.resize(800,400)
        # d=QApplication.desktop()
        # self.move ((d.width()-self.width())/2,((d.height()-self.height())/2))
        self.callback=callback
        self.hookselectdialog=hookselectdialog
        self.selectedp=(0,'',0)
        self.setWindowTitle(_TR('选择进程'))
        self.setWindowIcon(qtawesome.icon("fa.gear" )) 
        w=QWidget()
        self.layout1=QVBoxLayout()
        self.label=QLabel(_TR('如果没看见想要附加的进程，可以尝试点击下方按钮后点击游戏窗口,或者尝试使用管理员权限运行本软件') )
        self.button=QPushButton(_TR('点击此按钮后点击游戏窗口'))
        self.button.clicked.connect(functools.partial(mouseselectwindow,self.selectwindowcallback))
        self.layout1.addWidget(self.label)
        self.layout1.addWidget(self.button)
        self.layout2=QHBoxLayout()
        self.processIdEdit=QLineEdit()
        self.layout2.addWidget(QLabel(_TR('进程号，找不到的情况下可以手动输入')))
        self.layout2.addWidget(self.processIdEdit)
        self.processEdit=QLineEdit()
        self.layout3=QHBoxLayout()
        self.layout3.addWidget(QLabel(_TR('程序名')))
        self.layout3.addWidget(self.processEdit)
        self.processList=QListView()
        self.buttonBox=QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout1.addLayout(self.layout2)
        self.layout1.addLayout(self.layout3)
        self.layout1.addWidget(self.processList)
        self.layout1.addWidget(self.buttonBox)
        w.setLayout(self.layout1)
        #self.setLayout(self.layout1) 
        self.setCentralWidget(w)
        #print(time.time()-t1)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)  
        self.processList.clicked.connect(self.selectedfunc)  
        self.processIdEdit.textEdited.connect(self.editpid)  
        self.processEdit.textEdited.connect(self.editexe)
         
    def showEvent(self,e):

        self.hookselectdialog.realshowhide.emit(False)  
        ########################### 
        self.model=QStandardItemModel(self.processList)  
        #print(time.time()-t1)
        self.processlist= ListProcess()
        #print(time.time()-t1)
        self.processList.setModel(self.model)
        for pid,pexe,hwnd  in self.processlist: 
            if pexe in self.iconcache:
                icon=self.iconcache[pexe]
            else:
                icon=getExeIcon(pexe)  
                self.iconcache[pexe]=icon
            item=QStandardItem(icon , pexe)
            item.setEditable(False)
            self.model.appendRow(item)
        
        #print(time.time()-t1) 
    def editpid(self,process):
            try:
                self.selectedp=(int(process),getpidexe(int(process)),getwindowhwnd(int(process)))
                self.processEdit.setText(self.selectedp[1])
            except:
                pass
    def editexe(self,process):
            for i in range(self.model.rowCount()):
                self.processList.setRowHidden(i,not (process.lower() in self.model.item(i).text().lower()))
    def selectedfunc(self,index): 
        self.processEdit.setText(self.processlist[index.row()][1] )
        self.processIdEdit.setText(str(self.processlist[index.row()][0]  ))
        self.selectedp=self.processlist[index.row()] 
    def accept(self):
        self.callback(self.selectedp)
        self.close() 
if __name__=='__main__':
    app = QApplication(sys.argv) 
    a=AttachProcessDialog()
    a.show()

    app.exit(app.exec_())