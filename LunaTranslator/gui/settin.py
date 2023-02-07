 
from PyQt5.QtCore import Qt,QSize,pyqtSignal  
from PyQt5.QtWidgets import  QColorDialog,QSpinBox,QDoubleSpinBox,QPushButton,QComboBox,QLabel,QScrollArea,QWidget,QGridLayout,QApplication,QTabBar,QVBoxLayout
from PyQt5.QtGui import QColor  
from utils.config import globalconfig 
from PyQt5.QtWidgets import  QTabWidget 
import qtawesome  
import functools
from gui.switchbutton import MySwitch 
from gui.settingpage1 import setTabOne
from gui.settingpage2 import setTabTwo
from traceback import print_exc
from utils.config import globalconfig ,_TR
from gui.settingpage_xianshishezhi import setTabThree 
from gui.settingpage_tts import setTab5 

from gui.settingpage7 import setTab7
from gui.settingpage_about import setTab_about
from gui.rotatetab import  rotatetab
from gui.settingpage_cishu import setTabcishu
from gui.settingpage_quick import setTab_quick
from gui.setting_lang import setTablang
from utils.wavmp3player import wavmp3player
from gui.closeashidewindow import closeashidewindow

class Settin(closeashidewindow) : 
    loadtextractorfalse=pyqtSignal( ) 
    voicelistsignal=pyqtSignal(list)
    mp3playsignal=pyqtSignal(str,int) 
    versiontextsignal=pyqtSignal( str)
    progresssignal=pyqtSignal(str,int)
    clicksourcesignal=pyqtSignal(str) 
    fontbigsmallsignal=pyqtSignal(int)  
    def automakegrid(self,grid,lis,save=False,savelist=None,ww=0): 
        maxl=0
    
        for nowr,line in enumerate(lis):
                nowc=0
                if save:
                    ll=[]
                for i in line:
                        if type(i)==str:
                                wid,cols=QLabel(""),1
                        elif type(i)!=tuple:
                                wid,cols=i,1
                        elif len(i)==2:
                                
                                wid,cols=i
                                if type(wid)==str  :
                                    wid=QLabel(_TR(wid))
                        grid.addWidget(wid,nowr,nowc,1,cols)
                        if save:
                            ll.append(wid)
                        nowc+=cols   
                maxl=max(maxl,nowc)
                if save:
                    savelist.append(ll)

         
        
        if  globalconfig['languageuse'] in [0,1]:
            for c in range(maxl):

                grid.setColumnMinimumWidth(c,ww//maxl)
    def callbackwrap(self,d,k,call,_):
        d[k]=_
        if call:
            try: 
                call(_)
            except:
                print_exc()
    def getspinbox(self,mini,maxi,d,key,double=False, step=1,callback=None,name=None,dec=1 ):
        if double:
            s=QDoubleSpinBox()
            s.setDecimals(dec)
        else:
            s=QSpinBox() 
        s.setMinimum(mini)
        s.setMaximum(maxi)
        s.setSingleStep(step)
        s.setValue(d[key])
        s.valueChanged.connect(functools.partial(self.callbackwrap,d,key,callback)) 
        if name:
            setattr(self,name,s)
        return s
    def getsimpleswitch(self,d,key,enable=True,callback=None,name=None,pair=None):
        b=MySwitch(self.rate,sign=d[key],enable=enable)
        b.clicked.connect(functools.partial(self.callbackwrap,d,key,callback) )
        
        if pair:
            if pair not in dir(self):
                setattr(self,pair,{})
            getattr(self,pair)[name]=b 
        elif name:
            setattr(self,name,b)
        return b
    def yuitsu_switch(self,configdictkey,dictobjectn,key,callback,checked):  
        dictobject=getattr(self,dictobjectn)  
        if checked :  
            for k in dictobject:
                if k==key:
                    continue
                if  ( configdictkey=='sourcestatus' and globalconfig[configdictkey][k]==True) or (configdictkey!='sourcestatus' and globalconfig[configdictkey][k]['use']==True  ): 
                     
                    dictobject[k].setChecked(False)    
        if configdictkey=='sourcestatus':
            globalconfig[configdictkey][key] =checked
        else:
            globalconfig[configdictkey][key]['use']=checked
        if callback : 
            callback(key,checked)
    def getcolorbutton(self,d,key,callback,name=None,icon="fa.paint-brush",constcolor=None,enable=True,transparent=True):

        b=QPushButton(qtawesome.icon(icon, color=constcolor if constcolor else d[key]), ""  )
        b.setEnabled(enable)
         
        b.setIconSize(QSize(int(20*self.rate),
                                 int(20*self.rate)))
        if transparent:
            b.setStyleSheet("background: transparent;") 
        b.clicked.connect(  callback)  
        if name:
            setattr(self,name,b)
        return b
    def getsimplecombobox(self,lst,d,k,callback=None,name=None):
        s=QComboBox( )  
        s.addItems(lst)
        if d[k]>=len(lst):
            d[k]=0
        s.setCurrentIndex(d[k])
        s.currentIndexChanged.connect(functools.partial(self.callbackwrap,d,k,callback) )
        if name:
            setattr(self,name,s)
        return s
    def __init__(self, object):
        
        super(Settin, self).__init__(object.translation_ui) 
        #self.setWindowFlag(Qt.Tool,False)
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player=wavmp3player() 
        self.localocrstarted=False
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)  
        self.object = object  
        self.needupdate=False
        # 界面缩放比例
        self.rate = self.object.screen_scale_rate
        # 界面尺寸
        self.window_width = int((900 if globalconfig['languageuse'] in [0,1] else 1200)*self.rate)
         
        self.window_height = int(600*self.rate)
         
        self.savelastrect=None
        self.setFixedSize(self.window_width, self.window_height) 
        
        d=QApplication.desktop()

        globalconfig['setting_geo'][0]=min(max(globalconfig['setting_geo'][0],0),d.width()-self.width())
        globalconfig['setting_geo'][1]=min(max(globalconfig['setting_geo'][1],0),d.height()-self.height())
        self.move (*globalconfig['setting_geo'])
        #self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        #self.setWindowFlags( Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR("设置"))
        self.setWindowIcon(qtawesome.icon("fa.gear" )) 
        self.setstylesheet()
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
         
        #self.tab_widget.setGeometry(self.geometry())  
        self.tabbar=rotatetab(self.tab_widget)
         
        
        # tabbar.setStyleSheet("""   
        #         font:18pt '黑体';       
        #        """ )
        
        self.tab_widget.setTabBar(self.tabbar) 
        self.tab_widget.tabBar().setObjectName("basetabbar")
        self.tab_widget.setStyleSheet(
            '''QTabBar#basetabbar:tab { 
                width: %spx;
                height: %spx;
                font:%spt  ;  }
            '''%(50*self.rate,self.window_width*0.2,18 if globalconfig['languageuse'] in [0,1] else 10  )
        )
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.hooks=[] 

        import time
        t1=time.time()
        
        setTabOne(self)  
        setTabTwo(self)  
         
        
        setTabThree(self) 
        setTab5(self)
        setTablang(self)
        setTab7(self)
        setTabcishu(self)
        
        setTab_quick(self) 
        setTab_about(self)
        
        self.usevoice=0
     
    def setstylesheet(self):
        self.setStyleSheet("font: %spt '"%(11 if globalconfig['languageuse'] in [0,1] else 10)+(globalconfig['settingfonttype']  )+"' ;  " )  
    def makegrid(self,grid,save=False,savelist=None,savelay=None ):
        scrollwidth=20*self.rate
        gridlayoutwidget = QWidget( )  
        gridlay=QGridLayout( )     
        gridlayoutwidget.setLayout(gridlay)   
        
        gridlayoutwidget.setFixedWidth( self.window_width*0.8-scrollwidth)
        gridlayoutwidget.setFixedHeight(len(grid)*35*self.rate)
        self.automakegrid(gridlay,grid,save,savelist,gridlayoutwidget.width()) 
        if save:
            savelay.append(gridlay)
        return gridlayoutwidget
    def makescroll(self,widget ):  
        scrollwidth=20*self.rate
        scroll = QScrollArea( )   
        scroll.setHorizontalScrollBarPolicy(1)
        scroll.setStyleSheet('''QScrollArea{background-color:transparent;border:0px}''')  
        scroll.verticalScrollBar().setStyleSheet("QScrollBar{width:%spx;}"%scrollwidth)
        
        scrollwidget=QWidget()
        scrollwidgetlayout=QVBoxLayout()
        scrollwidgetlayout.setContentsMargins(0,0,0,0)
        scrollwidget.setLayout(scrollwidgetlayout) 
        masklabel=QLabel(scrollwidget)
        masklabel.setGeometry(0,0,2000,2000)
        masklabel.setStyleSheet("color:white;background-color:white;")  
        scrollh=0
    
        scrollwidgetlayout.addWidget(widget) 
        scrollh=scrollh+widget.height() 

        scrollwidget.setGeometry(0,0,self.window_width*0.8 , scrollh) 

        scroll.setWidget(scrollwidget) 
        return scroll
    def makesubtab(self,titles,widgets):
        tab=QTabWidget()
        for i,wid in enumerate(widgets): 
            self.tabadd(tab,titles[i],[wid])
        return tab
    def tabadd(self,tab,title,widgets): 
        if len(widgets)==1:
            tab.addTab(widgets[0],_TR(title))
        else:
            basewidget=QWidget()
            basewidget.setObjectName("basewidget")
            basewidget.setStyleSheet(("QWidget#basewidget:{color:white;background-color:white;}")) 
            tab.addTab(basewidget, _TR(title)) 

            baselayout=QVBoxLayout()
            baselayout.setContentsMargins(0,0,0,0)
            basewidget.setLayout(baselayout) 
            for wid in widgets:
                baselayout.addWidget(wid)
    def yitiaolong(self,title,grid ):  
        gridlayoutwidget=self.makegrid(grid )  
        if gridlayoutwidget.height()>self.height(): 
            gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        self.tabadd(self.tab_widget,_TR(title),[gridlayoutwidget]) 
    def closeEvent(self, event) : 
            globalconfig['setting_geo']=(self.geometry().topLeft().x(),self.geometry().topLeft().y())
            super( ).closeEvent(event)  
    def ChangeTranslateColor(self, translate_type,button,item=None,name=None) :
            nottransbutton=globalconfig['fanyi'].keys()
            if translate_type not in nottransbutton:
                color = QColorDialog.getColor(QColor(globalconfig[translate_type]), self )  
            else:
                color = QColorDialog.getColor(QColor(globalconfig['fanyi'][translate_type]['color']), self )
            if not color.isValid() :
                return
            if button is None:
                button=getattr(item,name)
            button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
             
            if translate_type not in nottransbutton: 
                globalconfig[translate_type]=color.name()  
            else:
                globalconfig['fanyi'][translate_type]['color']=color.name() 
            if translate_type=='backcolor': 
                self.object.translation_ui.set_color_transparency()
             
