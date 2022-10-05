
from queue import Queue
import time
from utils.config import globalconfig,noundictconfig
import traceback
import json
import requests
import traceback
from threading import Thread
class basetrans:

    @classmethod
    def settypename(self,typename):
        self.typename=typename
    def __init__(self) :

        self.queue=Queue() 

        self.inittranslator() 
        self.t=Thread(target=self.fythread) 
        self.t.setDaemon(True)
        self.t.start()
        self.newline=None
    def gettask(self,content):
        self.queue.put((content))
     
    def inittranslator(self):
        pass
    def translate(self,content):
        pass
    def show(self,res):
        pass
    def show__(self,res):
        if res!='':
            self.show(res)
     
    
    def fythread(self):
        while True: 
            while True:
                content,skip=self.queue.get()
                self.newline=content
                if self.queue.empty():
                    break
            
            if globalconfig['fanyi'][self.typename]['use']==False:
                 
                break
            if skip:
                continue
            if (set(content) -set('「…」、。？！―'))==set():
                continue 
            
            zhanweifu=0
            mp={}
            use=noundictconfig['use']
            if use:
                for key in noundictconfig['dict']:
                    if key in content:
                        content.replace(key,'{XX'++zhanweifu+'}')
                        mp['{XX'++zhanweifu+'}']=key
                        zhanweifu+=1

            res=self.translate(content)
            if use:
                for key in mp:
                    res.replace(key,mp[key])

            if res is None:
                break
            if self.queue.empty() and content==self.newline:
                self.show__(res)

    

            