
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QTextBrowser,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QDialogButtonBox,QLineEdit,QPushButton,QDialog,QAction,QMenu
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome
import subprocess
import json
import os
import re
import sys 
class languageset(QDialog): 
    getnewsentencesignal=pyqtSignal(str) 
    getnewtranssignal=pyqtSignal(str,str) 
    showsignal=pyqtSignal()
    def __init__(self,language_list):
        super(languageset, self).__init__( )
         
        self.setWindowIcon(qtawesome.icon("fa.gear"  ))
        self.setMinimumSize(400,100)
        self.setWindowTitle('语言设置 LanguageSetting')
        font = QFont()
        #font.setFamily("Arial Unicode MS") 
        font.setPointSize(20)
        self.setFont(font)
        self.current=0
        language_listcombox=QComboBox()
        language_listcombox.addItems(language_list)
        language_listcombox.currentIndexChanged.connect(lambda x:setattr(self,'current',x))
        vb=QVBoxLayout(self)
        
        vb.addWidget(language_listcombox)
        bt=QPushButton('OK')
        vb.addWidget(bt)
        bt.clicked.connect(self.accept)
