 
import functools 
from utils.config import globalconfig  ,_TR
from gui.settingpage_ocr import getocrgrid 
from gui.settingpage_hook import gethookgrid

from gui.settingpage_clipboard import setTabclip ,txtsettings
def setTabOne(self) :
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())
  
        grids=[
                [ ('选择文本输入源',3)],
                [   ('剪贴板',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'copy',name='copy',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','copy',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('OCR',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'ocr',name='ocr',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','ocr',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('HOOK',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'textractor',name='textractor',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','textractor',self.object.starttextsource),pair='sourceswitchs'),1)],
                
                [('TXT文件',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'txt',name='txt',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','txt',self.object.starttextsource),pair='sourceswitchs'),1),('',6),('选择游戏',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda :self.object.AttachProcessDialog.showsignal.emit()),1)],
                [('',10),('选择文本',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda  : self.object.hookselectdialog.showsignal.emit() ),1)],
                 
                
        ] 
 
        
        pages=[]
        for  i,gridmaker in enumerate([ gethookgrid ,getocrgrid ,setTabclip,txtsettings]):
                
                ocrgrid=gridmaker(self)
                gridlayoutwidget=self.makegrid(ocrgrid )  
                if i==1:
                        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
                pages.append(gridlayoutwidget)
        tab=self.makesubtab(['HOOK设置','OCR设置','剪贴板设置','TXT设置'],pages) 

        gridlayoutwidget=self.makegrid(grids )   
        
        self.tabadd(self.tab_widget, ('文本源设置'),[gridlayoutwidget,tab ]) 