
from queue import Queue 
from utils.config import globalconfig  
from threading import Thread
import os
from traceback import print_exc
class basetrans:
    @property
    def langmap(self):
        return {
            'ali':['zh','ja','en'],
            'bing':['zh-Hans','ja','en'],
            'baidu':['zh','jp','en'],
            'baiduapi':['zh','jp','en'],
            'byte':['zh','ja','en'],
            'caiyun':['zh','ja','en'],
            'caiyunapi':['zh','ja','en'],
            'deepl':['ZH','JA','EN'],
            'deeplapi':['ZH','JA','EN'],
            'deeplapi-free':['ZH','JA','EN'],
            'google':['zh-CN','ja','en'],
            'google2':['zh-CN','ja','en'],
            'huoshan':['zh','ja','en'],
            'huoshanapi':['zh','ja','en'],
            'iciba':['zh','ja','en'],
            'papago':['zh-CN','ja','en'],
            'qqimt':['zh','ja','en'],
            'sougou':['zh-CHS','ja','en'],
            'sougou2':['zh-CHS','ja','en'],
            'tencent':['zh','jp','en'],
            'tencentapi':['zh','ja','en'],
            'xiaoniu':['zh','ja','en'],
            'yeekit':['nzh','nja','nen'],
            'youdao':['zh-CHS','ja','en'],
            'youdao2':['zh-cn','ja','en'],
            'youdao4':['','jap','eng'],
            'youdao3':['ZH_CN','JA','EN'],
            'youdao5':['zh-CHS','ja','en'],
            'youdaoapi':['zh-CHS','ja','en'],

        }
    @property
    def srclang(self):
        return self.langmap[self.typename][[1,2][globalconfig['srclang']]] 
    @property
    def tgtlang(self):
        return self.langmap[self.typename][[0,2][globalconfig['tgtlang']]] 
    @classmethod
    def settypename(self,typename):
        self.typename=typename
    def __init__(self) :
         
        self.queue=Queue() 
        try: 
            self.inittranslator() 
        except:
            print_exc()
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
     
    
    def fythread(self):
        while True: 
            while True:
                contentraw,(contentsolved,mp),skip=self.queue.get()
                self.newline=contentraw
                if self.queue.empty():
                    break
            
            if globalconfig['fanyi'][self.typename]['use']==False:
                 
                break
            if skip:
                continue
            
            try: 
                if self.typename in ['rengong','premt']:
                    res=self.translate(contentraw)
                else:
                    res=self.translate(contentsolved)
            except:
                print_exc()
                try:
                    self.inittranslator()
                except:
                    print_exc()
                res='' 
            if res!='' and self.queue.empty() and contentraw==self.newline:
                self.show(contentraw,(self.typename,res,mp))

    

            