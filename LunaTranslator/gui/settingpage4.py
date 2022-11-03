  
import functools
import sqlite3
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog 
import functools 
from traceback import print_exc
import functools

from PyQt5.QtWidgets import    QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout

from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import qtawesome 
import subprocess
from utils.config import globalconfig ,postprocessconfig,noundictconfig
from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox  
from utils.subproc import subproc
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton 
from PyQt5.QtGui import QColor,QFont,QPixmap,QIcon
import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize
import qtawesome
from PyQt5.QtCore import QThread
import subprocess
from utils.config import globalconfig ,postprocessconfig,savehook_new
from utils.getpidlist import getwindowlist
import threading
import json
from gui.inputdialog import getsomepath
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
import os
import win32con,win32api,win32process,win32gui
self_pid=os.getpid() 
from PyQt5.QtWinExtras  import QtWin  
def getExeIcon( name ): 
        
        try:
            large, small = win32gui.ExtractIconEx(name,0)
            pixmap =QtWin.fromHICON(large[0])
            return pixmap
        except:
            return None

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
                        if object:
                                object.close()
                except:
                        print_exc()
        button.clicked.connect(clicked)
        button4=QPushButton(dialog)
        button4.setText('使用LocaleEmulator开始游戏')
        def clicked4():  
                try:
                    if os.path.exists(model.item(table.currentIndex().row(),1).text()):
                        le=os.path.join(globalconfig['LocaleEmulator'],'LEProc.exe')
                        print(le,os.path.exists(le))
                        if os.path.exists(le):
                                print('"'+le+'"   "'+ model.item(table.currentIndex().row(),1).text()+'"')
                                game=model.item(table.currentIndex().row(),1).text()
                                win32api.ShellExecute(None, "open", le, f'-run "{game}"', os.path.dirname(game), win32con.SW_SHOW)
                                #subprocess.Popen('"'+le+'"   "'+ model.item(table.currentIndex().row(),1).text()+'"' ) 
                                dialog.close()
                                if object:
                                        object.close()
                except:
                        print_exc()
        button4.clicked.connect(clicked4)
        button2=QPushButton(dialog)
        button2.setText('删除游戏')
        def clicked2(): 
                savehook_new.pop(model.item(table.currentIndex().row(),1).text())
                model.removeRow(table.currentIndex().row())
                with open('./userconfig/savehook_new.json','w',encoding='utf8') as ff:
                        ff.write(json.dumps(savehook_new,ensure_ascii=False))
        button2.clicked.connect(clicked2)
         
        formLayout.addWidget(table) 
        formLayout.addWidget(button)
        formLayout.addWidget(button4)
        formLayout.addWidget(button2) 
        dialog.resize(QSize(800,400))
    dialog.show()
 
