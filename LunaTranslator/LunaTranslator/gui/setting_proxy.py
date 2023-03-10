
import os,time,threading

from PyQt5.QtWidgets import QWidget,QLabel ,QProgressBar,QLineEdit,QPushButton 
from utils.config import globalconfig  ,_TR 
from utils.utils import makehtml,getsysproxy
def _setproxy(proxy):  
            print("set proxy",proxy)
            os.environ['https_proxy']=proxy
            os.environ['http_proxy']=proxy

def refreshsysproxy():
        lastsysproxy=None
        
        while globalconfig['usesysproxy'] and globalconfig['useproxy']:
            
            proxy=getsysproxy()
            if lastsysproxy!=proxy:
                lastsysproxy=proxy
                _setproxy(proxy)  
            time.sleep(5)
            
def checkproxy():
     if globalconfig['useproxy']:
            if globalconfig['usesysproxy']:
                 threading.Thread(target=refreshsysproxy).start()
            else:
                 _setproxy(globalconfig['proxy'])
     else:
        _setproxy('')


def setTab_proxy_dicrect(self) : 
    checkproxy()

def setTab_proxy_lazy(self):
     
        proxy=QLineEdit(globalconfig['proxy'])
        btn=QPushButton(('确定' ))
        def __resetproxy(x):
            globalconfig.__setitem__('proxy',proxy.text())
            _setproxy(globalconfig['proxy'] if globalconfig['useproxy'] else '')
        btn.clicked.connect(lambda x: __resetproxy(x))

        
        def _ifusesysproxy(x):
             proxy.setEnabled(not x)
             btn.setEnabled(not x)
             checkproxy()
        _ifusesysproxy(globalconfig['usesysproxy'])
        grid1=[ 
            
            [    ("使用代理",5),(self.getsimpleswitch(globalconfig  ,'useproxy',callback=lambda x:checkproxy()),1),('',10)],
            [
                ("自动获取系统代理",5),(self.getsimpleswitch(globalconfig  ,'usesysproxy',callback=lambda x:_ifusesysproxy(x)))
            ],
            [        ("手动设置代理(ip:port)",5),        (proxy,5),(btn,2),  
            ], 
        ]

        return self.makescroll(self.makegrid(grid1 )  )

def setTab_proxy(self) : 
    self.tabadd_lazy(self.tab_widget, ('代理设置'), lambda :setTab_proxy_lazy(self)) 