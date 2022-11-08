 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QListView,QDialogButtonBox ,QApplication,QPushButton,QMainWindow
from PyQt5.QtGui import  QStandardItemModel,QPixmap,QColor,QIcon,QStandardItem ,QFont
from PyQt5.QtWinExtras  import QtWin 
import win32gui 
import functools
import sys
import time   
from utils.getpidlist import getwindowhwnd,getpidexe,ListProcess,mouseselectwindow,getExeIcon
import qtawesome
class AttachProcessDialog(QMainWindow):
     
        
    iconcache={}
    def selectwindowcallback(self,pid,hwnd,name_): 
         
                    self.processEdit.setText(name_)
                    self.processIdEdit.setText(str(pid))
                    self.selectedp=(pid,name_,hwnd) 
    def __init__(self ,p):
        super(AttachProcessDialog, self).__init__( p ) 
        #self.setWindowModality(Qt.WindowModal)
        self.resize(800,400)
        
        self.object=p.object
        self.setWindowTitle('选择进程')
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        f=QFont() 
        f.setPointSize(13)
        self.setFont(f)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        t1=time.time()
        w=QWidget()
        self.layout1=QVBoxLayout()
        self.label=QLabel('如果没看见想要附加的进程，可以尝试点击下方按钮后点击游戏窗口,或者尝试使用管理员权限运行本软件') 
        self.button=QPushButton('点击此按钮后点击游戏窗口')
        self.button.clicked.connect(functools.partial(mouseselectwindow,self.selectwindowcallback))
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
        w.setLayout(self.layout1)
        #self.setLayout(self.layout1) 
        self.setCentralWidget(w)
        #print(time.time()-t1)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close) 
        
        self.processList.clicked.connect(self.selectedfunc)
        #self.processList.doubleClicked.connect(self.accept)
        #print(time.time()-t1)
        
        def gg(process):
            self.selectedp=(int(process),getpidexe(int(process)),getwindowhwnd(int(process)))
        self.processIdEdit.textEdited.connect(gg)
        #print(time.time()-t1)
        #self.processEdit.returnPressed.connect(self.accept)
    def show(self):
        self.selectedp=(0,'',0)
        model=QStandardItemModel(self.processList)
        self.model=model 
        transparent=QPixmap(100,100)
        transparent.fill(QColor.fromRgba(0))
        #print(time.time()-t1)
        self.processlist= ListProcess()
        #print(time.time()-t1)
        self.processList.setModel(model)
        for pid,pexe,hwnd  in self.processlist: 
            if pexe in self.iconcache:
                icon=self.iconcache[pexe]
            else:
                icon=getExeIcon(pexe)

                if icon is None:
                    icon=transparent
                icon=QIcon(icon)
                self.iconcache[pexe]=icon
            item=QStandardItem(icon , pexe)
            item.setEditable(False)
            model.appendRow(item)
        def ff(process):
            for i in range(model.rowCount()):
                self.processList.setRowHidden(i,not (process.lower() in model.item(i).text().lower()))
        self.processEdit.textEdited.connect(ff)
        #print(time.time()-t1)
        super(AttachProcessDialog,self).show()
    def selectedfunc(self,index): 
        self.processEdit.setText(self.processlist[index.row()][1] )
        self.processIdEdit.setText(str(self.processlist[index.row()][0]  ))
        self.selectedp=self.processlist[index.row()] 
    def accept(self):
        self.callback(self.selectedp)
        self.close()
    def closeEvent(self, a0 ) -> None:
        self.hide()
if __name__=='__main__':
    app = QApplication(sys.argv) 
    a=AttachProcessDialog()
    a.show()

    app.exit(app.exec_())