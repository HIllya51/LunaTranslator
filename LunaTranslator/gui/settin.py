from PyQt5.QtCore import Qt,QSize,pyqtSignal ,QRect 
 
from PyQt5.QtWidgets import  QColorDialog
from PyQt5.QtGui import QColor ,QFont
from utils.config import globalconfig 
from PyQt5.QtWidgets import  QTabWidget,QMainWindow 
import qtawesome   
      
from gui.settingpage1 import setTabOne
from gui.settingpage2 import setTabTwo
from gui.settingpage3 import setTabThree
from gui.settingpage4 import setTab4 
from gui.settingpage5 import setTab5 
from gui.rotatetab import customtabstyle
class Settin(QMainWindow) :
    resetsourcesignal=pyqtSignal()
    loadtextractorfalse=pyqtSignal( ) 
    voicelistsignal=pyqtSignal(list)
    autostarthooksignal=pyqtSignal(int,str,tuple)
    def __init__(self, object):

        super(Settin, self).__init__()

        self.object = object  
        
        # 界面缩放比例
        self.rate = self.object.screen_scale_rate
        # 界面尺寸
        self.window_width = int(800*self.rate)
        self.window_height = int(400*self.rate)
         
        self.setFixedSize(self.window_width, self.window_height) 
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        
        self.setWindowTitle("设置")
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        
        self.setStyleSheet("font: 11pt '黑体' ; color: \"#595959\"" )
        
        #self.setFont((QFont("黑体",11,QFont.Bold)))
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(self.geometry()) 
        self.tab_widget.setTabPosition(QTabWidget.West)
         
        self.hooks=[] 
        setTabOne(self)
        setTabTwo(self)
        setTabThree(self) 
        setTab5(self)
        setTab4(self)

        self.setStyle(customtabstyle()) #必须放后面 不然其他样式全都失效
        self.usevoice=0
     
    def hideEvent(self,e):
        if self.object.hookselectdialog.hiding==False:
            self.object.hookselectdialog.hide()
        if 'a' in dir(self):
            self.a.close()
    
    
    

    # 根据分辨率定义控件位置尺寸
    def customSetGeometry(self, object, x, y, w, h) :

        object.setGeometry(QRect(int(x*self.rate),
                                 int(y*self.rate), int(w*self.rate),
                                 int(h*self.rate)))
 
    def customSetIconSize(self, object, w, h) :

        object.setIconSize(QSize(int(w * self.rate),
                                 int(h * self.rate)))
   
    def closeEvent(self, event) : 
        self.closed=True
        
            
    def ChangeTranslateColor(self, translate_type,button) :
            if translate_type=='raw':
                color = QColorDialog.getColor(QColor(globalconfig['rawtextcolor']), self, "设定原文显示时的颜色")
            elif translate_type=='back':
                color = QColorDialog.getColor(QColor(globalconfig['backcolor']), self, "设定背景颜色")
            else:
                color = QColorDialog.getColor(QColor(globalconfig['fanyi'][translate_type]['color']), self, "设定所选翻译显示时的颜色")
            if not color.isValid() :
                return
        
            button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
            if translate_type=='raw':
                globalconfig['rawtextcolor']=color.name()
            elif translate_type=='back':
                globalconfig['backcolor']=color.name()
                self.object.translation_ui.translate_text.setStyleSheet("border-width: 0;\
                                            border-style: outset;\
                                            border-top: 0px solid #e8f3f9;\
                                            color: white;\
                                            font-weight: bold;\
                                            background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
                self.object.translation_ui._TitleLabel.setStyleSheet("border-width: 0;\
                                            border-style: outset;\
                                            border-top: 0px solid #e8f3f9;\
                                            color: white;\
                                            font-weight: bold;\
                                            background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
            else:
                globalconfig['fanyi'][translate_type]['color']=color.name() 
