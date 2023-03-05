 
import functools
from utils.config import globalconfig   
from traceback import print_exc 
from system_hotkey import SystemHotkey 
import pyperclip
from utils.somedef import key_first,key_first_reg,key_second,key_second_reg
def setTab_quick_direct(self):
    self.hotkeys={}
    self.hotkeys_savelast={}
    self.usedkey=[] 
        
    self.bindfunctions={ 
            '_A':lambda :self.object.settin_ui.clicksourcesignal.emit('copy'),
            '_B':lambda :self.object.settin_ui.clicksourcesignal.emit('ocr'),
            '_C':lambda :self.object.settin_ui.clicksourcesignal.emit('textractor'),
            '_D':lambda :self.object.settin_ui.clicksourcesignal.emit('embedded'),
            '_E':lambda :self.object.settin_ui.clicksourcesignal.emit('txt'),

            '_1':self.object.translation_ui.startTranslater,
            '_2':self.object.translation_ui.changeTranslateMode,
            '_3':self.showsignal.emit,
            '_4':lambda:pyperclip.copy( self.object.translation_ui.original) ,
            '_5':self.object.translation_ui.changeshowhideraw,
            '_6':lambda: self.object.transhis.showsignal.emit(),
            '_7':self.object.translation_ui.langdu,
            '_8':self.object.translation_ui.changemousetransparentstate,
            '_9':self.object.translation_ui.changetoolslockstate,
            '_10':self.object.translation_ui.showsavegame_signal.emit,
            '_11':lambda :self.object.AttachProcessDialog.showsignal.emit(),
            '_12':lambda:self.object.hookselectdialog.showsignal.emit(),
            '_13':lambda: self.object.translation_ui.clickRange_signal.emit(False),
            '_14':self.object.translation_ui.showhide_signal.emit,
            '_15':self.object.translation_ui.bindcropwindow_signal.emit,
            '_16':self.object.translation_ui.showhideuisignal.emit,
            '_17':self.object.translation_ui.quitf_signal.emit,
            '_18':lambda:self.object.settin_ui.fontbigsmallsignal.emit(1),
            '_19':lambda:self.object.settin_ui.fontbigsmallsignal.emit(-1),
            '_20':self.object.translation_ui.fullsgame_signal.emit,
            '_21':self.object.translation_ui.grabwindowsignal.emit,
            '_22':self.object.translation_ui.muteprocessignal.emit,
            "_23":  self.object.translation_ui.rangequick.emit ,
            
        }
    for name in globalconfig['quick_setting']['all']: 
        if name not in self.bindfunctions:
                    continue
        self.hotkeys[name]=None
        regist_or_not_key(self,name,self.bindfunctions[name])

def setTab_quick(self):
    
 
    self.tabadd_lazy(self.tab_widget, ('快捷按键'), lambda :setTab_quick_lazy(self))   
def setTab_quick_lazy(self) :
  
        
        
         
        grids=[
            [(("是否使用快捷键"),4),self.getsimpleswitch(globalconfig['quick_setting']  ,'use',callback=functools.partial(__enable,self )  ),((''),8)]
        ]
        for name in globalconfig['quick_setting']['all']: 
                if name not in self.bindfunctions:
                    continue
                key1=self.getsimplecombobox(key_first,globalconfig['quick_setting']['all'][name],'key1')
                key2=self.getsimplecombobox(key_second,globalconfig['quick_setting']['all'][name],'key2') 
                key1.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key1',key1,key2))
                key2.currentIndexChanged.connect(functools.partial(__changekey,self,name,'key2',key1,key2))
                
                grids.append(
                    [((globalconfig['quick_setting']['all'][name]['name']),4),
                    self.getsimpleswitch(globalconfig['quick_setting']['all'][name] ,'use',callback=functools.partial(fanyiselect,self,name)),
                    (key1,2),
                    (key2,2)
                    ]
                )
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        return gridlayoutwidget
        #self.yitiaolong("快捷按键",grids)
def __enable(self,x ): 
            for quick in globalconfig['quick_setting']['all']:
                if quick not in self.bindfunctions:
                    continue
                regist_or_not_key(self,quick,self.bindfunctions[quick])
def fanyiselect( self,who,checked):  
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
        try:
            k1,k2=self.hotkeys_savelast[name]
            if k1=="":
                self.hotkeys[name].unregister((k2,))
            else:
                self.hotkeys[name].unregister((k1,k2))
            self.usedkey.remove(self.hotkeys_savelast[name])
        except:
            pass
    self.hotkeys[name]=None
    if globalconfig['quick_setting']['all'][name]['use'] and globalconfig['quick_setting']['use'] : 
        
        k1index=globalconfig['quick_setting']['all'][name]['key1']
        k2index=globalconfig['quick_setting']['all'][name]['key2']
        if k1index==-1 or k2index==-1:
            return
        k1=key_first_reg[k1index]
        k2=key_second_reg[k2index]
        if (k1,k2) in self.usedkey:
            return
        hk=SystemHotkey()
        try:
            if k1=="":

                hk.register((k2,),callback=lambda x: callback()) 
            else:
                hk.register((k1,k2),callback=lambda x: callback()) 
            self.hotkeys_savelast[name]=(k1,k2)
            self.hotkeys[name]=hk
            self.usedkey.append((k1,k2))
        except:
            print_exc()
 