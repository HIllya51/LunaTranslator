 
from PyQt5.QtWidgets import QWidget,QLabel ,QComboBox,QScrollArea 
import functools
from utils.config import globalconfig  
import gui.switchbutton
import gui.attachprocessdialog  
from traceback import print_exc
import gui.selecthook  
from system_hotkey import SystemHotkey
import pyperclip   
key_first=['Ctrl','Shift','Alt','Win' ]
key_first_reg=['control','shift','alt','super' ]
key_second=['F'+chr(ord('1')+i) for i in range(9)]+['F10','F11','F12']+[chr(ord('A')+i) for i in range(26)]+[chr(ord('0')+i) for i in range(10)]
key_second_reg=['f'+chr(ord('1')+i) for i in range(9)]+['f10','f11','f12']+[chr(ord('a')+i) for i in range(26)]+[chr(ord('0')+i) for i in range(10)]
def setTab_quick(self) :
 
        tab = QWidget()
        scroll = QScrollArea() 
        self.tab_widget.addTab(scroll, "快捷键设置") 
          
        tab.resize(2000,scroll.height())
        scroll.setWidget(tab)
        scroll.setHorizontalScrollBarPolicy(1)
        masklabel=QLabel(tab)
        masklabel.setGeometry(0,0,2000,2000)
        masklabel.setStyleSheet("color:white;background-color:white;")
        

        self.tab_quick=tab

        self.hotkeys={}
        self.hotkeys_savelast={}
        self.usedkey=[]
        self.bindfunctions={
            '_A':lambda :self.object.settin_ui.clicksourcesignal.emit(0),
            '_B':lambda :self.object.settin_ui.clicksourcesignal.emit(1),
            '_C':lambda :self.object.settin_ui.clicksourcesignal.emit(2),

            '_1':self.object.translation_ui.startTranslater,
            '_2':self.object.translation_ui.changeTranslateMode,
            '_3':self.object.translation_ui.clickSettin,
            '_4':lambda: pyperclip.copy(self.object.translation_ui.original) ,
            '_5':self.object.translation_ui.changeshowhideraw,
            '_6':self.object.translation_ui.transhis.showsignal.emit,
            '_7':self.object.translation_ui.langdu,
            '_8':self.object.translation_ui.changemousetransparentstate,
            '_9':self.object.translation_ui.changetoolslockstate,
            '_10':self.object.translation_ui.showsavegame_signal.emit,
            '_11':self.object.translation_ui.settingprocess_signal.emit,
            '_12':self.object.translation_ui.settinghookthread_signal.emit,
            '_13':self.object.translation_ui.clickRange_signal.emit,
            '_14':self.object.translation_ui.showhide_signal.emit,
            '_15':self.object.translation_ui.bindcropwindow_signal.emit,
            '_16':self.object.translation_ui.showhideui,
            '_17':self.object.translation_ui.quitf_signal.emit,
            '_18':lambda:self.object.settin_ui.fontbigsmallsignal.emit(1),
            '_19':lambda:self.object.settin_ui.fontbigsmallsignal.emit(-1),
            '_20':self.object.translation_ui.fullsgame_signal.emit,
            '_21':self.object.translation_ui.grabwindowsignal.emit
        }
        label = QLabel(tab)
        self.customSetGeometry(label, 20, 25, 200, 20)
        label.setText("是否使用快捷键")
        p=gui.switchbutton.MySwitch(tab, sign=globalconfig['quick_setting']['use'] )
        self.customSetGeometry(p, 220, 25, 20,20 )
        def __enable(x ):
            globalconfig['quick_setting'].__setitem__('use',x)
            for quick in globalconfig['quick_setting']['all']:
                regist_or_not_key(self,quick,self.bindfunctions[quick])
        p.clicked.connect(lambda x: __enable(x))
        initfanyiswitchs_auto(self) 
         
def initfanyiswitchs_auto(self):
        num=0
        
        for quick in globalconfig['quick_setting']['all']:
            y=70+35*num
            x=20 
            initfanyiswitchs(self,quick,x,y)
            num+=1
        
        self.tab_quick.setFixedHeight((y+50)*self.rate )
def regist_or_not_key(self,name,callback):
    if self.hotkeys[name] :
        self.hotkeys[name].unregister(self.hotkeys_savelast[name])
        self.usedkey.remove(self.hotkeys_savelast[name])
    self.hotkeys[name]=None
    if globalconfig['quick_setting']['all'][name]['use'] and globalconfig['quick_setting']['use'] : 
        if  globalconfig['quick_setting']['all'][name]['key1']==-1 or globalconfig['quick_setting']['all'][name]['key2']==-1:
            return
        if (key_first_reg[globalconfig['quick_setting']['all'][name]['key1']],key_second_reg[globalconfig['quick_setting']['all'][name]['key2']]) in self.usedkey:
            return
        hk=SystemHotkey()
        try:
            hk.register((key_first_reg[globalconfig['quick_setting']['all'][name]['key1']],key_second_reg[globalconfig['quick_setting']['all'][name]['key2']]),callback=lambda x: callback()) 
            self.hotkeys_savelast[name]=(key_first_reg[globalconfig['quick_setting']['all'][name]['key1']],key_second_reg[globalconfig['quick_setting']['all'][name]['key2']])
            self.hotkeys[name]=hk
            self.usedkey.append((key_first_reg[globalconfig['quick_setting']['all'][name]['key1']],key_second_reg[globalconfig['quick_setting']['all'][name]['key2']]))
        except:
            print_exc()
def initfanyiswitchs(self,name,x,y):
        
        label = QLabel(self.tab_quick)
        self.customSetGeometry(label,x,y,200,20)
        label.setText(globalconfig['quick_setting']['all'][name]['name'])
        p=gui.switchbutton.MySwitch(self.tab_quick, sign=globalconfig['quick_setting']['all'][name]['use'] )
        
        self.customSetGeometry(p,x+200,y,20,20) 
        def fanyiselect( who,checked): 
            globalconfig['quick_setting']['all'][who]['use']=checked 
            regist_or_not_key(self,name,self.bindfunctions[name])
        p.clicked.connect(functools.partial( fanyiselect,name))
        
        key1=QComboBox(self.tab_quick)
        self.customSetGeometry(key1,x+230,y,100,20)
        key2=QComboBox(self.tab_quick)
        self.customSetGeometry(key2,x+340,y,100,20)

        key1.addItems(key_first)
        key2.addItems(key_second)
 
        key1.setCurrentIndex(globalconfig['quick_setting']['all'][name]['key1'])
        key2.setCurrentIndex(globalconfig['quick_setting']['all'][name]['key2'])
        def __changekey(s,who,keyn,x):
            back=globalconfig['quick_setting']['all'][who][keyn]
            globalconfig['quick_setting']['all'][who][keyn]=x
            if (key_first_reg[globalconfig['quick_setting']['all'][name]['key1']],key_second_reg[globalconfig['quick_setting']['all'][name]['key2']]) in self.usedkey:
                globalconfig['quick_setting']['all'][who][keyn]=back
                {'key1':key1,'key2':key2}[keyn].setCurrentIndex(back)
                return
            regist_or_not_key(s,who,self.bindfunctions[name])
        key1.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key1'))
        key2.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key2'))
        self.hotkeys[name]=None
      
        regist_or_not_key(self,name,self.bindfunctions[name])
        