from traceback import print_exc
from queue import Queue  

from utils.config import globalconfig,translatorsetting,static_data
from threading import Thread,Lock
import os,time ,codecs
import zhconv
from functools import partial 
from utils.utils import timeoutfunction,quote_identifier
import sqlite3

from utils.utils import getproxy
from utils.exceptions import ArgsEmptyExc,TimeOut
from utils.wrapper import stripwrapper
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
    def proxy(self):
        if ('useproxy' not in  globalconfig['fanyi'][self.typename]) or globalconfig['fanyi'][self.typename]['useproxy']:
            return getproxy()
        else:
            return {'https':None,'http':None}
    @property
    def srclang(self):
        try:
            l=static_data["language_list_translator_inner"][globalconfig['srclang3']]
            return self.langmap_x[l] 
        except:
            return ''
    @property
    def tgtlang(self):
        try:
            l=static_data["language_list_translator_inner"][globalconfig['tgtlang3']]
            return self.langmap_x[l] 
        except:
            return '' 
    @property
    def config(self):
        try:
            return stripwrapper(translatorsetting[self.typename]['args'])
        except:
            return {}
    def countnum(self,query):
        try:
            translatorsetting[self.typename]['args']['字数统计']=str(int(self.config['字数统计'])+len(query))
            translatorsetting[self.typename]['args']['次数统计']=str(int(self.config['次数统计'])+1)
        except:
            translatorsetting[self.typename]['args']['字数统计']=str( len(query))
            translatorsetting[self.typename]['args']['次数统计']='1'

    def checkempty(self,items):
        emptys=[]
        for item in items:
            if (self.config[item])=='':
                emptys.append(item)
        if len(emptys):
            raise ArgsEmptyExc(emptys)
            
    
    ############################################################
    def __init__(self,typename ) :  
        self.typename=typename
        self.multiapikeycurrentidx=0
        self.queue=Queue() 
        
        
        _=dict(zip(static_data["language_list_translator_inner"],static_data["language_list_translator_inner"]))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        self.langmap_x=_

        timeoutfunction(self.inittranslator,max(globalconfig['translatortimeout'],5))
        self.lastrequeststime=0
        self._cache={}
        
        self.newline=None

        if self.typename not in static_data["fanyi_pre"]:
            try:
                self.sqlwrite2=sqlite3.connect(f'./translation_record/cache/{typename}.sqlite',check_same_thread = False, isolation_level=None)
                try:
                    self.sqlwrite2.execute('CREATE TABLE cache(srclang,tgtlang,source,trans);')
                except:
                    pass
            except:
                print_exc
            self.sqlqueue=Queue()
            Thread(target= self.sqlitethread).start()
        Thread(target=self.fythread).start() 
    
    def sqlitethread(self):
        while True:
            task=self.sqlqueue.get()
            try:
                
                src,trans=task 
                src=quote_identifier(src)  
                trans=quote_identifier(trans)
                self.sqlwrite2.execute(f'INSERT into cache VALUES({quote_identifier(self.srclang)},{quote_identifier(self.tgtlang)},{src},{trans})')
                
            except:
                print_exc()
    @property
    def needzhconv(self):
        l=static_data["language_list_translator_inner"][globalconfig['tgtlang3']]
        return l=='cht' and 'cht' not in self.langmap()
    
    @property
    def using(self):
        return globalconfig['fanyi'][self.typename]['use']
    def gettask(self,content):
        self.queue.put((content)) 
    
    
    def longtermcacheget(self,src):
        src=quote_identifier(src)
        ret=self.sqlwrite2.execute(f'SELECT * FROM cache WHERE source = {src}').fetchall()
        for srclang,tgtlang,source,trans in ret:
            if (srclang,tgtlang)==(self.srclang,self.tgtlang):
                return trans
    
    def longtermcacheset(self,src,tgt):
        self.sqlqueue.put((src,tgt))
    def shorttermcacheget(self,src):
        langkey=(self.srclang,self.tgtlang)
        if langkey not in self._cache:
            self._cache[langkey]={}
        try:
            return self._cache[langkey][src]
        except KeyError:
            return None
        
    def shorttermcacheset(self,src,tgt):
        langkey=(self.srclang,self.tgtlang)
        
        if langkey not in self._cache:
            self._cache[langkey]={}
        self._cache[langkey][src] = tgt
    def cached_translate(self,contentsolved):

        res=self.shorttermcacheget(contentsolved)
        if res:
            return res
        if globalconfig['uselongtermcache']:
            res=self.longtermcacheget(contentsolved)
            if res:
                return res
        
        res=self.translate(contentsolved)
        
         
        if globalconfig['uselongtermcache']:
            self.longtermcacheset(contentsolved,res)
        self.shorttermcacheset(contentsolved,res)
        
        return res
    
    def maybecachetranslate(self,contentraw,contentsolved):
        if self.typename not in static_data["fanyi_pre"]:
            res=self.cached_translate(contentsolved)
        else: 
            res=self.translate(contentraw)
        return res
    
    @property
    def onlymanual(self):
        if 'manual' not in globalconfig['fanyi'][self.typename] :
            return False
        return globalconfig['fanyi'][self.typename]['manual']
    def fythread(self):
        while self.using:  
            t=time.time()
            if self.typename not in static_data["fanyi_offline"]+static_data["fanyi_pre"] and ((t-self.lastrequeststime) <globalconfig['transtimeinternal']):
                time.sleep(globalconfig['transtimeinternal']-(t-self.lastrequeststime))
            self.lastrequeststime=t
            while True:
                callback,contentraw,contentsolved,skip,embedcallback,shortlongskip=self.queue.get() 
                if self.queue.empty():
                    break
            
            if skip:
                continue
            if shortlongskip and self.onlymanual:
                continue
            runtime=2 if globalconfig['errorretry'] else 1
            for i in range(runtime):
                
                    
                    
                try:
                    if self.queue.empty() and self.using:
                        if i!=0:
                            timeoutfunction(self.inittranslator,max(globalconfig['translatortimeout'],5),ignoreexceptions=False)

                        res=timeoutfunction(partial(self.maybecachetranslate,contentraw,contentsolved),globalconfig['translatortimeout'],default='',ignoreexceptions=False) 
                        if self.needzhconv:
                            res=zhconv.convert(res,  'zh-tw' )  
                        
                        callback(res,embedcallback) 
                    break
                except Exception as e:
                    retry=True
                    
                    if isinstance(e,ArgsEmptyExc):
                        msg=str(e)
                        retry=False
                    elif isinstance(e,TimeOut):
                        msg=str(e)
                    else:
                        print_exc()
                        msg=str(type(e))[8:-2]+' '+str(e).replace('\n','').replace('\r','')
                    
                    msg='<msg>'+msg
                    if retry==False:
                        if globalconfig['showtranexception']:
                            callback(msg,embedcallback) 
                        break
                    else:
                        if i==runtime-1:
                            if globalconfig['showtranexception']:
                                callback(msg,embedcallback) 
            

            