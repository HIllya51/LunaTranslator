 
from PyQt5.QtCore import Qt,QSize,pyqtSignal  
from PyQt5.QtWidgets import  QColorDialog,QSpinBox,QDoubleSpinBox,QPushButton,QComboBox,QLabel,QScrollArea,QWidget,QGridLayout,QApplication,QTabBar,QVBoxLayout
from PyQt5.QtGui import QColor  ,QResizeEvent 
from PyQt5.QtWidgets import  QTabWidget 
import qtawesome  
import functools,time
from traceback import print_exc 
from utils.config import globalconfig ,_TR
from utils.utils import wavmp3player
from utils.config import globalconfig 

from gui.settingpage1 import setTabOne,setTabOne_direct
from gui.settingpage2 import setTabTwo
from gui.settingpage_xianshishezhi import setTabThree ,setTabThree_direct
from gui.settingpage_tts import setTab5 ,setTab5_direct 
from gui.settingpage_cishu import setTabcishu
from gui.settingpage_quick import setTab_quick,setTab_quick_direct
from gui.setting_lang import setTablang
from gui.setting_proxy import setTab_proxy
from gui.settingpage7 import setTab7 ,settab7direct
from gui.settingpage_about import setTab_about,setTab_about_dicrect  
from gui.usefulwidget import MySwitch 
from gui.usefulwidget import  rotatetab
from gui.usefulwidget import closeashidewindow   
class gridwidget(QWidget):
    pass
