import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import     QTableView, QAbstractItemView, QLabel, QVBoxLayout 
from PyQt5.QtWidgets import  QDialog,QVBoxLayout ,QHeaderView 
from PyQt5.QtCore import Qt,QSize  

from PyQt5.QtGui import QStandardItem, QStandardItemModel   
from PyQt5.QtWidgets import  QLabel ,QSlider, QFontComboBox  ,QDialog,QGridLayout
from gui.inputdialog import multicolorset
from myutils.config import globalconfig ,_TR,_TRL  ,magpie10_config
from myutils.wrapper import Singleton
import qtawesome,gobject,json
from myutils.hwnd import showintab
from gui.inputdialog import getsomepath1
from gui.usefulwidget import getsimplecombobox,getspinbox,getcolorbutton,getsimpleswitch,selectcolor
def __changeuibuttonstate(self,x):  
    gobject.baseobject.translation_ui.refreshtoolicon()
    self.show_hira_switch .setEnabled(x)
    self.show_fenciswitch .setEnabled(x) 
def setTabThree_direct(self):
    self.fontSize_spinBox=getspinbox(1,100,globalconfig,'fontsize',double=True,step=0.1 )
    self.fontbigsmallsignal.connect(lambda t:self.fontSize_spinBox.setValue(self.fontSize_spinBox.value()+0.5*t))
    self.show_original_switch=getsimpleswitch(globalconfig,'isshowrawtext',callback=lambda x: __changeuibuttonstate(self,x))
    self.show_hira_switch=getsimpleswitch(globalconfig,'isshowhira',enable=globalconfig['isshowrawtext'])
    self.show_fenciswitch=getsimpleswitch(globalconfig,'show_fenci',enable=globalconfig['isshowrawtext'])
 
def setTabThree(self) :
       
    self.tabadd_lazy(self.tab_widget, ('显示设置'), lambda :setTabThree_lazy(self))  

@Singleton
class dialog_toolbutton(QDialog): 
    def __init__(self, parent ) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR('窗口按钮设置'))
        model=QStandardItemModel(   )
        model.setHorizontalHeaderLabels(_TRL(['显示','图标','图标2', '说明']))

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
        self.model.insertRow(row,[QStandardItem( ),QStandardItem(),QStandardItem(),QStandardItem( _TR(globalconfig['toolbutton']['buttons'][k]['tip'])+" "+belong ) ])  
        self.table.setIndexWidget(self.model.index(row, 0),getsimpleswitch(globalconfig['toolbutton']['buttons'][k],'use',callback=lambda _:gobject.baseobject.translation_ui.showhidetoolbuttons()))


        self.table.setIndexWidget(self.model.index(row, 1),getcolorbutton('','',lambda:dialog_selecticon(self,globalconfig['toolbutton']['buttons'][k],'icon'),qicon=qtawesome.icon(globalconfig['toolbutton']['buttons'][k]['icon'] ,color=globalconfig['buttoncolor'] )  ))
        if 'icon2' in globalconfig['toolbutton']['buttons'][k]:
            self.table.setIndexWidget(self.model.index(row,2),getcolorbutton('','',lambda:dialog_selecticon(self,globalconfig['toolbutton']['buttons'][k],'icon2'),qicon=qtawesome.icon(globalconfig['toolbutton']['buttons'][k]['icon2'] ,color=globalconfig['buttoncolor'] )  ))

