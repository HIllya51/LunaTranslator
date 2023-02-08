 
import functools 
from utils.config import globalconfig  ,_TR
from gui.settingpage_ocr import getocrgrid 
from gui.settingpage_hook import gethookgrid ,gethookembedgrid
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

def setTabOne(self) :
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())
  
        grids=[
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
 
        
        pages=[]
        for  i,ocrgrid in enumerate([ gethookgrid ,getocrgrid ,setTabclip,txtsettings,gethookembedgrid]):
                 
                gridlayoutwidget=self.makegrid(ocrgrid(self))  
                if i==1:
                        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
                pages.append(gridlayoutwidget)
        tab=self.makesubtab(['HOOK设置','OCR设置','剪贴板设置','TXT设置','内嵌设置'],pages) 

        gridlayoutwidget=self.makegrid(grids )   
        
        self.tabadd(self.tab_widget, ('文本源设置'),[gridlayoutwidget,tab ]) 