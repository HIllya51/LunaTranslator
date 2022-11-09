 
from PyQt5.QtCore import Qt,QSize,pyqtSignal ,QRect ,QUrl,QObject
 
from PyQt5.QtWidgets import  QColorDialog,QSpinBox,QDoubleSpinBox,QPushButton,QComboBox,QLabel,QScrollArea,QWidget,QGridLayout,QApplication
from PyQt5.QtGui import QColor ,QFont
from utils.config import globalconfig 
from PyQt5.QtWidgets import  QTabWidget,QMainWindow 
import qtawesome   ,win32con,win32gui
import os
from gui.switchbutton import MySwitch
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent ,QSoundEffect 
from gui.settingpage1 import setTabOne
from gui.settingpage2 import setTabTwo

from utils.config import globalconfig ,_TR
from gui.settingpage_xianshishezhi import setTabThree
from gui.settingpage4 import setTab4 
from gui.settingpage_tts import setTab5 
from gui.settingpage_ocr import setTab6 
from gui.settingpage7 import setTab7
from gui.settingpage_about import setTab_about
from gui.rotatetab import  rotatetab
from gui.settingpage_cishu import setTabcishu
from gui.settingpage_quick import setTab_quick
class wavmp3player(QObject):
    def __init__(self):
        super().__init__( )
        self.mp3=QMediaPlayer()
        self.wav=QSoundEffect()
    def mp3playfunction(self,path,volume):
        if os.path.exists(path)==False:
            return
        self.mp3.stop()
        self.wav.stop() 
        
        if path[-4:]=='.wav':
            self.wav.setSource(QUrl.fromLocalFile(path))#path))
            self.wav.setVolume(volume)
            self.wav.play()
        elif path[-4:]=='.mp3': 
            self.mp3.setMedia(QMediaContent(QUrl(path)))
            self.mp3.setVolume(volume)
            self.mp3.play()
