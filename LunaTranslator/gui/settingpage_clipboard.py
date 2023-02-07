 
from PyQt5.QtWidgets import QWidget,QLabel,QStyle ,QPushButton,QGridLayout,QSpinBox,QComboBox,QScrollArea,QLineEdit,QApplication,QFileDialog
from PyQt5.QtGui import QColor 
from PyQt5.QtCore import Qt 
import functools,sqlite3
from utils.config import globalconfig ,translatorsetting
import os,json
from traceback import print_exc
from gui.pretransfile import sqlite2json
from utils.config import globalconfig ,_TR,_TRL
from utils.utils import selectdebugfile
import socket
from gui.inputdialog import autoinitdialog 

def setTabclip(self) :
          
        grids=[[('提取的文本自动复制到剪贴板',5),(self.getsimpleswitch(globalconfig ,'outputtopasteboard',name='outputtopasteboard'),1)]]
        self.yitiaolong("剪贴板设置",grids)