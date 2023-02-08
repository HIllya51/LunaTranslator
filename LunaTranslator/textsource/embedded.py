  
from utils.config import globalconfig ,_TR   
from textsource.textsourcebase import basetext   
import functools,queue
class embedded(basetext  ): 
    def __init__(self,textgetmethod,pid,hwnd,pname,fallbackfunction,parent) : 
        self.textgetmethod, self.pid,self.hwnd,self.pname,self.fallbackfunction =textgetmethod,pid,hwnd,pname,fallbackfunction 
        self.parent=parent 
        self.newline=queue.Queue()
        self.agentreceiveddata=''
        self.newline.put("<handling-1>"+_TR("连接进程")+str(self.pid)) 
        self.parent.startembedsignal.emit(pid,self) 
        super(embedded,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
    def timeout(self):
        self.newline.put('<error>'+_TR("连接超时"))
        self.embeddedfailed()
    def unrecognizedengine(self):
        self.newline.put("<error>"+_TR("无法识别的引擎"))
        self.embeddedfailed()
    def getenginename(self,name): 
        self.newline.put("<handling>"+_TR("识别到引擎")+name)
    def translate(self,text ,embedcallback):
        self.agentreceiveddata=text
        self.newline.put((self.agentreceiveddata,False, embedcallback))
    def gettextthread(self ):
            #print(333333)
            paste_str=self.newline.get()
            return paste_str
    def embeddedfailed(self):
        self.end() 
        if globalconfig['embedded']['fallbacktonormalhook']:
            self.newline.put("<error>"+_TR("内嵌失败，尝试使用普通HOOK"))
            self.fallbackfunction()
    def runonce(self): 
        self.textgetmethod(self.agentreceiveddata,False)
     