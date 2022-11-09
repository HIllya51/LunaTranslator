
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QDialogButtonBox,QLineEdit,QPushButton,QDialog
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome
import subprocess
import json
import os
import re
import sys

from utils.config import globalconfig ,_TR,_TRL
import win32gui
from utils.config import globalconfig
class transhist(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    showsignal=pyqtSignal()
    def __init__(self,p):
        super(transhist, self).__init__(p)
        self.setupUi() 
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.showsignal.connect(self.showfunction)
        self.setWindowTitle(_TR('历史翻译'))
    def showfunction(self): 
        self.showNormal() 
    def closeEvent(self, event) : 
         
            self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"  ))
        font = QFont()
        #font.setFamily("Arial Unicode MS") 
        font.setPointSize(12)
        self.setGeometry(0,0,1000,300)
        self.textOutput = QPlainTextEdit(self)
        self.textOutput.setFont(font)
        self.setCentralWidget(self.textOutput) 
         
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
        self.textOutput.setObjectName("textOutput") 
   
        self.hiding=True
       
    def getnewsentence(self,sentence):
        scrollbar = self.textOutput.verticalScrollBar()
        self.textOutput.appendPlainText(sentence)
        scrollbar.setValue(scrollbar.maximum())
     