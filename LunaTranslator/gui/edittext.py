
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QTextBrowser,QMainWindow,QFontDialog,QAction,QMenu,QHBoxLayout,QWidget,QPushButton,QVBoxLayout
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal ,QSize
import qtawesome
import subprocess
import json,threading
import os
import re
import sys

from utils.config import globalconfig ,_TR,_TRL
import win32gui
from utils.config import globalconfig
class edittext(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str)  
    showsignal=pyqtSignal()
    def __init__(self,p):
        super(edittext, self).__init__(p)
        self.p=p
        self.sync=True
        self.setupUi() 
        
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)  
        self.showsignal.connect(self.showfunction) 
        self.setWindowTitle(_TR('编辑'))
    def showfunction(self): 
        if self.isMinimized():
            self.showNormal()
        elif self.isHidden(): 
            self.show() 
        else:
            self.hide()
    def closeEvent(self, event) : 
            globalconfig['edit_geo']=list(self.geometry().getRect())
            self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"  ))
        font = QFont() 
        font.fromString(globalconfig['edit_fontstring'])


        d=QApplication.desktop()

        globalconfig['edit_geo'][0]=min(max(globalconfig['edit_geo'][0],0),d.width()-globalconfig['edit_geo'][2])
        globalconfig['edit_geo'][1]=min(max(globalconfig['edit_geo'][1],0),d.height()-globalconfig['edit_geo'][3])
        self.setGeometry(*globalconfig['edit_geo'])
        self.textOutput = QTextBrowser(self)
        self.textOutput.setFont(font)
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.charformat=self.textOutput.currentCharFormat()
        self.textOutput.customContextMenuRequested.connect(self.showmenu  )
        #self.setCentralWidget(self.textOutput) 
        
        self.textOutput.setUndoRedoEnabled(True)
        self.textOutput.setReadOnly(False)
        self.textOutput.setObjectName("textOutput") 

        qv=QHBoxLayout() 
        w=QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)


       
        bt1=QPushButton(icon=qtawesome.icon("fa.rotate-right" ,color=globalconfig['buttoncolor']))
        bt1.setIconSize(QSize(int(20*self.p.rate),
                                 int(20*self.p.rate)))
        bt2=QPushButton(icon=qtawesome.icon("fa.forward" if self.sync else 'fa.play' ,color="#FF69B4" if self.sync else globalconfig['buttoncolor']))
        bt2.setIconSize(QSize(int(20*self.p.rate),
                                 int(20*self.p.rate)))
        self.bt2=bt2
        bt2.clicked.connect(self.changestate)
        bt1.clicked.connect(self.run)
        qvb=QVBoxLayout()
        qvb.addWidget(bt1)
        qvb.addWidget(bt2)

        qv.addLayout(qvb) 
        qv.addWidget(self.textOutput)

        

        self.hiding=True
    def run(self):
        threading.Thread(target=self.p.object.textgetmethod,args=(self.textOutput.toPlainText(),False)).start()
    def changestate(self):
        self.sync=not self.sync 
        self.bt2.setIcon(qtawesome.icon("fa.forward" if self.sync else 'fa.play' ,color="#FF69B4" if self.sync else globalconfig['buttoncolor']))
    def showmenu(self,p):  
        menu=QMenu(self ) 
        qingkong=QAction(_TR("清空"))  
        ziti=QAction(_TR("字体") ) 
        menu.addAction(qingkong)  
        menu.addAction(ziti)
        action=menu.exec(self.mapToGlobal(p))
        if action==qingkong:
            self.textOutput.clear()
         
        elif action==ziti :
            
            font, ok = QFontDialog.getFont(self.textOutput.font(), parent=self)
            
             
            if ok : 
                globalconfig['edit_fontstring']=font.toString()
                self.textOutput.setFont(font)
    def getnewsentence(self,sentence):
        if self.sync: 
            self.textOutput.setCurrentCharFormat(self.charformat)
            self.textOutput.setPlainText(sentence) 
    