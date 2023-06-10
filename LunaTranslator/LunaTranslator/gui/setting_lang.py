  
import os 
from myutils.config import globalconfig ,_TR,_TRL ,static_data 

def setTablang(self) : 
    self.tabadd_lazy(self.tab_widget, ('语言设置'), lambda :setTablanglz(self)) 
def setTablanglz(self) :  
        grids=[
            [('翻译及OCR语言',15)],
            [ 
                ("源语言",5),(self.getsimplecombobox(_TRL(static_data['language_list_translator']  ),globalconfig,'srclang3'),5),],
            [
                ("目标语言",5),(self.getsimplecombobox(_TRL(static_data['language_list_translator']  ),globalconfig,'tgtlang3'),5) ,
            ],
            [''],
            [('本软件显示语言(重启生效)',5),(self.getsimplecombobox((static_data['language_list_show']),globalconfig,'languageuse'),5),(self.getcolorbutton(globalconfig,'',callback=lambda :os.startfile(os.path.abspath('./files/lang/{}.json'.format(static_data["language_list_translator_inner"][globalconfig["languageuse"]]))),icon='fa.gear',constcolor="#FF69B4"),1)], 
           
            [''],
        ]
         
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        return gridlayoutwidget