class Settin(closeashidewindow) : 
    voicelistsignal=pyqtSignal(list)
    mp3playsignal=pyqtSignal(str,int) 
    versiontextsignal=pyqtSignal( str)
    progresssignal=pyqtSignal(str,int) 
    fontbigsmallsignal=pyqtSignal(int)  
    clicksourcesignal=pyqtSignal(str)
    opensolvetextsig=pyqtSignal()
    showandsolvesig=pyqtSignal(str)
    def resizefunction(self):
         
        for w in self.needfitwidgets: 
            w.setFixedWidth(self.size().width()- self.window_width*0.2 -self.scrollwidth)
        for grid,maxl in self.needfitcols:
            for c in range(maxl):
                grid.setColumnMinimumWidth(c,self.size().width()- self.window_width*0.2-self.scrollwidth//maxl)
        
    def resizeEvent(self, a0: QResizeEvent) -> None: 
        
        self.resizefunction() 
        return super().resizeEvent(a0)
    def automakegrid(self,grid,lis,save=False,savelist=None  ): 
        maxl=0
    
        for nowr,line in enumerate(lis):
                nowc=0
                if save:
                    ll=[]
                for i in line:
                        if type(i)==str:
                            cols=1
                            wid=QLabel(_TR(i))
                        elif type(i)!=tuple:
                                wid,cols=i,1
                        elif len(i)==2:
                                
                                wid,cols=i
                                if type(wid)==str  :
                                    wid=QLabel(_TR(wid))
                        elif len(i)==3:
                            wid,cols,arg=i
                            if arg=='link'and  type(wid)==str  :
                                wid=QLabel((wid))
                                wid.setOpenExternalLinks(True)
                        grid.addWidget(wid,nowr,nowc,1,cols)
                        if save:
                            ll.append(wid)
                        nowc+=cols   
                maxl=max(maxl,nowc)
                if save:
                    savelist.append(ll)

                grid.setRowMinimumHeight(nowr,35)
        self.needfitcols.append([grid,maxl])
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
    def getsimpleswitch(self,d,key,enable=True,callback=None,name=None,pair=None,default=None):
        if default:
            if key not in d:
                d[key]=default

        b=MySwitch(sign=d[key],enable=enable)
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
                globalconfig[configdictkey][k]['use']=k==key
                dictobject[k].setChecked(k==key)     
        
        if callback : 
            callback(key,checked)
    def getcolorbutton(self,d,key,callback,name=None,icon="fa.paint-brush",constcolor=None,enable=True,transparent=True,qicon=None):
        if qicon is None:
            qicon=qtawesome.icon(icon, color=constcolor if constcolor else d[key])
        b=QPushButton(qicon, ""  )
        b.setEnabled(enable)
         
        b.setIconSize(QSize(int(25),int(25)))
        if transparent:
            b.setStyleSheet('''background-color: rgba(255, 255, 255, 0);''') 
        b.clicked.connect(  callback)  
        if name:
            setattr(self,name,b)
        return b
    def getsimplecombobox(self,lst,d,k,callback=None,name=None):
        s=QComboBox( )  
        s.addItems(lst)
        if (k not in d) or (d[k]>=len(lst)):d[k]=0
        s.setCurrentIndex(d[k])
        s.currentIndexChanged.connect(functools.partial(self.callbackwrap,d,k,callback) )
        if name:
            setattr(self,name,s)
        return s
    
    def __init__(self, object): 
        super(Settin, self).__init__(object.translation_ui,globalconfig,'setting_geo_2') 
        #self.setWindowFlag(Qt.Tool,False)
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player=wavmp3player() 
        self.localocrstarted=False
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)  
        self.opensolvetextsig.connect(self.opensolvetextfun)
        self.object = object  
        self.needupdate=False
        self.needfitwidgets=[]
        self.needfitcols=[]
        self.setMinimumSize(100,100)
        # 界面缩放比例
        
        self.window_width = int((900 if globalconfig['languageuse']==0 else 1200))
         
        self.window_height = int(500)
        self.scrollwidth=20
        self.savelastrect=None 
           
        
        self.hooks=[] 

         
        self.usevoice=0
        self.isfirstshow=True

        setTabOne_direct(self)
        settab7direct(self)
        setTabThree_direct(self) 
        setTab5_direct(self)
        setTab_quick_direct(self)

        setTab_about_dicrect(self)

        self.setstylesheet()
    def opensolvetextfun(self):
        self.show() 
        self.tab_widget.setCurrentIndex(3)
    def showEvent(self,e):
        if self.isfirstshow:
            self.setWindowTitle(_TR("设置"))
            self.setWindowIcon(qtawesome.icon("fa.gear" )) 
            
            self.tab_widget = QTabWidget(self)
            self.setCentralWidget(self.tab_widget)
            self.tabbar=rotatetab(self.tab_widget)
            self.tab_widget.setTabBar(self.tabbar) 
            self.tab_widget.tabBar().setObjectName("basetabbar")
            self.tab_widget.currentChanged.connect(self.basetabchanged)
            self.tab_widget.setStyleSheet(
                '''QTabBar#basetabbar:tab { 
                    width: %spx;
                    height: %spx;
                    font:%spt  ;  }
                '''%(50,self.window_width*0.2,15 if globalconfig['languageuse']==0 else 10  )
            )
            self.tab_widget.setTabPosition(QTabWidget.West)
            setTabOne(self)   
            setTabTwo(self)  
            
            setTabThree(self)  
            setTab7(self) 
            setTabcishu(self) 
            setTab5(self)
            
            setTab_quick(self) 
            
            setTablang(self) 
            setTab_proxy(self)
            setTab_about(self) 
            self.isfirstshow=False
    def setstylesheet(self):
        self.setStyleSheet("font: %spt '"%(globalconfig['settingfontsize'])+(globalconfig['settingfonttype']  )+"' ;  " )  
    def makevbox(self,wids): 
        q=QWidget()
        v=QVBoxLayout()
        q.setLayout(v)
        v.setContentsMargins(0,0,0,0)
        for wid in wids:
            v.addWidget(wid)
        return q
    def makegrid(self,grid,save=False,savelist=None,savelay=None  ):
        
         
        gridlayoutwidget = gridwidget(  )  
        gridlay=QGridLayout( )     
        gridlayoutwidget.setLayout(gridlay)   
        gridlayoutwidget.setStyleSheet("gridwidget{background-color:transparent;}") 
        self.needfitwidgets.append(gridlayoutwidget)
        gridlayoutwidget.setFixedHeight(len(grid)*35)
        self.automakegrid(gridlay,grid,save,savelist  ) 
        if save:
            savelay.append(gridlay)
        return gridlayoutwidget
    def makescroll(self,widget ):   
        scroll = QScrollArea( )   
        scroll.setHorizontalScrollBarPolicy(1)
        scroll.setStyleSheet('''QScrollArea{background-color:transparent;border:0px}''')  
        scroll.verticalScrollBar().setStyleSheet("QScrollBar{width:%spx;}"%self.scrollwidth)
         
        self.needfitwidgets.append(widget)
        scroll.setWidget(widget) 
        return scroll 
    def basetabchanged(self,i):
        try:
            w=self.tab_widget.currentWidget()
            if 'lazyfunction' in dir(w):
                w.lazyfunction()
                delattr(w,'lazyfunction') 
                self.resizefunction()  
        except: 
            print_exc()
    def makesubtab(self,titles,widgets):
        tab=QTabWidget()
        for i,wid in enumerate(widgets): 
            self.tabadd(tab,titles[i], wid )
        return tab
     
    def makesubtab_lazy(self,titles,functions):
        tab=QTabWidget()
        def __(t,i):
            try:
                w=t.currentWidget()
                if 'lazyfunction' in dir(w):
                    w.lazyfunction()
                    delattr(w,'lazyfunction') 
                    self.resizefunction()  
            except: 
                print_exc()
        tab.currentChanged.connect(functools.partial(__,tab))
        for i,func in enumerate(functions): 
            self.tabadd_lazy(tab,titles[i], func )
        return tab
    def tabadd_lazy(self,tab,title,getrealwidgetfunction):
        q=QWidget()
        v=QVBoxLayout()
        q.setLayout(v)
        v.setContentsMargins(0,0,0,0) 
        q.lazyfunction=lambda :v.addWidget(getrealwidgetfunction()) 
        self.tabadd(tab,title, q )  
    def tabadd(self,tab,title,widgets):  
            tab.addTab(widgets,_TR(title)) 
     
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
             
