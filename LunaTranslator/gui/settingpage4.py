  
import functools  
from PyQt5.QtWidgets import   QComboBox    
from utils.config import globalconfig  
from utils.config import globalconfig ,_TR,_TRL 
from gui.dialog_savedgame import dialog_savedgame
from gui.codeacceptdialog import codeacceptdialog
def changecodepage(self,_):
        try:

                globalconfig['codepage_index']=_
                self.object.textsource.setcodepage()
        except:
                pass
def changedelay(self,_):
        try:

                globalconfig['textthreaddelay']=_
                self.object.textsource.setdelay()
        except:
                pass
def setTab4(self) :

        s=QComboBox( )  
        s.addItems(_TRL(['日语(CP932,SHIFT-JIS)','UTF8(CP65001)','简体中文(CP936,GBK)','繁体中文(CP950,BIG5)','韩语(CP949,EUC-KR)','越南语(CP1258)','泰语(CP874)','阿拉伯语(CP1256)','希伯来语(CP1255)','土耳其语(CP1254)','希腊语(CP1253)','北欧(CP1257)','中东欧(CP1250)','西里尔(CP1251)','拉丁(CP1252)']))
        s.setCurrentIndex(globalconfig['codepage_index'])
        codepagecombo=s
        s.currentIndexChanged.connect(functools.partial(changecodepage,self))

        grids=[
                
                [('检测到游戏时自动开始',5),(self.getsimpleswitch(globalconfig,'autostarthook'),1),'','','','','','','','',''],
               # [('转区方式',5),(self.getsimplecombobox(_TRL(['Locale.Emulator','Locale_Remulator']),globalconfig,'localeswitchmethod'),5)],
               # [('LocaleEmulator路径设置',5),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'LocaleEmulator',globalconfig,'LocaleEmulator','LocaleEmulator',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1),("不支持64位",5)],
              #  [('Locale_Remulator路径设置',5),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'Locale_Remulator',globalconfig,'Locale_Remulator','Locale_Remulator',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1),("支持64位，但是不一定管用",8)],
                [('已保存游戏',5),(self.getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],

                [('代码页',5),(codepagecombo,5)],
                [('刷新延迟(ms)',5),(self.getspinbox(1,10000,globalconfig,'textthreaddelay',callback=functools.partial(changedelay,self)),3)],
                [('过滤乱码文本',5),(self.getsimpleswitch(globalconfig,'filter_chaos_code'),1),(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [('移除非选定HOOK',5),(self.getsimpleswitch(globalconfig,'remove_useless_hook'),1) ],
        ]
         
        self.yitiaolong("HOOK设置",grids) 
        