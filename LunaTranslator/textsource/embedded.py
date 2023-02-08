  
from utils.config import globalconfig ,_TR  
from textsource.textractor import textractor 
from textsource.textsourcebase import basetext  
import threading,time,sys
from PyQt5.QtCore import  QThread
from PyQt5.QtWidgets import QMainWindow,QApplication 
from embedded.rpcman3 import RpcServer
from embedded.gameagent3 import GameAgent 
class embedded(basetext  ): 
    def __init__(self,textgetmethod,pid,hwnd,pname,fallbackfunction,parent) : 
        self.textgetmethod, self.pid,self.hwnd,self.pname,self.fallbackfunction =textgetmethod,pid,hwnd,pname,fallbackfunction 
        self.parent=parent
        self.parent.startembedsignal.emit(pid) 
        super(embedded,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
         
    def embeddedfailed(self):
        self.end()
        self.fallbackfunction()
    def runonce(self): 
        self.textgetmethod(self.runonce_line,False)
    
    def end(self):

        
        self.ending=True
     