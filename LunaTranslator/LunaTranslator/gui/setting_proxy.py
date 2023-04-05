
from PyQt5.QtWidgets import QWidget,QLabel ,QProgressBar,QLineEdit,QPushButton 
from utils.config import globalconfig  ,_TR 

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
        ]

        return self.makescroll(self.makegrid(grid1 )  )

def setTab_proxy(self) : 
    self.tabadd_lazy(self.tab_widget, ('代理设置'), lambda :setTab_proxy_lazy(self)) 