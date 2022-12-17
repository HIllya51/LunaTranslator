import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QGridLayout
import qtawesome 
 
from utils.config import globalconfig 
from gui.inputdialog import multicolorset
import functools

import gui.attachprocessdialog  
import gui.selecthook  
from gui.inputdialog import getsomepath1
def setTabcishu(self) :
       
        def __changemecabstate(self,x):
                globalconfig['mecab']['use']=x 
                self.object.starthira()
         
         
        grids=[ 
                [('分词',10)],
                [('使用MeCab辞书分词',10),(self.getsimpleswitch(globalconfig['mecab'],'use',callback= lambda x: __changemecabstate(self,x)),1),self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'mecab',globalconfig['mecab'],'path' ,'mecab',lambda  :self.object.starthira(),True) ,icon='fa.gear',constcolor="#FF69B4"),'','','','','','','',''],
                [('不同词性颜色设置(需要Mecab)',10),'',self.getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4")],
                [''],
                [('开启快捷查词(点击原文可查词)',10),(self.getsimpleswitch(globalconfig,'usesearchword'),1),self.getcolorbutton(globalconfig,'',callback=self.object.translation_ui.searchwordW.show,icon='fa.search',constcolor="#FF69B4")],

                [''],
                [('辞书',10)],
        ]
        def cishuselect(self, who,checked ): 
            globalconfig['cishu'][who]['use']=checked 
            self.object.startxiaoxueguan(who) 
        for cishu in globalconfig['cishu']:
                grids.append([
                        (globalconfig['cishu'][cishu]['name'],10),
                        self.getsimpleswitch(globalconfig['cishu'][cishu],'use',callback=functools.partial( cishuselect,self,cishu)),
                        self.getcolorbutton(globalconfig,'',
                                callback= functools.partial(getsomepath1,self,globalconfig['cishu'][cishu]['name'],globalconfig['cishu'][cishu],'path' ,globalconfig['cishu'][cishu]['name'],functools.partial(self.object.startxiaoxueguan,cishu),globalconfig['cishu'][cishu]['isdir'],globalconfig['cishu'][cishu]['filter']) ,icon='fa.gear',constcolor="#FF69B4") 
                                if 'path' in globalconfig['cishu'][cishu] else ''
                ])
                 
        
   
        self.yitiaolong("辞书设置",grids)