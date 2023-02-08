  
from utils.config import globalconfig ,_TR  
from textsource.textractor import textractor 
from textsource.textsourcebase import basetext  
import threading,time
from PyQt5.QtCore import  QThread
from PyQt5.QtWidgets import QMainWindow,QApplication 
from embedded.rpcman3 import RpcServer
from embedded.gameagent3 import GameAgent 
class embedded(basetext  ): 
    def __init__(self,textgetmethod,hookselectdialog,pid,hwnd,pname,fallbackfunction,autostarthookcode=None) :
        self.textractor=None 
         
        self.textgetmethod,self.hookselectdialog,self.pid,self.hwnd,self.pname,self.fallbackfunction,self.autostarthookcode=textgetmethod,hookselectdialog,pid,hwnd,pname,fallbackfunction,autostarthookcode
        
        rpc=RpcServer()
        qth=QThread()
        qth.run=lambda: rpc.start()
        #rpc.start()   
        qth.start()
        
        ga=GameAgent(rpc)
        ga.attachProcess(pid=pid)
        rpc.engineTextReceived.connect(ga.sendEmbeddedTranslation)
        rpc.clearAgentTranslation() 
        super(embedded,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
         
    def embeddedfailed(self):
        self.end()
        self.fallbackfunction()
    def runonce(self): 
        self.textgetmethod(self.runonce_line,False)
    
    def end(self):

        
        self.ending=True
     