 
import functools    
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QFontComboBox  ,QLabel
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
                [('刷新延迟(ms)',5),(getspinbox(0,10000,globalconfig,'textthreaddelay',callback=lambda x:gobject.baseobject.textsource.setsettings()),3)],
                [('文本缓冲区长度',5),(getspinbox(0,10000,globalconfig,'flushbuffersize',callback=lambda x:gobject.baseobject.textsource.setsettings()),3)],
                [('过滤包含乱码的文本行',5),(getsimpleswitch(globalconfig,'filter_chaos_code'),1),(getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [''],
                [('区分人名和文本',5),getsimpleswitch(globalconfig,'allow_set_text_name')]
                
        ]
         
        return grids

def gethookembedgrid(self) :   
        self.gamefont_comboBox = QFontComboBox( ) 
        def callback(x):
                globalconfig['embedded'].__setitem__('changefont_font',x)
                try:
                        gobject.baseobject.textsource.flashembedsettings()
                except:
                        pass
        self.gamefont_comboBox.activated[str].connect(callback)   
        self.gamefont_comboBox.setCurrentFont(QFont(globalconfig['embedded']['changefont_font']))  
        grids=[
                 
                [('保留原文',5),(getsimpleswitch( globalconfig['embedded'],'keeprawtext',callback=lambda _:gobject.baseobject.textsource.flashembedsettings())  ,1) ],
                 
                [('翻译等待时间(s)',5),'',(getspinbox(0,30,globalconfig['embedded'],'timeout_translate',double=True,step=0.1,callback=lambda x:gobject.baseobject.textsource.flashembedsettings()),3) ],
                [('使用最快翻译而非指定翻译器',5),(getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
                [('内嵌的翻译器',5),'',(getsimplecombobox(_TRL([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']]),globalconfig['embedded'],'translator'),5) ],
                [('将汉字转换成繁体/日式汉字',5),(getsimpleswitch( globalconfig['embedded'] ,'trans_kanji'),1) ],
                [('在重叠显示的字间插入空格',5),'',(getsimplecombobox(_TRL(['不插入空格','每个字后插入空格','仅在无法编码的字后插入']),globalconfig['embedded'],'insertspace_policy',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),5) ],
                [('修改游戏字体',5),(getsimpleswitch( globalconfig['embedded'] ,'changefont',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),1), (self.gamefont_comboBox,5) ],
                #[('修改字体字符集',5),(getsimpleswitch( globalconfig['embedded'] ,'changecharset',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),1) ,(getsimplecombobox(_TRL(static_data["charsetmapshow"]),globalconfig['embedded'],'changecharset_charset',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),5)],

        ]
        
        return grids
        
def setTabclip(self) :
          
        grids=[
            [
                ('提取的文本自动复制到剪贴板',5),(getsimpleswitch(globalconfig ,'outputtopasteboard' ),1),('',3)
                
            ],
            [('排除复制自翻译器的文本',5),(getsimpleswitch(globalconfig ,'excule_from_self' ),1), ], 
            
        ]
        return grids


def setTabOne_direct(self) :  
        
        self.tab1grids=[
                [ ('选择文本输入源',8)],
                
                [
                        ('剪贴板',3),(getsimpleswitch(globalconfig['sourcestatus2']['copy'],'use',name='copy',parent=self,callback= functools.partial(yuitsu_switch,self, globalconfig['sourcestatus2'],'sourceswitchs','copy',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                        ('OCR',3),(getsimpleswitch(globalconfig['sourcestatus2']['ocr'],'use',name='ocr',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus2'],'sourceswitchs','ocr',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                        
                     ('HOOK',3),(getsimpleswitch(globalconfig['sourcestatus2']['texthook'],'use',name='texthook',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus2'],'sourceswitchs','texthook',gobject.baseobject.starttextsource),pair='sourceswitchs'),1), 
                     
                      
                ], 
        ]  

        getcolorbutton(globalconfig ,'',name='selectbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit())
        getcolorbutton(globalconfig ,'',name='selectbuttonembed',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit())
        getcolorbutton(globalconfig ,'',name='selecthookbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda  : gobject.baseobject.hookselectdialog.showsignal.emit() )
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())


        self.threshold1label=QLabel()
        self.threshold2label=QLabel()

def setTabOne(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本输入'), lambda :setTabOne_lazy(self)) 

 
def setTabOne_lazy(self) : 
        
         
         
        tab=self.makesubtab_lazy(['HOOK设置','OCR设置','剪贴板','内嵌翻译'],
                                [       
                                        lambda:self.makescroll(self.makegrid(gethookgrid(self))),
                                        lambda:self.makescroll(self.makegrid(getocrgrid(self))),
                                        lambda:self.makescroll(self.makegrid(setTabclip(self))),
                                        lambda:self.makescroll(self.makegrid(gethookembedgrid(self) )),
                                ]) 

        gridlayoutwidget=self.makegrid(self.tab1grids )    
        return self.makevbox([gridlayoutwidget,tab]) 