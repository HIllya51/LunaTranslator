
from threading import Thread
import os,time,sys
from traceback import print_exc
def debugsaveerr():
    def __():
        while True:
            time.sleep(1)
            sys.stderr.flush()
    if len(sys.argv)==1: 
        try:
            sys.stderr=open('./cache/errlog.txt','w',encoding='utf8')
            Thread(target=__).start()
        except:
            pass
def argsort(l):
    ll=list(range(len(l)))
    ll.sort(key= lambda x:l[x])
    return ll
import os

def selectdebugfile(path ):
    p=None
    if os.path.exists(os.path.join('./LunaTranslator',path)):
        p= os.path.abspath(os.path.join('./LunaTranslator',path)) 
    if p  :
        os.startfile(p)
    return p
class Threadwithresult(Thread):
    def __init__(self, func,  defalut=None):
        super(Threadwithresult, self).__init__()
        self.func = func 
        self.result=defalut
    def run(self):
        try:
            self.result = self.func( )
        except:
            print_exc()
    def get_result(self,timeout=1):
        Thread.join(self,timeout)  
        return self.result
def timeoutfunction( func, timeout=100,default=None):
    t=Threadwithresult(func=func,  defalut=default)
    t.start()
    return t.get_result(timeout)