@Singleton
class dialog_selecticon(QDialog): 
    def __init__(self, parent ,dict,key) -> None:
    
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.dict=dict
        self.key=key
        self.setWindowTitle(_TR('选择图标')) 
        with open('./files/fonts/fontawesome4.7-webfont-charmap.json','r',encoding='utf8') as ff:
            js=json.load(ff)
        

        layout=QGridLayout()
        self.setLayout(layout)
        for i,name in enumerate(js):
            layout.addWidget(getcolorbutton('','',functools.partial(self.selectcallback,'fa.'+name),qicon=qtawesome.icon('fa.'+name,color=globalconfig['buttoncolor'] )  ),i//30,i%30)
        self.show()
    def selectcallback(self,_):
        self.dict[self.key]=_
        self.close()
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
    self.font_comboBox.setCurrentFont(QFont(globalconfig['fonttype']))  
    self.font_comboBox2 = QFontComboBox( ) 
    self.font_comboBox2.activated[str].connect(lambda x:globalconfig.__setitem__('fonttype2',x))  
    self.font_comboBox2.setCurrentFont(QFont(globalconfig['fonttype2']))  

    self.sfont_comboBox = QFontComboBox( ) 
    def callback(x):
        globalconfig.__setitem__('settingfonttype',x)
        self.setstylesheet()
    self.sfont_comboBox.activated[str].connect(callback)  
    self.sfont_comboBox.setCurrentFont(QFont(globalconfig['settingfonttype'])) 
      
    
    textgrid=[
        [('原文字体',3),(self.font_comboBox,5),'',('译文字体',3),(self.font_comboBox2,5)],
        [('字体大小',3),(self.fontSize_spinBox,2),'',('额外的行间距',3),(getspinbox(0,100,globalconfig,'extra_space'),2)],
        [('居中显示',4),getsimpleswitch(globalconfig,'showatcenter'),'',('加粗字体',4),getsimpleswitch(globalconfig,'showbold' )],
         [ '',],
         [('字体样式',3),(getsimplecombobox(_TRL(['普通字体','空心字体','描边字体','阴影字体','描边字体_reverse']),globalconfig,'zitiyangshi'),5)],
        [('特殊字体样式填充颜色',4),getcolorbutton(globalconfig,'miaobiancolor',transparent=False,callback=lambda: selectcolor(self,globalconfig, "miaobiancolor", self.miaobian_color_button), name='miaobian_color_button',parent=self)],
        [('空心线宽',3),(getspinbox(0.1,100,globalconfig,'miaobianwidth',double=True,step=0.1),2),'',('描边宽度',3 ),(getspinbox(0.1,100,globalconfig,'miaobianwidth2',double=True,step=0.1),2),'',('阴影强度',3),(getspinbox(1,20,globalconfig,'shadowforce'),2)],
        [''],
        
        [('显示原文',4),self.show_original_switch,'',('原文颜色',4), getcolorbutton(globalconfig,'rawtextcolor',callback=lambda: selectcolor(self,globalconfig, "rawtextcolor", self.original_color_button),name='original_color_button',parent=self)],
        [('显示假名',4),self.show_hira_switch,'',('假名颜色',4),getcolorbutton(globalconfig,'jiamingcolor',callback=lambda: selectcolor(self,globalconfig, "jiamingcolor", self.jiamingcolor_b),name='jiamingcolor_b',parent=self),'',('假名字体缩放',3),(getspinbox(0.05,1,globalconfig,'kanarate',double=True,step=0.05,dec=2),2)],  
        [('语法加亮',4 ),self.show_fenciswitch,'',
         ('词性颜色(需要Mecab)',4), getcolorbutton(globalconfig,'',callback=lambda  : multicolorset(self),icon='fa.gear',constcolor="#FF69B4") ,],
        [("显示翻译器名称",4),(getsimpleswitch(globalconfig  ,'showfanyisource'),1)],
        [''],
        [('收到翻译结果时才刷新',4),getsimpleswitch(globalconfig,'refresh_on_get_trans')],
        [''],
        [('可选取模式(阴影字体下无效)',6),getsimpleswitch(globalconfig,'selectable',callback=lambda x:gobject.baseobject.translation_ui.translate_text.setselectable() )],
    ]
    def __changefontsize(x):
        self.setstylesheet()
        self.resizefunction()
    def __changeshowintab(x):
        gobject.baseobject.translation_ui.showintab=x
        showintab(gobject.baseobject.translation_ui.winId(),x)
    uigrid=[
        [('设置界面字体',4),(self.sfont_comboBox,5)],
           [ ('字体大小',4),(getspinbox(1,100,globalconfig  ,'settingfontsize',callback=__changefontsize),2)], 
           [ ('不透明度',4),(self.horizontal_slider,8),(self.horizontal_slider_label,2)], 
           [('翻译窗口背景颜色',4),getcolorbutton(globalconfig,'backcolor',callback=lambda: selectcolor(self,globalconfig, "backcolor", self.back_color_button,callback=gobject.baseobject.translation_ui.set_color_transparency),name='back_color_button',parent=self),'',('工具按钮颜色',4),getcolorbutton(globalconfig,'buttoncolor',callback=lambda:selectcolor(self,globalconfig,'buttoncolor',self.buttoncolorbutton,callback=lambda:gobject.baseobject.translation_ui.refreshtooliconsignal.emit()) ,name='buttoncolorbutton',parent=self),'',('工具按钮大小',4),(getspinbox(5,100,globalconfig  ,'buttonsize',callback=lambda _:gobject.baseobject.translation_ui.refreshtooliconsignal.emit()),2)],
           [''],
           [('窗口按钮设置',6),getcolorbutton(globalconfig,'',callback=lambda x: dialog_toolbutton(self),icon='fa.gear',constcolor="#FF69B4")],
           [''],
        [('游戏最小化时窗口隐藏',6),(getsimpleswitch(globalconfig,'minifollow'),1)], 
        [('游戏失去焦点时窗口隐藏',6),(getsimpleswitch(globalconfig,'focusfollow'),1)], 
        [('游戏失去焦点时取消置顶',6),(getsimpleswitch(globalconfig,'focusnotop'),1)], 
        [('游戏窗口移动时同步移动',6),(getsimpleswitch(globalconfig,'movefollow'),1)],
        [('固定窗口尺寸',6),getsimpleswitch(globalconfig,'fixedheight'),],
        [("自动隐藏窗口",6),(getsimpleswitch(globalconfig  ,'autodisappear'),1),'',("隐藏延迟(s)",3),(getspinbox(1,100,globalconfig  ,'disappear_delay'),2)],
        
        [('任务栏中显示',6),getsimpleswitch(globalconfig,'showintab' ,callback=__changeshowintab)],
        [('子窗口任务栏中显示',6),getsimpleswitch(globalconfig,'showintab_sub')],
           
    ]  
    alleffect=['无','Bicubic','Bilinear','Jinc','Lanczos','Nearest','SSimDownscaler']
    downsname=magpie10_config.get('downscalingEffect',{'name':'无'}).get('name')
    if downsname not in alleffect:
        alleffect.append(downsname)
    idx=alleffect.index(downsname)
    downscalecombo=getsimplecombobox(alleffect,{1:idx},1)
    def _downschange(idx):
        if idx==0:
            magpie10_config.pop('downscalingEffect')
        else:
            magpie10_config['downscalingEffect']={'name':alleffect[idx]}
    downscalecombo.currentIndexChanged.connect(_downschange)
    fullscreengrid=[
        [('全屏化方式',4),(getsimplecombobox(_TRL(['内置Magpie10','自行下载的Magpie10','游戏原生全屏', 'SW_SHOWMAXIMIZED']),globalconfig,'fullscreenmethod_2'),6)],
        [''],
        [('自行下载的Magpie10路径',4),(getcolorbutton(globalconfig,'',callback=lambda x: getsomepath1(self,'Magpie路径',globalconfig,'magpie10path','Magpie路径',isdir=True),icon='fa.gear',constcolor="#FF69B4"),1)],
        [''],
 
        [("内置Magpie10设置",4) ],
        [("通用",4)],
        [('',1),('默认降采样效果',4),(downscalecombo,6)],
        [("常规",4)],
        [('',1),('缩放模式',4),(getsimplecombobox([_['name'] for _ in magpie10_config['scalingModes'] ],magpie10_config['profiles'][globalconfig['profiles_index']],'scalingMode'),6)],
        [('',1),('捕获模式',4),(getsimplecombobox(['Graphics Capture','Desktop Duplication','GDI','DwmSharedSurface'],magpie10_config['profiles'][globalconfig['profiles_index']],'captureMethod'),6)],
        [('',1),('3D游戏模式',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'3DGameMode'))],
        [("性能",4)],
        [('',1),('显示帧率',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'showFPS'))],
        [('',1),('垂直同步',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'VSync'))],
        [('',1),('垂直同步_允许额外的延迟以提高性能',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'tripleBuffering'))],
        [("源窗口",4)],
        [('',1),('缩放时禁用窗口大小调整',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'disableWindowResizing'))],
        [('',1),('捕获标题栏',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'captureTitleBar'))],
        [('',1),('自定义剪裁',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'croppingEnabled'))],
        [("光标",4)],
        [('',1),('绘制光标',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'drawCursor'))],
        [('',1),('绘制光标_缩放系数',4),(getsimplecombobox(['0.5x','0.75x','无缩放','1.25x','1.5x','2x','和源窗口相同'],magpie10_config['profiles'][globalconfig['profiles_index']],'cursorScaling'),6)],
        [('',1),('绘制光标_插值算法',4),(getsimplecombobox(['最邻近','双线性'],magpie10_config['profiles'][globalconfig['profiles_index']],'cursorInterpolationMode'),6)],
        [('',1),('缩放时调整光标速度',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'adjustCursorSpeed'))],
        [("高级",4)],
        [('',1),('禁用DirectFlip',4),(getsimpleswitch(magpie10_config['profiles'][globalconfig['profiles_index']],'disableDirectFlip'))],
        [('',1),('允许缩放最大化或全屏的窗口',4),(getsimpleswitch(magpie10_config,'allowScalingMaximized'))],
        [('',1),('缩放时模拟独占全屏',4),(getsimpleswitch(magpie10_config,'simulateExclusiveFullscreen'))],
        [''],
        
          

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
    gobject.baseobject.translation_ui.set_color_transparency()
     