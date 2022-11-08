  
import functools
import sqlite3
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QGridLayout
import functools 
from traceback import print_exc
import functools
import time
from PyQt5.QtWidgets import    QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout

from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import subprocess 
from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox  
from utils.subproc import subproc
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton 
from PyQt5.QtGui import QColor,QFont,QPixmap,QIcon
import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize 
import subprocess
from utils.config import globalconfig ,savehook_new
from utils.getpidlist import getwindowlist,getExeIcon
import threading
import json
from gui.inputdialog import autoinitdialog,getsomepath1

import os
import win32con,win32api,win32process,win32gui
self_pid=os.getpid() 
from PyQt5.QtWinExtras  import QtWin  
 
def autosaveshow(object):
     
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle('已保存游戏')
    #dialog.setWindowModality(Qt.ApplicationModal) 
    formLayout = QVBoxLayout(dialog)  # 配置layout
    if True:
        model=QStandardItemModel(  dialog)
        row=0
        for k in savehook_new:                                   # 2
                item = QStandardItem('')
                transparent=QPixmap(100,100)
                transparent.fill(QColor.fromRgba(0))
                icon=getExeIcon(k)
                if icon is None:
                    icon=transparent
                icon=QIcon(icon)
                item.setIcon(icon)
                model.setItem(row, 0, item)
                item = QStandardItem(k)
                model.setItem(row, 1, item)
                # item = QStandardItem(json.dumps(js[k],ensure_ascii=False))
                # model.setItem(row, 2, item)
                row+=1
        model.setHorizontalHeaderLabels(['图标', '游戏'])#,'HOOK'])
        table = QTableView(dialog)
        #table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
        table.setWordWrap(False) 
        table.setModel(model)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText('开始游戏')
        def clicked(): 
                try:
                    if os.path.exists(model.item(table.currentIndex().row(),1).text()):
                        #subprocess.Popen(model.item(table.currentIndex().row(),1).text()) 
                        game=model.item(table.currentIndex().row(),1).text()
                        win32api.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW)
                         
                        dialog.close() 
                except:
                        print_exc()
        button.clicked.connect(clicked)
        button4=QPushButton(dialog)
        button4.setText('使用LocaleEmulator开始游戏')
        def clicked4():  
                try:
                    if os.path.exists(model.item(table.currentIndex().row(),1).text()):
                        
                        le=os.path.join(os.path.abspath(globalconfig['LocaleEmulator']),'LEProc.exe')

                        if os.path.exists(le):
                                #print('"'+le+'"   "'+ model.item(table.currentIndex().row(),1).text()+'"')
                                game=model.item(table.currentIndex().row(),1).text()
                                win32api.ShellExecute(None, "open", le, f'-run "{game}"', os.path.dirname(game), win32con.SW_SHOW)
                                #subprocess.Popen('"'+le+'"   "'+ model.item(table.currentIndex().row(),1).text()+'"' ) 
                                dialog.close() 
                except:
                        print_exc()
        button4.clicked.connect(clicked4)
        button2=QPushButton(dialog)
        button2.setText('删除游戏')
        def clicked2(): 
                savehook_new.pop(model.item(table.currentIndex().row(),1).text())
                model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
         
        formLayout.addWidget(table) 
        formLayout.addWidget(button)
        formLayout.addWidget(button4)
        formLayout.addWidget(button2) 
        dialog.resize(QSize(800,400))
    dialog.show()
 
def setTab4(self) :

        
        
        grids=[
                
                [(QLabel('检测到游戏时自动开始'),1),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','',''],
                
                [(QLabel('LocaleEmulator路径设置'),1),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'LocaleEmulator 路径',globalconfig,'LocaleEmulator','LocaleEmulator:',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1)],
                [(QLabel('已保存游戏'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:autosaveshow(self)),1)],

                
                
        ]
         
        self.yitiaolong("HOOK设置",grids) 
        self.minmaxmoveoberve=subproc('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE,keep=True)  
        self.minmaxmoveobservethread=threading.Thread(target=minmaxmoveobservefunc,args=(self,))
        self.minmaxmoveobservethread.start()
        #threading.Thread(target=minmaxmoveobservefunc2,args=(self,)).start() 
        self.autostarthooksignal.connect(functools.partial(autostarthookfunction,self))
        

def autostarthookfunction(self,pid,hwnd,pexe,hookcode):
           
        from textsource.textractor import textractor
        self.object.hookselectdialog.changeprocessclearsignal.emit()
        if self.object.savetextractor:
                self.object.textsource=self.object.savetextractor
                self.object.textsource.reset(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,hwnd,pexe,True,hookcode)

        else:
                self.object.textsource=textractor(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,hwnd,pexe,True,hookcode) 
                self.object.savetextractor=self.object.textsource

# def minmaxmoveobservefunc2(self):
#         while(True):
#                 time.sleep(0.3)
                 
#                 try:
#                         hwnd=win32gui.GetForegroundWindow()

#                         pid=win32process.GetWindowThreadProcessId(hwnd) [1]
                        
#                         if globalconfig['focusfollow']:
#                              if self.object.textsource.pid:
#                                 if pid==self_pid:
#                                         pass
#                                 elif pid==self.object.textsource.pid: 
#                                         if self.object.translation_ui.isHidden():
#                                                 self.object.translation_ui.hookfollowsignal.emit(3,(0,0)) 
                                        
#                                 else:
#                                         self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
#                 except:
#                         #print_exc()
#                         pass
def minmaxmoveobservefunc(self):
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                 
                x=str(x,encoding='utf8')
                x=x.replace('\r','').replace('\n','')
                 
                x=x.split(' ')
                 
                if len(x) not in [2,6]:
                        break
                x=[int(_) for _ in x]
                if len(x)==2:
                        pid,action=x
                elif len(x)==6:
                        pid,action,x1,y1,x2,y2=x
                
                try:
                  if self.object.textsource.pid:
                      
                     if pid==self_pid:
                            continue
                     plist=getwindowlist()
                     if self.object.textsource.pid not in plist:
                            #print('game exit') 
                            self.object.textsource=None
                            continue
                     if pid==self.object.textsource.pid: 
                        if action==1 and globalconfig['movefollow']:
                                self.movestart=[x1,y1,x2,y2]
                                
                        elif action==2 and globalconfig['movefollow']: 
                                moveend=[x1,y1,x2,y2]
                                self.object.translation_ui.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                        elif action==3 and globalconfig['minifollow']: 
                                self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                        elif action==4 and  globalconfig['minifollow']:
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))
                     if action==5 and  globalconfig['focusfollow']: 
                        try:
                                if pid==self.object.translation_ui.callmagpie.pid:
                                        continue
                        except:
                                pass
                        if pid==self_pid:
                                pass
                         
                        elif pid==self.object.textsource.pid: 
                                if self.object.translation_ui.isHidden():
                                        self.object.translation_ui.hookfollowsignal.emit(3,(0,0)) 
                                
                        else:
                                self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                except:
                  #print_exc()
                  pass