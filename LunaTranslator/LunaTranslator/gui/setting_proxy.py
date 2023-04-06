
from PyQt5.QtWidgets import QWidget,QLabel ,QProgressBar,QLineEdit,QPushButton 
from utils.config import globalconfig  ,_TR 
from utils.config import globalconfig ,translatorsetting 
from utils import somedef
def getall(self,l,item='fanyi'):
    grids=[] 
    i=0 
    line=[]
    for fanyi in globalconfig[item]:
        
        if fanyi not in l:
            continue
 
        i+=1
         
        line+=[(globalconfig[item][fanyi]['name'],6),
        self.getsimpleswitch(globalconfig[item][fanyi],'useproxy',default=True) ] 
        if i%3==0  :
            grids.append(line)
            line=[]
        else:
            line+=['']
    if len(line) :
        grids.append(line)
    return grids
def setTab_proxy_lazy(self):
     
        proxy=QLineEdit(globalconfig['proxy'])
        btn=QPushButton(_TR('确定' ))
        
        btn.clicked.connect(lambda x:globalconfig.__setitem__('proxy',proxy.text()))

        
        def _ifusesysproxy(x):
             proxy.setEnabled(not x)
             btn.setEnabled(not x)
        _ifusesysproxy(globalconfig['usesysproxy'])
        grid1=[ 
            
            [    ("使用代理",5),(self.getsimpleswitch(globalconfig  ,'useproxy'),1),('',10)],
            [
                ("自动获取系统代理",5),(self.getsimpleswitch(globalconfig  ,'usesysproxy',callback=lambda x:_ifusesysproxy(x)))
            ],
            [        ("手动设置代理(ip:port)",5),        (proxy,5),(btn,2),  
            ], 
            [''],
            [('使用代理的项目',5)]
        ]
        lixians=set(somedef.fanyi_offline)
        alls=set(globalconfig['fanyi'].keys())
        mt=set(somedef.fanyi_pre)
        online=alls-lixians-mt 
        mianfei=set()
        for _ in online:
            if _ not in translatorsetting : 
                mianfei.add(_) 
        shoufei=online-mianfei  
         
        mianfei=getall(self,l=mianfei,item='fanyi')
        shoufei=getall(self,l=shoufei,item='fanyi')
        ocrs=getall(self,l=set(globalconfig['ocr'].keys())-set(['local','windowsocr']),item='ocr')
        tab=self.makesubtab_lazy(['在线翻译','注册在线翻译','在线OCR'],[ 
            lambda:self.makescroll( self.makegrid(mianfei )   ),
            lambda:self.makescroll( self.makegrid(shoufei )   ),
            lambda:self.makescroll( self.makegrid(ocrs )   ), 
        ]) 

        gridlayoutwidget=self.makegrid(grid1 )    
        return self.makevbox([gridlayoutwidget,tab])
         

def setTab_proxy(self) : 
    self.tabadd_lazy(self.tab_widget, ('代理设置'), lambda :setTab_proxy_lazy(self)) 