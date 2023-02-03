 
import functools 
from utils.config import globalconfig  
 
def setTabOne(self) :
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())
  
        grids=[
                [ ('选择文本输入源',3)],
                [   ('剪贴板',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'copy',name='copy',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','copy',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('OCR',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'ocr',name='ocr',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','ocr',self.object.starttextsource),pair='sourceswitchs'),1),'',
                    ('Textractor',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'textractor',name='textractor',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','textractor',self.object.starttextsource),pair='sourceswitchs'),1)],
                
                [('TXT文件',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'txt',name='txt',callback= functools.partial(self.yuitsu_switch,'sourcestatus','sourceswitchs','txt',self.object.starttextsource),pair='sourceswitchs'),1),('',6),('选择游戏',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda :self.object.AttachProcessDialog.showsignal.emit()),1)],
                [('',10),('选择文本',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=lambda  : self.object.hookselectdialog.showsignal.emit() ),1)],
                [''], 
                [('提取的文本自动复制到剪贴板',5),(self.getsimpleswitch(globalconfig ,'outputtopasteboard',name='outputtopasteboard'),1)], 
        ] 
        self.yitiaolong("基本设置",grids)
         