import functools 

from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox 
 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog
from PyQt5.QtGui import QColor,QFont
import functools
from utils.config import globalconfig 
import qtawesome
from utils.config import globalconfig 


from gui.inputdialog import GetUserPlotItems
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab6(self) :
     
        tab = QWidget()
        self.tab_widget.addTab(tab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(tab), " OCR设置")
 
        #initfanyiswitchs_auto(self)

def initocrswitchs_auto(self):
        num=0
        
        for fanyi in globalconfig['fanyi']:
            y=70+40*(num//3)
            x=20+220*(num%3)
            initfanyiswitchs(self,fanyi,(x, y, 65, 20),(x+70, y, 20,20),(x+110, y, 20,20),(x+150, y, 20,20))
            num+=1

# def initfanyiswitchs(self,name,namepos,switchpos,colorpos,settingpos):

#         label = QLabel(self.tab_2)
#         self.customSetGeometry(label, *namepos)
#         label.setText(globalconfig['fanyi'][name]['name']+":")
#         p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['fanyi'][name]['use'], textOff='关闭',textOn='使用')
        
#         self.customSetGeometry(p, *switchpos)
#         def fanyiselect( who,checked):
#             if checked : 
#                 globalconfig['fanyi'][who]['use']=True
#                 self.object.prepare(who)

#             else:
#                 globalconfig['fanyi'][who]['use']=False 
#         p.clicked.connect(functools.partial( fanyiselect,name))
#         s=QPushButton(qtawesome.icon('fa.paint-brush', color=globalconfig['fanyi'][name]['color']), "", self.tab_2)
         
#         self.customSetIconSize(s, 20, 20)
#         self.customSetGeometry(s, *colorpos) 
#         s.setStyleSheet("background: transparent;" )
#         s.clicked.connect(lambda: self.ChangeTranslateColor(name,s))  
     

        
#         if 'argsfile' in globalconfig['fanyi'][name]:
#             s1 = QPushButton( "", self.tab_2)
#             self.customSetIconSize(s1, 20, 20)
#             self.customSetGeometry(s1, *settingpos)
#             s1.setStyleSheet("background: transparent;") 
            
#             s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
#             s1.clicked.connect(lambda x:GetUserPlotItems(self,name))
      