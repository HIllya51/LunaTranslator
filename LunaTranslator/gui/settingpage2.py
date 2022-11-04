 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog,QSpinBox,QComboBox,QScrollArea,QLineEdit
from PyQt5.QtGui import QColor,QFont
import functools
from utils.config import globalconfig 
import os
import qtawesome
import gui.switchbutton
import gui.attachprocessdialog  
from traceback import print_exc
import gui.selecthook 
import importlib
from gui.inputdialog import GetUserPlotItems
def setTabTwo(self) :
  
        tab = QWidget()
        scroll = QScrollArea() 
        self.tab_widget.addTab(scroll, "翻译设置") 
          
        tab.resize(2000,scroll.height())
        scroll.setWidget(tab)
        scroll.setHorizontalScrollBarPolicy(1)
        masklabel=QLabel(tab)
        masklabel.setGeometry(0,0,2000,2000)
        masklabel.setStyleSheet("color:white;background-color:white;")
        

        self.tab_2=tab 


        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20,20, 140, 20)
        label.setText("是否显示翻译器名称")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['showfanyisource'] )
        self.customSetGeometry(p, 160, 20, 20,20 )
        p.clicked.connect(lambda x: globalconfig.__setitem__('showfanyisource',x))
 
        initfanyiswitchs_auto(self) 
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 50, 200, 20)
        label.setText("最短翻译字数")
        self.minlength=QSpinBox(self.tab_2)
        self.minlength.setMinimum(0)
        self.minlength.setMaximum(500)
        self.minlength.setValue(globalconfig['minlength']) 
        self.customSetGeometry(self.minlength, 150,50,50,20)
        self.minlength.valueChanged.connect(lambda x:globalconfig.__setitem__('minlength',x)) 



        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 220, 50, 200, 20)
        label.setText("最长翻译字数")
        self.maxlength=QSpinBox(self.tab_2)
        self.maxlength.setMinimum(0)
        self.maxlength.setMaximum(500)
        self.maxlength.setValue(globalconfig['maxlength']) 
        self.customSetGeometry(self.maxlength, 350, 50,50,20)
        self.maxlength.valueChanged.connect(lambda x:globalconfig.__setitem__('maxlength',x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 420, 50, 200, 20)
        label.setText("在线翻译超时(s)")
        self.translatortimeout=QSpinBox(self.tab_2)
        self.translatortimeout.setMinimum(1)
        self.translatortimeout.setMaximum(20)
        import socket
        socket.setdefaulttimeout(globalconfig['translatortimeout'])
        self.translatortimeout.setValue(globalconfig['translatortimeout']) 
        self.customSetGeometry(self.translatortimeout, 550,50,50,20)
        def __timeout(x):

            globalconfig.__setitem__('translatortimeout',x)
            socket.setdefaulttimeout(globalconfig['translatortimeout'])
        self.translatortimeout.valueChanged.connect(lambda x:__timeout(x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 220, 20, 200, 20)
        label.setText("源语言")
        self.srclangcom=QComboBox(self.tab_2) 
        self.srclangcom.addItems(['日文','英文']) 
        self.srclangcom.setCurrentIndex(globalconfig['srclang'])
        self.customSetGeometry(self.srclangcom, 350,20,50,20)
        self.srclangcom.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('srclang',x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20,80, 140, 20)
        label.setText("预翻译采用模糊匹配")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['premtsimiuse'] )
        self.customSetGeometry(p, 160, 80, 20,20 )
        p.clicked.connect(lambda x: globalconfig.__setitem__('premtsimiuse',x))

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 220, 80, 200, 20)
        label.setText("模糊匹配相似度限制")
        self.maxlength=QSpinBox(self.tab_2)
        self.maxlength.setMinimum(0)
        self.maxlength.setMaximum(500)
        self.maxlength.setValue(globalconfig['premtsimi']) 
        self.customSetGeometry(self.maxlength, 350, 80,50,20)
        self.maxlength.valueChanged.connect(lambda x:globalconfig.__setitem__('premtsimi',x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20,110, 140, 20)
        label.setText("使用代理(ip:port)")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['useproxy'] )
        self.customSetGeometry(p, 160, 110, 20,20 )
        def _setproxy(x):
            globalconfig.__setitem__('useproxy',x)
            if x:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
            else:
                os.environ['https_proxy']='' 
                os.environ['http_proxy']=''
        _setproxy(globalconfig['useproxy'])
        p.clicked.connect(lambda x: _setproxy(x))


        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 220, 110, 100, 20)
        label.setText("http(s):")
        l=QLineEdit(self.tab_2)
        self.customSetGeometry(l, 350,110, 200, 20)
        l.setText(globalconfig['proxy'])
        b=QPushButton('确定',self.tab_2)
        self.customSetGeometry(b, 550, 110, 50, 20)
        b.clicked.connect(lambda x: globalconfig.__setitem__('proxy',l.text()))
