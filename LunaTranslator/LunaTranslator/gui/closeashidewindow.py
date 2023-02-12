
from PyQt5.QtWidgets import  QMainWindow ,QApplication
from PyQt5.QtGui import QFont,QCloseEvent
from PyQt5.QtCore import Qt,pyqtSignal 
class closeashidewindow(QMainWindow): 
    showsignal=pyqtSignal() 
    realshowhide=pyqtSignal(bool)
    def __init__(self, args,dic=None,key=None) -> None:
        super().__init__(args )
        self.showsignal.connect(self.showfunction)  
        self.realshowhide.connect(self.realshowhidefunction)
        d=QApplication.desktop()
        self.dic,self.key=dic,key
        if self.dic:
            dic[key][0]=min(max(dic[key][0],0),d.width()-dic[key][2])
            dic[key][1]=min(max(dic[key][1],0),d.height()-dic[key][3])
            self.setGeometry(*dic[key])
    def realshowhidefunction(self,show):
        if show:
            self.showNormal()
        else:
            self.hide()
    def showfunction(self): 
        if self.isMinimized():
            self.showNormal() 
        elif self.isHidden(): 
            self.show()  
        else:
            self.hide()  
    def resizeEvent(self, a0 ) -> None:
        if self.dic:
            if self.isMaximized()==False: 
                self.dic[self.key]=list(self.geometry().getRect())
    def moveEvent(self, a0 ) -> None:
        if self.dic:
            if self.isMaximized()==False: 
                self.dic[self.key]=list(self.geometry().getRect())
    def closeEvent(self, event:QCloseEvent) :  
        self.hide() 
        event.ignore() 
        if self.dic:
            if self.isMaximized()==False: 
                self.dic[self.key]=list(self.geometry().getRect())