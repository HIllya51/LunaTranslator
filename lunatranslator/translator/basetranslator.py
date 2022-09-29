
from queue import Queue
import time
from utils.config import globalconfig
import traceback
import json
import requests
import traceback
from threading import Thread
class basetrans:
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
                content,skip=self.queue.get()
                self.newline=content
                if self.queue.empty():
                    break
            if skip:
                continue
            if globalconfig['fanyi'][self.typename]['use']==False:
                continue
            if (set(content) -set('「…」、。？！―'))==set():
                continue
            res=self._1realfy(content)
            if res is None:
                break
            if self.queue.empty() and content==self.newline:
                self.show__(res)


            