def initfanyiswitchs_auto(self):
        
        y=170
        x=20 

        
        lixians=set(('jb7','dreye','kingsoft'))
        alls=set(globalconfig['fanyi'].keys())
        mt=set(('rengong','premt'))
        online=alls-lixians-mt

        mianfei=set()
        for _ in online:
            if 'argsfile' not in globalconfig['fanyi'][_]:
                mianfei.add(_)
        
        shoufei=online-mianfei 

         
        y=initsome(self,x,y,lixians,'离线翻译')  
        y=initsome(self,x,y,mianfei,'免费在线翻译')
        y=initsome(self,x,y,shoufei,'注册在线翻译')
        y=initsome(self,x,y,mt,'预翻译')

        self.tab_2.setFixedHeight((y )*self.rate )
def initsome(self,x,_y,l,label):
    num=0
    
    y=_y
    label = QLabel(label,self.tab_2)
    self.customSetGeometry(label, x,y,100,20) 
    _y+=30
    for fanyi in globalconfig['fanyi']:
        if fanyi not in l:
            continue
        y=_y+30*(num//3)
        x=20+200*(num%3)
        try:
            importlib.import_module('translator.'+fanyi)
        except:
            print_exc()
            continue
        initfanyiswitchs(self,fanyi,(x, y,100, 20),(x+100, y, 20,20),(x+130, y, 20,20),(x+160, y, 20,20))
        num+=1
    y+=60
    return y
def initfanyiswitchs(self,name,namepos,switchpos,colorpos,settingpos):

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, *namepos)
        label.setText(globalconfig['fanyi'][name]['name']+":")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['fanyi'][name]['use'], textOff='关闭',textOn='使用')
        
        self.customSetGeometry(p, *switchpos)
        def fanyiselect( who,checked):
            if checked : 
                globalconfig['fanyi'][who]['use']=True
                self.object.prepare(who)

            else:
                globalconfig['fanyi'][who]['use']=False 
        p.clicked.connect(functools.partial( fanyiselect,name))
        s=QPushButton(qtawesome.icon('fa.paint-brush', color=globalconfig['fanyi'][name]['color']), "", self.tab_2)
         
        self.customSetIconSize(s, 20, 20)
        self.customSetGeometry(s, *colorpos) 
        s.setStyleSheet("background: transparent;" )
        s.clicked.connect(lambda: self.ChangeTranslateColor(name,s))  
     

        
        if 'argsfile' in globalconfig['fanyi'][name]:
            s1 = QPushButton( "", self.tab_2)
            self.customSetIconSize(s1, 20, 20)
            self.customSetGeometry(s1, *settingpos)
            s1.setStyleSheet("background: transparent;") 
            
            s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
            aclass=importlib.import_module('translator.'+name).TS
            df=aclass.defaultsetting()
            s1.clicked.connect(lambda x:GetUserPlotItems(self,globalconfig['fanyi'][name]['argsfile'],df,globalconfig['fanyi'][name]['name']+'设置'))
     