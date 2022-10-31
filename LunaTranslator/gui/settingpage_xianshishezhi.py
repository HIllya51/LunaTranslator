import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QDoubleSpinBox,QFontComboBox ,QComboBox
import qtawesome 
 
from utils.config import globalconfig 
  
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  

def setTabThree(self) :
     
        self.tab_3 = QWidget()
        self.tab_widget.addTab(self.tab_3, "显示设置") 
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 20, 90, 20)
        label.setText("不透明度:") 
        self.horizontal_slider = QSlider(self.tab_3)
        self.customSetGeometry(self.horizontal_slider, 120, 20, 320, 20)
        self.horizontal_slider.setMaximum(100)
        self.horizontal_slider.setMinimum(1)
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.horizontal_slider.setValue(0)
        self.horizontal_slider.setValue(globalconfig['transparent'])
        self.horizontal_slider.valueChanged.connect(functools.partial(changeHorizontal,self))  
        self.horizontal_slider_label = QLabel(self.tab_3)
        self.customSetGeometry(self.horizontal_slider_label, 450, 20, 30, 20)
        self.horizontal_slider_label.setText("{}%".format(globalconfig['transparent'])) 
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 50, 145, 20)
        label.setText("字体大小:") 
         
        self.fontSize_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.fontSize_spinBox, 95,50, 50, 20)
        self.fontSize_spinBox.setRange(1,100) 
        self.fontSize_spinBox.setValue(globalconfig['fontsize']) 
        self.fontSize_spinBox.setSingleStep(0.1)
        self.fontSize_spinBox.setDecimals(1)
        self.fontSize_spinBox.valueChanged.connect(lambda x:globalconfig.__setitem__('fontsize',x))
        
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 50, 145, 20)
        label.setText("字体类型:")
 
        self.font_comboBox = QFontComboBox(self.tab_3)
        self.customSetGeometry(self.font_comboBox, 350, 50, 185, 20)
        self.font_comboBox.activated[str].connect(lambda x:globalconfig.__setitem__('fonttype',x))  
        self.comboBox_font = QFont(globalconfig['fonttype'])
        self.font_comboBox.setCurrentFont(self.comboBox_font)  
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 110, 60, 20)
        label.setText("字体样式")
        self.font_type_combo=QComboBox(self.tab_3)
        self.font_type_combo.addItems(['普通字体','空心字体','描边字体'])
        self.font_type_combo.setCurrentIndex(globalconfig['zitiyangshi'])
        self.customSetGeometry(self.font_type_combo, 95, 110,100,20)
        self.font_type_combo.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('zitiyangshi',x) )
 
        
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 140, 145, 20)
        label.setText("描边宽度:") 
         
        self.miaobian_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.miaobian_spinBox, 350,140, 50, 20)
        self.miaobian_spinBox.setRange(0,100) 
        self.miaobian_spinBox.setValue(globalconfig['miaobianwidth2']) 
        self.miaobian_spinBox.setSingleStep(0.1)
        self.miaobian_spinBox.setDecimals(1)
        self.miaobian_spinBox.valueChanged.connect(lambda x:globalconfig.__setitem__('miaobianwidth2',x))

        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 140, 145, 20)
        label.setText("空心线宽:") 
         
        self.kongxin_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.kongxin_spinBox, 95,140, 50, 20)
        self.kongxin_spinBox.setRange(0,100) 
        self.kongxin_spinBox.setValue(globalconfig['miaobianwidth']) 
        self.kongxin_spinBox.setSingleStep(0.1)
        self.kongxin_spinBox.setDecimals(1)
        self.kongxin_spinBox.valueChanged.connect(lambda x:globalconfig.__setitem__('miaobianwidth',x))

        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 220, 100, 20)
        label.setText("固定窗口尺寸:")
 
        self.fixedheight_switch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['fixedheight'] )
        self.customSetGeometry(self.fixedheight_switch, 120, 220,20,20)
        self.fixedheight_switch.clicked.connect(lambda x:globalconfig.__setitem__('fixedheight',x)) 
        
        label=QLabel(self.tab_3)
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 250, 150, 20)
        label.setText("翻译结果繁简体显示:") 
        self.fanjiancombo=QComboBox(self.tab_3)
        self.fanjiancombo.addItems(['大陆简体','马新简体','台灣正體','香港繁體','简体','繁體'])
        self.fanjiancombo.setCurrentIndex(globalconfig['fanjian'])
        self.customSetGeometry(self.fanjiancombo, 170, 250,100,20)
        self.fanjiancombo.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('fanjian',x) )

        
        label=QLabel(self.tab_3)
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 280, 230, 20)
        label.setText("翻译窗口顺时针旋转(重启生效)") 
        self.anglecombo=QComboBox(self.tab_3)
        self.anglecombo.addItems(['0','90','180','270'])
        self.anglecombo.setCurrentIndex(globalconfig['rotation'])
        self.customSetGeometry(self.anglecombo, 250, 280,100,20)
        self.anglecombo.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('rotation',x) )

        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 310, 160, 20)
        label.setText("可选取模式")
         
        s =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['selectable'])
        self.customSetGeometry(s ,120, 310, 20,20)
        def __changeselectmode(x):
                globalconfig.__setitem__('selectable',x)
                if x:
                        self.object.translation_ui.masklabel.hide()
                else:
                        self.object.translation_ui.masklabel.show()
        s .clicked.connect(lambda x:__changeselectmode(x))  


        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 80, 60, 20)
        label.setText("显示原文:")
        
        def __changeuibuttonstate(self,x): 
                globalconfig.__setitem__('isshowrawtext',x)
                self.object.translation_ui.showhiderawbutton.setIcon(qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color="white")) 
                self.show_hira_switch .setEnabled(x)
                self.showatmiddleswitch .setEnabled(x) 
        self.show_original_switch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['isshowrawtext'])
        self.customSetGeometry(self.show_original_switch, 95, 80, 20,20)
        self.show_original_switch.clicked.connect(lambda x: __changeuibuttonstate(self,x))  

        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 450, 80, 150, 20)
        label.setText("显示分词结果:")
         
        self.showatmiddleswitch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['show_fenci'])
        self.customSetGeometry(self.showatmiddleswitch, 600, 80, 20,20)
        self.showatmiddleswitch.clicked.connect(lambda x:globalconfig.__setitem__('show_fenci',x))  
         
        self.showatmiddleswitch .setEnabled(globalconfig['isshowrawtext'])
        
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 170, 60, 20)
        label.setText("居中显示:")
         
        s1 =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['showatcenter'])
        self.customSetGeometry(s1, 95, 170, 20,20)
        s1.clicked.connect(lambda x:globalconfig.__setitem__('showatcenter',x))  
        
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 170, 60, 20)
        label.setText("加粗字体")
         
        s1 =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['showbold'])
        self.customSetGeometry(s1, 350, 170, 20,20)
        s1.clicked.connect(lambda x:globalconfig.__setitem__('showbold',x))  
 

        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 80, 60, 20)
        label.setText("显示假名:")
 
        self.show_hira_switch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['isshowhira'])
        self.customSetGeometry(self.show_hira_switch, 350, 80,20,20)
        self.show_hira_switch.clicked.connect(lambda x:globalconfig.__setitem__('isshowhira',x)) 
        self.show_hira_switch .setEnabled(globalconfig['isshowrawtext'])
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 110, 60, 20)
        label.setText("原文颜色:")

        
        self.original_color_button = QPushButton(qtawesome.icon("fa.paint-brush", color=globalconfig['rawtextcolor']), "", self.tab_3)
        self.customSetIconSize(self.original_color_button, 20, 20)
        self.customSetGeometry(self.original_color_button, 350, 110, 20, 20)
        self.original_color_button.setStyleSheet("background: transparent;")
        self.original_color_button.clicked.connect(lambda: self.ChangeTranslateColor("raw", self.original_color_button)) 
        
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 450, 140, 60, 20)
        label.setText("填充颜色:")

        
        self.miaobian_color_button = QPushButton(qtawesome.icon("fa.paint-brush", color=globalconfig['miaobiancolor']), "", self.tab_3)
        self.customSetIconSize(self.miaobian_color_button, 20, 20)
        self.customSetGeometry(self.miaobian_color_button, 600, 140, 20, 20)
        self.miaobian_color_button.setStyleSheet("background: transparent;")
        self.miaobian_color_button.clicked.connect(lambda: self.ChangeTranslateColor("miaobian", self.miaobian_color_button)) 


        label = QLabel(self.tab_3)
        self.customSetGeometry(label,450, 110, 60, 20)
        label.setText("背景颜色:") 
        self.back_color_button = QPushButton(qtawesome.icon("fa.paint-brush", color=globalconfig['backcolor']), "", self.tab_3)
        self.customSetIconSize(self.back_color_button, 20, 20)
        self.customSetGeometry(self.back_color_button, 600, 110, 20, 20)
        self.back_color_button.setStyleSheet("background: transparent;")
        self.back_color_button.clicked.connect(lambda: self.ChangeTranslateColor("back", self.back_color_button)) 
 
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
 