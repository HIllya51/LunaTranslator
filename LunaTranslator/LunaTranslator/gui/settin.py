 
from PyQt5.QtCore import Qt,QSize,pyqtSignal  
from PyQt5.QtWidgets import  QColorDialog,QSpinBox,QDoubleSpinBox,QPushButton,QComboBox,QLabel,QScrollArea,QWidget,QGridLayout,QApplication,QTabBar,QVBoxLayout
from PyQt5.QtGui import QColor  ,QResizeEvent 
from PyQt5.QtWidgets import  QTabWidget 
import qtawesome  
import functools,time
from traceback import print_exc 
from myutils.config import globalconfig ,_TR
from myutils.utils import wavmp3player
from myutils.config import globalconfig 
from myutils.hwnd import getScreenRate
from gui.settingpage1 import setTabOne,setTabOne_direct
from gui.settingpage2 import setTabTwo,settab2d
from gui.settingpage_xianshishezhi import setTabThree ,setTabThree_direct
from gui.settingpage_tts import setTab5 ,setTab5_direct 
from gui.settingpage_cishu import setTabcishu
from gui.settingpage_quick import setTab_quick,setTab_quick_direct
from gui.setting_lang import setTablang
from gui.setting_proxy import setTab_proxy
from gui.settingpage7 import setTab7 ,settab7direct
from gui.settingpage_about import setTab_about,setTab_about_dicrect  
from gui.usefulwidget import  rotatetab
from gui.usefulwidget import closeashidewindow   
class gridwidget(QWidget):
    pass
class Settin(closeashidewindow) : 
    voicelistsignal=pyqtSignal(list,int)
    mp3playsignal=pyqtSignal(str,int) 
    versiontextsignal=pyqtSignal( str)
    progresssignal=pyqtSignal(str,int) 
    fontbigsmallsignal=pyqtSignal(int)  
    clicksourcesignal=pyqtSignal(str)
    opensolvetextsig=pyqtSignal()
    showandsolvesig=pyqtSignal(str)
    def resizefunction(self):
         
        for w in self.needfitwidgets: 
            w.setFixedWidth(int(self.size().width()- self.window_width*0.2 -self.scrollwidth))
        for grid,maxl in self.needfitcols:
            for c in range(maxl):
                grid.setColumnMinimumWidth(c,int(self.size().width()- self.window_width*0.2-self.scrollwidth//maxl))
        
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
                            if type(wid)==str  :
                                wid=QLabel((wid))
                                if arg=='link':
                                    wid.setOpenExternalLinks(True)
                        grid.addWidget(wid,nowr,nowc,1,cols)
                        if save:
                            ll.append(wid)
                        nowc+=cols   
                maxl=max(maxl,nowc)
                if save:
                    savelist.append(ll)

                grid.setRowMinimumHeight(nowr,int(35*self.rate))
        self.needfitcols.append([grid,maxl])
    
    def __init__(self, parent): 
        self.needfitwidgets=[]
        self.needfitcols=[]
        super(Settin, self).__init__(parent,globalconfig,'setting_geo_2') 
        #self.setWindowFlag(Qt.Tool,False)
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player=wavmp3player() 
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)  
        self.opensolvetextsig.connect(self.opensolvetextfun)
        
        
        self.setMinimumSize(100,100)
        # 界面缩放比例
        self.rate = getScreenRate()
        # 界面尺寸
        self.window_width = int((900 if globalconfig['languageuse']==0 else 1200)*self.rate)
         
        self.window_height = int(500*self.rate)
        self.scrollwidth=20*self.rate
        self.savelastrect=None 
           
        
        self.hooks=[] 

         
        self.usevoice=0
        self.isfirstshow=True

        setTabOne_direct(self)
        settab2d(self)
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
            
            self.tab_widget = self.makesubtab_lazy() 
            self.setCentralWidget(self.tab_widget)
            self.tabbar=rotatetab(self.tab_widget)
            self.tab_widget.setTabBar(self.tabbar) 
            self.tab_widget.tabBar().setObjectName("basetabbar")
            self.tab_widget.setStyleSheet(
                '''QTabBar#basetabbar:tab { 
                    width: %spx;
                    height: %spx;
                    font:%spt  ;  }
                '''%(50*self.rate,self.window_width*0.2,globalconfig['tabfont_chs'] if globalconfig['languageuse']==0 else globalconfig['tabfont_otherlang']  )
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
        gridlayoutwidget.setFixedHeight(int(len(grid)*35*self.rate))
        margins=gridlay.contentsMargins()
        gridlay.setContentsMargins(margins.left(),0,margins.right(),0)
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
     
    def makesubtab(self,titles,widgets):
        tab=QTabWidget()
        for i,wid in enumerate(widgets): 
            self.tabadd(tab,titles[i], wid )
        return tab
     
    def makesubtab_lazy(self,titles=None,functions=None):
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
        if titles and functions:
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
     