def setTab4(self) :
     
        self.tab_4 = QWidget()
        self.tab_widget.addTab(self.tab_4, "HOOK设置") 
 
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 20, 200, 20)
        # label.setText("textractor模式特殊设置")

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 50, 200, 20)
        label.setText("游戏最小化时窗口隐藏")
        self.minifollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['minifollow'])
        self.customSetGeometry(self.minifollowswitch, 250, 50, 20,20)
        self.minifollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('minifollow',x)) 

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 80, 200, 20)
        label.setText("游戏窗口移动时同步移动")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['movefollow'])
        self.customSetGeometry(self.movefollowswitch, 250, 80,20,20)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('movefollow',x)) 
        
        
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 110, 200, 20)
        label.setText("检测到游戏时自动开始")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['autostarthook'])
        self.customSetGeometry(self.movefollowswitch, 250, 110,20,20)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('autostarthook',x)) 
        
        
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 140, 200, 20)
        # label.setText("提取hook线程全部文本")
        
        # self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['extractalltext'])
        # self.customSetGeometry(self.movefollowswitch, 200, 140,20,20)
        # self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('extractalltext',x)) 
        
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 170, 200, 20)
        label.setText("LocaleEmulator路径设置")
        s1 = QPushButton( "", self.tab_4)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1, 250, 170,20,20)
        s1.setStyleSheet("background: transparent;") 
        
        s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        s1.clicked.connect(lambda x: getsomepath(self,'LocaleEmulator 路径',globalconfig['LocaleEmulator'],'LocaleEmulator:',lambda x:globalconfig.__setitem__('LocaleEmulator',x),True))
      
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 200, 200, 20)
        label.setText("已保存游戏")
        s1 = QPushButton( "", self.tab_4)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1, 250, 200,20,20)
        s1.setStyleSheet("background: transparent;") 
        
        s1.setIcon(qtawesome.icon("fa.gamepad", color="#FF69B4"  )) 
        s1.clicked.connect(lambda: autosaveshow(self))

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 260, 200, 20)
        label.setText("录制翻译文件")
        self.minifollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['transkiroku'])
        self.customSetGeometry(self.minifollowswitch, 250, 260, 20,20)
        self.minifollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('transkiroku',x)) 

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 290, 200, 20)
        label.setText("优先使用的翻译源：")
        transkirokuuse =QComboBox(self.tab_4) 
        self.customSetGeometry(transkirokuuse, 250, 290, 100,20) 
        transkirokuuse.addItems([globalconfig['fanyi'][k]['name'] for k  in globalconfig['fanyi']])
        transkirokuuse.setCurrentIndex(list(globalconfig['fanyi'].keys()).index(globalconfig['transkirokuuse']))
        transkirokuuse.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('transkirokuuse',list(globalconfig['fanyi'].keys())[x]))
        
        bt = QPushButton(self.tab_4)
        self.customSetGeometry(bt, 20, 320, 200, 25)
        bt.setText("导出sqlite文件为json文件") 

        def _sqlite2json():
                f=QFileDialog.getOpenFileName(filter="*.sqlite")
                if f[0]!='' :
                        try:
                                sql=sqlite3.connect(f[0],check_same_thread=False)
                                ret=sql.execute(f'SELECT * FROM artificialtrans  ').fetchall()
                                js={}
                                for _id,source,mt,ut  in ret:
                                        js[source]={'userTrans':ut,'machineTrans':mt}
                                with open(os.path.join(os.path.dirname(f[0]), os.path.basename(f[0]).replace('.'+os.path.basename(f[0]).split('.')[-1],'.json')),'w',encoding='utf8') as ff:
                                        ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
                        except:
                                print_exc()
        bt.clicked.connect(lambda x:_sqlite2json()) 
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 110, 200, 20)
        # #label.setText("窗口失去焦点不再置顶")
        # label.setText("窗口失去焦点最小化")
        # self.focusfollowswitch =gui.switch.SwitchButton(self.tab_4, sign= globalconfig['focusfollow'], startX=(65-20)*self.rate)
        # self.customSetGeometry(self.focusfollowswitch, 200,110, 65, 20)
        # self.focusfollowswitch.checkedChanged.connect(lambda x:globalconfig.__setitem__('focusfollow',x)) 
        # #self.focusfollowswitch.checkedChanged.connect(lambda x:setss(self,x)) 
        self.hookpid=None
        self.minmaxmoveoberve=subproc('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE)  
        self.minmaxmoveobservethread=threading.Thread(target=minmaxmoveobservefunc,args=(self,))
        self.minmaxmoveobservethread.start()

        self.autostarthooksignal.connect(functools.partial(autostarthookfunction,self))
        

def autostarthookfunction(self,arch,pid,pexe,hookcode):
          
         
        self.hookpid=pid
        from textsource.textractor import textractor
        self.object.hookselectdialog.changeprocessclearsignal.emit()
        if self.object.savetextractor:
                self.object.textsource=self.object.savetextractor
                self.object.textsource.reset(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,pexe,arch,True,hookcode)

        else:
                self.object.textsource=textractor(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,pexe,arch,True,hookcode) 
                self.object.savetextractor=self.object.textsource
 
def minmaxmoveobservefunc(self):
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                if globalconfig['sourcestatus']['textractor']==False:
                        continue
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
                
                if self.hookpid:
                      
                     if pid==self_pid:
                            continue
                     plist=getwindowlist()
                     if self.hookpid not in plist:
                            #print('game exit')
                            self.hookpid=None
                            self.object.textsource=None
                            continue
                     if pid==self.hookpid: 
                        if action==1 and globalconfig['movefollow']:
                                self.movestart=[x1,y1,x2,y2]
                                
                        elif action==2 and globalconfig['movefollow']: 
                                moveend=[x1,y1,x2,y2]
                                self.object.translation_ui.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                        elif action==3 and globalconfig['minifollow']: 
                                self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                        elif action==4 and  globalconfig['minifollow']:
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))
              