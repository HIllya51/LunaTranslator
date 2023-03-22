 
import functools    
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QFontComboBox  
from gui.settingpage_ocr import getocrgrid  
from utils.config import globalconfig ,_TR,_TRL  
from gui.dialog_savedgame import dialog_savedgame 
from gui.codeacceptdialog import codeacceptdialog  
from utils import somedef
from utils.utils import makehtml
def gethookgrid(self) :
 
        grids=[
                [('获取最新引擎以及申请支持更多游戏',5),(makehtml('https://github.com/HIllya51/Textractor_Extra'),5,'link')], 
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1)],
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],


                [('刷新延迟(ms)',5),(self.getspinbox(1,10000,globalconfig,'textthreaddelay',callback=lambda x:self.object.textsource.setdelay()),3)],
                [('过滤包含乱码的文本行',5),(self.getsimpleswitch(globalconfig,'filter_chaos_code'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                
        ]
         
        return grids

def gethookembedgrid(self) :  
        def __insertspace(i):
                if i==0:
                        self.object.ga.sendSetting('embeddedSpaceSmartInserted',False )
                        self.object.ga.sendSetting('embeddedSpaceAlwaysInserted',False )
                elif i==1:
                        self.object.ga.sendSetting('embeddedSpaceSmartInserted',False )
                        self.object.ga.sendSetting('embeddedSpaceAlwaysInserted',True )
                elif i==2:
                        self.object.ga.sendSetting('embeddedSpaceSmartInserted',True )
                        self.object.ga.sendSetting('embeddedSpaceAlwaysInserted',False )
        self.gamefont_comboBox = QFontComboBox( ) 
        def callback(x):
                globalconfig['embedded'].__setitem__('changefont_font',x)
                try:
                        self.object.ga.sendSetting('embeddedFontFamily',globalconfig['embedded']['changefont_font'] if x else '')
                except:
                        pass
        self.gamefont_comboBox.activated[str].connect(callback)   
        self.gamefont_comboBox.setCurrentFont(QFont(globalconfig['embedded']['changefont_font']))  
        grids=[
                 
                [('获取最新引擎以及申请支持更多游戏',5),'',(makehtml('https://github.com/HIllya51/TextEmbedder'),8,'link')], 
                [('保留原文',5),(self.getsimpleswitch( globalconfig['embedded'],'keeprawtext',callback=lambda x:self.object.ga.sendSetting('embeddedScenarioTextVisible',x ))  ,1) ],
                 
                [('翻译等待时间(s)',5),'',(self.getspinbox(0,30,globalconfig['embedded'],'timeout_translate',double=True,step=0.1,callback=lambda x:self.object.ga.sendSetting('embeddedTranslationWaitTime',int(x*1000))),3) ],
                [('使用最快翻译而非指定翻译器',5),(self.getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
                [('内嵌的翻译器',5),'',(self.getsimplecombobox(_TRL([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']]),globalconfig['embedded'],'translator'),5) ],
                [('将汉字转换成繁体/日式汉字',5),(self.getsimpleswitch( globalconfig['embedded'] ,'trans_kanji'),1) ],
                [('在重叠显示的字间插入空格',5),'',(self.getsimplecombobox(_TRL(['不插入空格','每个字后插入空格','仅在无法编码的字后插入']),globalconfig['embedded'],'insertspace_policy',callback=__insertspace),5) ],
                [('修改游戏字体',5),(self.getsimpleswitch( globalconfig['embedded'] ,'changefont',callback=lambda x:self.object.ga.sendSetting('embeddedFontFamily',globalconfig['embedded']['changefont_font'] if x else '')),1), (self.gamefont_comboBox,5) ],
                [('修改字体字符集',5),(self.getsimpleswitch( globalconfig['embedded'] ,'changecharset',callback=lambda x:self.object.ga.sendSetting('embeddedFontCharSetEnabled',x)),1) ,(self.getsimplecombobox(_TRL(somedef.charsetmapshow),globalconfig['embedded'],'changecharset_charset',callback=lambda x:self.object.ga.sendSetting('embeddedFontCharSet',somedef.charsetmap[x])),5)],

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
                        ('剪贴板',3),(self.getsimpleswitch(globalconfig['sourcestatus']['copy'],'use',name='copy',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','copy',self.object.starttextsource),pair='sourceswitchs'),1),'',
                        ('HOOK',3),(self.getsimpleswitch(globalconfig['sourcestatus']['textractor'],'use',name='textractor',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','textractor',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('选择游戏',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor']['use'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda :self.object.AttachProcessDialog.showsignal.emit()),1)
                ],
                [   
                    ('OCR',3),(self.getsimpleswitch(globalconfig['sourcestatus']['ocr'],'use',name='ocr',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','ocr',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('HOOK_内嵌',3),(self.getsimpleswitch(globalconfig['sourcestatus']['embedded'],'use',name='embedded',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','embedded',self.object.starttextsource),pair='sourceswitchs'),1),'',
                        ('选择文本',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor']['use'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda  : self.object.hookselectdialog.showsignal.emit() ),1)
                ],
                
                [
                        ('TXT文件',3),(self.getsimpleswitch(globalconfig['sourcestatus']['txt'],'use',name='txt',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','txt',self.object.starttextsource),pair='sourceswitchs'),1) 
                        
                        
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
                                        lambda:self.makescroll(self.makegrid(gethookembedgrid(self) ))
                                ]) 

        gridlayoutwidget=self.makegrid(self.tab1grids )    
        return self.makevbox([gridlayoutwidget,tab]) 