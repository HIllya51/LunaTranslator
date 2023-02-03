
from queue import Queue  

from utils.config import globalconfig,translatorsetting
from threading import Thread
import os,time
from traceback import print_exc


class basetrans:
     
    @property
    def srclang(self):
        try:
            l=globalconfig['normallanguagelist'][globalconfig['srclang2']]
            if l=='cht' and l not in globalconfig['fanyi'][self.typename]['lang']:
                l='zh'
            if l in globalconfig['fanyi'][self.typename]['lang']:
                return globalconfig['fanyi'][self.typename]['lang'][l]
            else:
                return l
             
        except:
            return ''
    @property
    def tgtlang(self):
        try:
            l=globalconfig['normallanguagelist'][globalconfig['tgtlang2']]
            if l=='cht' and l not in globalconfig['fanyi'][self.typename]['lang']:
                l='zh'
            if l in globalconfig['fanyi'][self.typename]['lang']:
                return globalconfig['fanyi'][self.typename]['lang'][l]
            else:
                return l
             
        except:
            return '' 
    @property
    def config(self):
        try:
            return translatorsetting[self.typename]
        except:
            return {}
    def __init__(self,typename) : 
        self.typename=typename
        self.queue=Queue() 
        try: 
            self.inittranslator() 
        except:
            print_exc()
        self.lastrequeststime=0
        self._cache={}
        self._MAXCACHE = 512
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
      
    def cached_translate(self,contentsolved):
        langkey=(self.srclang,self.tgtlang)
        if langkey not in self._cache:
            self._cache[langkey]={}
        try:
            return self._cache[langkey][contentsolved]
        except KeyError:
            pass
        
        if len(self._cache[langkey]) >= self._MAXCACHE:
            # Drop the oldest item
            try:
                del self._cache[langkey][next(iter(self._cache))]
            except  :
                pass
    
        res=self.translate(contentsolved)
        self._cache[langkey][contentsolved] = res
         
        return res
    def fythread(self):
        while True:  
            t=time.time()
            if self.typename not in globalconfig['fanyi_offline']+globalconfig['fanyi_pre'] and t-self.lastrequeststime <globalconfig['transtimeinternal']:
                time.sleep(t-self.lastrequeststime)
            self.lastrequeststime=t
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
                if self.typename in globalconfig['fanyi_offline']+globalconfig['fanyi_pre']:
                    res=self.translate(contentraw)
                else:
                    
                    res=self.cached_translate(contentsolved)
                    
            except:
                print_exc()
                try:
                    self.inittranslator()
                except:
                    print_exc()
                res=None 
                
            
            if res is not None  and self.queue.empty() and contentraw==self.newline:
                self.show(contentraw,(self.typename,res,mp))

    

            