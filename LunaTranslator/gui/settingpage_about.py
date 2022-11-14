 
from traceback import print_exc
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QLabel ,QProgressBar
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
    

    with open('files/about.txt','r',encoding='utf8') as ff:
        about=ff.read()
    with open('files/version.txt','r',encoding='utf8') as ff:
        version=ff.read() 
    url='https://github.com/HIllya51/LunaTranslator/releases/'
    self.versiontextsignal.emit(about  %(version, _TR('获取中'),'',url,url))
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
    self.versiontextsignal.emit(about %(version, _version,'' if version== _version else  newcontent,url,'LunaTranslator.zip'))
    if _version!=_TR("获取失败") and version!=_version:
        if globalconfig['autoupdate']:
            self.downloadprogress.show()
            self.progresssignal.emit('……',0)
        
            savep=f'./update/LunaTranslator_{_version}.zip'
            if os.path.exists('update')==False:
                    os.mkdir('update')
            def endcallback():
                if os.path.exists('./update/LunaTranslator'):
                    shutil.rmtree('./update/LunaTranslator')
                # zipf=zipfile.ZipFile('./update/LunaTranslator.zip')
                # zipf.extractall('./update')
                self.needupdate=True
                self.updatefile=savep
            mutithreaddownload(savep,url,self.progresssignal.emit,lambda: globalconfig.__getitem__('autoupdate'),endcallback) 
     
def updateprogress(self,text,val):
    self.downloadprogress.setValue(val)
    self.downloadprogress.setFormat(text)
     
def setTab_about(self) :
         
        self.tab_about = QWidget()
        self.tab_widget.addTab(self.tab_about, _TR("资源下载&更新") )
        label = QLabel(self.tab_about)
        self.customSetGeometry(label, 20, 20, 200, 20)
        label.setText(_TR("自动下载更新(需要连接github)"))
        self.updateswitch =gui.switchbutton.MySwitch(self.tab_about, sign= globalconfig['autoupdate'])
        self.customSetGeometry(self.updateswitch , 250, 20, 20,20)
        def changeupdate(x):
            globalconfig.__setitem__('autoupdate',x)
            if x:
                threading.Thread(target=lambda :getversion(self)).start()
        self.updateswitch.clicked.connect(lambda x:  changeupdate( x)) 

        self.downloadprogress=QProgressBar(self.tab_about)
        self.customSetGeometry(self.downloadprogress, 20, 50, 500, 20)
        
        self.downloadprogress.hide()
        self.downloadprogress.setRange(0,10000)

        self.downloadprogress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progresssignal.connect(lambda text,val:updateprogress(self,text,val))


        self.versionlabel = QLabel(self.tab_about)
        self.versionlabel.setOpenExternalLinks(True)
            
        self.versionlabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.customSetGeometry(self.versionlabel, 20, 100, 600, 500)

        
        self.versiontextsignal.connect(lambda x:self.versionlabel.setText(x) )
        self.versionlabel.setWordWrap(True)
        self.versionlabel.setAlignment(Qt.AlignTop)
        threading.Thread(target=lambda :getversion(self)).start()