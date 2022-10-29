
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
class transhist(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    showsignal=pyqtSignal()
    def __init__(self):
        super(transhist, self).__init__()
        self.setupUi() 
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.showsignal.connect(self.show)
        self.setWindowTitle('历史翻译')
    def closeEvent(self, event) : 
         
            self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"  ))
        font = QFont()
        #font.setFamily("Arial Unicode MS")
        font.setFamily(globalconfig['fonttype'])
        font.setPointSize(15)
        self.setGeometry(0,0,1000,300)
        self.textOutput = QPlainTextEdit(self)
        self.textOutput.setFont(font)
        self.setCentralWidget(self.textOutput) 
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
        self.textOutput.setObjectName("textOutput") 
   
        self.hiding=True
       
    def getnewsentence(self,sentence):
        scrollbar = self.textOutput.verticalScrollBar()
        atBottom = scrollbar.value() + 3 > scrollbar.maximum() or scrollbar.value() / scrollbar.maximum() > 0.975 
        cursor=QTextCursor (self.textOutput.document())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(sentence+'\n')
        if (atBottom):
            scrollbar.setValue(scrollbar.maximum())
     