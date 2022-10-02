  
import threading
from selenium import webdriver
from selenium.webdriver.support.select import Select 
import os
import re
import requests 
from traceback import print_exc
from utils.config import globalconfig
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.edge.service import Service as edgeservice
import time
import zipfile
import winreg
def get_Chrome_version():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
    version, types = winreg.QueryValueEx(key, 'version')
    return version
def get_server_chrome_versions():
    '''return all versions list'''
    versionList = []
    url = "https://registry.npmmirror.com/-/binary/chromedriver/"
    rep = requests.get(url).json()
    for item in rep:
        if item['name'][-1]=='/':
            item['name']=item['name'][:-1]
        versionList.append(item["name"])
    return versionList
 
 
class edgetts():
    def trydownloaddriver(self,who,v):
        if who=='edge':
            savep='files/webdriver/edgedriver_win64.zip'
            url=f'https://msedgedriver.azureedge.net/{v}/edgedriver_win64.zip'
        else:
            savep='files/webdriver/chromedriver_win32.zip'
            url=v
        try:
            with closing(requests.get( url, stream=True)) as response:
                file_size=0
                chunk_size = 1024  # 单次请求最大值
                self.content_size = int(response.headers['content-length'])  # 内容体总大小

                with open(savep, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        file_size+=len(data)
                        self.signalprocess.emit(f'正在下载webdriver 总大小{int(1000*(int(self.content_size/1024)/1024))/1000} MB 进度 {int(10000*(file_size/self.content_size))/100}%')
                self.signalprocess.emit(f'下载完毕')
        except:
            self.signal.emit('语音朗读器加载失败,下载webdriver失败','#ff0000')
            print_exc()
            return False
        
        zip_file = zipfile.ZipFile(savep)
        zip_list = zip_file.namelist()
        for f in zip_list :
            zip_file.extract(f, 'files/webdriver/')
        zip_file.close()
        return True
    def __init__(self,signal,signalprocess,object): 
        self.signal=signal
        self.object=object
        self.signalprocess=signalprocess
        edgepath=r'C:\Program Files (x86)\Microsoft\Edge\Application'
        chromepath=r'C:\Program Files\Google\Chrome\Application' 
        edgeok=False
        print('start')
        if os.path.exists(edgepath):
            print('edge exits')
            for f in os.listdir(edgepath): 
                if re.match('\d+\.\d+\.\d+\.\d+',f):
                    version=f
                    break 
            print(version)
            if 'edgeversion' not in globalconfig  or  globalconfig['edgeversion']!=version or os.path.exists('./files/webdriver/msedgedriver.exe')==False:
                
                self.trydownloaddriver('edge',version)
                globalconfig['edgeversion']=version
            print('download ok')
            EDGE = {
                "browserName": "MicrosoftEdge",
                "version": "",
                "platform": "WINDOWS",
                "ms:edgeOptions": {
                    'extensions': [],
                    'args': [
                        '--headless',
                        '--disable-gpu',
                        '--remote-debugging-port=9222',
                    ]}
            }
            try:
                print('11')

                waite=5
                __=[]
                def _(__):
                    service=edgeservice("./files/webdriver/msedgedriver.exe")
                    service.creationflags = CREATE_NO_WINDOW


                    browser = webdriver.Edge(service=service,
                                                service_log_path="nul",
                                                capabilities=EDGE)
                    if len(__)==0:
                        self.browser=browser
                        __.append(1)
                t=threading.Thread(target=_,args=(__,))
                t.start()
                for i in range(waite):
                    time.sleep(1)
                    if len(__)==1:
                        break
                if len(__)==1:
                    edgeok=True
                else:
                    __.append(1)
                    print('dwd')
                    edgeok=False
            except:
                print_exc()
                
                pass
        print('edge error')
        if edgeok==False: 
            try:
                chromeVersion=get_Chrome_version()
            except:
                return 
            print(chromeVersion)
            if 'chromeversion' not in globalconfig  or  globalconfig['chromeversion']!=chromeVersion or os.path.exists('./files/webdriver/chromedriver.exe')==False:

                if 'chromeversion'  in globalconfig :
                    print(globalconfig['chromeversion'])
                versionList = get_server_chrome_versions()
                diff=False
                if chromeVersion in versionList:
                    download_url = f"http://chromedriver.storage.googleapis.com/{chromeVersion}/chromedriver_win32.zip"
                else:
                    chrome_main_version = int(chromeVersion.split(".")[0]) 
                    for version in versionList:
                        if version.startswith(str(chrome_main_version)):
                            diff=True
                            download_url = f"http://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip"
                            print(download_url)
                            break
                
                if download_url == "":
                    self.signal.emit('加载语音朗读器失败','#ff0000') 
                    return 
                down=True
                if 'chromeversion'  in globalconfig and os.path.exists('./files/webdriver/chromedriver.exe') :
                    if diff and globalconfig['chromeversion']==version:
                        down=False
                if down:
                    self.trydownloaddriver('chrome',download_url)
                    
                globalconfig['chromeversion']=version
                
            # 使用谷歌浏览器
            option = webdriver.ChromeOptions()
            option.add_argument("--headless")
            try:
                                
                service = Service("./files/webdriver/chromedriver.exe")
                service.creationflags = CREATE_NO_WINDOW
                self.browser = webdriver.Chrome(   service_log_path="nul",service=service,
                                            options=option)
            except:
                print_exc()
                self.signal.emit('加载语音朗读器失败','#ff0000') 
                return 

        self.browser.get(os.path.join(os.getcwd(),r'files\edgetts.html'))
        select=self.browser.find_element_by_id('select')
        self.select=Select(select) 
        self.voicelist=[option.get_attribute('data-name') for option in self.select.options]
        self.object.settin_ui.loadvoicesignal.emit(self.voicelist)
        print(self.voicelist)
        self.signal.emit('加载语音朗读器完毕','#0000ff') 
    def read(self,content,usevoice):
        try:
            self.browser.find_element_by_id('txt').clear()
            self.browser.find_element_by_id('txt').send_keys(content) 
            self.select.select_by_index(usevoice)
            self.browser.find_element_by_id('play').click()
        except:
            pass
    def close(self):
        try:
            self.browser.close() 
            self.browser.quit()
        except:
            pass
if __name__=='__main__':
    js=edgetts()   
    js.read('アマツツミ + 予約特典 +同梱特典',0)
     