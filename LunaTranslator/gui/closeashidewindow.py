
from PyQt5.QtWidgets import QApplication,QTextBrowser,QMainWindow,QFontDialog,QAction,QMenu,QHBoxLayout,QWidget,QPushButton,QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt,pyqtSignal ,QSize,QPoint
class closeashidewindow(QMainWindow): 
    showsignal=pyqtSignal()
    def __init__(self, args) -> None:
        super().__init__(args )
        self.showsignal.connect(self.showfunction) 
        self.savelastgeo=None
    def showfunction(self): 
        if self.isMinimized():
            self.showNormal() 
        elif self.isHidden(): 
            self.show()  
        else:
            self.hide()  
    def showEvent(self, a0 ) -> None:
        if self.savelastgeo:
            self.setGeometry(self.savelastgeo)
        super().showEvent(a0)
    def hideEvent(self, a0 ) -> None:
        self.savelastgeo=self.geometry()
        super().hideEvent(a0)
    def closeEvent(self, event) :  
        self.hide() 
        self.savelastgeo=self.geometry()