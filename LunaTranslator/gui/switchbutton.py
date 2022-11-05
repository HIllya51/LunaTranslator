
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect,pyqtSignal ,QSize
import qtawesome
import utils.screen_rate  
class MySwitch(QtWidgets.QPushButton):
    realclicksignal=pyqtSignal(bool)
    def __init__(self, parent = None,sign=True ,enable=True):
        super().__init__(parent) 
        self.setCheckable(True)
        self.setChecked(sign)  
        self.setStyleSheet('''background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;''')
        self.rate= utils.screen_rate.getScreenRate() 
        self.clicked.connect(self.clickfunction)
        self.clicked=self.realclicksignal
        self.setIconSize(QSize(int(30*self.rate),
                                 int(30*self.rate)))
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
 