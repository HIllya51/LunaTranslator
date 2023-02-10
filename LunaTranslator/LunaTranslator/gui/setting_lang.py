  
import os 
from utils.config import globalconfig ,_TR,_TRL 


def setTablang(self) : 
    self.tabadd_lazy(self.tab_widget, ('语言设置'), lambda :setTablanglz(self)) 
def setTablanglz(self) : 
        langlist=globalconfig['language_list_translator'] 
        grids=[
            [ 
                ("源语言",5),(self.getsimplecombobox(_TRL(langlist ),globalconfig,'srclang2'),5),'',
                ("目标语言",5),(self.getsimplecombobox(_TRL(langlist ),globalconfig,'tgtlang2'),5) ,
            ],
            [('翻译器显示语言(重启生效)',8),(self.getsimplecombobox((globalconfig['language_list_show']),globalconfig,'languageuse'),5),(self.getcolorbutton(globalconfig,'',callback=lambda :os.startfile(os.path.abspath(f'./files/lang/{globalconfig["language_list"][globalconfig["languageuse"]]}.json')),icon='fa.gear',constcolor="#FF69B4"),1)], 
           
            [''],
        ]
         
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        return gridlayoutwidget