import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, \
    QGraphicsDropShadowEffect, QPushButton, QApplication, QComboBox,QLabel,QTextBrowser
from PyQt5.QtGui import QFont,QColor,QPalette,QTextCursor
from PyQt5.QtCore import Qt
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent )
        
 

        self.resize(500,500)
        f=QFont()
        f.setPointSize(20)

        self.tt=QTextBrowser(self)
        self.tt.setGeometry(0,0,300,300)
        self.tt.setFont(f)
         
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)
        
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)

        
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)

        
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)

         
         
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)

         
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(20)
        self.shadow2.setOffset(0) 
        self.shadow2.setColor(QColor("blue"))
         
        self.lb=QLabel("你好sdsdsd",self.tt)
        self.lb.setGraphicsEffect(self.shadow2)
       # self.tt.setGraphicsEffect(self.shadow21)
        
        self.lb.setFont(f)
        p=self.palette()
        p.setColor(QPalette.Foreground, QColor("white"))
        self.lb.setPalette(p)
        self.lb.move(1,9)

         
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()