class Settin(QMainWindow) :
    resetsourcesignal=pyqtSignal()
    loadtextractorfalse=pyqtSignal( ) 
    voicelistsignal=pyqtSignal(list)
    mp3playsignal=pyqtSignal(str,int)
    autostarthooksignal=pyqtSignal(int,int,str,list) 
    versiontextsignal=pyqtSignal( str)
    progresssignal=pyqtSignal(str,int)
    clicksourcesignal=pyqtSignal(int)
    fontbigsmallsignal=pyqtSignal(int) 
    def showEvent(self, a0   ) -> None:
         win32gui.SetWindowPos(int(self. winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE) 
         self.realishide=False
         print('show')
         return super().showEvent(a0)
    def hideEvent(self, a0 ) -> None:
         self.realishide=True
         return super().hideEvent(a0)
    def automakegrid(self,grid,lis): 
        maxl=0
        for nowr,line in enumerate(lis):
                nowc=0
                for i in line:
                        if type(i)==str:
                                wid,cols=QLabel(""),1
                        elif type(i)!=tuple:
                                wid,cols=i,1
                        elif len(i)==2:
                                
                                wid,cols=i
                                if type(wid)==str  :
                                    if wid=="":
                                        wid=QLabel("")
                                    else:
                                        wid=QLabel(_TR(wid))
                        grid.addWidget(wid,nowr,nowc,1,cols)
                        nowc+=cols   
                maxl=max(maxl,nowc)
                
        ww=self.window_width-180*self.rate-self.object.scrollwidth
        
        
        for c in range(maxl):

            grid.setColumnMinimumWidth(c,ww//maxl)
    def getspinbox(self,mini,maxi,d,key,double=False, step=1,callback=None,name=None ):
        if double:
            s=QDoubleSpinBox()
            s.setDecimals(1)
        else:
            s=QSpinBox() 
        s.setMinimum(mini)
        s.setMaximum(maxi)
        s.setSingleStep(step)
        s.setValue(d[key])
        if callback:
            s.valueChanged.connect(lambda x:callback(x))
        else:
            s.valueChanged.connect(lambda x:d.__setitem__(key,x))
        if name:
            setattr(self,name,s)
        return s
    def getsimpleswitch(self,d,key,enable=True,callback=None,name=None):
        b=MySwitch(sign=d[key],enable=enable)
        if callback:
            b.clicked.connect( callback )
        else:
            b.clicked.connect(lambda x:d.__setitem__(key,x))
        if name:
            setattr(self,name,b)
        return b
     
    def getcolorbutton(self,d,key,callback,name=None,icon="fa.paint-brush",constcolor=None,enable=True):

        b=QPushButton(qtawesome.icon(icon, color=constcolor if constcolor else d[key]), ""  )
        b.setEnabled(enable)
        self.customSetIconSize(b, 20, 20)  
        b.setStyleSheet("background: transparent;") 
        b.clicked.connect(  callback)  
        if name:
            setattr(self,name,b)
        return b
    def getsimplecombobox(self,lst,d,k):
        s=QComboBox( )  
        s.addItems(lst)
        s.setCurrentIndex(d[k])
        s.currentIndexChanged.connect(lambda x:d.__setitem__(k,x))
        return s
    def __init__(self, object):
        
        super(Settin, self).__init__(object.translation_ui) 
        #self.setWindowFlag(Qt.Tool,False)
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player=wavmp3player()
        self.realishide=True
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)
        self.object = object  
        self.needupdate=False
        # 界面缩放比例
        self.rate = self.object.screen_scale_rate
        # 界面尺寸
        self.window_width = int(900*self.rate)
        self.window_height = int(550*self.rate)
        
        self.savelastrect=None
        self.setFixedSize(self.window_width, self.window_height) 
        d=QApplication.desktop()
        self.move ((d.width()-self.width())/2,((d.height()-self.height())/2))
        #self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        #self.setWindowFlags( Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR("设置"))
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        
        self.setStyleSheet("font: 11pt '"+globalconfig['settingfonttype']+"' ; color: \"#595959\"" )  
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        
        #self.tab_widget.setGeometry(self.geometry())  
        tabbar=rotatetab(self.tab_widget)
         
        
        # tabbar.setStyleSheet("""   
        #         font:18pt '黑体';       
        #        """ )
        
        self.tab_widget.setTabBar(tabbar) 
        self.tab_widget.setStyleSheet(
            '''QTabBar:tab { 
                width: %spx;
                height: %spx;
                font:18pt  ;  }
            '''%(50*self.rate,180*self.rate)
        )
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.hooks=[] 

        import time
        t1=time.time()
        
        setTabOne(self) 
        setTabTwo(self) 
        setTab4(self)
        setTab6(self)
        setTabThree(self) 
        setTab5(self)
        
        setTab7(self)
        setTabcishu(self)
        
        setTab_quick(self) 
        setTab_about(self)
        
        self.usevoice=0
      
    def yitiaolong(self,title,grid):
        lay,t=self. getscrollwidgetlayout(title)
        t.setFixedHeight(len(grid)*30*self.rate)

        self.automakegrid(lay,grid) 
    def getscrollwidgetlayout(self,title):
        scroll = QScrollArea()  
        self.tab_widget.addTab(scroll, _TR(title))   
        
        scroll.setHorizontalScrollBarPolicy(1)
        scroll.setStyleSheet('''QScrollArea{
background-color:transparent;
}''')
        t = QWidget() 
        lay=QGridLayout( )     
        t.setLayout(lay)  
        scroll.setWidget(t)
        sw=self.object.scrollwidth
        
        t.setFixedWidth(self.window_width-180*self.rate-sw)
        masklabel=QLabel(t)
        masklabel.setGeometry(0,0,2000,2000)
        masklabel.setStyleSheet("color:white;background-color:white;")
        return  lay,t
    # 根据分辨率定义控件位置尺寸
    def customSetGeometry(self, object, x, y, w, h) :

        object.setGeometry(QRect(int(x*self.rate),
                                 int(y*self.rate), int(w*self.rate),
                                 int(h*self.rate)))
 
    def customSetIconSize(self, object, w, h) : 
        object.setIconSize(QSize(int(w * self.rate),
                                 int(h * self.rate))) 
    def closeEvent(self, event) : 
        self.hide()
    def ChangeTranslateColor(self, translate_type,button,item=None,name=None) :
            nottransbutton=['rawtextcolor','backcolor','miaobiancolor','shadowcolor','buttoncolor']
            if translate_type in nottransbutton:
                color = QColorDialog.getColor(QColor(globalconfig[translate_type]), self )  
            else:
                color = QColorDialog.getColor(QColor(globalconfig['fanyi'][translate_type]['color']), self )
            if not color.isValid() :
                return
            if button is None:
                button=getattr(item,name)
            button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
            
            nottransbutton=['rawtextcolor','backcolor','miaobiancolor','shadowcolor','buttoncolor']
            if translate_type in nottransbutton: 
                globalconfig[translate_type]=color.name()  
            else:
                globalconfig['fanyi'][translate_type]['color']=color.name() 
            if translate_type=='backcolor': 
                self.object.translation_ui.translate_text.setStyleSheet("border-width: 0;\
                                            border-style: outset;\
                                            border-top: 0px solid #e8f3f9;\
                                            color: white;\
                                             \
                                            background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
                self.object.translation_ui._TitleLabel.setStyleSheet("border-width: 0;\
                                            border-style: outset;\
                                            border-top: 0px solid #e8f3f9;\
                                            color: white;\
                                            font-weight: bold;\
                                            background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
             
