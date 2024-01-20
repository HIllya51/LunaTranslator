import platform
import requests 
import shutil
from myutils.utils import getproxy
from traceback import print_exc
import zipfile,os
from myutils.config import globalconfig  ,_TR ,static_data
import windows
def getvesionmethod():
    url='https://github.com/HIllya51/LunaTranslator/releases/'
    
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
                'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        res= requests.get('https://api.github.com/repos/HIllya51/LunaTranslator/releases/latest', headers=headers ,verify = False,proxies=getproxy()).json() 
        #print(res)
        _version=res['tag_name']
        return _version
    except:
        print_exc()
        return None
def update():
    if platform.architecture()[0]=='64bit': 
        bit=''  
    elif platform.architecture()[0]=='32bit':
        bit='_x86'
    with open('./cache/update/update.bat','w',encoding='utf8') as ff:
                
                ff.write(r''' 
@echo off 
:waitloop
tasklist | find "LunaTranslator_main.exe" > nul
if %errorlevel%==0 (
    timeout /t 1 > nul
    goto waitloop
)
timeout 1
xcopy .\cache\update\LunaTranslator'''+bit+r''' .\ /s /e /c /y /h /r 
exit
                ''') 
    windows.ShellExecute(None, "open", 'cache\\update\\update.bat', "", os.path.dirname('.'), windows.SW_HIDE)

def updatemethod(_version,progresscallback):

    if platform.architecture()[0]=='64bit': 
        bit=''  
    elif platform.architecture()[0]=='32bit':
        bit='_x86'
    else:
        raise Exception
    url="https://github.com/HIllya51/LunaTranslator/releases/download/{}/LunaTranslator{}.zip".format(_version,bit)

    progresscallback('……',0)

    savep='./cache/update/LunaTranslator{}.zip'.format(bit)
    def endcallback():
        if os.path.exists('./cache/update/LunaTranslator'):
            shutil.rmtree('./cache/update/LunaTranslator')
        zipf=(zipfile.ZipFile('./cache/update/LunaTranslator{}.zip'.format(bit)))
        zipf.extractall('./cache/update')
        update()
    def checkalready(size):
        if os.path.exists(savep):
            stats = os.stat(savep)
            if stats.st_size==size:
                progresscallback('总大小{} MB 进度 {}% '.format(int(1000*(int(size/1024)/1024))/1000,int(10000*(size/size))/100),10000)
                endcallback()
                return True
        return False
    try:
        r2 = requests.get(url,stream=True,verify = False,proxies=getproxy()) 
        size = int(r2.headers['Content-Length'])
        if checkalready(size):return
        with open(savep, "wb") as file: 
                sess=requests.session()
                r = sess.get(url,stream=True, verify = False,proxies=getproxy()) 
                file_size=0
                for i in r.iter_content(chunk_size=1024): 
                    if globalconfig['autoupdate']==False: 
                        return
                    if i:  
                        file.write(i) 
                        thislen=len(i)
                        file_size+=thislen 
                        
                        progresscallback('总大小{} MB 进度 {}% '.format(int(1000*(int(size/1024)/1024))/1000,int(10000*(file_size/size))/100),int(10000*file_size/size))
                        
        if globalconfig['autoupdate']==False: 
            return
        if checkalready(size):return
    except:
        print_exc()
        progresscallback('自动更新失败，请手动更新',0)