 
import functools
from myutils.config import globalconfig   ,static_data,_TR
from traceback import print_exc 
from myutils.winsyshotkey import SystemHotkey ,registerException
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox,QKeySequenceEdit,QLabel
import winsharedutils 
import gobject
from gui.usefulwidget import getsimpleswitch
from myutils.hwnd import grabwindow
def setTab_quick_direct(self):
    self.hotkeymanager=SystemHotkey()
    self.referlabels={}
    self.registok={}
    self.bindfunctions={ 
            '_A':lambda :gobject.baseobject.settin_ui.clicksourcesignal.emit('copy'),
            '_B':lambda :gobject.baseobject.settin_ui.clicksourcesignal.emit('ocr'),
            '_C':lambda :gobject.baseobject.settin_ui.clicksourcesignal.emit('texthook'),

            '_1':gobject.baseobject.translation_ui.startTranslater,
            '_2':gobject.baseobject.translation_ui.changeTranslateMode,
            '_3':self.showsignal.emit,
            '_4':lambda:winsharedutils.clipboard_set( gobject.baseobject.currenttext) ,
            '_5':gobject.baseobject.translation_ui.changeshowhideraw,
            '_6':lambda: gobject.baseobject.transhis.showsignal.emit(),
            '_7':gobject.baseobject.translation_ui.langdu,
            '_8':lambda: gobject.baseobject.translation_ui.changemousetransparentstate(0),
            '_9':gobject.baseobject.translation_ui.changetoolslockstate,
            '_10':lambda : gobject.baseobject.translation_ui.showsavegame_signal.emit(0),
            '_10_2':lambda : gobject.baseobject.translation_ui.showsavegame_signal.emit(1),
            '_11':lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit(),
            '_12':lambda:gobject.baseobject.hookselectdialog.showsignal.emit(),
            '_13':lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(False),
            '_14':gobject.baseobject.translation_ui.showhide_signal.emit,
            '_15':gobject.baseobject.translation_ui.bindcropwindow_signal.emit,
            '_16':gobject.baseobject.translation_ui.showhideuisignal.emit,
            '_17':gobject.baseobject.translation_ui.quitf_signal.emit,
            '_18':lambda:gobject.baseobject.settin_ui.fontbigsmallsignal.emit(1),
            '_19':lambda:gobject.baseobject.settin_ui.fontbigsmallsignal.emit(-1),
            '_20':gobject.baseobject.translation_ui.fullsgame_signal.emit,
            '_21':lambda:grabwindow(),
            '_22':gobject.baseobject.translation_ui.muteprocessignal.emit,
            "_23":lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(True),
            
        }
    for name in globalconfig['quick_setting']['all']: 
        if name not in self.bindfunctions:
                    continue 
        referlabel=QLabel()
        self.referlabels[name]=referlabel
        regist_or_not_key(self,name )

def setTab_quick(self):
    
 
    self.tabadd_lazy(self.tab_widget, ('快捷按键'), lambda :setTab_quick_lazy(self))   


class CustomKeySequenceEdit(QKeySequenceEdit):
    changeedvent=pyqtSignal(str)
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)
        
    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence() 
        if len(value.toString()):
            self.clearFocus()
        self.changeedvent.emit(value.toString().replace('Meta','Win'))
        self.setKeySequence(QKeySequence(value)) 
def setTab_quick_lazy(self) : 
         
        grids=[
            [(("是否使用快捷键"),4),getsimpleswitch(globalconfig['quick_setting']  ,'use',callback=functools.partial(__enable,self )  ),((''),8)]
        ]
        for name in globalconfig['quick_setting']['all']: 
                if name not in self.bindfunctions:
                    continue
                key1=CustomKeySequenceEdit(QKeySequence(globalconfig['quick_setting']['all'][name]['keystring'])) 
                key1.changeedvent.connect(functools.partial(__changekeynew,self,name))  
                 
                grids.append(
                    [((globalconfig['quick_setting']['all'][name]['name']),4),
                    getsimpleswitch(globalconfig['quick_setting']['all'][name] ,'use',callback=functools.partial(fanyiselect,self,name)),
                    (key1,2),
                    (self.referlabels[name],4)
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
                regist_or_not_key(self,quick )
def fanyiselect( self,who,checked):  
            regist_or_not_key(self,who )
class unsupportkey(Exception):
     pass
def parsekeystringtomodvkcode(keystring):
    keys=[]
    mode=0
    if keystring[-1]=='+':
        keys+=['+']
        keystring=keystring[:-2]
    ksl=keystring.split('+')
    ksl=ksl+keys
    unsupports=[] 
    if ksl[-1].upper() in static_data['vkcode_map']: 
        vkcode=static_data['vkcode_map'][ksl[-1].upper()]
    else:
        unsupports.append(ksl[-1])
     
    for k in ksl[:-1]: 
        if k.upper() in static_data['mod_map']:
            mode=mode| static_data['mod_map'][k.upper()]
        else:
            unsupports.append(k)
    if len(unsupports):
          raise unsupportkey(unsupports)
    return mode,vkcode
def __changekeynew(self,name,keystring):
    globalconfig['quick_setting']['all'][name]['keystring']=keystring
     
    regist_or_not_key(self,name)  
def regist_or_not_key(self,name):
    self.referlabels[name].setText('')
    
    if name in self.registok:
        self.hotkeymanager.unregister(self.registok[name]) 

    keystring=globalconfig['quick_setting']['all'][name]['keystring']
    if keystring=='' or (not (globalconfig['quick_setting']['all'][name]['use'] and globalconfig['quick_setting']['use'])) :
        return
    
    try:
        mode,vkcode=parsekeystringtomodvkcode(keystring)
    except unsupportkey as e: 
        self.referlabels[name].setText(_TR("不支持的键位")+','.join(e.args[0]))
        return
    
    try:
        self.hotkeymanager.register((mode,vkcode),callback=self.bindfunctions[name]) 
        self.registok[name]=(mode,vkcode)
    except registerException:
        self.referlabels[name].setText(_TR("快捷键冲突") )
    