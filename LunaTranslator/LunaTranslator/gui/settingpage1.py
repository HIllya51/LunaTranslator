 
import functools    
from gui.settingpage_ocr import getocrgrid  
from utils.config import globalconfig ,_TR,_TRL  
from gui.dialog_savedgame import dialog_savedgame 
from gui.codeacceptdialog import codeacceptdialog  
def gethookgrid(self) :
 
        grids=[
                
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','','','','','','',''], 
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],

                [('代码页',5),(self.getsimplecombobox(_TRL(globalconfig['codepage_display']),globalconfig,'codepage_index' ,lambda x: self.object.textsource.setcodepage()),5)],
                [('刷新延迟(ms)',5),(self.getspinbox(1,10000,globalconfig,'textthreaddelay',callback=lambda x:self.object.textsource.setdelay()),3)],
                [('过滤乱码文本',5),(self.getsimpleswitch(globalconfig,'filter_chaos_code'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [('移除非选定HOOK',5),(self.getsimpleswitch(globalconfig,'remove_useless_hook'),1) ],
  
        ]
         
        return grids

def gethookembedgrid(self) : 
        def __changetimeout(x):
                self.object.ga.settimeout(x*1000)
        grids=[
                 
                [('仅支持部分游戏',12)],
                [('内嵌失败时自动回到普通HOOK',5),(self.getsimpleswitch( globalconfig['embedded'],'fallbacktonormalhook' ),1) ],
                
                [('内嵌失败等待时间(s)',5),(self.getspinbox(1,30,globalconfig['embedded'],'timeout_connect'),3) ],
                [('翻译等待时间(s)',5),(self.getspinbox(0,30,globalconfig['embedded'],'timeout_translate',double=True,step=0.1,callback=__changetimeout),3) ],
                [('使用最快翻译而非指定翻译器',5),(self.getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
                [('内嵌的翻译器',5),(self.getsimplecombobox([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']],globalconfig['embedded'],'translator'),5) ],
                [('将汉字转换成繁体/日式汉字',5),(self.getsimpleswitch( globalconfig['embedded'] ,'trans_kanji'),1) ],
        ]
        
        return grids
        
def setTabclip(self) :
          
        grids=[
            [
                ('提取的文本自动复制到剪贴板',5),(self.getsimpleswitch(globalconfig ,'outputtopasteboard' ),1),('',8)
                
            ],
            [('排除复制自翻译器的文本',5),(self.getsimpleswitch(globalconfig ,'excule_from_self' ),1), ], 
            
        ]
        return grids

def txtsettings(self):
    grids=[[("TXT读取间隔(s)",6),(self.getspinbox(0,10,globalconfig,'txtreadlineinterval',step=0.1,double=True),3),('',10)],['']]
    return grids

def setTabOne_direct(self) :  
        
        self.tab1grids=[
                [ ('选择文本输入源',3)],
                [
                        ('剪贴板',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'copy',name='copy',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','copy',self.object.starttextsource),pair='sourceswitchs'),1),'',
                        ('HOOK',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'textractor',name='textractor',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','textractor',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('选择游戏',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda :self.object.AttachProcessDialog.showsignal.emit()),1)
                ],
                [   
                    ('OCR',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'ocr',name='ocr',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','ocr',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('HOOK_内嵌',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'embedded',name='embedded',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','embedded',self.object.starttextsource),pair='sourceswitchs'),1),'',
                        ('选择文本',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda  : self.object.hookselectdialog.showsignal.emit() ),1)
                ],
                
                [
                        ('TXT文件',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'txt',name='txt',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','txt',self.object.starttextsource),pair='sourceswitchs'),1) 
                        
                        
                ]
        ]  
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())
def setTabOne(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本输入'), lambda :setTabOne_lazy(self)) 
def setTabOne_lazy(self) : 
        
         
         
        tab=self.makesubtab_lazy(['HOOK设置','OCR设置','剪贴板设置','TXT设置','内嵌设置'],
                                [       
                                        lambda:self.makescroll(self.makegrid(gethookgrid(self))),
                                        lambda:self.makescroll(self.makegrid(getocrgrid(self))),
                                        lambda:self.makescroll(self.makegrid(setTabclip(self))),
                                        lambda:self.makescroll(self.makegrid(txtsettings(self))),
                                        lambda:self.makescroll(self.makegrid(gethookembedgrid(self)))
                                ]) 

        gridlayoutwidget=self.makegrid(self.tab1grids )    
        return self.makevbox([gridlayoutwidget,tab]) 