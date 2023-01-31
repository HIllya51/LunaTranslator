 
from traceback import print_exc
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QLabel ,QProgressBar,QLineEdit,QPushButton
import threading
import os
import shutil
import zipfile
import threading
from threading import Lock 
from utils.config import globalconfig  ,_TR
import gui.switchbutton
from utils.downloader import mutithreaddownload
def getversion(self):
     
    # with open('files/about.txt','r',encoding='utf8') as ff:
    #     about=ff.read()
    with open('files/version.txt','r',encoding='utf8') as ff:
        version=ff.read() 
    url='https://github.com/HIllya51/LunaTranslator/releases/'
    self.versiontextsignal.emit(_TR('当前版本')+':'+  version+'  '+_TR("最新版本")+':'+ _TR('获取中'))#,'',url,url))
    try:
        requests.packages.urllib3.disable_warnings()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
             'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        res= requests.get('https://api.github.com/repos/HIllya51/LunaTranslator/releases/latest', headers=headers,proxies={'http': None,'https': None} ,verify = False).json() 
        _version=res['tag_name']
       # print(version)
        url=res['assets'][0]['browser_download_url']
        newcontent='更新内容：'+res['body']
    except:
        print_exc()
        _version=_TR("获取失败")
        newcontent=''
    self.versiontextsignal.emit((_TR('当前版本')+':'+  version+'  '+_TR("最新版本")+':'+ _version) ) #,'' if version== _version else  newcontent,url,'LunaTranslator.zip'))
    if _version!=_TR("获取失败") and version!=_version:
        if globalconfig['autoupdate']:
            self.downloadprogress.show()
            self.progresssignal.emit('……',0)
        
            savep=f'./cache/update/LunaTranslator.zip' 
            def endcallback():
                if os.path.exists('./cache/update/LunaTranslator'):
                    shutil.rmtree('./cache/update/LunaTranslator')
                zipf=(zipfile.ZipFile('./cache/update/LunaTranslator.zip'))
                zipf.extractall('./cache/update')
                self.needupdate=True
                self.updatefile=savep
            mutithreaddownload(savep,url,self.progresssignal.emit,lambda: globalconfig.__getitem__('autoupdate'),endcallback) 
 
def updateprogress(self,text,val):
    self.downloadprogress.setValue(val)
    self.downloadprogress.setFormat(text)
     
def setTab_about(self) :
        def changeupdate(x):
            globalconfig.__setitem__('autoupdate',x)
            if x:
                threading.Thread(target=lambda :getversion(self)).start()
        
        self.downloadprogress=QProgressBar()
         
        self.downloadprogress.hide()
        self.downloadprogress.setRange(0,10000)

        self.downloadprogress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progresssignal.connect(lambda text,val:updateprogress(self,text,val))



        def _setproxy(x):
            globalconfig.__setitem__('useproxy',x)
            if x:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
            else:
                os.environ['https_proxy']='' 
                os.environ['http_proxy']=''
        #_setproxy(globalconfig['useproxy'])
        if globalconfig['useproxy']:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
        proxy=QLineEdit(globalconfig['proxy'])
        btn=QPushButton(_TR('确定' ))
        def __resetproxy(x):
            globalconfig.__setitem__('proxy',proxy.text())
            if globalconfig['useproxy']:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
        btn.clicked.connect(lambda x: __resetproxy(x))

        self.versionlabel = QLabel()
        self.versionlabel.setOpenExternalLinks(True)
        self.versionlabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse) 
        self.versiontextsignal.connect(lambda x:self.versionlabel.setText(x) )

        self.versionlabel1 = QLabel(_TR('项目网站')+':<a href="https://github.com/HIllya51/LunaTranslator">https://github.com/HIllya51/LunaTranslator</a>')
        self.versionlabel1.setOpenExternalLinks(True)
        self.versionlabel1.setTextInteractionFlags(Qt.LinksAccessibleByMouse)  
        self.versionlabel2 = QLabel(_TR('使用说明')+':<a href="https://hillya51.github.io/">https://hillya51.github.io/</a>')
        self.versionlabel2.setOpenExternalLinks(True)
        self.versionlabel2.setTextInteractionFlags(Qt.LinksAccessibleByMouse)  
        
        self.versionlabel3 = QLabel('如果你感觉该软件对你有帮助，欢迎微信扫码或者前往<a href="https://afdian.net/a/HIllya51">爱发电</a>赞助，谢谢，么么哒~')
        self.versionlabel3.setOpenExternalLinks(True)
        self.versionlabel3.setTextInteractionFlags(Qt.LinksAccessibleByMouse)  
        self.versionlabel4 = QLabel('<img src="./files/zan.jpg" heigth=500 width=500>' ) 
        grids=[ 
            [
                ("使用代理",5),(self.getsimpleswitch(globalconfig  ,'useproxy',callback=lambda x: _setproxy(x)),1),''],
            [        ("代理设置(ip:port)",5),        (proxy,5),(btn,2),  
            ],
            [''],

                [(self.downloadprogress,10)],
                [('自动下载更新(需要连接github)',5),(self.getsimpleswitch(globalconfig ,'autoupdate',callback= lambda x:changeupdate(x)),1) ],
                [(self.versionlabel,10)],
                
                [''],
                [(self.versionlabel1,10)],
                [(self.versionlabel2,10)],
                [(self.versionlabel3,10)] ,
                [(self.versionlabel4,10)] 
        ]  
        w=self.yitiaolong("其他设置",grids,fixheight=False ) 

        w.setFixedHeight(len(grids)*30*self.rate+500)
         
        # self.versionlabel = QLabel(widget )
        # self.versionlabel.setGeometry(0,500,600,500)
        # self.versionlabel.setOpenExternalLinks(True)
            
        # self.versionlabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse) 
        # self.versiontextsignal.connect(lambda x:self.versionlabel.setText(x) )
        # self.versionlabel.setWordWrap(True)
        # self.versionlabel.setAlignment(Qt.AlignTop)
        threading.Thread(target=lambda :getversion(self)).start()