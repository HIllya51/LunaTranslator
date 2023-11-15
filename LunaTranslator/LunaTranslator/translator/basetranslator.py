from traceback import print_exc
from queue import Queue  

from myutils.config import globalconfig,translatorsetting,static_data
from threading import Thread,Lock
import os,time ,codecs
import zhconv
import sqlite3

from myutils.utils import getproxy
from myutils.exceptions import ArgsEmptyExc
from myutils.wrapper import stripwrapper
class TimeOut(Exception):
    pass
class Threadwithresult(Thread):
    def __init__(self, func,  defalut,ignoreexceptions):
        super(Threadwithresult, self).__init__()
        self.func = func 
        self.result=defalut
        self.istimeout=True
        self.ignoreexceptions=ignoreexceptions
        self.exception=None
    def run(self):
        try:
            self.result = self.func( )
        except Exception as e:
            self.exception=e
        self.istimeout=False
    def get_result(self,timeout=1,checktutukufunction=None):
        #Thread.join(self,timeout)  
        #不再超时等待，只检查是否是最后一个请求，若是则无限等待，否则立即放弃。
        while checktutukufunction and checktutukufunction() and self.istimeout:
            Thread.join(self,0.1) 
            
        if self.ignoreexceptions:
            return self.result
        else:
            if self.istimeout:
                 raise TimeOut()
            elif self.exception:
                 raise self.exception
            else:
                 return self.result
def timeoutfunction( func, timeout=100,default=None,ignoreexceptions=False,checktutukufunction=None):
    t=Threadwithresult(func,  default,ignoreexceptions)
    t.start()
    return t.get_result(timeout,checktutukufunction)

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
    @property
    def is_gpt_like(self):
        try:
            return translatorsetting[self.typename]['is_gpt_like']
        except:
            return False
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
     
    @property
    def multiapikeycurrent(self):
        
        class alternatedict(dict): 
            def __getitem__(self2, __key) :
                t=super().__getitem__(__key)
                if type(t)!=str:
                    raise Exception("Incorrect use of multiapikeycurrent")
                if '|' in t:
                    ts=t.split('|') 
                    t=ts[self.multiapikeycurrentidx% len(ts)]
                return t.strip()
        return alternatedict(translatorsetting[self.typename]['args'])
    ############################################################
    def __init__(self,typename ) :  
        self.typename=typename
        self.multiapikeycurrentidx=-1
        self.queue=Queue() 
        
        
        _=dict(zip(static_data["language_list_translator_inner"],static_data["language_list_translator_inner"]))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        self.langmap_x=_
        try:
            self.inittranslator()
        except:
            print_exc()
        
        self.lastrequesttime=0
        self._cache={}
        
        self.newline=None

        if self.transtype!='pre':
            try:
                self.sqlwrite2=sqlite3.connect('./translation_record/cache/{}.sqlite'.format(typename),check_same_thread = False, isolation_level=None)
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
                self.sqlwrite2.execute('INSERT into cache VALUES(?,?,?,?)',(self.srclang,self.tgtlang,src,trans))
                
            except:
                print_exc()
    @property
    def needzhconv(self):
        l=static_data["language_list_translator_inner"][globalconfig['tgtlang3']]
        return l=='cht' and 'cht' not in self.langmap()
    
    @property
    def using(self):
        return globalconfig['fanyi'][self.typename]['use']
    
    @property
    def transtype(self):
        return globalconfig['fanyi'][self.typename].get('type','free')
    def gettask(self,content):
        self.queue.put((content)) 
    
    
    def longtermcacheget(self,src):
        try:
            ret=self.sqlwrite2.execute('SELECT * FROM cache WHERE source = ?',(src,)).fetchall()
            #有的时候，莫名其妙的卡住，不停的查询失败时的那个句子。。。
        except:
            return None
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
    def cached_translate(self,contentsolved,hira,is_auto_run):
        is_using_gpt_and_retrans= is_auto_run==False and self.is_gpt_like
        if is_using_gpt_and_retrans==False:
            res=self.shorttermcacheget(contentsolved)
            if res:
                return res
        if globalconfig['uselongtermcache']:
            res=self.longtermcacheget(contentsolved)
            if res:
                return res
        
        if self.transtype=='offline':
            res=self.dispatch_translate(contentsolved,hira)
        else:
            res=self.intervaledtranslate(contentsolved,hira)
         
        if globalconfig['uselongtermcache']:
            self.longtermcacheset(contentsolved,res)
        self.shorttermcacheset(contentsolved,res)
        
        return res
    
    def maybecachetranslate(self,contentraw,contentsolved,hira,is_auto_run):
        if self.transtype=='pre':
            res=self.translate(contentraw)
        else: 
            res=self.cached_translate(contentsolved,hira,is_auto_run)
        return res
    def intervaledtranslate(self,content,hira):
        interval=globalconfig['requestinterval']
        current=time.time() 
        self.current=current 
        sleeptime=interval-(current-self.lastrequesttime)
         
        if sleeptime>0:
            time.sleep(sleeptime) 
        self.lastrequesttime=time.time() 
        if (current!=self.current) or (self.using==False):
            raise Exception

        self.multiapikeycurrentidx+=1
         
        res=self.dispatch_translate(content,hira)
        
        return res
    def dispatch_translate(self,content,hira):
        if 'translate_with_extra' in dir(self):
            res=self.translate_with_extra(content,{'hira':hira})
        else:
            res=self.translate(content)
        return res
    @property
    def onlymanual(self):
        if 'manual' not in globalconfig['fanyi'][self.typename] :
            return False
        return globalconfig['fanyi'][self.typename]['manual']
    def fythread(self):
        self.needreinit=False
        while self.using:  
            
            savelast=[]
            while True:
                _=self.queue.get() 
                callback,contentraw,contentsolved,skip,embedcallback,is_auto_run,hira=_
                if embedcallback is not None:
                    savelast.clear()
                
                savelast.append(_)
                if self.queue.empty():
                    break
            if savelast[0][4] is not None:
                callback,contentraw,contentsolved,skip,embedcallback,is_auto_run,hira=savelast.pop(0)
                for _ in savelast:
                    self.gettask(_)
            if embedcallback is None:
                if skip:
                    continue
                if is_auto_run and self.onlymanual:
                    continue
            
                
            try:
                checktutukufunction=lambda:( (embedcallback is not None) or   self.queue.empty()) and self.using
                if checktutukufunction(): 
                    def reinitandtrans():
                        if self.needreinit:
                            self.needreinit=False
                            self.inittranslator()
                        return self.maybecachetranslate(contentraw,contentsolved,hira,is_auto_run)
                    res=timeoutfunction(reinitandtrans,checktutukufunction=checktutukufunction ) 
                    if self.needzhconv:
                        res=zhconv.convert(res,  'zh-tw' )  
                    
                    callback(res,embedcallback) 
                
            except Exception as e:
                if self.using and globalconfig['showtranexception']:
                    if isinstance(e,ArgsEmptyExc):
                        msg=str(e)
                    elif isinstance(e,TimeOut):
                        #更改了timeout机制。timeout只会发生在队列非空时，故直接放弃
                        continue
                    else:
                        print_exc()
                        msg=str(type(e))[8:-2]+' '+str(e).replace('\n','').replace('\r','')
                        self.needreinit=True
                    msg='<msg_1>'+msg
            
                    callback(msg,embedcallback) 
                    
        