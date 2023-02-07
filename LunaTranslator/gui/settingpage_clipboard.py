 
from utils.config import globalconfig 
from utils.config import globalconfig ,_TR,_TRL 

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