  
import functools,win32api,win32gui,win32process
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
from utils.config import globalconfig ,savehook_new,savehook_new2
from utils.getpidlist import getwindowlist,getExeIcon,getpidexe
import threading
import json
from gui.inputdialog import autoinitdialog,getsomepath1

from utils.config import globalconfig ,_TR,_TRL
import os
import win32con,win32api 
self_pid=os.getpid()   
def autosaveshow(object):
     
    dialog = QDialog(object,Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR('已保存游戏'))
    #dialog.setWindowModality(Qt.ApplicationModal) 
    formLayout = QVBoxLayout(dialog)  # 配置layout
    def closeEvent(  a0  ) -> None:
                rows=model.rowCount() 
                 
                for row in range(rows): 
                        savehook_new2[model.item(row,3).text()]['title']=model.item(row,2).text()
                 
                return QDialog().closeEvent(a0)
    dialog.closeEvent=closeEvent
    if True:
        model=QStandardItemModel(  dialog)
        table = QTableView(dialog)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
        table.setWordWrap(False) 
        table.setModel(model) 
        table
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        row=0
        for k in savehook_new:                                   # 2
                 
                transparent=QPixmap(100,100)
                transparent.fill(QColor.fromRgba(0))
                icon=getExeIcon(k)
                if icon is None:
                    icon=transparent
                icon=QIcon(icon) 
                model.setItem(row, 1, QStandardItem(icon,'')) 
                model.setItem(row, 3, QStandardItem(k)) 
                model.setItem(row, 0, QStandardItem(''))
                
                if k not in savehook_new2:
                        savehook_new2[k]={}
                        savehook_new2[k]['leuse']=True
                        savehook_new2[k]['title']='' 
                model.setItem(row, 2, QStandardItem(savehook_new2[k]['title']))
                table.setIndexWidget(model.index(row, 0),object.getsimpleswitch(savehook_new2[k],'leuse'))
                # item = QStandardItem(json.dumps(js[k],ensure_ascii=False))
                # model.setItem(row, 2, item)
                row+=1
        model.setHorizontalHeaderLabels(_TRL(['使用LE','','标题', '游戏']))#,'HOOK'])
        
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText(_TR('开始游戏'))
        def clicked(): 
                try:
                    game=model.item(table.currentIndex().row(),3).text() 
                    if os.path.exists(game):
                        #subprocess.Popen(model.item(table.currentIndex().row(),1).text()) 
                        print(game)
                        le=os.path.join(os.path.abspath(globalconfig['LocaleEmulator']),'LEProc.exe')
                        if savehook_new2[game]['leuse'] and os.path.exists(le):
                                win32api.ShellExecute(None, "open", le, f'-run "{game}"', os.path.dirname(game), win32con.SW_SHOW)
                        else:
                                win32api.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW)
                                 
                         
                        dialog.close() 
                except:
                        print_exc()
        button.clicked.connect(clicked)
         
        button2=QPushButton(dialog)
        button2.setText(_TR('删除游戏'))
        def clicked2(): 
                savehook_new.pop(model.item(table.currentIndex().row(),3).text())
                model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
         
        formLayout.addWidget(table) 
        formLayout.addWidget(button) 
        formLayout.addWidget(button2) 
        dialog.resize(QSize(800,400))
    dialog.show()
 
def setTab4(self) :

        
        
        grids=[
                
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','','','','','','',''],
                
                [('LocaleEmulator路径设置',5),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'LocaleEmulator',globalconfig,'LocaleEmulator','LocaleEmulator',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1)],
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:autosaveshow(self)),1)],

                
                
        ]
         
        self.yitiaolong("HOOK设置",grids) 
        self.minmaxmoveoberve=subproc('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE,keep=True)  
        self.minmaxmoveobservethread=threading.Thread(target=minmaxmoveobservefunc,args=(self,))
        self.minmaxmoveobservethread.start()  
          
def minmaxmoveobservefunc(self):
        
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                #print(x)
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
                            self.object.translation_ui.hookfollowsignal.emit(3,(0,0))  
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
                        
                        #print(pid)
                        if pid==self_pid: 
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))  
                        elif pid==self.object.textsource.pid: 
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))   
                        elif pid==self.object.translation_ui.callmagpie.pid:
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))   
                        else: 
                                try:
                                        cn=win32gui.GetClassName(win32gui.GetForegroundWindow()) 
                                         
                                        if cn=='Shell_TrayWnd':
                                                continue 
                                        exe=getpidexe(pid)
                                        if os.path.basename(exe).lower()=='magpie.exe':
                                                continue
                                except:
                                        pass
                                plist=getwindowlist()
                                if self.object.textsource.pid not in plist:
                                        #print('game exit') 
                                        self.object.textsource=None
                                else:
                                        self.object.translation_ui.hookfollowsignal.emit(4,(0,0)) 
                except:
                  #print_exc()
                  pass