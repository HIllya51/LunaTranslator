  
import functools,win32api,win32gui,win32process
import sqlite3
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QGridLayout
import functools 
from traceback import print_exc
from collections import OrderedDict
import time,uuid
from PyQt5.QtWidgets import    QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout
import qtawesome
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import subprocess 
from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox  
from utils.subproc import subproc
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton 
from PyQt5.QtGui import QColor,QFont,QPixmap,QIcon
import functools,win32file
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize 
import subprocess
from utils.config import globalconfig ,savehook_new,savehook_new2
from utils.getpidlist import getwindowlist,getExeIcon,getpidexe
import threading
import json
from utils.le3264 import le3264run 
from utils.chaos import checkencoding
from utils.config import globalconfig ,_TR,_TRL
import os
import win32con,win32api 

def autosaveshow(object):
     
    dialog = QDialog(object,Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR('已保存游戏'))
    #dialog.setWindowModality(Qt.ApplicationModal) 
    formLayout = QVBoxLayout(dialog)  # 配置layout
    
    def selectexe(item,mm,r):
        f=QFileDialog.getOpenFileName(directory=item.savetext )
        res=f[0]
        if res!='':
                res=res.replace('/','\\')
                savehook_new[res]=savehook_new[item.savetext]
                savehook_new.pop(item.savetext) 
                savehook_new2[res]=savehook_new2[item.savetext]
                savehook_new2.pop(item.savetext)
                item.savetext=res 
                transparent=QPixmap(100,100)
                transparent.fill(QColor.fromRgba(0))
                icon=getExeIcon(res)
                if icon is None:
                    icon=transparent
                icon=QIcon(icon) 
                mm.setItem(r, 1, QStandardItem(icon,''))  

    if True:
        model=QStandardItemModel(  dialog)
        table = QTableView(dialog)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
        table.setWordWrap(False) 
        table.setModel(model) 
        
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
                keyitem=QStandardItem()
                keyitem.savetext=k
                model.setItem(row, 2, keyitem) 
                model.setItem(row, 0, QStandardItem(''))  
                model.setItem(row, 3,QStandardItem(savehook_new2[k]['title']) ) 
                table.setIndexWidget(model.index(row, 0),object.getsimpleswitch(savehook_new2[k],'leuse'))
                _=QPushButton()
                _.setIcon(qtawesome.icon( 'fa.gear', color="#FF69B4"))  
                _.setStyleSheet("background: transparent;") 
                _.clicked.connect(functools.partial(selectexe,keyitem,model,row ))
                table.setIndexWidget(model.index(row, 2),_) 
                # item = QStandardItem(json.dumps(js[k],ensure_ascii=False))
                # model.setItem(row, 2, item)
                row+=1
        model.setHorizontalHeaderLabels(_TRL(['转区','','路径', '游戏']))#,'HOOK'])
         
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText(_TR('开始游戏'))
        def clicked(): 
                try:
                        
                    game=model.item(table.currentIndex().row(),2).savetext
                    if os.path.exists(game):
                        #subprocess.Popen(model.item(table.currentIndex().row(),1).text()) 
                        print(game)
                        if game not in savehook_new2:
                                savehook_new2[game]={}
                                savehook_new2[game]['leuse']=True
                                savehook_new2[game]['title']=game
                        if savehook_new2[game]['leuse'] :
                                le3264run(game)
                        else:
                                win32api.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW)
                                 
                                 
                        savehook_new.move_to_end(game,False)
                        dialog.close() 
                except:
                        print_exc()
        button.clicked.connect(clicked)
        button3=QPushButton(dialog)
        button3.setText(_TR('添加游戏'))
        
        def clicked3(): 
                
                f=QFileDialog.getOpenFileName(directory='' )
                res=f[0]
                if res!='':
                        row=0#model.rowCount() 
                        res=res.replace('/','\\')
                        if res in savehook_new:
     
                                return
                        transparent=QPixmap(100,100)
                        transparent.fill(QColor.fromRgba(0))
                        icon=getExeIcon(res)
                        if icon is None:
                                icon=transparent
                        icon=QIcon(icon) 
                        
                        #model.setItem(row, 1, QStandardItem(icon,''))  
                        keyitem=QStandardItem()
                        keyitem.savetext=res
                        # model.setItem(row, 2, keyitem) 
                        # model.setItem(row, 0, QStandardItem(''))  
                        # model.setItem(row, 3,QStandardItem(res) ) 

                        model.insertRow(0,[QStandardItem(''),QStandardItem(icon,''),keyitem,QStandardItem(res)])
                        savehook_new2[res]={}
                        savehook_new2[res]['leuse']=True
                        savehook_new2[res]['title']=res 
 
                        savehook_new[res]=[]
                        savehook_new.move_to_end(res,False)
                        table.setIndexWidget(model.index(row, 0),object.getsimpleswitch(savehook_new2[res],'leuse'))
                        
                        _=QPushButton()
                        _.setIcon(qtawesome.icon( 'fa.gear', color="#FF69B4"))
                        
                        _.setStyleSheet("background: transparent;") 
                        _.clicked.connect(functools.partial(selectexe,keyitem ))
                        table.setIndexWidget(model.index(row, 2),_) 
                        table.setCurrentIndex(model.index(row,0)) 
                        
        button3.clicked.connect(clicked3)
        button2=QPushButton(dialog)
        button2.setText(_TR('删除游戏'))
        def clicked2(): 
                
                savehook_new.pop(model.item(table.currentIndex().row(),2).savetext)
                
                model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
         
        formLayout.addWidget(table) 
        formLayout.addWidget(button) 
        formLayout.addWidget(button3) 
        formLayout.addWidget(button2) 
        dialog.resize(QSize(800,400))
        def closeEvent(  a0  ) -> None:
                button.setFocus()
                rows=model.rowCount() 
                 
                for row in range(rows):  
                        savehook_new2[model.item(row,2).savetext]['title']=model.item(row,3).text()
                 
                return QDialog().closeEvent(a0)
    dialog.closeEvent=closeEvent
    dialog.show()

