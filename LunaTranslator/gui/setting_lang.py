 
from PyQt5.QtWidgets import QWidget,QLabel,QStyle ,QPushButton,QGridLayout,QSpinBox,QComboBox,QScrollArea,QLineEdit,QApplication,QFileDialog
from PyQt5.QtGui import QColor 
from PyQt5.QtCore import Qt 
import functools,sqlite3
from utils.config import globalconfig ,translatorsetting
import os,json
from traceback import print_exc

from utils.config import globalconfig ,_TR,_TRL
import time
import importlib
import socket
from gui.inputdialog import autoinitdialog
 
def setTablang(self) :
        def changelang_restartocr(idx):
            globalconfig['srclang2']=idx
            self.object.localocrstarter()
        langlist=globalconfig['language_list_translator']
        srclangcombo=self.getsimplecombobox(_TRL(langlist),globalconfig,'srclang2')
        srclangcombo.currentIndexChanged.connect(changelang_restartocr)
        grids=[
            [ 
                ("源语言",5),(srclangcombo,5),'',
                ("目标语言",5),(self.getsimplecombobox(_TRL(langlist),globalconfig,'tgtlang2'),5) ,
            ],
            [('翻译器显示语言(重启生效)',8),(self.getsimplecombobox((globalconfig['language_list']),globalconfig,'languageuse'),5),(self.getcolorbutton(globalconfig,'',callback=lambda :os.startfile(os.path.abspath(f'./files/lang/{globalconfig["language_list"][globalconfig["languageuse"]]}.json')),icon='fa.gear',constcolor="#FF69B4"),1)], 
           
            [''],
        ]
         
         
        self.yitiaolong("语言设置",grids)