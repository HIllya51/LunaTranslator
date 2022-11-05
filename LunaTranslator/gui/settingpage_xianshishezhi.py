import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QDoubleSpinBox,QFontComboBox ,QComboBox,QSpinBox,QGridLayout,QHBoxLayout
import qtawesome 
 
from utils.config import globalconfig 
  
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def fontbigsmallfunction(self,t):
        self.fontSize_spinBox.setValue(self.fontSize_spinBox.value()+0.1*t)

def autogrid(grid,wid,cols=1,newline=False):
        if newline:
                grid.nowr+=1
                grid.nowc=0
        grid.addWidget(wid,grid.nowr,grid.nowc,1,cols)
        grid.nowc+=cols 
def automakegrid(grid,lis): 
        for nowr,line in enumerate(lis):
                nowc=0
                for i in line:
                        if type(i)==str:
                                wid,cols=QLabel(""),1
                        elif type(i)!=tuple:
                                wid,cols=i,1
                        elif len(i)==2:
                                wid,cols=i
                        grid.addWidget(wid,nowr,nowc,1,cols)
                        nowc+=cols  
def __changeuibuttonstate(self,x): 
                globalconfig.__setitem__('isshowrawtext',x)
                self.object.translation_ui.showhiderawbutton.setIcon(qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color=globalconfig['buttoncolor'])) 
                self.show_hira_switch .setEnabled(x)
                self.showatmiddleswitch .setEnabled(x) 

