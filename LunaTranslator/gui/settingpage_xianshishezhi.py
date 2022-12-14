import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel ,QSlider, QFontComboBox  ,QGridLayout,QLineEdit,QPushButton
import json,os
 
from gui.inputdialog import multicolorset
from utils.config import globalconfig ,_TR,_TRL

from gui.inputdialog import autoinitdialog,getsomepath1
def fontbigsmallfunction(self,t):
        self.fontSize_spinBox.setValue(self.fontSize_spinBox.value()+0.1*t)
 
def __changeuibuttonstate(self,x): 
                globalconfig.__setitem__('isshowrawtext',x)
                self.object.translation_ui.refreshtoolicon()
                self.show_hira_switch .setEnabled(x)
                self.showatmiddleswitch .setEnabled(x) 

def setTabThree(self) :
      

        self.horizontal_slider = QSlider(  ) 
        self.horizontal_slider.setMaximum(100)
        self.horizontal_slider.setMinimum(1)
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.horizontal_slider.setValue(0)
        self.horizontal_slider.setValue(globalconfig['transparent'])
        self.horizontal_slider.valueChanged.connect(functools.partial(changeHorizontal,self))  
        self.horizontal_slider_label =  QLabel() 
        self.horizontal_slider_label.setText("{}%".format(globalconfig['transparent'])) 
        self.font_comboBox = QFontComboBox( ) 
        self.font_comboBox.activated[str].connect(lambda x:globalconfig.__setitem__('fonttype',x))  
        self.comboBox_font = QFont(globalconfig['fonttype'])
        self.font_comboBox.setCurrentFont(self.comboBox_font)  
        self.sfont_comboBox = QFontComboBox( ) 
        def callback(x):
                globalconfig.__setitem__('settingfonttype',x)
                self.setStyleSheet("font: %spt '"%(11 if globalconfig['languageuse'] in [0,1] else 10)+globalconfig['settingfonttype']+"' ; color: \"#595959\"" )  
        self.sfont_comboBox.activated[str].connect(callback)  
        self.scomboBox_font = QFont(globalconfig['settingfonttype'])
        self.sfont_comboBox.setCurrentFont(self.scomboBox_font) 
        def __changeselectmode_():
                self.object.translation_ui.masklabel.setHidden(globalconfig['selectable'])
                self.object.translation_ui.translate_text.toplabel2.setHidden(globalconfig['selectable'] and globalconfig['zitiyangshi']!=3) 
                self.object.translation_ui.translate_text.toplabel.setHidden(globalconfig['selectable'] and globalconfig['zitiyangshi']!=3)
        def __changeselectmode(x):
                globalconfig.__setitem__('selectable',x) 
                __changeselectmode_()
        __changeselectmode_()
        def _settoolbariconcolor( ):
                self.ChangeTranslateColor("buttoncolor", self.buttoncolorbutton)
                self.object.translation_ui.refreshtooliconsignal.emit()
        def _usexxxbutton(name,x):
                globalconfig['buttonuse'].__setitem__(name,x)
                self.object.translation_ui.showhidetoolbuttons() 
        try:
                with open(os.path.join(globalconfig['magpiepath'],'ScaleModels.json'),'r') as ff:
                        _magpiemethod=json.load(ff)
                        magpiemethod=[_['name'] for _ in _magpiemethod]

        except:
                magpiemethod=[]#['Lanczos','FSR','FSRCNNX','ACNet','Anime4K','CRT-Geom','Integer Scale 2x','Integer Scale 3x']
         
        magpiesettingdialog=[
                {'t':'switch','d':globalconfig['magpieflags'],'k':'Is3DMode','l':'3D????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'DisableWindowResizing','l':'?????????????????????????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'CropTitleBarOfUWP','l':'??????UWP??????????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'VSync','l':'????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'DisableLowLatency','l':'????????????????????????????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'ShowFPS','l':'????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'NoCursor','l':'???????????????'},
                {'t':'switch','d':globalconfig['magpieflags'],'k':'AdjustCursorSpeed','l':'???????????????????????????'},
                {'t':'combo','d':globalconfig['magpieflags'],'k':'CursorZoomFactor','l':'??????????????????','list':['0.5x','0.75x','1x','1.25x','1.5x','2x','2.5x','3x','??????????????????'],'map':[0.5,0.75,1,1.25,1.5,2,2.5,3,0]},
                {'t':'combo','d':globalconfig['magpieflags'],'k':'CursorInterpolationMode','l':'????????????','list':['?????????','?????????']},
        ]
 
        buttongrid=[
                [('????????????',2),(self.horizontal_slider,8),(self.horizontal_slider_label,2)],
                [('????????????',4), self.getcolorbutton(globalconfig,'rawtextcolor',callback=lambda: self.ChangeTranslateColor("rawtextcolor", self.original_color_button),name='original_color_button'),'',('????????????????????????',4),self.getcolorbutton(globalconfig,'backcolor',callback=lambda: self.ChangeTranslateColor("backcolor", self.back_color_button),name='back_color_button'),'',('??????????????????',4),self.getcolorbutton(globalconfig,'buttoncolor',callback=_settoolbariconcolor ,name='buttoncolorbutton')],
                [('????????????',4),self.getsimpleswitch(globalconfig,'isshowrawtext',callback=lambda x: __changeuibuttonstate(self,x),name='show_original_switch')],
                 
                [('?????????????????????',3),(self.font_comboBox,5),'',('????????????????????????',3),(self.sfont_comboBox,5)],
                [('????????????',3),(self.getspinbox(1,100,globalconfig,'fontsize',double=True,step=0.1,name='fontSize_spinBox'),2),'',('????????????',4),self.getsimpleswitch(globalconfig,'showatcenter'),'',('????????????',4),self.getsimpleswitch(globalconfig,'showbold' )],
                [''],
                [('????????????',3),(self.getsimplecombobox(_TRL(['????????????','????????????','????????????','????????????']),globalconfig,'zitiyangshi'),2),'',('??????????????????????????????',4),self.getcolorbutton(globalconfig,'miaobiancolor',callback=lambda: self.ChangeTranslateColor("miaobiancolor", self.miaobian_color_button),name='miaobian_color_button')],
                [('????????????',3),(self.getspinbox(1,100,globalconfig,'miaobianwidth',double=True,step=0.1),2),'',('????????????',3 ),(self.getspinbox(1,100,globalconfig,'miaobianwidth2',double=True,step=0.1),2),'',('????????????',3),(self.getspinbox(1,10,globalconfig,'shadowforce'),2)],
                [''],
                [('??????????????????',4 ),self.getsimpleswitch(globalconfig,'show_fenci',enable=globalconfig['isshowrawtext'],name='showatmiddleswitch'),'',
                 ('????????????(??????Mecab)',4), self.getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4") ,],
                [('????????????',4),self.getsimpleswitch(globalconfig,'isshowhira',enable=globalconfig['isshowrawtext'],name='show_hira_switch'),'',('????????????',4),self.getcolorbutton(globalconfig,'jiamingcolor',callback=lambda: self.ChangeTranslateColor("jiamingcolor", self.jiamingcolor_b),name='jiamingcolor_b'),'',('??????????????????',3),(self.getspinbox(0.05,1,globalconfig,'kanarate',double=True,step=0.05,dec=2),2)],
                [''],
                [("??????????????????",4),(self.getsimpleswitch(globalconfig  ,'autodisappear'),1),'',("????????????(s)",3),(self.getspinbox(1,100,globalconfig  ,'disappear_delay'),2)],
                [''],
                [("?????????????????????",4),(self.getsimpleswitch(globalconfig  ,'showfanyisource'),1)],
                [''],
                [('????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'showraw' ,callback=functools.partial(_usexxxbutton,'showraw')),'',('????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'copy' ,callback=functools.partial(_usexxxbutton,'copy')),'',('??????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'langdu' ,callback=functools.partial(_usexxxbutton,'langdu'))],
                [       ('??????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'move' ,callback=functools.partial(_usexxxbutton,'move')),'',
                        ('????????????????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'noundict' ,callback=functools.partial(_usexxxbutton,'noundict')),'',
                ],
                [('????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'history' ,callback=functools.partial(_usexxxbutton,'history')),'' ,
                ('??????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'edit' ,callback=functools.partial(_usexxxbutton,'edit')),'' ,
                ('???????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'gamepad' ,callback=functools.partial(_usexxxbutton,'gamepad'))],
                [('??????????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'resize' ,callback=functools.partial(_usexxxbutton,'resize')),'',('??????????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'fullscreen' ,callback=functools.partial(_usexxxbutton,'fullscreen')),'',('????????????????????????',4),self.getsimpleswitch(globalconfig['buttonuse'],'muteprocess' ,callback=functools.partial(_usexxxbutton,'muteprocess'))],
                [''],
                [('???????????????',4),(self.getsimplecombobox(_TRL(['Magpie','??????????????????', 'SW_SHOWMAXIMIZED']),globalconfig,'fullscreenmethod'),6)],
                [''],
                [("Magpie??????",4),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'Magpie??????',globalconfig,'magpiepath','Magpie??????',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1),'',("Magpie??????",4),(self.getcolorbutton(globalconfig,'',callback=lambda x: autoinitdialog(self,'Magpie??????',500,magpiesettingdialog),icon='fa.gear',constcolor="#FF69B4"),1)],
                [('Magpie??????',4),(self.getsimplecombobox(magpiemethod,globalconfig,'magpiescalemethod'),6)],
                [('Magpie????????????',4),(self.getsimplecombobox(['Graphics Capture','Desktop Duplication','GDI','DwmSharedSurface'],globalconfig,'magpiecapturemethod'),6)],
                [''],
                [('??????????????????????????????',4),(self.getsimpleswitch(globalconfig,'minifollow'),1)],
                [('?????????????????????????????????',4),(self.getsimpleswitch(globalconfig,'focusfollow'),1)],
                [('?????????????????????????????????',4),(self.getsimpleswitch(globalconfig,'movefollow'),1)],
                [''],
                
                [('??????????????????',6),self.getsimpleswitch(globalconfig,'fixedheight'),],
                
                [('???????????????(?????????????????????)',6),self.getsimpleswitch(globalconfig,'selectable',callback=__changeselectmode)],
                [('??????????????????(????????????)',6),self.getsimpleswitch(globalconfig,'showintab' ),],
                [('???????????????????????????(????????????)',6),(self.getsimplecombobox(['0','90','180','270'],globalconfig,'rotation'),4)],
                
               [('??????????????????????????????',6),self.getsimpleswitch(globalconfig,'forcekeepontop'),],
        ] 
        self.yitiaolong("????????????",buttongrid) 
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
        