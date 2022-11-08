import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QGridLayout
import qtawesome 
 
from utils.config import globalconfig 
from gui.inputdialog import multicolorset
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
from gui.inputdialog import getsomepath1
def setTabcishu(self) :
       
        def __changemecabstate(self,x):
                globalconfig['mecab']['use']=x 
                self.object.starthira()
         
         
        grids=[ 
                [(QLabel('使用MeCab辞书分词'),10),(self.getsimpleswitch(globalconfig['mecab'],'use',callback= lambda x: __changemecabstate(self,x)),1),self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'mecab',globalconfig['mecab'],'path' ,'mecab',lambda  :self.object.starthira(),True) ,icon='fa.gear',constcolor="#FF69B4"),'','','','','','','',''],
                [(QLabel('不同词性颜色设置(需要Mecab，否则为随机颜色)'),10),'',self.getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('开启快捷查词(点击原文可查词)'),10),(self.getsimpleswitch(globalconfig,'usesearchword'),1),self.getcolorbutton(globalconfig,'',callback=self.object.translation_ui.searchwordW.show,icon='fa.search',constcolor="#FF69B4")],
                [(QLabel('小学馆辞书'),10),'',self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'小学馆',globalconfig['xiaoxueguan'],'path' ,'小学馆',lambda  :self.object.startxiaoxueguan(1),False) ,icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('灵格斯词典'),10),'',self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'灵格斯',globalconfig['linggesi'],'path' ,'灵格斯',lambda  :self.object.startxiaoxueguan(3),True) ,icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('DICT词典(日英)'),10),'',self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'edict',globalconfig['edict'],'path' ,'edict',lambda  :self.object.startxiaoxueguan(2),False),icon='fa.gear',constcolor="#FF69B4")],
              
        ] 
   
        self.yitiaolong("辞书设置",grids)