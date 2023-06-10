import traceback
import time
import random,threading 
import time
class stripwrapper(dict):
        def __getitem__(self,item):
            t=super().__getitem__(item)
            if type(t)==str:
                return t.strip()
            else:
                return t
def Singleton(cls,**kw):
        _instance={}
        def _singleton(*args,**kwagrs): 
                try:
                    if _instance[cls] .isHidden():
                        _instance[cls].deleteLater() 
                        _instance[cls]=cls(*args,**kwagrs)
                    else: 
                        _instance[cls].activateWindow() 
                        _instance[cls].show() 
                except:
                        _instance[cls]=cls(*args,**kwagrs) 
                return _instance[cls]
        return _singleton
def Singleton_close(cls,**kw):
        _instance={}
        _lock=threading.Lock()
        _status={}
        def _singleton(*args,**kwagrs):
                _lock.acquire()
                if len(_status):    #qapp.processevent会导致卡在#1处，从而多次点击鼠标都会弹出
                    _lock.release()
                    return None
                _status[0]=0
                _lock.release()
                try: 
                    if _instance[cls].isHidden():
                        _instance[cls].deleteLater() 
                        _instance[cls]=cls(*args,**kwagrs) #1
                    else: 
                        _instance[cls].close()
                except:
                    _instance[cls]=cls(*args,**kwagrs) 
                _lock.acquire()
                _status.pop(0)
                _lock.release()
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
        t=threading.Thread(target=func,args=args,kwargs=kwargs) 
        t.start() 
        
    return _wrapper 

def timer(func):
    def _wrapper(*args,**kwargs): 
        t=time.time()
        res=func(*args,**kwargs) 
        print(time.time()-t)
        return res 
    return _wrapper 

