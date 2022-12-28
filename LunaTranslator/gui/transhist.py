
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QTextBrowser,QMainWindow,QFontDialog,QAction,QMenu
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
    getnewtranssignal=pyqtSignal(str,str) 
    showsignal=pyqtSignal()
    def __init__(self,p):
        super(transhist, self).__init__(p)
        self.setupUi() 
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.getnewtranssignal.connect(self.getnewtrans) 
        self.showsignal.connect(self.showfunction)
        self.hiderawflag=False
        self.hideapiflag=False
        self.setWindowTitle(_TR('历史翻译'))
    def showfunction(self): 
        if self.isMinimized():
            self.showNormal()
        elif self.isHidden(): 
            self.show() 
        else:
            self.hide()
    def closeEvent(self, event) : 
            globalconfig['hist_geo']=list(self.geometry().getRect())
            self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"  ))
        font = QFont() 
        font.fromString(globalconfig['hist_fontstring'])
        self.setGeometry(*globalconfig['hist_geo'])
        self.textOutput = QTextBrowser(self)
        self.textOutput.setFont(font)
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        
        
        self.textOutput.customContextMenuRequested.connect(self.showmenu  )
        self.setCentralWidget(self.textOutput) 
        
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
        self.textOutput.setObjectName("textOutput") 
   
        self.hiding=True
    def showmenu(self,p):  
        menu=QMenu(self ) 
        qingkong=QAction(_TR("清空")) 
        hideshowraw=QAction(_TR("显示原文"    if self.hiderawflag else "不显示原文") ) 
        hideshowapi=QAction(_TR("显示api"    if self.hideapiflag else "不显示api") ) 
        ziti=QAction(_TR("字体") ) 
        menu.addAction(qingkong)
        menu.addAction(hideshowraw)
        menu.addAction(hideshowapi)
        menu.addAction(ziti)
        action=menu.exec(self.mapToGlobal(p))
        if action==qingkong:
            self.textOutput.clear()
        elif action==hideshowraw:
             
            self.hiderawflag=not self.hiderawflag
        elif action==hideshowapi:
            
            self.hideapiflag=not self.hideapiflag
        elif action==ziti :
            
            font, ok = QFontDialog.getFont(self.textOutput.font(), parent=self)
            
             
            if ok : 
                globalconfig['hist_fontstring']=font.toString()
                self.textOutput.setFont(font)
    def getnewsentence(self,sentence):
        
        sentence= '<hr>' if globalconfig['hist_split'] else '\n'+sentence
        if self.hiderawflag:
            sentence=''
        self.textOutput.append(sentence) 
    def getnewtrans(self,api,sentence):
        if self.hideapiflag:
            res=sentence
        else:
            res=api+'  '+sentence
        self.textOutput.append(res) 