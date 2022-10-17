
from queue import Queue 
from utils.config import globalconfig  
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
            
            if self.typename=='rengong':
                res=self.translate(contentraw)
            else:
                res=self.translate(contentsolved)
             
            
            if res!='' and self.queue.empty() and contentraw==self.newline:
                self.show(contentraw,(self.typename,res,mp))

    

            