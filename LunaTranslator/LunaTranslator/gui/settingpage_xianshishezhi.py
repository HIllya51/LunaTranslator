import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import    QHBoxLayout, QTableView, QAbstractItemView, QLabel, QVBoxLayout
import win32utils 
from PyQt5.QtWidgets import  QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QLineEdit
from PyQt5.QtCore import Qt,QSize  

from PyQt5.QtGui import QStandardItem, QStandardItemModel   
from PyQt5.QtWidgets import  QWidget,QLabel ,QSlider, QFontComboBox  ,QPushButton,QDialog
import json,os,hashlib
from traceback import print_exc
from gui.inputdialog import multicolorset
from utils.config import globalconfig ,_TR,_TRL  
from utils.wrapper import Singleton
import qtawesome
from utils.hwnd import ListProcess,showintab
from gui.inputdialog import autoinitdialog,getsomepath1
from gui.usefulwidget import getQMessageBox
def __changeuibuttonstate(self,x):  
    self.object.translation_ui.refreshtoolicon()
    self.show_hira_switch .setEnabled(x)
    self.show_fenciswitch .setEnabled(x) 
def setTabThree_direct(self):
    self.fontSize_spinBox=self.getspinbox(1,100,globalconfig,'fontsize',double=True,step=0.1 )
    self.fontbigsmallsignal.connect(lambda t:self.fontSize_spinBox.setValue(self.fontSize_spinBox.value()+0.5*t))
    self.show_original_switch=self.getsimpleswitch(globalconfig,'isshowrawtext',callback=lambda x: __changeuibuttonstate(self,x))
    self.show_hira_switch=self.getsimpleswitch(globalconfig,'isshowhira',enable=globalconfig['isshowrawtext'])
    self.show_fenciswitch=self.getsimpleswitch(globalconfig,'show_fenci',enable=globalconfig['isshowrawtext'])
 
def setTabThree(self) :
       
    self.tabadd_lazy(self.tab_widget, ('显示设置'), lambda :setTabThree_lazy(self))  

@Singleton
class dialog_toolbutton(QDialog): 
    def __init__(self, object ) -> None:
        super().__init__(object, Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR('窗口按钮设置'))
        self.object=object
        model=QStandardItemModel(   )
        model.setHorizontalHeaderLabels(_TRL(['显示','图标', '说明']))

        layout = QVBoxLayout(self)  # 
        self.model=model
        
        table = QTableView()
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
        table.setWordWrap(False) 
        table.setModel(model) 
        self.table=table 
        for row,k in enumerate(globalconfig['toolbutton']['rank']):
            self.newline(row,k)
        layout.addWidget(table)
        
        self.resize(QSize(800,400))
        self.show() 
    
    def newline(self,row,k): 
        if 'belong' in globalconfig['toolbutton']['buttons'][k]:
            belong="("+_TR("仅")+' '.join(globalconfig['toolbutton']['buttons'][k]['belong'])+")"
        else:belong=""
        self.model.insertRow(row,[QStandardItem( ),QStandardItem(),QStandardItem( _TR(globalconfig['toolbutton']['buttons'][k]['tip'])+" "+belong ) ])  
        self.table.setIndexWidget(self.model.index(row, 0),self.object.getsimpleswitch(globalconfig['toolbutton']['buttons'][k],'use',callback=lambda _:self.object.object.translation_ui.showhidetoolbuttons()))
        self.table.setIndexWidget(self.model.index(row, 1),self.object.getcolorbutton('','',lambda:1,qicon=qtawesome.icon(globalconfig['toolbutton']['buttons'][k]['icon'] ,color=globalconfig['buttoncolor'] ) ))
