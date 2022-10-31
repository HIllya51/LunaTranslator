 
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
from contextlib import closing
from utils.config import globalconfig ,postprocessconfig,savehook_new
import gui.switchbutton
def getversion(self):
    with open('files/about.txt','r',encoding='utf8') as ff:
        about=ff.read()
    url='https://github.com/HIllya51/LunaTranslator/releases/'
    self.versiontextsignal.emit(about  %(self.version, '获取中','',url,url))
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
        version=res['tag_name']
       # print(version)
        url=res['assets'][0]['browser_download_url']
        newcontent='更新内容：'+res['body']
    except:
        print_exc()
        version="获取失败"
        newcontent=''
    self.versiontextsignal.emit(about %(self.version, version,'' if self.version== version else  newcontent,url,'LunaTranslator.zip'))
    if version!="获取失败" and self.version!=version:
        if globalconfig['autoupdate']:
            self.downloadprogress.show()
            self.progresssignal.emit('……',0)
            try:
                savep='./update/update.zip'
                if os.path.exists('update')==False:
                        os.mkdir('update')
                with open(savep, "wb") as file:
                    global file_size
                    file_size=0
                    def download(start,end,sz):
                        headers = {
                            'Range': f'bytes={start}-{end}',
                        }
                        r = requests.get(url,stream=True,headers=headers,verify = False)#stream=True设置流式下载
                        #分多次下载数据
                        pos = start
                        for i in r.iter_content(chunk_size=1024):#设置每次获取的大小
                            if globalconfig['autoupdate']==False: 
                                    return
                            if i:#判断是否为空数据
                                lock.acquire()  # 获得使用权
                                file.seek(pos)
                                file.write(i)
                                global file_size
                                file_size+=len(i)
                                lock.release()  # 释放使用权
                                self.progresssignal.emit(f'总大小{int(1000*(int(sz/1024)/1024))/1000} MB 进度 {int(10000*(file_size/sz))/100:.2f}%',int(10000*file_size/sz))
                                pos += 1024
                                
                        #print(f'正在下载webdriver 总大小{int(1000*(int(content_size/1024)/1024))/1000} MB 进度 {int(10000*(file_size/content_size))/100}%')
                        
                #=====获取资源大小=======
                    r2 = requests.get(url,stream=True,verify = False)
                    #print(r2.headers['Content-Length'])#5298163
                    
                    #=====分两段来下载视频=======
                    lock = Lock()#创建锁的锁的对象
                    
                    # download(0,1298163)#开头，结尾(不包含)
                    # download(1298163,5298163)
                    thread_num = 4
                    size = int(r2.headers['Content-Length'])
                    ts=[]
                    for i in range(thread_num):
                        if i == thread_num-1:
                            t1=threading.Thread(target=download,args=(i*(size//thread_num),size,size))
                            t1.start()
                            ts.append(t1)
                        else:
                            t1 = threading.Thread(target=download, args=(i*(size//thread_num), (i+1)*(size//thread_num),size))
                            t1.start()
                            ts.append(t1)
                    for t in ts:
                        t.join()
                    
                if globalconfig['autoupdate']==False: 
                    return
                if os.path.exists('./update/LunaTranslator'):
                    shutil.rmtree('./update/LunaTranslator')
                zipf=zipfile.ZipFile('./update/update.zip')
                zipf.extractall('./update')
                self.needupdate=True
                
            except:
                print_exc()
                self.progresssignal.emit('自动更新失败，请手动更新',0)
def updateprogress(self,text,val):
    self.downloadprogress.setValue(val)
    self.downloadprogress.setFormat(text)
     
def setTab_about(self) :
        with open('files/version.txt','r')as ff:
            self.version=ff.read() 
        self.tab_about = QWidget()
        self.tab_widget.addTab(self.tab_about, "资源下载&更新") 
        label = QLabel(self.tab_about)
        self.customSetGeometry(label, 20, 20, 200, 20)
        label.setText("自动下载更新(需要连接github)")
        self.updateswitch =gui.switchbutton.MySwitch(self.tab_about, sign= globalconfig['autoupdate'])
        self.customSetGeometry(self.updateswitch , 250, 20, 20,20)
        def changeupdate(x):
            globalconfig.__setitem__('autoupdate',x)
            if x:
                threading.Thread(target=lambda :getversion(self)).start()
        self.updateswitch.clicked.connect(lambda x:  changeupdate( x)) 

        self.downloadprogress=QProgressBar(self.tab_about)
        self.customSetGeometry(self.downloadprogress, 20, 50, 300, 20)
        
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