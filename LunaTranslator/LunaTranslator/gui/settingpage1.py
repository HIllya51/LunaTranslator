 
import functools    
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QFontComboBox  ,QLabel,QLineEdit
from gui.settingpage_ocr import getocrgrid  
from myutils.config import globalconfig ,_TR,_TRL  ,static_data
from gui.dialog_savedgame import dialog_savedgame 
import threading,gobject
from gui.usefulwidget import getsimplecombobox,getspinbox,getcolorbutton,yuitsu_switch,getsimpleswitch
from gui.codeacceptdialog import codeacceptdialog   
def gethookgrid(self) :
 
        grids=[
                [('选择游戏',5),self.selectbutton,('',5)],
                [('选择文本',5),self.selecthookbutton],
                [''],
                [('检测到游戏时自动开始',5),(getsimpleswitch(globalconfig,'autostarthook'),1)],
                
                [('已保存游戏',5),(getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],
                [''],
                [('过滤反复刷新的句子',5),(getsimpleswitch(globalconfig,'direct_filterrepeat'),1)],
                [('刷新延迟(ms)',5),(getspinbox(1,10000,globalconfig,'textthreaddelay',callback=lambda x:gobject.baseobject.textsource.setdelay()),3)],
                [('过滤包含乱码的文本行',5),(getsimpleswitch(globalconfig,'filter_chaos_code'),1),(getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                
        ]
         
        return grids

def gethookembedgrid(self) :  
        def __insertspace(i):
                if i==0:
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceSmartInserted',False )
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceAlwaysInserted',False )
                elif i==1:
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceSmartInserted',False )
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceAlwaysInserted',True )
                elif i==2:
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceSmartInserted',True )
                        gobject.baseobject.textsource.sendSetting('embeddedSpaceAlwaysInserted',False )
        self.gamefont_comboBox = QFontComboBox( ) 
        def callback(x):
                globalconfig['embedded'].__setitem__('changefont_font',x)
                try:
                        gobject.baseobject.textsource.sendSetting('embeddedFontFamily',globalconfig['embedded']['changefont_font'] if x else '')
                except:
                        pass
        self.gamefont_comboBox.activated[str].connect(callback)   
        self.gamefont_comboBox.setCurrentFont(QFont(globalconfig['embedded']['changefont_font']))  
        grids=[
                 [('选择游戏',5),self.selectbuttonembed],
                 [''],
                [('保留原文',5),(getsimpleswitch( globalconfig['embedded'],'keeprawtext',callback=lambda x:gobject.baseobject.textsource.sendSetting('embeddedScenarioTextVisible',x ))  ,1) ],
                 
                [('翻译等待时间(s)',5),'',(getspinbox(0,30,globalconfig['embedded'],'timeout_translate',double=True,step=0.1,callback=lambda x:gobject.baseobject.textsource.sendSetting('embeddedTranslationWaitTime',int(x*1000))),3) ],
                [('使用最快翻译而非指定翻译器',5),(getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
                [('内嵌的翻译器',5),'',(getsimplecombobox(_TRL([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']]),globalconfig['embedded'],'translator'),5) ],
                [('将汉字转换成繁体/日式汉字',5),(getsimpleswitch( globalconfig['embedded'] ,'trans_kanji'),1) ],
                [('在重叠显示的字间插入空格',5),'',(getsimplecombobox(_TRL(['不插入空格','每个字后插入空格','仅在无法编码的字后插入']),globalconfig['embedded'],'insertspace_policy',callback=__insertspace),5) ],
                [('修改游戏字体',5),(getsimpleswitch( globalconfig['embedded'] ,'changefont',callback=lambda x:gobject.baseobject.textsource.sendSetting('embeddedFontFamily',globalconfig['embedded']['changefont_font'] if x else '')),1), (self.gamefont_comboBox,5) ],
                [('修改字体字符集',5),(getsimpleswitch( globalconfig['embedded'] ,'changecharset',callback=lambda x:gobject.baseobject.textsource.sendSetting('embeddedFontCharSetEnabled',x)),1) ,(getsimplecombobox(_TRL(static_data["charsetmapshow"]),globalconfig['embedded'],'changecharset_charset',callback=lambda x:gobject.baseobject.textsource.sendSetting('embeddedFontCharSet',static_data["charsetmap"][x])),5)],

        ]
        
        return grids
        
def setTabclip(self) :
          
        grids=[
            [
                ('提取的文本自动复制到剪贴板',5),(getsimpleswitch(globalconfig ,'outputtopasteboard' ),1),('',8)
                
            ],
            [('排除复制自翻译器的文本',5),(getsimpleswitch(globalconfig ,'excule_from_self' ),1), ], 
            
        ]
        return grids


def setTabOne_direct(self) :  
        
        self.tab1grids=[
                [ ('选择文本输入源',3)],
                
                [
                        ('剪贴板',3),(getsimpleswitch(globalconfig['sourcestatus']['copy'],'use',name='copy',parent=self,callback= functools.partial(yuitsu_switch,self, globalconfig['sourcestatus'],'sourceswitchs','copy',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                        ('OCR',3),(getsimpleswitch(globalconfig['sourcestatus']['ocr'],'use',name='ocr',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus'],'sourceswitchs','ocr',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                        ('',4) 
                       
                ],
                [   
                     ('HOOK',3),(getsimpleswitch(globalconfig['sourcestatus']['texthook'],'use',name='texthook',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus'],'sourceswitchs','texthook',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                    ('HOOK_内嵌',3),(getsimpleswitch(globalconfig['sourcestatus']['embedded'],'use',name='embedded',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus'],'sourceswitchs','embedded',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                      
                ], 
        ]  

        (getcolorbutton(globalconfig ,'',name='selectbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit()),1)
        (getcolorbutton(globalconfig ,'',name='selectbuttonembed',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit()),1)
        (getcolorbutton(globalconfig ,'',name='selecthookbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda  : gobject.baseobject.hookselectdialog.showsignal.emit() ),1)
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())
def setTabOne(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本输入'), lambda :setTabOne_lazy(self)) 

 
def setTabOne_lazy(self) : 
        
         
         
        tab=self.makesubtab_lazy(['HOOK设置','OCR设置','剪贴板设置','内嵌设置'],
                                [       
                                        lambda:self.makescroll(self.makegrid(gethookgrid(self))),
                                        lambda:self.makescroll(self.makegrid(getocrgrid(self))),
                                        lambda:self.makescroll(self.makegrid(setTabclip(self))),
                                        lambda:self.makescroll(self.makegrid(gethookembedgrid(self) )),
                                ]) 

        gridlayoutwidget=self.makegrid(self.tab1grids )    
        return self.makevbox([gridlayoutwidget,tab]) 