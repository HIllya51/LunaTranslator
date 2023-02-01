import traceback
import time
import random
from threading import Thread
import time
def Singleton(cls,**kw):
        _instance={}
        def _singleton(*args,**kwagrs):
                if cls not in  _instance: 
                        _instance[cls]=cls(*args,**kwagrs) 
                else: 
                        if _instance[cls] .isHidden():
                            _instance[cls]=cls(*args,**kwagrs)
                        else: 
                            _instance[cls].activateWindow() 
                            _instance[cls].show() 
                return _instance[cls]
        return _singleton
def Singleton_close(cls,**kw):
        _instance={}
        def _singleton(*args,**kwagrs):
                if cls not in  _instance: 
                        _instance[cls]=cls(*args,**kwagrs) 
                else: 
                        if _instance[cls].isHidden():
                            _instance[cls]=cls(*args,**kwagrs)
                        else: 
                            _instance[cls].close()
                return _instance[cls]
        return _singleton
def retryer(**kw):
    def wrapper(func):
        def _wrapper(*args,**kwargs): 
            for _ in range(kw['trytime']):
                 
                try:
                    return func(*args,**kwargs)
                except Exception as ex:
                    traceback.print_exc()
                    time.sleep(random.randint(2,min(2**(_+2),32)))
                    #print('重试次数：',_+1) 
            
        return _wrapper
    return wrapper
def threader(func):
    def _wrapper(*args,**kwargs): 
        t=Thread(target=func,args=args,kwargs=kwargs)
        t.setDaemon(True)
        t.start() 
        
    return _wrapper 

def timer(func):
    def _wrapper(*args,**kwargs): 
        t=time.time()
        res=func(*args,**kwargs)
        #print(func)
        #print(time.time()-t)
        return res

        
    return _wrapper 

