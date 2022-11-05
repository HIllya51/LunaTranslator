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
from gui.inputdialog import getsomepath
def setTabcishu(self) :
      
        t = QWidget()
        self.tab_widget.addTab(t, "辞书设置")  
        lay=QGridLayout( )    
        t.setLayout(lay)  
        def __changemecabstate(self,x):
                globalconfig['mecab']['use']=x 
                self.object.starthira()
        def __getmecabpath(self):
                getsomepath(self,'mecab',globalconfig['mecab']['path'],'mecab',lambda x:globalconfig['mecab'].__setitem__('path',x),True)
                self.object.starthira()
        def __getpath(self):
                getsomepath(self,'小学馆',globalconfig['xiaoxueguan']['path'],'小学馆',lambda x:globalconfig['xiaoxueguan'].__setitem__('path',x),False)
                self.object.startxiaoxueguan(1)
        def __getpath2(self):
                getsomepath(self,'灵格斯',globalconfig['linggesi']['path'],'灵格斯',lambda x:globalconfig['linggesi'].__setitem__('path',x),True)
                self.object.startxiaoxueguan(3)
        def __getpath3(self):
                getsomepath(self,'edict',globalconfig['edict']['path'],'edict',lambda x:globalconfig['edict'].__setitem__('path',x),False)
                self.object.startxiaoxueguan(2)
        grids=[ 
                [(QLabel('使用MeCab辞书分词'),4),(self.getsimpleswitch(globalconfig['mecab'],'use',callback= lambda x: __changemecabstate(self,x)),1),self.getcolorbutton(globalconfig,'',callback=lambda  : __getmecabpath(self),icon='fa.gear',constcolor="#FF69B4"),'','','',''],
                [(QLabel('显示不同颜色词性(需要Mecab)'),4),(self.getsimpleswitch(globalconfig,'showcixing'),1),self.getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('开启快捷查词(点击原文可查词)'),4),(self.getsimpleswitch(globalconfig,'usesearchword'),1),self.getcolorbutton(globalconfig,'',callback=self.object.translation_ui.searchwordW.show,icon='fa.search',constcolor="#FF69B4")],
                [(QLabel('小学馆辞书'),4),'',self.getcolorbutton(globalconfig,'',callback=lambda  :__getpath(self),icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('灵格斯词典'),4),'',self.getcolorbutton(globalconfig,'',callback=lambda  :__getpath2(self),icon='fa.gear',constcolor="#FF69B4")],
                [(QLabel('DICT词典(日英)'),4),'',self.getcolorbutton(globalconfig,'',callback=lambda  :__getpath3(self),icon='fa.gear',constcolor="#FF69B4")],
                [''],
                [''],
                [''],
                [''],
                ['']
        ] 
   
        self.automakegrid(lay,grids)