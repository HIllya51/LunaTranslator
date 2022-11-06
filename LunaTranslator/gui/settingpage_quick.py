 
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
            '_21':self.object.translation_ui.grabwindowsignal.emit,
            '_22':self.object.translation_ui.muteprocessignal.emit
        }
         
        
        
         
        grids=[
            [(QLabel("是否使用快捷键"),4),self.getsimpleswitch(globalconfig['quick_setting']  ,'use',callback=functools.partial(__enable,self )  ),(QLabel(''),10)]
        ]
        for name in globalconfig['quick_setting']['all']: 
            key1=QComboBox() 
            key2=QComboBox() 
            key1.addItems(key_first)
            key2.addItems(key_second)
    
            key1.setCurrentIndex(globalconfig['quick_setting']['all'][name]['key1'])
            key2.setCurrentIndex(globalconfig['quick_setting']['all'][name]['key2'])
            
            key1.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key1',key1,key2))
            key2.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key2',key1,key2))
            self.hotkeys[name]=None
        
            regist_or_not_key(self,name,self.bindfunctions[name])
            grids.append(
                [(QLabel(globalconfig['quick_setting']['all'][name]['name']),4),
                self.getsimpleswitch(globalconfig['quick_setting']['all'][name] ,'use',callback=functools.partial(fanyiselect,self,name)),
                (key1,3),
                (key2,3)
                ]
            )
        self.yitiaolong("快捷键设置",grids)
def __enable(self,x ):
            globalconfig['quick_setting'].__setitem__('use',x)
            for quick in globalconfig['quick_setting']['all']:
                regist_or_not_key(self,quick,self.bindfunctions[quick])
def fanyiselect( self,who,checked): 
            globalconfig['quick_setting']['all'][who]['use']=checked 
            regist_or_not_key(self,who,self.bindfunctions[who])
def __changekey(self,who,keyn, key1,key2,x):
    back=globalconfig['quick_setting']['all'][who][keyn]
    globalconfig['quick_setting']['all'][who][keyn]=x
    if (key_first_reg[globalconfig['quick_setting']['all'][who]['key1']],key_second_reg[globalconfig['quick_setting']['all'][who]['key2']]) in self.usedkey:
        globalconfig['quick_setting']['all'][who][keyn]=back
        {'key1':key1,'key2':key2}[keyn].setCurrentIndex(back)
        return
    regist_or_not_key(self,who,self.bindfunctions[who])
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
 