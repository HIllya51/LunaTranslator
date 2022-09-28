
from queue import Queue
import time
from utils.config import globalconfig
import traceback
import json
import requests
import traceback
from threading import Thread
class basetrans:

    def updateheader(self,hosturl):
        self.session.headers.update({
            'Origin': hosturl,
             
            'Referer': hosturl,
        })
    def __init__(self) :

        self.queue=Queue()
        
        
        self.headers=  {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        #proxies = { "http": None, "https": None}
    
        self.session=requests.session( )
        self.session.trust_env=False
        self.session.headers.update(self.headers)

        self.inittranslator() 
        self.t=Thread(target=self.fythread)
        
        
        self.t.setDaemon(True)
        self.t.start()
        
    def gettask(self,content):
        self.queue.put((content))
     
    def inittranslator(self):
        pass
    def realfy(self,content):
        pass
    def show(self,res):
        pass
    def show__(self,res):
        if res!='':
            self.show(res)
    def _1realfy(self,content):
        try:
            return self.realfy(content)
        except Exception as ex:
             
            traceback.print_exc()
            
            return ''
    
    def fythread(self):
        while True:
            
            while True:
                content=self.queue.get()
                if self.queue.empty():
                    break
            if globalconfig['fanyi'][self.typename]['use']==False:
                 
                continue
            if len(content)<6:
                continue
            if (set(content) -set('「…」、。？！―'))==set():
                continue
            res=self._1realfy(content)
            if res is None:
                break
            if self.queue.empty():
                self.show__(res)


            