
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
    def closeEvent(self, event) :  
            self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"  ))
        font = QFont()
        #font.setFamily("Arial Unicode MS")
        font.setFamily(globalconfig['fonttype'])
        font.setPointSize(15)
        self.resize(500,500)
        self.textOutput = QPlainTextEdit(self)
        self.textOutput.setFont(font)
        self.setCentralWidget(self.textOutput) 
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
   
        self.hiding=True
       
    def getnewsentence(self,sentence):
        self.textOutput.clear()
     
        self.textOutput.appendHtml(sentence)
        scrollbar = self.textOutput.verticalScrollBar()
        scrollbar.setValue(0)
     