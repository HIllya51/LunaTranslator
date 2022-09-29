import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QSpinBox,QFontComboBox 
import qtawesome 
import subprocess
from utils.config import globalconfig 
import threading
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  

st=subprocess.STARTUPINFO()
st.dwFlags=subprocess.STARTF_USESHOWWINDOW
st.wShowWindow=subprocess.SW_HIDE
def setTab4(self) :
     
        self.tab_4 = QWidget()
        self.tab_widget.addTab(self.tab_4, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_4), " 其他设置")
 
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 20, 200, 20)
        label.setText("textractor模式特殊设置")

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 50, 200, 20)
        label.setText("窗口最小化追随")
        self.minifollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['minifollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.minifollowswitch, 200, 50, 66,22)
        self.minifollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('minifollow',x)) 

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 80, 200, 20)
        label.setText("窗口移动追随")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['movefollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.movefollowswitch, 200, 80,66, 22)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('movefollow',x)) 

        
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 110, 200, 20)
        # #label.setText("窗口失去焦点不再置顶")
        # label.setText("窗口失去焦点最小化")
        # self.focusfollowswitch =gui.switch.SwitchButton(self.tab_4, sign= globalconfig['focusfollow'], startX=(65-20)*self.rate,textOff='关闭',textOn='使用')
        # self.customSetGeometry(self.focusfollowswitch, 200,110, 65, 20)
        # self.focusfollowswitch.checkedChanged.connect(lambda x:globalconfig.__setitem__('focusfollow',x)) 
        # #self.focusfollowswitch.checkedChanged.connect(lambda x:setss(self,x)) 
        self.hookpid=None
        self.minmaxmoveoberve=subprocess.Popen('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE,startupinfo=st)
        self.minmaxmoveobservethread=threading.Thread(target=minmaxmoveobservefunc,args=(self,))
        self.minmaxmoveobservethread.start()
def minmaxmoveobservefunc(self):
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                x=str(x,encoding='utf8')
                x=x.replace('\r','').replace('\n','')
                 
                x=x.split(' ')
                print(x)
                if len(x) not in [2,6]:
                        break
                x=[int(_) for _ in x]
                if len(x)==2:
                        pid,action=x
                elif len(x)==6:
                        pid,action,x1,y1,x2,y2=x
                 
                if pid==self.hookpid: 
                        if action==1 and globalconfig['movefollow']:
                            self.movestart=[x1,y1,x2,y2]
                             
                        elif action==2 and globalconfig['movefollow']: 
                            moveend=[x1,y1,x2,y2]
                            self.object.translation_ui.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                        elif action==3 and globalconfig['minifollow']: 
                            self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                        elif action==4 and  globalconfig['minifollow']:
                            self.object.translation_ui.hookfollowsignal.emit(3,(0,0))