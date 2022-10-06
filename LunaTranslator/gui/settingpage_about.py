from time import time
from traceback import print_exc
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QLabel 
import threading
def getversion(self):
    with open('./files/version.txt','r',encoding='utf8') as ff:
        about=ff.read()
                
    try:
                
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
             'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        version=requests.get('http://api.bilibili.com/x/space/acc/info?mid=1144809437',timeout=2,headers=headers,proxies={'http':None,"https":None}).json()
       # print(version)
        version=version['data']['sign']
         
    except:
        version="获取失败"
    self.versionlabel.setText(about %version)
def setTab_about(self) :

        self.tab_about = QWidget()
        self.tab_widget.addTab(self.tab_about, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_about), " 关于")


        self.versionlabel = QLabel(self.tab_about)
        self.versionlabel.setOpenExternalLinks(True)
            
        self.versionlabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.customSetGeometry(self.versionlabel, 20, 20, 500, 500)
        self.versiontextsignal.connect(lambda: getversion(self))
        
        self.versiontextsignal.emit()