
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QDialogButtonBox,QLineEdit,QPushButton
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome
import subprocess
import json
import os
import re
import sys

from utils.config import globalconfig
class searchwordW(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    def __init__(self,p):
        super(searchwordW, self).__init__(p)
        self.setupUi() 
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.setWindowTitle('查词')
        self.p=p
    def closeEvent(self, event) :  
        self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"  ))
        font = QFont()
        #font.setFamily("Arial Unicode MS")
        font.setFamily(globalconfig['fonttype'])
        font.setPointSize(12)
        self.setGeometry(0,0,500,300)
        self.centralWidget = QWidget(self) 
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout(self.centralWidget)  
         
        self.vboxlayout = QVBoxLayout()  
        
        
        self.userhooklayout = QHBoxLayout() 
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook=QLineEdit()
        self.userhook.setFont(font)
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert=QPushButton("搜索")
        self.userhookinsert.setFont(font) 
        self.userhookinsert.clicked.connect(lambda :self.search(self.userhook.text()))
        self.userhooklayout.addWidget(self.userhookinsert)
 
        

        self.textOutput = QPlainTextEdit(self)
        self.textOutput.setFont(font) 
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
         
        self.vboxlayout.addWidget(self.textOutput)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)
  
 
        
   
        self.hiding=True
    def getnewsentence(self,sentence):
        self.userhook.setText(sentence)
        self.search(sentence)
    def search(self,sentence):
        self.textOutput.clear()
        res=self.p.object.xiaoxueguan.search(sentence)
        if res is None:
            res='未查到'
        
        self.textOutput.appendHtml(res)
        scrollbar = self.textOutput.verticalScrollBar()
        scrollbar.setValue(0)
     