def codeacceptdialog(object ,title=  '接受的编码' ,label=[  '接受的编码'] ):
    dialog = QDialog(object,Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR(title))
    #dialog.setWindowModality(Qt.ApplicationModal)
    
    formLayout = QVBoxLayout(dialog)  # 配置layout
        
    model=QStandardItemModel(len(globalconfig['accept_encoding']),1 , dialog)
    row=0
    for key in  (globalconfig['accept_encoding']):                                   # 2
            
            item = QStandardItem( key )
            model.setItem(row, 0, item)
            row+=1
    model.setHorizontalHeaderLabels(_TRL(label))
    table = QTableView(dialog)
    table.setModel(model)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
    #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #table.clicked.connect(self.show_info)
    button=QPushButton(dialog)
    button.setText(_TR('添加行'))
    def clicked1(): 
        model.insertRow(0,[ QStandardItem('')]) 
    button.clicked.connect(clicked1)
    button2=QPushButton(dialog)
    button2.setText(_TR('删除选中行'))
    def clicked2():
        
        model.removeRow(table.currentIndex().row())
    button2.clicked.connect(clicked2) 
    def clicked3(_): 
        button.setFocus() 
        rows=model.rowCount() 
        ll=[]
        for row in range(rows):
                
            code=model.item(row,0).text()
            
            if checkencoding(code):
                ll.append(code) 
        globalconfig['accept_encoding']=ll 
         
    dialog.closeEvent=(clicked3)
    formLayout.addWidget(table)
    formLayout.addWidget(button)
    formLayout.addWidget(button2) 
    dialog.resize(QSize(600,400))
    dialog.show()


def changecodepage(self,_):
        try:

                globalconfig['codepage_index']=_
                self.object.textsource.setcodepage()
        except:
                pass
def changedelay(self,_):
        try:

                globalconfig['textthreaddelay']=_
                self.object.textsource.setdelay()
        except:
                pass
def setTab4(self) :

        s=QComboBox( )  
        s.addItems(_TRL(['日语(CP932,SHIFT-JIS)','UTF8(CP65001)','简体中文(CP936,GBK)','繁体中文(CP950,BIG5)','韩语(CP949,EUC-KR)','越南语(CP1258)','泰语(CP874)','阿拉伯语(CP1256)','希伯来语(CP1255)','土耳其语(CP1254)','希腊语(CP1253)','北欧(CP1257)','中东欧(CP1250)','西里尔(CP1251)','拉丁(CP1252)']))
        s.setCurrentIndex(globalconfig['codepage_index'])
        codepagecombo=s
        s.currentIndexChanged.connect(functools.partial(changecodepage,self))

        grids=[
                
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','','','','','','',''],
               # [('转区方式',5),(self.getsimplecombobox(_TRL(['Locale.Emulator','Locale_Remulator']),globalconfig,'localeswitchmethod'),5)],
               # [('LocaleEmulator路径设置',5),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'LocaleEmulator',globalconfig,'LocaleEmulator','LocaleEmulator',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1),("不支持64位",5)],
              #  [('Locale_Remulator路径设置',5),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'Locale_Remulator',globalconfig,'Locale_Remulator','Locale_Remulator',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1),("支持64位，但是不一定管用",8)],
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:autosaveshow(self)),1)],

                [('代码页',5),(codepagecombo,5)],
                [('刷新延迟(ms)',5),(self.getspinbox(1,10000,globalconfig,'textthreaddelay',callback=functools.partial(changedelay,self)),3)],
                [('过滤乱码文本',5),(self.getsimpleswitch(globalconfig,'filter_chaos_code'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [('移除非选定HOOK',5),(self.getsimpleswitch(globalconfig,'remove_useless_hook'),1) ],
        ]
         
        self.yitiaolong("HOOK设置",grids) 
        