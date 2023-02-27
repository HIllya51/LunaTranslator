
from PyQt5.QtWidgets import  QMainWindow ,QApplication,QPushButton,QTabBar,QStylePainter,QStyleOptionTab,QStyle
from PyQt5.QtGui import QFont,QCloseEvent
from PyQt5.QtCore import Qt,pyqtSignal ,QSize ,QRect ,QPoint 
 
import qtawesome 
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

class MySwitch(QPushButton):
    realclicksignal=pyqtSignal(bool)
    def __init__(self,rate, parent = None,sign=True ,enable=True):
        super().__init__(parent) 
        self.setCheckable(True)
        self.setChecked(sign)  
        self.setStyleSheet('''background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;''')
        self.rate= rate
        
        self.clicked.connect(self.clickfunction)
        self.clicked=self.realclicksignal
        self.setIconSize(QSize(int(25*self.rate),
                                 int(25*self.rate)))
        #self.setIcon(qtawesome.icon("fa.check" ,color="#FF69B4" if self.isChecked() else '#dadbdc'))
        self.setIcon(qtawesome.icon("fa.check" ,color="#FF69B4") if self.isChecked() else qtawesome.icon("fa.times" ,color='#dadbdc'))
        self.setEnabled(enable)
    def clickfunction(self,_):
        #self.setIcon(qtawesome.icon("fa.check" ,color="#FF69B4" if self.isChecked() else '#dadbdc'))
        self.setIcon(qtawesome.icon("fa.check" ,color="#FF69B4") if self.isChecked() else qtawesome.icon("fa.times" ,color='#dadbdc'))
        self.realclicksignal.emit(_)
    def setChecked(self,  a0)  :
        super().setChecked(a0)
        self.clickfunction(a0)



class rotatetab(QTabBar): 
    def tabSizeHint(self, index): 
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s
    def paintEvent(self, e) : 
        painter = QStylePainter(self)
        opt = QStyleOptionTab() 
        for i in range(self.count()) :
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save() 
            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r 
            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()  
         