def setTabThree(self) :
     
        self.tab_3 = QWidget()
        self.tab_widget.addTab(self.tab_3, "显示设置") 
        
        self.fontbigsmallsignal.connect(functools.partial(fontbigsmallfunction,self)) 
        self.xianshishezhilayout=QGridLayout(self.tab_3)    
        self.tab_3.setLayout(self.xianshishezhilayout)
        self.xianshishezhilayout.nowr=-1
         
        self.horizontal_slider = QSlider(self.tab_3 ) 
        self.horizontal_slider.setMaximum(100)
        self.horizontal_slider.setMinimum(1)
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.horizontal_slider.setValue(0)
        self.horizontal_slider.setValue(globalconfig['transparent'])
        self.horizontal_slider.valueChanged.connect(functools.partial(changeHorizontal,self))  
        self.horizontal_slider_label = QLabel( ) 
        self.horizontal_slider_label.setText("{}%".format(globalconfig['transparent'])) 
        self.font_comboBox = QFontComboBox(self.tab_3) 
        self.font_comboBox.activated[str].connect(lambda x:globalconfig.__setitem__('fonttype',x))  
        self.comboBox_font = QFont(globalconfig['fonttype'])
        self.font_comboBox.setCurrentFont(self.comboBox_font)  
                
        def __changeselectmode(x):
                globalconfig.__setitem__('selectable',x)
                if x:
                        self.object.translation_ui.masklabel.hide()
                else:
                        self.object.translation_ui.masklabel.show()
        def _useresizebutton(x):
                globalconfig.__setitem__('useresizebutton',x)
                self.object.translation_ui.showhidetoolbuttons() 
        def _usefullscreenbutton(x):
                globalconfig.__setitem__('usefullscreenbutton',x)
                self.object.translation_ui.showhidetoolbuttons() 
        buttongrid=[
                [(QLabel('不透明度'),2),(self.horizontal_slider,8),(self.horizontal_slider_label,2)],
                [(QLabel('原文颜色'),3), self.getcolorbutton(globalconfig,'rawtextcolor',callback=lambda: self.ChangeTranslateColor("rawtextcolor", self.original_color_button),name='original_color_button'),'',(QLabel('翻译窗口背景颜色'),3),self.getcolorbutton(globalconfig,'backcolor',callback=lambda: self.ChangeTranslateColor("backcolor", self.back_color_button),name='back_color_button'),'',(QLabel('工具按钮颜色（重启生效）'),3),self.getcolorbutton(globalconfig,'buttoncolor',callback=lambda: self.ChangeTranslateColor("buttoncolor", self.back_color_button),name='buttoncolorbutton')],
                [(QLabel('显示原文'),3),self.getsimpleswitch(globalconfig,'isshowrawtext',callback=lambda x: __changeuibuttonstate(self,x),name='show_original_switch'),'',(QLabel('显示假名'),3),self.getsimpleswitch(globalconfig,'isshowhira',enable=globalconfig['isshowrawtext'],name='show_hira_switch'),'',(QLabel('显示分词结果'),3 ),self.getsimpleswitch(globalconfig,'show_fenci',enable=globalconfig['isshowrawtext'],name='showatmiddleswitch')],
                [(QLabel('字体大小'),2),(self.getspinbox(1,100,globalconfig,'fontsize',double=True,step=0.1,name='fontSize_spinBox'),2),'',(QLabel('字体类型'),2),(self.font_comboBox,2),'',(QLabel('加粗字体'),3),self.getsimpleswitch(globalconfig,'showbold' )],
                [(QLabel('字体样式'),2),(self.getsimplecombobox(['普通字体','空心字体','描边字体','阴影字体'],globalconfig,'zitiyangshi'),2),'',(QLabel('特殊字体样式填充颜色'),3),self.getcolorbutton(globalconfig,'miaobiancolor',callback=lambda: self.ChangeTranslateColor("miaobiancolor", self.back_color_button),name='miaobian_color_button'),'',(QLabel('居中显示'),3),self.getsimpleswitch(globalconfig,'showatcenter')],
                [(QLabel('空心线宽'),2),(self.getspinbox(1,100,globalconfig,'miaobianwidth',double=True,step=0.1),2),'',(QLabel('描边宽度'),2 ),(self.getspinbox(1,100,globalconfig,'miaobianwidth2',double=True,step=0.1),2),'',(QLabel('阴影强度'),2),(self.getspinbox(1,10,globalconfig,'shadowforce'),2)],
                [''],
                [(QLabel('固定窗口尺寸'),3),self.getsimpleswitch(globalconfig,'fixedheight'),'',(QLabel('可选取模式'),3),self.getsimpleswitch(globalconfig,'selectable',callback=__changeselectmode)],
                [(QLabel('翻译结果繁简体显示'),3),(self.getsimplecombobox(['大陆简体','马新简体','台灣正體','香港繁體','简体','繁體'],globalconfig,'fanjian'),3),'',(QLabel('翻译窗口顺时针旋转(重启生效)'),3),self.getsimplecombobox(['0','90','180','270'],globalconfig,'rotation')],
                [''],
                [(QLabel('显示调整游戏窗口按钮'),3),self.getsimpleswitch(globalconfig,'useresizebutton' ,callback=_useresizebutton),'',(QLabel('显示全屏游戏窗口按钮'),3),self.getsimpleswitch(globalconfig,'usefullscreenbutton' ,callback=_usefullscreenbutton),'',(QLabel('使用Magpie全屏'),3),self.getsimpleswitch(globalconfig,'usemagpie' )],
                [(QLabel('Magpie算法'),3),(self.getsimplecombobox(['Lanczos','FSR','FSRCNNX','ACNet','Anime4K','CRT-Geom','Integer Scale 2x','Integer Scale 3x'],globalconfig,'magpiescalemethod'),3),'',(QLabel('Magpie捕获模式'),3),(self.getsimplecombobox(['Graphics Capture','Desktop Duplication','GDI','DwmSharedSurface'],globalconfig,'magpiecapturemethod'),3)],
                [''],
                [''],
                ['']
        ]
        automakegrid(self.xianshishezhilayout,buttongrid)
                    

        self.fontbigsmallsignal.connect(functools.partial(fontbigsmallfunction,self))
  
         
def changeHorizontal(self) :

        globalconfig['transparent'] = self.horizontal_slider.value() 
        self.horizontal_slider_label.setText("{}%".format(globalconfig['transparent']))
        #  
        self.object.translation_ui.translate_text.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                              \
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
        self.object.translation_ui._TitleLabel.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                                 font-weight: bold;\
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
        
        if self.object.translation_ui.mousetransparent:
                self.object.translation_ui.mousetransbutton.click()
        # # 重置状态栏界面
        # self.object.translation_ui.statusbar.setStyleSheet("font: 10pt %s;"
        #                            #  "color: %s;"
        #                               #"background-color: rgba(%s, %s, %s, 0.1)"
        #                               "background-color: rgba(62,62,62, 0.1)"
        #                            #   %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['fonttype']))
        #                               #,self.icon_color))
        #                              % (globalconfig['fonttype'] ))
 