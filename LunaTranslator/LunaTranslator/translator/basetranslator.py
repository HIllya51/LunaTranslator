
from queue import Queue  

from utils.config import globalconfig,translatorsetting
from threading import Thread
import os,time 
import zhconv
from functools import partial
from utils import somedef
from utils.utils import timeoutfunction

class basetrans: 
    def langmap(self):
        return {}
    def end(self):
        pass
    def inittranslator(self):
        pass
    def translate(self,content):
        return ''
    ############################################################
    @property
    def srclang(self):
        try:
            l=somedef.language_list_translator_inner[globalconfig['srclang3']]
            return self.langmap_x[l] 
        except:
            return ''
    @property
    def tgtlang(self):
        try:
            l=somedef.language_list_translator_inner[globalconfig['tgtlang3']]
            return self.langmap_x[l] 
        except:
            return '' 
    @property
    def config(self):
        try:
            return translatorsetting[self.typename]['args']
        except:
            return {}
    def countnum(self,query):
        try:
            self.config['字数统计']=str(int(self.config['字数统计'])+len(query))
            self.config['次数统计']=str(int(self.config['次数统计'])+1)
        except:
            self.config['字数统计']=str( len(query))
            self.config['次数统计']='1'

 
    ############################################################
    def __init__(self,typename ,callback) :  
        self.typename=typename
        self.queue=Queue() 
        self.callback=callback
        timeoutfunction(self.inittranslator,globalconfig['translatortimeout'])
        
        _=dict(zip(somedef.language_list_translator_inner,somedef.language_list_translator_inner))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        self.langmap_x=_

        
        self.lastrequeststime=0
        self._cache={}
        self._MAXCACHE = 512 
        self.newline=None
        Thread(target=self.fythread).start() 
    
    @property
    def needzhconv(self):
        l=somedef.language_list_translator_inner[globalconfig['tgtlang3']]
        return l=='cht' and 'cht' not in self.langmap()
    
    @property
    def using(self):
        return globalconfig['fanyi'][self.typename]['use']
    def gettask(self,content):
        self.queue.put((content)) 
    
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
    
    def maybecachetranslate(self,contentraw,contentsolved):
        if self.typename in somedef.fanyi_pre:
            res=self.translate(contentraw)
        else: 
            res=self.cached_translate(contentsolved)
        return res
    def fythread(self):
        while self.using:  
            t=time.time()
            if self.typename not in somedef.fanyi_offline+somedef.fanyi_pre and t-self.lastrequeststime <globalconfig['transtimeinternal']:
                time.sleep(t-self.lastrequeststime)
            self.lastrequeststime=t
            while True:
                contentraw,(contentsolved,mp),skip,embedcallback=self.queue.get() 
                if self.queue.empty():
                    break
            self.newline=contentraw
            if skip:
                continue
            
            
            res=timeoutfunction(partial(self.maybecachetranslate,contentraw,contentsolved),globalconfig['translatortimeout']) 
            if res is None:
                timeoutfunction(self.inittranslator,globalconfig['translatortimeout'])
                res=timeoutfunction(partial(self.maybecachetranslate,contentraw,contentsolved),globalconfig['translatortimeout']) 
            if res is None:
                continue 
            if self.needzhconv:
                res=zhconv.convert(res,  'zh-tw' )  
            if self.queue.empty() and contentraw==self.newline and self.using:
                self.callback(contentraw,(self.typename,res,mp),embedcallback) 
        self.end()

            