from distutils.command.config import config
import functools 
 
from cmath import exp
import functools
from turtle import end_fill

from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout

from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import qtawesome
from PyQt5.QtCore import QThread
import subprocess
from utils.config import globalconfig ,postprocessconfig,noundictconfig
from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox 
 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog
from PyQt5.QtGui import QColor,QFont
import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize
from utils.config import globalconfig 
import qtawesome
from utils.config import globalconfig 

import importlib
from gui.inputdialog import GetUserPlotItems
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab_about(self) :
     
        self.tab_about = QWidget()
        self.tab_widget.addTab(self.tab_about, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_about), " 关于")


        label = QLabel(self.tab_about)
        self.customSetGeometry(label, 20, 20, 500, 500)
        try:
            with open('version.txt','r',encoding='utf8') as ff:
                about=ff.read()
            
            label.setOpenExternalLinks(True)
            label.setText(about)
            label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)


        except:
            pass