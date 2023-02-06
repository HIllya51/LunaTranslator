   
from utils.config import globalconfig  
from utils.config import globalconfig ,_TR,_TRL 
from gui.dialog_savedgame import dialog_savedgame
from gui.codeacceptdialog import codeacceptdialog 
def setTab4(self) :
 
        grids=[
                
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','','','','','','',''], 
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],

                [('代码页',5),(self.getsimplecombobox(_TRL(globalconfig['codepage_display']),globalconfig,'codepage_index' ,lambda x: self.object.textsource.setcodepage()),5)],
                [('刷新延迟(ms)',5),(self.getspinbox(1,10000,globalconfig,'textthreaddelay',callback=lambda x:self.object.textsource.setdelay()),3)],
                [('过滤乱码文本',5),(self.getsimpleswitch(globalconfig,'filter_chaos_code'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [('移除非选定HOOK',5),(self.getsimpleswitch(globalconfig,'remove_useless_hook'),1) ],

                [''],
                [''],
                [('--实验性的--',5)],
                [('使用内嵌翻译',5),(self.getsimpleswitch( globalconfig['embedded'],'use',callback=lambda x:self.object.textsource.startembedengine()),1) ],
                [('内嵌的翻译器',5),(self.getsimplecombobox([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']],globalconfig['embedded'],'use',name="embedded_translator_select"),5) ],
                [('使用最快翻译而非指定翻译器',5),(self.getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
        ]
        
        self.embedded_translator_select.currentIndexChanged
        self.yitiaolong("HOOK设置",grids) 
        