def setTabThree_lazy(self) :
      

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
        self.setstylesheet()
    self.sfont_comboBox.activated[str].connect(callback)  
    self.scomboBox_font = QFont(globalconfig['settingfonttype'])
    self.sfont_comboBox.setCurrentFont(self.scomboBox_font) 
      
    def _settoolbariconcolor( ):
        self.ChangeTranslateColor("buttoncolor", self.buttoncolorbutton)
        self.object.translation_ui.refreshtooliconsignal.emit()
     
    try:
        with open(os.path.join('./files/plugins/Magpie_v0.9.1','ScaleModels.json'),'r') as ff:
            _magpiemethod=json.load(ff)
            magpiemethod=[_['name'] for _ in _magpiemethod]

    except:
        magpiemethod=[]#['Lanczos','FSR','FSRCNNX','ACNet','Anime4K','CRT-Geom','Integer Scale 2x','Integer Scale 3x']
     
    magpiesettingdialog=[
        {'t':'switch','d':globalconfig['magpieflags'],'k':'Is3DMode','l':'3D游戏模式'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'DisableWindowResizing','l':'缩放时禁用窗口大小调整'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'CropTitleBarOfUWP','l':'剪裁UWP窗口的标题栏'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'VSync','l':'垂直同步'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'DisableLowLatency','l':'允许额外的延迟以提高性能'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'ShowFPS','l':'显示帧率'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'NoCursor','l':'不绘制光标'},
        {'t':'switch','d':globalconfig['magpieflags'],'k':'AdjustCursorSpeed','l':'缩放时调整光标速度'},
        {'t':'combo','d':globalconfig['magpieflags'],'k':'CursorZoomFactor','l':'光标缩放系数','list':['0.5x','0.75x','1x','1.25x','1.5x','2x','2.5x','3x','和源窗口相同'],'map':[0.5,0.75,1,1.25,1.5,2,2.5,3,0]},
        {'t':'combo','d':globalconfig['magpieflags'],'k':'CursorInterpolationMode','l':'插值算法','list':['最邻近','双线性']},
    ]
 
    
    
    textgrid=[
        [('文本字体',3),(self.font_comboBox,5)],
        [('字体大小',3),(self.fontSize_spinBox,2),'',('居中显示',4),self.getsimpleswitch(globalconfig,'showatcenter'),'',('加粗字体',4),self.getsimpleswitch(globalconfig,'showbold' )],
         [ '',],
         [('字体样式',3),(self.getsimplecombobox(_TRL(['普通字体','空心字体','描边字体','阴影字体']),globalconfig,'zitiyangshi'),5)],
        [('特殊字体样式填充颜色',4),self.getcolorbutton(globalconfig,'miaobiancolor',transparent=False,callback=lambda: self.ChangeTranslateColor("miaobiancolor", self.miaobian_color_button),name='miaobian_color_button')],
        [('空心线宽',3),(self.getspinbox(0.1,100,globalconfig,'miaobianwidth',double=True,step=0.1),2),'',('描边宽度',3 ),(self.getspinbox(0.1,100,globalconfig,'miaobianwidth2',double=True,step=0.1),2),'',('阴影强度',3),(self.getspinbox(1,20,globalconfig,'shadowforce'),2)],
        [''],
        
        [('显示原文',4),self.show_original_switch,'',('原文颜色',4), self.getcolorbutton(globalconfig,'rawtextcolor',callback=lambda: self.ChangeTranslateColor("rawtextcolor", self.original_color_button),name='original_color_button')],
        [('显示假名',4),self.show_hira_switch,'',('假名颜色',4),self.getcolorbutton(globalconfig,'jiamingcolor',callback=lambda: self.ChangeTranslateColor("jiamingcolor", self.jiamingcolor_b),name='jiamingcolor_b'),'',('假名字体缩放',3),(self.getspinbox(0.05,1,globalconfig,'kanarate',double=True,step=0.05,dec=2),2)],  
        [('语法加亮',4 ),self.show_fenciswitch,'',
         ('词性颜色(需要Mecab)',4), self.getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4") ,],
        [("显示翻译器名称",4),(self.getsimpleswitch(globalconfig  ,'showfanyisource'),1)],
        [''],
        [('收到翻译结果时才刷新',4),self.getsimpleswitch(globalconfig,'refresh_on_get_trans')],
        [''],
        [('可选取模式(阴影字体下无效)',6),self.getsimpleswitch(globalconfig,'selectable',callback=lambda x:self.object.translation_ui.translate_text.setselectable() )],
    ]
    def __changefontsize(x):
        self.setstylesheet()
        self.resizefunction()
    def __changeshowintab(x):
        self.object.translation_ui.showintab=x
        showintab(self.object.translation_ui.winId(),x)
    uigrid=[
        [('设置界面字体',4),(self.sfont_comboBox,5)],
           [ ('字体大小',4),(self.getspinbox(1,100,globalconfig  ,'settingfontsize',callback=__changefontsize),2)], 
           [ ('不透明度',4),(self.horizontal_slider,8),(self.horizontal_slider_label,2)], 
           [('翻译窗口背景颜色',4),self.getcolorbutton(globalconfig,'backcolor',callback=lambda: self.ChangeTranslateColor("backcolor", self.back_color_button),name='back_color_button'),'',('工具按钮颜色',4),self.getcolorbutton(globalconfig,'buttoncolor',callback=_settoolbariconcolor ,name='buttoncolorbutton'),'',('工具按钮大小',4),(self.getspinbox(5,100,globalconfig  ,'buttonsize',callback=lambda _:self.object.translation_ui.refreshtooliconsignal.emit()),2)],
           [''],
           [('窗口按钮设置',6),self.getcolorbutton(globalconfig,'',callback=lambda x: dialog_toolbutton(self),icon='fa.gear',constcolor="#FF69B4")],
           [''],
        [('游戏最小化时窗口隐藏',6),(self.getsimpleswitch(globalconfig,'minifollow'),1)], 
        [('游戏失去焦点时窗口隐藏',6),(self.getsimpleswitch(globalconfig,'focusfollow'),1)], 
        [('游戏窗口移动时同步移动',6),(self.getsimpleswitch(globalconfig,'movefollow'),1)],
        [('固定窗口尺寸',6),self.getsimpleswitch(globalconfig,'fixedheight'),],
        [("自动隐藏窗口",6),(self.getsimpleswitch(globalconfig  ,'autodisappear'),1),'',("隐藏延迟(s)",3),(self.getspinbox(1,100,globalconfig  ,'disappear_delay'),2)],
        
        [('任务栏中显示',6),self.getsimpleswitch(globalconfig,'showintab' ,callback=__changeshowintab),],
           
    ]  
     
    fullscreengrid=[
        [('全屏化方式',4),(self.getsimplecombobox(_TRL(['内置Magpie9','Magpie10','游戏原生全屏', 'SW_SHOWMAXIMIZED']),globalconfig,'fullscreenmethod_2'),6)],
        [''],
        [("Magpie9设置",4),(self.getcolorbutton(globalconfig,'',callback=lambda x: autoinitdialog(self,'Magpie设置',500,magpiesettingdialog),icon='fa.gear',constcolor="#FF69B4"),1)],
        [('Magpie算法',4),(self.getsimplecombobox(magpiemethod,globalconfig,'magpiescalemethod'),6)],
        [('Magpie捕获模式',4),(self.getsimplecombobox(['Graphics Capture','Desktop Duplication','GDI','DwmSharedSurface'],globalconfig,'magpiecapturemethod'),6)],
        [''],
        [('Magpie10路径',4),(self.getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'Magpie路径',globalconfig,'magpie10path','Magpie路径',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1)],
          

    ] 
    tab=self.makesubtab_lazy(['文本设置', '界面设置','游戏全屏'],[
        lambda:self.makescroll(self.makegrid(textgrid )   ),
        lambda:self.makescroll(self.makegrid(uigrid )   ),
        lambda:self.makescroll(self.makegrid(fullscreengrid )   )

        ]) 
 
    
    return tab
     
def changeHorizontal(self) :

    globalconfig['transparent'] = self.horizontal_slider.value() 
    self.horizontal_slider_label.setText("{}%".format(globalconfig['transparent']))
    #  
    self.object.translation_ui.set_color_transparency()
     