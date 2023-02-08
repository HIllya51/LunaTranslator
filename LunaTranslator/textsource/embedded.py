  
from utils.config import globalconfig ,_TR   
from textsource.textsourcebase import basetext   
import functools,queue,time
class embedded(basetext  ): 
    def __init__(self,textgetmethod,hookselectdialog,pid,hwnd,pname,fallbackfunction,parent) : 
        self.textgetmethod, self.pid,self.hwnd,self.pname,self.fallbackfunction =textgetmethod,pid,hwnd,pname,fallbackfunction 
        self.parent=parent 
        hookselectdialog.changeprocessclearsignal.emit()
        self.hookselectdialog=hookselectdialog
        self.newline=queue.Queue()
        self.agentreceiveddata=''
        self.textgetmethod("<handling>"+_TR("HOOK_内嵌 连接进程")+str(self.pid)) 
        self.parent.startembedsignal.emit(pid,self) 
        super(embedded,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
    def timeout(self): 
        self.embeddedfailed(_TR("连接超时"))
    def detach(self):
        self.textgetmethod("<handling>"+_TR("HOOK_内嵌 进程结束")+str(self.pid)) 
    def unrecognizedengine(self): 
        self.embeddedfailed(_TR("无法识别的引擎"))
    def getenginename(self,name): 
        self.textgetmethod("<handling>"+_TR("识别到引擎")+name)
        self.enginename=name 
    def translate(self,text ,embedcallback):
        self.agentreceiveddata=text
        self.hookselectdialog.getnewsentencesignal.emit(text)
        if globalconfig['autorun']:
            self.newline.put((self.agentreceiveddata,False, embedcallback))
        else:
            embedcallback('zhs',text) 
    def gettextthread(self ): 
            paste_str=self.newline.get()
            return paste_str
    def embeddedfailed(self,result):
        self.end() 
        if globalconfig['embedded']['fallbacktonormalhook']: 
            self.textgetmethod("<error>"+result+'  '+ _TR("内嵌失败，尝试使用普通HOOK"))    
            self.fallbackfunction()
    def runonce(self): 
        self.textgetmethod(self.agentreceiveddata,False)
    def end(self):
        self.ending=True

        self.parent.ga.quit()