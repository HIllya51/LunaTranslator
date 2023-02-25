  
import os 
from utils.config import globalconfig ,_TR,_TRL 
from utils import somedef

def setTablang(self) : 
    self.tabadd_lazy(self.tab_widget, ('语言设置'), lambda :setTablanglz(self)) 
def setTablanglz(self) :  
        grids=[
            [('翻译及OCR语言',15)],
            [ 
                ("源语言",5),(self.getsimplecombobox(_TRL(somedef.language_list_translator  ),globalconfig,'srclang3'),5),],
            [
                ("目标语言",5),(self.getsimplecombobox(_TRL(somedef.language_list_translator  ),globalconfig,'tgtlang3'),5) ,
            ],
            [''],
            [('本软件显示语言(重启生效)',5),(self.getsimplecombobox((somedef.language_list_show),globalconfig,'languageuse'),5),(self.getcolorbutton(globalconfig,'',callback=lambda :os.startfile(os.path.abspath(f'./files/lang/{somedef.language_list_translator_inner[globalconfig["languageuse"]]}.json')),icon='fa.gear',constcolor="#FF69B4"),1)], 
           
            [''],
        ]
         
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        return gridlayoutwidget