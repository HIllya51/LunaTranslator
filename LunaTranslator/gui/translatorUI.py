 
import functools  
from threading import Thread
import threading 
import time
t1=time.time()
import os
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint,pyqtSignal  
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QPoint,QRect,QSize  ,QPointF
from PyQt5.QtGui import QPen,QColor,QFont,QTextCharFormat ,QIcon,QPixmap ,QPainter,QPainterPath,QPalette
from PyQt5.QtWidgets import  QLabel,QTextBrowser,QPushButton ,QSystemTrayIcon ,QAction,QMenu,QGraphicsEffect
import pyperclip 
from PyQt5.QtCore import QProcess ,QByteArray ,QTimer
from utils.config import globalconfig,postprocessconfig
import win32api,win32gui,win32con
import gui.rangeselect
import gui.transhist

class QTitleButton(QPushButton):
    """
    新建标题栏按钮类
    """

    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        self.setFont(QFont("Webdings"))  # 特殊字体以不借助图片实现最小化最大化和关闭按钮
        
 

class QUnFrameWindow(QWidget):
    """
    无边框窗口类
    """
    keeptopsignal=pyqtSignal()
    clear_text_sign = pyqtSignal() 
    displayres =  pyqtSignal(str,str ) 
    displayraw1 =  pyqtSignal( str,str,int )
    displayraw =  pyqtSignal( str,str )
    displaystatus=pyqtSignal(str) 
    startprocessignal=pyqtSignal(str,list)
    writeprocesssignal=pyqtSignal(QByteArray)
    killprocesssignal=pyqtSignal()
    hookfollowsignal=pyqtSignal(int,tuple)
    def keeptopfuntion(self):
        win32gui.BringWindowToTop(int(self.winId()))
    def hookfollowsignalsolve(self,code,other): 
        if code==3:
            if self.hideshownotauto:
                self.show()
        elif code==4:
            if self.hideshownotauto:
                self.hide() 
        elif code==5:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)
            self.move(self.pos().x()+self.rate *other[0],self.pos().y()+self.rate *other[1])
    def showres(self,_type,res): 
        if globalconfig['showfanyisource']:
            #print(_type)
            self.showline(globalconfig['fanyi'][_type]['name']+'  '+res,globalconfig['fanyi'][_type]['color']  )
        else:
            self.showline(res,globalconfig['fanyi'][_type]['color']  )
        
        self.logff.write(globalconfig['fanyi'][_type]['name']+'  '+res+'\n')
        
        self.transhis.getnewsentencesignal.emit(globalconfig['fanyi'][_type]['name']+'  '+res)
    def showraw(self,res,color,show ):
        self.clearText()
        self.original=res 
        if show==1: 
            self.showline(res,color )
        
        self.logff.write('\n'+res+'\n')
        self.transhis.getnewsentencesignal.emit('\n'+res)
    def showline(self,res,color ): 
        
            
        if globalconfig['iskongxin'] == True :
            if self.lastcolor!=color:  
                self.format.setTextOutline(QPen(QColor(color), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                self.translate_text.mergeCurrentCharFormat(self.format)
            
            self.translate_text.append(res)
            
        else : 
            self.translate_text.append("<font color=%s>%s</font>"%(color,res)) 
    
    def clearText(self) :
     
        # 翻译界面清屏
        self.translate_text.clear()

        # 设定翻译时的字体类型和大小
        self.font.setFamily(globalconfig['fonttype'])
        self.font.setPointSizeF(globalconfig['fontsize'])
        self.translate_text.setFont(self.font) 
    def leftclicktray(self,reason):
            #鼠标左键点击
            if reason == QSystemTrayIcon.Trigger:
                
                if self.isHidden():
                    self.show_and_enableautohide() 
                else:
                    self.hide_and_disableautohide()
    def hide_and_disableautohide(self):
        self.hideshownotauto=False
        self.hide()
    def show_and_enableautohide(self):
        self.hideshownotauto=True
        self.show()
    def startprocessfunction(self,path,stdoutcallback):
        if 'p' in dir(self):
            self.p.kill()
        self.p = QProcess()    
        self.p.readyReadStandardOutput.connect(functools.partial(stdoutcallback[0],self.p))  
        self.p.start(path)

    def writeprocess(self,qb):
        self.p.write(qb)
    def killprocess(self):
        if 'p' in dir(self):
            self.p.kill() 
           
    def __init__(self, object):
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)  # 设置为顶级窗口，无边框
        #self.setFocusPolicy(Qt.StrongFocus)

        self.setAttribute(Qt.WA_TranslucentBackground) 

        
        self.object = object
        self.rate = self.object.screen_scale_rate 
        self.startprocessignal.connect(self.startprocessfunction)
        self.writeprocesssignal.connect(self.writeprocess)
        self.killprocesssignal.connect(self.killprocess)
        self._padding = 5*self.rate  # 设置边界宽度为5
        self.setMinimumWidth(300)
        self.hideshownotauto=True
        self.transhis=gui.transhist.transhist()
        self.logff=open('./log.txt','a',encoding='utf8')
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.keeptopsignal.connect(self.keeptopfuntion)
        self.hookfollowsignal.connect(self.hookfollowsignalsolve) 
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)
        self.displayraw.connect(self.showline) 
        self.clear_text_sign.connect(self.clearText)
        self.object = object 
        self.lastcolor='' 
        # 界面缩放比例
        
         
        self.original = ""    
        self._isTracking=False
        self.isontop=True
        self.initTitleLabel()  # 安放标题栏标签
         
        self.initLayout()  # 设置框架布局
        # self.setMinimumWidth(500)
        # self.setMinimumHeight(100)
        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        self.initDrag()  # 设置鼠标跟踪判断默认值
        self.setStyleSheet(''' 
      QTitleButton{
          background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;
      }
      QTitleButton#MinMaxButton:hover{
          background-color: #D0D0D1;
          border: 0px;
          font: 100 10pt;
      }
      QTitleButton#CloseButton:hover{
          background-color: #D32424;
          color: white;
          border: 0px;
          font: 100 10pt;
      }''')
          
        
        # label = QLabel(self.tab_3)
        # self.customSetGeometry(label, 20, 270, 100, 20)
        # label.setText("鼠标穿透窗口:")
 
        # self.fixedheight_switch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['fixedheight'] )
        # self.customSetGeometry(self.fixedheight_switch, 120, 270,20,20)
        # self.fixedheight_switch.clicked.connect(lambda x:globalconfig.__setitem__('fixedheight',x)) 

        # self.object.translation_ui.setAttribute(Qt.WA_TransparentForMouseEvents, True);

        self.mousetransparent=False
        self.buttons=[] 
                 
        self.takusanbuttons(qtawesome.icon("fa.rotate-right" ,color="white"),"MinMaxButton",self.startTranslater,0,"重新翻译")
        self.takusanbuttons(qtawesome.icon("fa.forward" ,color="#FF69B4" if globalconfig['autorun'] else 'white'),"MinMaxButton",self.changeTranslateMode,1,"自动翻译",'automodebutton')
        self.takusanbuttons(qtawesome.icon("fa.gear",color="white" ),"MinMaxButton",self.clickSettin,2,"设置")
        self.takusanbuttons(qtawesome.icon("fa.crop" ,color="white"),"MinMaxButton",self.clickRange,3,"选取OCR范围")
        self.takusanbuttons((qtawesome.icon("fa.square" ,color='white')),"MinMaxButton",self.showhide,4,"显示/隐藏范围框",'showhidebutton')
        self.takusanbuttons(qtawesome.icon("fa.copy" ,color="white"),"MinMaxButton",lambda: pyperclip.copy(self.original),5,"复制到剪贴板") 
        self.takusanbuttons(qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color="white"),"MinMaxButton", self.changeshowhideraw,6,"显示/隐藏原文",'showhiderawbutton') 
        
        self.takusanbuttons(qtawesome.icon("fa.rotate-left" ,color="white"),"MinMaxButton", self.transhis.show  ,7,"显示历史翻译") 
        self.takusanbuttons(qtawesome.icon("fa.music" ,color="white"),"MinMaxButton",self.langdu,8,"朗读") 
        self.takusanbuttons(qtawesome.icon("fa.mouse-pointer" ,color="white"),"MinMaxButton",self.changemousetransparentstate,9,"鼠标穿透窗口",'mousetransbutton') 
         
        self.takusanbuttons(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'),"MinMaxButton",self.changetoolslockstate,10,"锁定工具栏",'locktoolsbutton') 
        self.takusanbuttons(qtawesome.icon("fa.minus",color="white" ),"MinMaxButton",self.hide_and_disableautohide,-2,"最小化到托盘")
        self.takusanbuttons(qtawesome.icon("fa.times" ,color="white"),"CloseButton",self.quitf,-1,"退出")
        self.resize(int(globalconfig['width'] ), int(150*self.rate))
        self.move(QPoint(globalconfig['position'][0],globalconfig['position'][1])) 
         
        icon = QIcon()
        icon.addPixmap(QPixmap('./files/luna.jpg'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.setWindowTitle('LunaTranslator')

        self.tray = QSystemTrayIcon()  
        self.tray.setIcon(icon) 
        
        showAction = QAction("&显示", self, triggered = self.show_and_enableautohide)
        quitAction = QAction("&退出", self, triggered = self.quitf)
                
        
        self.tray.activated.connect(self.leftclicktray)

        # 创建菜单对象
        self.trayMenu = QMenu(self)
        # 将动作对象添加到菜单
        self.trayMenu.addAction(showAction)
        # 增加分割线
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(quitAction)
        # 将菜单栏加入到右键按钮中
        self.tray.setContextMenu(self.trayMenu) 
        self.tray.show()
        self.font = QFont() 
        self.font.setFamily(globalconfig['fonttype'])
        self.font.setPointSize(globalconfig['fontsize']) 
        self.translate_text = QTextBrowser(self) 
        self.translate_text.setText('欢迎使用')
        self.translate_text.setObjectName('text')
        self.translate_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translate_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translate_text.setFont(self.font)
        self.translate_text.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
        self._TitleLabel.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
        self.translate_text.move(0,30*self.rate)
        self.format = QTextCharFormat() 
        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()
        self.document.contentsChanged.connect(self.textAreaChanged) 
          
        self.masklabel = QLabel(self)  
         
        self.masklabel.setGeometry( 0, 30,9999,9999)
        self.masklabel.setMouseTracking(True)
        self.showhidestate=False
    def changemousetransparentstate(self,checked):
         
        self.mousetransparent= not self.mousetransparent
        if self.mousetransparent:
            # self.masklabel.setAttribute(Qt.WA_TransparentForMouseEvents,  self.mousetransparent) 
            # self.translate_text.setAttribute(Qt.WA_TransparentForMouseEvents,  self.mousetransparent)  
            self.translate_text.setStyleSheet("border-width:0;\
                                                                    border-style:outset;\
                                                                    border-top:0px solid #e8f3f9;\
                                                                    color:white;\
                                                               \
                                                                    background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),0))
            if globalconfig['locktools']==False:
                globalconfig['locktools']=not globalconfig['locktools'] 
                self.locktoolsbutton.setIcon(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'))
        
        else:
            self.object.translation_ui.translate_text.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
        self.mousetransbutton.setIcon(qtawesome.icon("fa.mouse-pointer" ,color="#FF69B4" if self.mousetransparent else 'white'))
    def showhide(self):
        
        self.showhidestate=not self.showhidestate
        #self.showhidebutton.setIcon(qtawesome.icon("fa.eye" if self.showhidestate else "fa.eye-slash" ,color="white"))
        self.showhidebutton.setIcon(qtawesome.icon("fa.square" ,color="#FF69B4" if self.showhidestate else 'white'))
        if self.showhidestate:
            self.object.range_ui.show()
        else:
            self.object.range_ui.hide()
    def changeshowhideraw(self,checked):
        self.object.settin_ui.show_original_switch.click()
        
    def changeTranslateMode(self, checked) : 
        globalconfig['autorun']=not globalconfig['autorun'] 
        self.automodebutton.setIcon(qtawesome.icon("fa.forward" ,color="#FF69B4" if globalconfig['autorun'] else 'white'))
    def changetoolslockstate(self,checked):
        if self.mousetransparent: 
            self.mousetransbutton.click()
        globalconfig['locktools']=not globalconfig['locktools'] 
        self.locktoolsbutton.setIcon(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'))
        
    def textAreaChanged(self) :
        if globalconfig['fixedheight']:
            return
        newHeight = self.document.size().height()
        
        width = self.width()
        self.resize(width, newHeight + 30*self.rate) 
         
    def clickSettin(self) :
          
        self.object.settin_ui.show()
        self.object.settin_ui.setFocus()
        # 按下范围框选键
    def clickRange(self): 
        self.showhidestate=False
        self.showhide()
        
        self.object.range_ui.hide()
        self.object.screen_shot_ui =gui.rangeselect.rangeselct(self.object)
        self.object.screen_shot_ui.show()
        
        self.show()
    def langdu(self):
        #print(self.original)
        
        if self.object.reader:
            self.object.reader.read(self.original )
        else:
            pass
    # 按下翻译键
    def startTranslater(self) :
        if hasattr(self.object,'textsource') and  self.object.textsource :
            Thread(target=self.object.textsource.runonce).start()
         
    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False

    def initTitleLabel(self):
        # 安放标题栏标签
        self._TitleLabel = QLabel(self)
        self._TitleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._TitleLabel.setFixedHeight(30*self.rate)
        # 设置标题栏标签鼠标跟踪（如不设，则标题栏内在widget上层，无法实现跟踪）
        self._TitleLabel.setMouseTracking(True)
        self._TitleLabel.setIndent(10)  # 设置标题栏文本缩进
        self._TitleLabel.move(0, 0)  # 标题栏安放到左上角

    def initLayout(self):
        # 设置框架布局
        self._MainLayout = QVBoxLayout()
        self._MainLayout.setSpacing(0)
        # 顶一个QLabel在竖放框架第一行，以免正常内容挤占到标题范围里
        self._MainLayout.addWidget(QLabel(), Qt.AlignLeft)
        self._MainLayout.addStretch()
        self.setLayout(self._MainLayout)
 
  
    def leaveEvent(self, QEvent) : 
        if globalconfig['locktools']:
            return 
        for button in self.buttons:
            button.hide()    
        self._TitleLabel.setStyleSheet("  background-color: rgba(0,0,0,0)")
    def enterEvent(self, QEvent) : 
 
        for button in self.buttons:
            button.show()  
        self._TitleLabel.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                                 font-weight: bold;\
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
    def resizeEvent(self, QResizeEvent):
         
         
        height = self.height() - 30*self.rate 
        
        #self.translate_text.resize(self.width(), height )
        self.translate_text.setGeometry(0, 30 * self.rate, self.width(), height * self.rate)
         
        for button in self.buttons:
              if button.adjast:
                button.adjast( ) 
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())  

        if self._move_drag ==False:
            # self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
            #                     for y in range(1, self.height() - self._padding)]
            # self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
            #                     for y in range(self.height() - self._padding, self.height() + 1)]
            # self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
            #                     for y in range(self.height() - self._padding, self.height() + 1)]
            self._right_rect = [self.width() - self._padding, self.width() + 1 ,30*self.rate, self.height() - self._padding]
            self._left_rect = [-1, self._padding,30*self.rate, self.height() - self._padding]
            self._bottom_rect = [self._padding, self.width() - self._padding,self.height() - self._padding, self.height() + 1]
            self._corner_rect = [self.width() - self._padding, self.width() + 1,self.height() - self._padding, self.height() + 1]
            self._lcorner_rect = [-1, self._padding,self.height() - self._padding, self.height() + 1]
    def isinrect(self,pos,rect):
        x,y=pos.x(),pos.y()
        x1,x2,y1,y2=rect
        if x>=x1 and x<=x2 and y<=y2 and y>=y1:
            return True
        else:
            return False
    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
         
        if (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(), self._corner_rect)):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._right_rect)):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._left_rect)):
            # 鼠标左键点击右侧边界区域
            self._left_drag = True 
            self.startxp=(event.globalPos() - self.pos() ) 
            self.startx=event.globalPos().x()
            self.startw=self.width()
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._bottom_rect)):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._lcorner_rect)):
            # 鼠标左键点击下侧边界区域
            self._lcorner_drag = True 
            self.startxp=(event.globalPos() - self.pos() ) 
            self.startx=event.globalPos().x()
            self.startw=self.width()
        # and (event.y() < self._TitleLabel.height()):
        elif (event.button() == Qt.LeftButton):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos() 

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势 
        pos=QMouseEvent.pos()
        if self._move_drag ==False:
            if self.isinrect( pos,self._corner_rect):
                self.setCursor(Qt.SizeFDiagCursor)
            elif self.isinrect( pos,self._lcorner_rect):
                self.setCursor(Qt.SizeBDiagCursor)
            elif self.isinrect(pos ,self._bottom_rect):
                self.setCursor(Qt.SizeVerCursor)
            elif self.isinrect(pos ,self._right_rect):
                self.setCursor(Qt.SizeHorCursor)
            elif self.isinrect(pos ,self._left_rect):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._right_drag:
            
            # 右侧调整窗口宽度
            self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._left_drag:
            # 右侧调整窗口宽度  
            self.setGeometry((QMouseEvent.globalPos() - self.startxp).x(),self.y(),self.startw-(QMouseEvent.globalPos().x() - self.startx),self.height())
            #self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y()) 
        elif Qt.LeftButton and self._lcorner_drag:
            # 下侧调整窗口高度
            self.setGeometry((QMouseEvent.globalPos() - self.startxp).x(),self.y(),self.startw-(QMouseEvent.globalPos().x() - self.startx),QMouseEvent.pos().y())
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(pos.x(),pos.y()) 
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition) 

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False
    def takusanbuttons(self,iconname,objectname,clickfunc,adjast=None,tips=None,save=None): 
        
        button=QTitleButton(self)
        button.setIcon(iconname)
        if tips:
            button.setToolTip(tips) 
        button.setIconSize(QSize(int(20*self.rate),
                                 int(20*self.rate)))
        if save:
              setattr(self,save,button)
        button.setObjectName(objectname)
        button.setFixedWidth(40*self.rate)
        button.setMouseTracking(True)
        button.setFixedHeight( self._TitleLabel.height() )
        button.clicked.connect(clickfunc)
         
        if adjast<0: 
            button.adjast=lambda  :button.move(self.width() + adjast*button.width() , 0) 
        else: 
            button.move(adjast*button.width() , 0) 
            button.adjast=None
        self.buttons.append(button)
    
    def customSetGeometry(self, object, x, y, w, h):
    
        object.setGeometry(QRect(int(x * self.rate),
                                 int(y * self.rate), int(w * self.rate),
                                 int(h * self.rate)))
  
    def quitf(self) :  
        import json  
        globalconfig['position']=[self.pos().x(),self.pos().y()]
        
        globalconfig['width']=self.width() 
        
        with open('./userconfig/config.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(globalconfig,ensure_ascii=False,sort_keys=False, indent=4))
        #self.hide()
        with open('./userconfig/postprocessconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(postprocessconfig,ensure_ascii=False,sort_keys=False, indent=4))
        
        self.logff.close()
        self.tray.hide()
        self.tray = None 
        self.object.range_ui.close()
        self.object.settin_ui.close()
        #print(4)
        self.object.hookselectdialog.realclose=True
        self.object.settin_ui.minmaxmoveoberve.kill()
        
        self.object.hookselectdialog.close()
        #print(5)
        # if 'textsource' in dir(self.object) and self.object.textsource and self.object.textsource.ending==False:
        #     self.object.textsource.end()
        #     if 'p' in dir(self.object.textsource):
        #         self.object.textsource.p.kill()
        #         self.object.textsource.p.terminate()
        #         self.object.textsource.p.waitForFinished () 
          
        # import ctypes 
        # for hookID in self.object.settin_ui.hooks:
        #     ctypes.windll.user32.UnhookWinEvent(hookID)
        #print(aa)  
        if self.object.textsource:
            self.object.textsource.end()
        
        self.close() 
        #print('closed')
        
        #sys.exit()
        os._exit(1) 
        #self.quit()
        #self.quit()
        #报异常来退出，不然老是有僵尸进程。